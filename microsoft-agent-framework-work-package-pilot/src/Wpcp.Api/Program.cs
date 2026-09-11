using System.Collections.Concurrent;
using System.Net;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Wpcp.Domain;
using Wpcp.Storage.Postgres;

var options = ApiOptions.Parse(args);
var fixture = SyntheticProviderFixture.Load(options.FixturePath);
using var providerClient = GitHubRepositoryAuthorization.CreateClient();
IRepositoryAuthorization authorization = new GitHubRepositoryAuthorization(providerClient);
await using var store = new PostgresImplementationRunStore(
    options.ConnectionString,
    fixture.RedactionPolicy);
await store.EnsureSchemaAsync();

var runtime = new ApiRuntime(Guid.NewGuid().ToString("D"), DateTimeOffset.UtcNow);
var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.WebHost.UseUrls(options.Urls);

var app = builder.Build();
app.Use(async (context, next) =>
{
    context.Response.Headers.CacheControl = "no-store";
    try { await next(context); }
    catch (Npgsql.NpgsqlException)
    {
        context.Response.StatusCode = 503;
        await context.Response.WriteAsJsonAsync(new { code = "run-store-unavailable" });
    }
});
app.MapGet("/healthz", () => Results.Text("Healthy"));

app.MapPost(
    "/api/v1/issues/{repositoryId}/{issueNumber:int}/runs",
    async (
        string repositoryId,
        int issueNumber,
        StartRunRequest? request,
        HttpContext context,
        CancellationToken cancellationToken) =>
    {
        if (!HasFixtureAccess(context, options))
        {
            return JsonError("synthetic-access-denied", StatusCodes.Status403Forbidden);
        }

        if (!TryCreateCommand(fixture, repositoryId, issueNumber, request, out var command))
        {
            return JsonError("invalid-start-command", StatusCodes.Status400BadRequest);
        }

        var access = await authorization.EvaluateAsync(fixture.FindRepositoryBinding(repositoryId)!, Credential(context), cancellationToken);
        if (!access.CanContribute || !access.IsHuman)
            return AccessError(access, "repository-contribution-required");
        command = command with { ActorId = $"{access.Actor!.Provider}:{access.Actor.SubjectId}", Actor = access.Actor,
            Repository = fixture.FindRepositoryBinding(repositoryId) };

        StartRunResult result;
        try
        {
            result = await store.StartAsync(command, cancellationToken);
        }
        catch (RepositoryBindingConflictException)
        {
            return JsonError("repository-access-denied", StatusCodes.Status403Forbidden);
        }
        catch (ArgumentException)
        {
            return JsonError("invalid-start-command", StatusCodes.Status400BadRequest);
        }
        catch (Npgsql.NpgsqlException)
        {
            return JsonError("run-store-unavailable", StatusCodes.Status503ServiceUnavailable);
        }

        if (result.Disposition is StartRunDisposition.Accepted or StartRunDisposition.Idempotent)
        {
            try
            {
                await ObserveApiProcessAsync(store, runtime, result.RunId, cancellationToken);
            }
            catch (Npgsql.NpgsqlException)
            {
                // The admission transaction is already durable. A retry of the
                // same command returns the same run and can record this observation.
                return JsonError("run-store-unavailable", StatusCodes.Status503ServiceUnavailable);
            }
        }

        return result.Disposition switch
        {
            StartRunDisposition.Accepted => Results.Json(result, statusCode: StatusCodes.Status201Created),
            StartRunDisposition.Idempotent => Results.Json(result, statusCode: StatusCodes.Status200OK),
            StartRunDisposition.CommandIdConflict or StartRunDisposition.IssueAlreadyHasRun =>
                Results.Json(result, statusCode: StatusCodes.Status409Conflict),
            _ => JsonError("invalid-start-command", StatusCodes.Status400BadRequest),
        };
    });

app.MapGet(
    "/api/v1/runs/{runId}",
    async (string runId, HttpContext context, CancellationToken cancellationToken) =>
    {
        if (!HasFixtureAccess(context, options))
        {
            return JsonError("synthetic-access-denied", StatusCodes.Status403Forbidden);
        }

        var decision = await store.DecideControlAsync(runId, null, null,
            (repository, ct) => authorization.EvaluateAsync(repository, Credential(context), ct), cancellationToken);
        if (!decision.Accepted) return Results.Json(decision, statusCode: DecisionStatus(decision));

        try
        {
            await ObserveApiProcessAsync(store, runtime, runId, cancellationToken);
        }
        catch (Npgsql.NpgsqlException)
        {
            return JsonError("run-store-unavailable", StatusCodes.Status503ServiceUnavailable);
        }

        var projection = await store.GetProjectionAsync(runId, cancellationToken);
        return Results.Json(projection! with { Authorization = decision with { Current = projection.Control } }, statusCode: StatusCodes.Status200OK);
    });

app.MapGet(
    "/api/v1/runs/{runId}/events",
    async (string runId, long? after, HttpContext context, CancellationToken cancellationToken) =>
    {
        if (!HasFixtureAccess(context, options))
        {
            return JsonError("synthetic-access-denied", StatusCodes.Status403Forbidden);
        }

        if (after is < 0)
        {
            return JsonError("invalid-event-position", StatusCodes.Status400BadRequest);
        }

        var decision = await store.DecideControlAsync(runId, null, null,
            (repository, ct) => authorization.EvaluateAsync(repository, Credential(context), ct), cancellationToken);
        if (!decision.Accepted) return Results.Json(decision, statusCode: DecisionStatus(decision));

        try
        {
            await ObserveApiProcessAsync(store, runtime, runId, cancellationToken);
        }
        catch (Npgsql.NpgsqlException)
        {
            return JsonError("run-store-unavailable", StatusCodes.Status503ServiceUnavailable);
        }

        var events = await store.GetEventsAfterAsync(runId, after ?? 0, cancellationToken);
        return Results.Json(events, statusCode: StatusCodes.Status200OK);
    });

app.MapGet("/api/v1/runs/{runId}/audit",
    async (string runId, HttpContext context, CancellationToken token) =>
    {
        if (!HasFixtureAccess(context, options)) return JsonError("synthetic-access-denied", 403);
        var decision = await store.DecideControlAsync(runId, null, null,
            (repository, ct) => authorization.EvaluateAsync(repository, Credential(context), ct), token);
        if (!decision.Accepted) return Results.Json(decision, statusCode: DecisionStatus(decision));
        return Results.Json(new { runId, entries = await store.GetAuditAsync(runId, token) });
    });

app.MapPost("/api/v1/runs/{runId}/control/{action}",
    async (string runId, string action, JsonElement body, HttpContext context, CancellationToken token) =>
    {
        if (!HasFixtureAccess(context, options)) return JsonError("synthetic-access-denied", 403);
        ControlMutation? mutation;
        try { mutation = body.Deserialize<ControlMutation>(new JsonSerializerOptions(JsonSerializerDefaults.Web)); }
        catch (JsonException) { mutation = null; }
        var decision = await store.DecideControlAsync(runId, action, mutation,
            (repository, ct) => authorization.EvaluateAsync(repository, Credential(context), ct), token);
        return Results.Json(decision, statusCode: DecisionStatus(decision));
    });

static int DecisionStatus(ControlDecision decision) => decision.Code switch
{
    "repository-provider-unavailable" => 503,
    "provider-authentication-required" => 401,
    "implementation-run-not-found" => 404,
    "invalid-control-action" or "invalid-control-mutation" => 400,
    _ when decision.Accepted => 200,
    _ when !decision.Access.CanContribute => 403,
    _ => 409,
};

try
{
    await app.RunAsync();
}
finally
{
    foreach (var observedRun in runtime.ObservedRuns)
    {
        try
        {
            await StopApiProcessAsync(store, runtime, observedRun.Key, observedRun.Value);
        }
        catch (Npgsql.NpgsqlException)
        {
            // Shutdown must not turn a previously durable run into a failed host
            // process merely because the supplemental lifecycle store is down.
        }
    }
}

static bool TryCreateCommand(
    SyntheticProviderFixture fixture,
    string repositoryId,
    int issueNumber,
    StartRunRequest? request,
    out StartRunCommand command)
{
    command = null!;
    if (request is null || string.IsNullOrWhiteSpace(request.CommandId) ||
        string.IsNullOrWhiteSpace(request.Note) ||
        request.Provenance is null)
    {
        return false;
    }

    var issue = fixture.FindIssue(repositoryId, issueNumber);
    if (issue is null)
    {
        return false;
    }

    try
    {
        command = new StartRunCommand(
            request.CommandId,
            "provider-pending",
            repositoryId,
            issue.IssueId,
            issueNumber,
            request.Note,
            new RunProvenance(
                request.Provenance.SourceRevision ?? string.Empty,
                request.Provenance.PackageRevision ?? string.Empty,
                request.Provenance.ConfigurationRevision ?? string.Empty,
                request.Provenance.ContractRevision ?? string.Empty));
        command.Validate();
        return true;
    }
    catch (ArgumentException)
    {
        return false;
    }
}

static string? Credential(HttpContext context)
{
    var value = context.Request.Headers.Authorization.ToString();
    return value.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase) ? value[7..] : null;
}

static IResult AccessError(RepositoryAccess access, string fallback) =>
    JsonError(access.FailureCode ?? fallback,
        access.FailureCode == "repository-provider-unavailable" ? 503 :
        access.FailureCode == "provider-authentication-required" ? 401 : 403);

static bool HasFixtureAccess(HttpContext context, ApiOptions options)
{
    var supplied = context.Request.Headers[FixtureAccessHeader.Name].ToString();
    if (string.IsNullOrEmpty(supplied))
    {
        return false;
    }

    var expectedBytes = Encoding.UTF8.GetBytes(options.FixtureAccessToken);
    var suppliedBytes = Encoding.UTF8.GetBytes(supplied);
    return suppliedBytes.Length == expectedBytes.Length &&
        CryptographicOperations.FixedTimeEquals(suppliedBytes, expectedBytes);
}

static async Task ObserveApiProcessAsync(
    IImplementationRunStore store,
    ApiRuntime runtime,
    string runId,
    CancellationToken cancellationToken)
{
    var observation = runtime.ObservedRuns.GetOrAdd(runId, static _ => new ApiRunObservation());
    await observation.Gate.WaitAsync(cancellationToken);
    try
    {
        if (!observation.Started)
        {
            await store.RecordLifecycleAsync(
                new LifecycleObservation(
                    runId,
                    LifecycleObservationKind.ProcessStarted,
                    "api",
                    runtime.ProcessId,
                    runtime.StartedAt),
                cancellationToken);
            observation.Started = true;
        }

        if (!observation.Stopped)
        {
            await store.RecordLifecycleAsync(
                new LifecycleObservation(
                    runId,
                    LifecycleObservationKind.Heartbeat,
                    "api",
                    runtime.ProcessId,
                    DateTimeOffset.UtcNow),
                cancellationToken);
        }
    }
    finally
    {
        observation.Gate.Release();
    }
}

static async Task StopApiProcessAsync(
    IImplementationRunStore store,
    ApiRuntime runtime,
    string runId,
    ApiRunObservation observation)
{
    await observation.Gate.WaitAsync(CancellationToken.None);
    try
    {
        if (!observation.Started || observation.Stopped)
        {
            return;
        }

        await store.RecordLifecycleAsync(
            new LifecycleObservation(
                runId,
                LifecycleObservationKind.ProcessStopped,
                "api",
                runtime.ProcessId,
                DateTimeOffset.UtcNow),
            CancellationToken.None);
        observation.Stopped = true;
    }
    finally
    {
        observation.Gate.Release();
    }
}

static IResult JsonError(string code, int statusCode) =>
    Results.Json(new { code }, statusCode: statusCode);

internal sealed record StartRunRequest(
    string? CommandId,
    string? Note,
    ProvenanceRequest? Provenance);

internal sealed record ProvenanceRequest(
    string? SourceRevision,
    string? PackageRevision,
    string? ConfigurationRevision,
    string? ContractRevision);

internal sealed class ApiRuntime(string processId, DateTimeOffset startedAt)
{
    public string ProcessId { get; } = processId;

    public DateTimeOffset StartedAt { get; } = startedAt;

    public ConcurrentDictionary<string, ApiRunObservation> ObservedRuns { get; } = new(StringComparer.Ordinal);
}

internal sealed class ApiRunObservation
{
    public SemaphoreSlim Gate { get; } = new(1, 1);

    public bool Started { get; set; }

    public bool Stopped { get; set; }
}

internal static class FixtureAccessHeader
{
    public const string Name = "X-Wpcp-Fixture-Access";
}

internal sealed record ApiOptions(
    string ConnectionString,
    string FixturePath,
    string FixtureAccessToken,
    string Urls)
{
    public static ApiOptions Parse(IReadOnlyList<string> arguments)
    {
        var values = ParseOptions(arguments);
        var connectionString = Value(values, "--connection-string") ??
            Environment.GetEnvironmentVariable("WPCP_CONNECTION_STRING");
        var fixturePath = Value(values, "--fixture");
        var fixtureAccessToken = Environment.GetEnvironmentVariable("WPCP_FIXTURE_ACCESS_TOKEN");
        var urls = Value(values, "--urls") ?? "http://127.0.0.1:5080";
        if (string.IsNullOrWhiteSpace(connectionString) || string.IsNullOrWhiteSpace(fixturePath) ||
            string.IsNullOrWhiteSpace(fixtureAccessToken))
        {
            throw new ArgumentException("The API requires --connection-string (or WPCP_CONNECTION_STRING), --fixture, and WPCP_FIXTURE_ACCESS_TOKEN.");
        }

        EnsureLoopbackUrls(urls);
        return new ApiOptions(connectionString, fixturePath, fixtureAccessToken, urls);
    }

    private static Dictionary<string, string> ParseOptions(IReadOnlyList<string> arguments)
    {
        var values = new Dictionary<string, string>(StringComparer.Ordinal);
        for (var index = 0; index < arguments.Count; index += 2)
        {
            if (!arguments[index].StartsWith("--", StringComparison.Ordinal) || index + 1 >= arguments.Count)
            {
                throw new ArgumentException("API options must be supplied as --name value pairs.");
            }

            values[arguments[index]] = arguments[index + 1];
        }
        return values;
    }

    private static string? Value(IReadOnlyDictionary<string, string> values, string name) =>
        values.TryGetValue(name, out var value) ? value : null;

    private static void EnsureLoopbackUrls(string urls)
    {
        var endpoints = urls.Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        if (endpoints.Length == 0 || endpoints.Any(endpoint => !IsLoopbackHttpUrl(endpoint)))
        {
            throw new ArgumentException("The synthetic fixture API may bind only loopback HTTP(S) URLs.");
        }
    }

    private static bool IsLoopbackHttpUrl(string value)
    {
        if (!Uri.TryCreate(value, UriKind.Absolute, out var parsed) ||
            (parsed.Scheme != Uri.UriSchemeHttp && parsed.Scheme != Uri.UriSchemeHttps))
        {
            return false;
        }

        return string.Equals(parsed.Host, "localhost", StringComparison.OrdinalIgnoreCase) ||
            (IPAddress.TryParse(parsed.Host, out var address) && IPAddress.IsLoopback(address));
    }
}

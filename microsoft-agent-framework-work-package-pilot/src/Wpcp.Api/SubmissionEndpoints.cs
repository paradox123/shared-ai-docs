using System.Net;
using static OperatorHttp;
using System.Text.Json;
using System.Text.RegularExpressions;
using Wpcp.Domain;
using Wpcp.Storage.Postgres;

internal static partial class SubmissionEndpoints
{
    public static void MapSubmissions(this WebApplication app, PostgresSubmissionStore store,
        IReadOnlyList<RepositoryBinding> bindings, IRepositoryAuthorization authorization, HttpClient github,
        PostgresImplementationRunStore runs, SubmissionExecutionConfiguration? execution)
    {
        app.MapPost("/api/v1/submissions", async (SubmitGitHubIssueRequest request,
            HttpContext context, CancellationToken token) => await WithSourceErrors(async () =>
        {
            var resolved = await ResolveAsync(request.SourceUrl, bindings, authorization, github, Credential(context), token);
            if (request.Start)
            {
                var existing = await store.FindBySourceAsync(resolved.Source.ProviderIssueId, token);
                if (existing is not null && existing.Repository != resolved.Repository) return Error("repository-identity-mismatch", 409);
                if (existing?.RunId is not null) return Results.Json(existing);
                await CheckRuntimeAsync(execution, token);
            }
            var admitted = await store.AdmitAsync(resolved.Title, resolved.Body, resolved.Source,
                resolved.Repository, resolved.Actor, token);
            if (!request.Start) return Results.Json(admitted.Submission, statusCode: admitted.Created ? 201 : 200);
            return await StartAsync(admitted.Submission, resolved.Actor, token);
        }));

        app.MapPost("/api/v1/submissions/{id:guid}/start", async (Guid id, HttpContext context,
            CancellationToken token) => await WithSourceErrors(async () =>
        {
            if (Credential(context) is null) return Error("provider-authentication-required", 401);
            var submission = await store.GetAsync(id, token);
            if (submission is null) return Error("submission-not-found", 404);
            var access = await authorization.EvaluateAsync(submission.Repository, Credential(context), token);
            if (!access.CanContribute || !access.IsHuman) return AccessError(access, "repository-contribution-required");
            if (submission.RunId is not null) return Results.Json(submission);
            var resolved = await ResolveAsync(submission.Source.Url, bindings, authorization, github, Credential(context), token);
            if (resolved.Repository != submission.Repository || resolved.Source.ProviderIssueId != submission.Source.ProviderIssueId)
                return Error("github-source-identity-mismatch", 409);
            await CheckRuntimeAsync(execution, token);
            return await StartAsync(submission, access.Actor!, token);
        }));

        async Task<IResult> StartAsync(Submission submission, ActorIdentity actor, CancellationToken token)
        {
            var created = await runs.StartSubmissionAsync(submission, actor, execution!, token);
            return Results.Json(await store.GetAsync(Guid.Parse(submission.SubmissionId), token), statusCode: created ? 202 : 200);
        }

        app.MapGet("/api/v1/submissions/{id:guid}/execution", async (Guid id, HttpContext context, CancellationToken token) =>
        {
            if (Credential(context) is null) return Error("provider-authentication-required", 401);
            var submission = await store.GetAsync(id, token);
            if (submission is null) return Error("submission-not-found", 404);
            var access = await authorization.EvaluateAsync(submission.Repository, Credential(context), token);
            if (!access.IsHuman || !access.CanRead) return AccessError(access, "repository-access-denied");
            var state = await runs.GetSubmissionExecutionAsync(id, token);
            return state is null ? Error("submission-not-started", 409) : Results.Json(state);
        });

        app.MapGet("/api/v1/submissions/{id:guid}", async (Guid id, HttpContext context, CancellationToken token) =>
        {
            if (Credential(context) is null) return Error("provider-authentication-required", 401);
            var submission = await store.GetAsync(id, token);
            if (submission is null) return Error("submission-not-found", 404);
            var access = await authorization.EvaluateAsync(submission.Repository, Credential(context), token);
            return access.IsHuman && access.CanRead ? Results.Json(submission) : AccessError(access, "repository-access-denied");
        });

        app.MapGet("/api/v1/submissions", async (HttpContext context, CancellationToken token) =>
        {
            if (Credential(context) is null) return Error("provider-authentication-required", 401);
            var submissions = await store.ListAsync(token);
            var allowed = new HashSet<RepositoryBinding>();
            foreach (var repository in bindings.Concat(submissions.Select(s => s.Repository)).Distinct())
            {
                var access = await authorization.EvaluateAsync(repository, Credential(context), token);
                if (access.FailureCode is "provider-authentication-required" or "repository-provider-unavailable" || !access.IsHuman)
                    return AccessError(access, "repository-access-denied");
                if (access.CanRead) allowed.Add(repository);
            }
            return Results.Json(new { submissions = submissions.Where(s => allowed.Contains(s.Repository)) });
        });
    }

    private sealed record ResolvedIssue(string Title, string Body, SubmissionSource Source,
        RepositoryBinding Repository, ActorIdentity Actor);
    private sealed class SourceFailure(string code, int status) : Exception
    {
        public string Code { get; } = code;
        public int Status { get; } = status;
    }

    private static async Task<IResult> WithSourceErrors(Func<Task<IResult>> work)
    {
        try { return await work(); }
        catch (SourceFailure error) { return Error(error.Code, error.Status); }
        catch (SubmissionRunConflictException) { return Error("issue-already-has-run", 409); }
        catch (RepositoryBindingConflictException) { return Error("repository-identity-mismatch", 409); }
        catch (ArgumentException) { return Error("submission-correlation-rejected", 422); }
        catch (Exception error) when (error is HttpRequestException or JsonException or InvalidOperationException
            or KeyNotFoundException or TaskCanceledException or FormatException)
        { return Error("github-source-unavailable", 503); }
    }

    private static async Task<ResolvedIssue> ResolveAsync(string? sourceUrl,
        IReadOnlyList<RepositoryBinding> bindings, IRepositoryAuthorization authorization,
        HttpClient github, string? credential, CancellationToken token)
    {
        var match = IssueUrl().Match(sourceUrl?.Trim() ?? "");
        if (!match.Success || !int.TryParse(match.Groups[3].Value, out var number))
            throw new SourceFailure("invalid-github-issue-url", 400);
        var name = match.Groups[1].Value + "/" + match.Groups[2].Value;
        var repository = bindings.FirstOrDefault(b => b.FullName.Equals(name, StringComparison.OrdinalIgnoreCase))
            ?? throw new SourceFailure("repository-not-configured", 403);
        var access = await authorization.EvaluateAsync(repository, credential, token);
        if (!access.CanContribute || !access.IsHuman)
            throw new SourceFailure(access.FailureCode ?? "repository-contribution-required",
                access.FailureCode == "provider-authentication-required" ? 401 :
                access.FailureCode == "repository-provider-unavailable" ? 503 : 403);
        var url = $"https://github.com/{repository.FullName}/issues/{number}";
        using var response = await GitHubRequests.GetAsync(github,
            $"repos/{repository.FullName}/issues/{number}", credential!, token);
        if (response.StatusCode == HttpStatusCode.NotFound) throw new SourceFailure("github-issue-not-found", 404);
        response.EnsureSuccessStatusCode();
        using var document = JsonDocument.Parse(await response.Content.ReadAsStringAsync(token));
        var issue = document.RootElement;
        if (issue.TryGetProperty("pull_request", out _)) throw new SourceFailure("github-source-is-pull-request", 422);
        if (issue.GetProperty("number").GetInt32() != number ||
            !url.Equals(issue.GetProperty("html_url").GetString(), StringComparison.OrdinalIgnoreCase))
            throw new SourceFailure("github-source-identity-mismatch", 409);
        if (issue.GetProperty("state").GetString() != "open") throw new SourceFailure("github-issue-closed", 422);
        if (!issue.GetProperty("labels").EnumerateArray().Any(l => l.GetProperty("name").GetString() == "ready-for-agent"))
            throw new SourceFailure("implementation-authorization-required", 422);
        var title = issue.GetProperty("title").GetString();
        var id = issue.GetProperty("id").GetInt64();
        if (id <= 0 || string.IsNullOrWhiteSpace(title)) throw new JsonException();
        return new(title, issue.GetProperty("body").GetString() ?? "",
            new("github", id, number, url, issue.GetProperty("updated_at").GetDateTimeOffset()), repository, access.Actor!);
    }

    private static async Task CheckRuntimeAsync(SubmissionExecutionConfiguration? configuration, CancellationToken token)
    {
        if (configuration is null) throw new SourceFailure("background-execution-not-configured", 503);
        if (!await PostgresImplementationRunStore.ArtifactStorageReadyAsync(token))
            throw new SourceFailure("artifact-storage-unavailable", 503);
        var serviceToken = Environment.GetEnvironmentVariable("WPCP_REAL_ADAPTER_TOKEN");
        if (string.IsNullOrWhiteSpace(serviceToken)) throw new SourceFailure("agent-credentials-unavailable", 503);
        try
        {
            using var client = new HttpClient(new HttpClientHandler { AllowAutoRedirect = false })
                { BaseAddress = new Uri(configuration.AdapterOrigin), Timeout = TimeSpan.FromSeconds(30) };
            client.DefaultRequestHeaders.Add("X-Wpcp-Adapter-Token", serviceToken);
            using var response = await client.GetAsync("submission-readiness", token);
            response.EnsureSuccessStatusCode();
            using var document = JsonDocument.Parse(await response.Content.ReadAsStringAsync(token));
            var readiness = document.RootElement;
            if (readiness.GetProperty("contractVersion").GetString() != "AgentSessionAdapter/v1" ||
                readiness.GetProperty("step").GetString() != SubmissionExecutionConfiguration.Step ||
                !readiness.GetProperty("runtimeReady").GetBoolean() || !readiness.GetProperty("sandboxReady").GetBoolean())
                throw new SourceFailure("agent-readiness-unavailable", 503);
        }
        catch (Exception error) when (error is HttpRequestException or JsonException or InvalidOperationException
            or KeyNotFoundException or TaskCanceledException)
        { throw new SourceFailure("agent-readiness-unavailable", 503); }
    }

    private static IResult Error(string code, int status) => Results.Json(new { code }, statusCode: status);

    [GeneratedRegex(@"\Ahttps://github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9_.-]+)/issues/([1-9][0-9]*)/?(?:\#[^\s]*)?\z", RegexOptions.IgnoreCase)]
    private static partial Regex IssueUrl();
}

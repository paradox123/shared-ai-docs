using System.Text.Json;
using Wpcp.Domain;
using Wpcp.Storage.Postgres;

var jsonOptions = new JsonSerializerOptions(JsonSerializerDefaults.Web);

try
{
    var options = WorkerOptions.Parse(args);
    var fixture = SyntheticProviderFixture.Load(options.FixturePath);
    await using var store = new PostgresImplementationRunStore(
        options.ConnectionString,
        fixture.RedactionPolicy);
    await store.EnsureSchemaAsync();

    var processId = $"{options.WorkerId}:{Guid.NewGuid():N}";
    await store.RecordLifecycleAsync(
        new LifecycleObservation(
            options.RunId,
            LifecycleObservationKind.ProcessStarted,
            "worker",
            processId,
            DateTimeOffset.UtcNow,
            options.AgentFrameworkWorkflowId,
            options.AgentFrameworkSessionId,
            options.DurableTaskOrchestrationId,
            options.DurableTaskTaskId,
            options.EvidenceNote));
    if (options.RepositoryPlanPath is not null)
        await Wpcp.Worker.RepositoryWorkflow.ExecuteAsync(store, options.RunId, options.RepositoryPlanPath, options.PauseAt);
    else if (options.FakeAgentOrigin is not null)
        await Wpcp.Worker.FakeAgentWorkflow.ExecuteAsync(store, options.RunId,
            options.FakeAgentOrigin, options.EvidenceNote ?? "controlled fake attempt",
            options.PauseAt, options.RejectBlocked, options.AgentTimeoutMilliseconds);
    for (var heartbeat = 0; heartbeat < options.HeartbeatCount; heartbeat++)
    {
        await Task.Delay(TimeSpan.FromMilliseconds(options.HeartbeatIntervalMilliseconds));
        await store.RecordLifecycleAsync(
            new LifecycleObservation(
                options.RunId,
                LifecycleObservationKind.Heartbeat,
                "worker",
                processId,
                DateTimeOffset.UtcNow));
    }

    var result = await store.RecordLifecycleAsync(
        new LifecycleObservation(
            options.RunId,
            LifecycleObservationKind.ProcessStopped,
            "worker",
            processId,
            DateTimeOffset.UtcNow));
    Console.Out.WriteLine(JsonSerializer.Serialize(result, jsonOptions));
}
catch (RepositoryExecutionRequiredException)
{
    Console.Out.WriteLine(JsonSerializer.Serialize(new { code = "repository-execution-required" }, jsonOptions));
    Environment.ExitCode = 2;
}
catch (AgentAssignmentConflictException)
{
    Console.Out.WriteLine(JsonSerializer.Serialize(new { code = "agent-assignment-conflict", category = "contract-incompatible" }, jsonOptions));
    Environment.ExitCode = 2;
}
catch (ArgumentException)
{
    Console.Out.WriteLine(JsonSerializer.Serialize(new { code = "invalid-worker-observation" }, jsonOptions));
    Environment.ExitCode = 2;
}
catch (Npgsql.NpgsqlException)
{
    Console.Out.WriteLine(JsonSerializer.Serialize(new { code = "run-store-unavailable", category = "infrastructure-failure" }, jsonOptions));
    Environment.ExitCode = 2;
}
catch (InvalidOperationException)
{
    Console.Out.WriteLine(JsonSerializer.Serialize(new { code = "implementation-run-not-found" }, jsonOptions));
    Environment.ExitCode = 2;
}
catch (Exception)
{
    Console.Out.WriteLine(JsonSerializer.Serialize(new { code = "worker-execution-failed", category = "infrastructure-failure" }, jsonOptions));
    Environment.ExitCode = 2;
}

internal sealed record WorkerOptions(
    string ConnectionString,
    string FixturePath,
    string RunId,
    string WorkerId,
    string? AgentFrameworkWorkflowId,
    string? AgentFrameworkSessionId,
    string? DurableTaskOrchestrationId,
    string? DurableTaskTaskId,
    string? EvidenceNote,
    int HeartbeatCount,
    int HeartbeatIntervalMilliseconds,
    string? FakeAgentOrigin,
    string? PauseAt,
    bool RejectBlocked,
    int AgentTimeoutMilliseconds,
    string? RepositoryPlanPath)
{
    public static WorkerOptions Parse(IReadOnlyList<string> arguments)
    {
        var values = ParseOptions(arguments);
        var connectionString = Value(values, "--connection-string") ??
            Environment.GetEnvironmentVariable("WPCP_CONNECTION_STRING");
        var fixturePath = Value(values, "--fixture");
        var runId = Value(values, "--run-id");
        var workerId = Value(values, "--worker-id");
        var heartbeatCount = PositiveIntegerOrDefault(values, "--heartbeat-count", 2);
        var heartbeatIntervalMilliseconds = PositiveIntegerOrDefault(
            values,
            "--heartbeat-interval-milliseconds",
            25);
        if (string.IsNullOrWhiteSpace(connectionString) || string.IsNullOrWhiteSpace(fixturePath) ||
            !Guid.TryParse(runId, out _) || string.IsNullOrWhiteSpace(workerId))
        {
            throw new ArgumentException("Missing worker lifecycle options.");
        }

        var pauseAt = Value(values, "--pause-at");
        if (pauseAt is not (null or "after-session-start" or "after-session-mapping" or "after-result-observed" or "after-git-effect" or "after-provider-effect" or "after-reconciled-effect" or "after-session-receipt"))
            throw new ArgumentException("Unknown fake fault boundary.");
        var rejectText = Value(values, "--reject-blocked");
        if (rejectText is not (null or "true" or "false"))
            throw new ArgumentException("--reject-blocked must be true or false.");
        return new WorkerOptions(
            connectionString,
            fixturePath,
            runId,
            workerId,
            Value(values, "--agent-framework-workflow-id"),
            Value(values, "--agent-framework-session-id"),
            Value(values, "--durable-task-orchestration-id"),
            Value(values, "--durable-task-task-id"),
            Value(values, "--evidence-note"),
            heartbeatCount,
            heartbeatIntervalMilliseconds,
            Value(values, "--fake-agent-origin"),
            pauseAt,
            rejectText == "true",
            PositiveIntegerOrDefault(values, "--agent-timeout-ms", 10000),
            Value(values, "--repository-plan"));
    }

    private static Dictionary<string, string> ParseOptions(IReadOnlyList<string> arguments)
    {
        var values = new Dictionary<string, string>(StringComparer.Ordinal);
        for (var index = 0; index < arguments.Count; index += 2)
        {
            if (!arguments[index].StartsWith("--", StringComparison.Ordinal) || index + 1 >= arguments.Count)
            {
                throw new ArgumentException("Options must be supplied as --name value pairs.");
            }

            values[arguments[index]] = arguments[index + 1];
        }
        return values;
    }

    private static string? Value(IReadOnlyDictionary<string, string> values, string name) =>
        values.TryGetValue(name, out var value) ? value : null;

    private static int PositiveIntegerOrDefault(
        IReadOnlyDictionary<string, string> values,
        string name,
        int defaultValue)
    {
        var raw = Value(values, name);
        if (raw is null)
        {
            return defaultValue;
        }

        return int.TryParse(raw, out var value) && value > 0
            ? value
            : throw new ArgumentException($"{name} must be a positive integer.");
    }
}

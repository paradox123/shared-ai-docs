using System.Text.Json;
using Wpcp.Domain;
using Wpcp.Storage.Postgres;

namespace Wpcp.Worker;

internal static class SubmissionDispatcher
{
    public static async Task RunAsync(string configurationPath, CancellationToken token)
    {
        var configuration = SubmissionConfiguration.Load(configurationPath);
        if (configuration.BackgroundExecution is null ||
            string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("WPCP_REAL_ADAPTER_TOKEN")))
            throw new ArgumentException("Background execution configuration and service credential are required.");
        var connectionString = Environment.GetEnvironmentVariable("WPCP_CONNECTION_STRING")
            ?? throw new ArgumentException("Connection required.");
        await using var store = new PostgresImplementationRunStore(connectionString, configuration.RedactionPolicy);
        await using var submissions = new PostgresSubmissionStore(connectionString, configuration.RedactionPolicy);
        await store.EnsureSchemaAsync(token);
        await submissions.EnsureSchemaAsync();
        while (!token.IsCancellationRequested)
        {
            try
            {
                await using var delivery = await store.ClaimSubmissionAsync(token);
                if (delivery is null) { await Task.Delay(500, token); continue; }
                // Preparation is durable before PUT. Even a worker that died before recording
                // a timeout may have delivered the request; a replacement cannot assume otherwise.
                var previous = (await store.GetProjectionAsync(delivery.RunId, token))!;
                var wasStarted = previous.Attempts.Any(a => a.Session is not null);
                if (!await PostgresImplementationRunStore.ArtifactStorageReadyAsync(token))
                {
                    await store.SetSubmissionExecutionAsync(delivery, wasStarted ? "reconciling" : "failed", "artifact-storage-unavailable", token);
                    if (wasStarted) await Task.Delay(1000, token);
                    continue;
                }
                if (delivery.Configuration != configuration.BackgroundExecution ||
                    !configuration.Repositories.Contains(delivery.Submission.Repository))
                {
                    await store.SetSubmissionExecutionAsync(delivery, wasStarted ? "reconciling" : "failed", "execution-configuration-changed", token);
                    if (wasStarted) await Task.Delay(1000, token);
                    continue;
                }
                if (!wasStarted) await store.SetSubmissionExecutionAsync(delivery, "running", null, token);
                var reconcile = false;
                var processId = $"submission-worker:{Environment.ProcessId}:{Guid.NewGuid():N}";
                await store.RecordLifecycleAsync(new(delivery.RunId, LifecycleObservationKind.ProcessStarted,
                    "worker", processId, DateTimeOffset.UtcNow, AgentFrameworkWorkflowId: "SubmissionAnalysisV1"), token);
                try
                {
                    await AgentSessionWorkflow.ExecuteAsync(store, delivery.RunId, delivery.Configuration.AdapterOrigin,
                        JsonSerializer.Serialize(delivery.Submission, new JsonSerializerOptions(JsonSerializerDefaults.Web)),
                        null, false, delivery.Configuration.TimeoutSeconds * 1000, mode: AgentSessionMode.SubmissionAnalysis);
                    var projection = (await store.GetProjectionAsync(delivery.RunId, token))!;
                    var attempt = projection.Attempts.Single(a => a.Session is not null);
                    await store.SetSubmissionExecutionAsync(delivery, attempt.State == "completed" ? "completed" : "failed",
                        attempt.State == "completed" ? null : attempt.Session!.FailureCategory ?? attempt.State, token);
                }
                catch (Npgsql.NpgsqlException) { throw; } // Recovery must reread receipts after database replacement.
                catch (AgentResponseUnavailableException error)
                {
                    reconcile = wasStarted || error.DeliveryUncertain;
                    if (!reconcile) await store.CompleteAgentAsync(delivery.RunId, error.Category, "unknown", token);
                    await store.SetSubmissionExecutionAsync(delivery, reconcile ? "reconciling" : "failed", error.Category, token);
                }
                catch (Exception error) when (error is not OperationCanceledException)
                {
                    var code = error is RepositoryExecutionRequiredException ? "repository-execution-required" : "worker-execution-failed";
                    var projection = (await store.GetProjectionAsync(delivery.RunId, token))!;
                    var activity = projection.Activities.SingleOrDefault(a => a.ActivityType == "submission-analysis");
                    if (projection.Attempts.Any(a => a.ActivityId == activity?.ActivityId && a.State == "running" && a.Session is not null))
                        await store.CompleteAgentAsync(delivery.RunId, code, "unknown", token);
                    await store.SetSubmissionExecutionAsync(delivery, "failed", code, token);
                }
                await store.RecordLifecycleAsync(new(delivery.RunId, LifecycleObservationKind.ProcessStopped,
                    "worker", processId, DateTimeOffset.UtcNow), token);
                if (reconcile) await Task.Delay(1000, token);
            }
            catch (Npgsql.NpgsqlException)
            {
                Console.Error.WriteLine("{\"code\":\"run-store-unavailable\"}");
                await Task.Delay(1000, token);
            }
        }
    }
}

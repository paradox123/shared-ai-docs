using Azure.Core;
using Azure.Identity;
using ManagedDurabilityProbe;
using Microsoft.Agents.AI.DurableTask;
using Microsoft.Agents.AI.DurableTask.Workflows;
using Microsoft.Agents.AI.Workflows;
using Microsoft.DurableTask.Client;
using Microsoft.DurableTask.Client.AzureManaged;
using Microsoft.DurableTask.Worker.AzureManaged;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

ProbeArguments probe = ProbeArguments.Parse(args);
string connectionString = Environment.GetEnvironmentVariable("DURABLE_TASK_SCHEDULER_CONNECTION_STRING")
    ?? throw new InvalidOperationException("DURABLE_TASK_SCHEDULER_CONNECTION_STRING is required.");
if (!connectionString.EndsWith(";Authentication=DefaultAzure", StringComparison.Ordinal))
{
    throw new InvalidOperationException("Only DefaultAzure authentication is allowed for this probe.");
}
Dictionary<string, string> connectionParts = connectionString
    .Split(';', StringSplitOptions.RemoveEmptyEntries)
    .Select(part => part.Split('=', 2))
    .ToDictionary(parts => parts[0], parts => parts[1], StringComparer.Ordinal);
string endpoint = connectionParts["Endpoint"];
string taskHub = connectionParts["TaskHub"];
TokenCredential developerCredential = new DefaultAzureCredential(
    new DefaultAzureCredentialOptions
    {
        ExcludeEnvironmentCredential = true,
        ExcludeWorkloadIdentityCredential = true,
        ExcludeManagedIdentityCredential = true,
        ExcludeVisualStudioCredential = true,
        ExcludeVisualStudioCodeCredential = true,
        ExcludeAzurePowerShellCredential = true,
        ExcludeAzureDeveloperCliCredential = true,
        ExcludeInteractiveBrowserCredential = true,
        ExcludeBrokerCredential = true,
        ExcludeAzureCliCredential = false,
    });

FileLedger ledger = new(probe.Ledger);
CheckpointOne checkpointOne = new(ledger, probe.WorkerName, probe.RunId);
CheckpointTwo checkpointTwo = new(ledger, probe.WorkerName, probe.RunId);
string durableNameSuffix = ProbeArguments.DurableNameSuffix(probe.RunId);
Workflow workflow = new WorkflowBuilder(checkpointOne)
    .WithName($"ManagedWorkerReplacementProbeV1_{durableNameSuffix}")
    .AddEdge(checkpointOne, checkpointTwo)
    .Build();

IHost host = Host.CreateDefaultBuilder(args)
    .ConfigureLogging(logging => logging.SetMinimumLevel(LogLevel.Warning))
    .ConfigureServices(services =>
    {
        services.ConfigureDurableWorkflows(
            options => options.AddWorkflow(workflow),
            workerBuilder: builder => builder.UseDurableTaskScheduler(endpoint, taskHub, developerCredential),
            clientBuilder: builder => builder.UseDurableTaskScheduler(endpoint, taskHub, developerCredential));
    })
    .Build();

await host.StartAsync();
ledger.Append("worker-start", probe.WorkerName, probe.RunId);

DurableTaskClient durableClient = host.Services.GetRequiredService<DurableTaskClient>();
if (probe.StartRun)
{
    IWorkflowClient workflowClient = host.Services.GetRequiredService<IWorkflowClient>();
    IWorkflowRun run = await workflowClient.RunAsync(workflow, probe.RunId, probe.RunId);
    if (run.RunId != probe.RunId)
    {
        throw new InvalidOperationException($"Expected run ID {probe.RunId}, got {run.RunId}.");
    }

    ledger.Append("run-start", probe.WorkerName, probe.RunId);
}

while (true)
{
    OrchestrationMetadata? metadata = await durableClient.GetInstanceAsync(probe.RunId, getInputsAndOutputs: true);
    if (metadata?.RuntimeStatus == OrchestrationRuntimeStatus.Completed)
    {
        ledger.Append("run-complete", probe.WorkerName, probe.RunId);
        await host.StopAsync();
        return;
    }

    if (metadata?.RuntimeStatus is OrchestrationRuntimeStatus.Failed or OrchestrationRuntimeStatus.Terminated)
    {
        string details = metadata.FailureDetails is null
            ? metadata.RuntimeStatus.ToString()
            : $"{metadata.RuntimeStatus}: {metadata.FailureDetails.ErrorMessage}";
        ledger.Append("run-failed", probe.WorkerName, probe.RunId, details: details);
        await host.StopAsync();
        Environment.ExitCode = 2;
        return;
    }

    await Task.Delay(TimeSpan.FromMilliseconds(250));
}

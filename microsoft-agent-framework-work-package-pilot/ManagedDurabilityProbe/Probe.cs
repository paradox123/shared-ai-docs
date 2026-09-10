using System.Diagnostics;
using System.Text.Json;
using Microsoft.Agents.AI.Workflows;

namespace ManagedDurabilityProbe;

internal sealed record ProbeArguments(string WorkerName, string RunId, string Ledger, bool StartRun)
{
    public static string DurableNameSuffix(string runId)
    {
        const string Prefix = "managed-gate-";
        string suffix = runId.StartsWith(Prefix, StringComparison.Ordinal)
            ? runId[Prefix.Length..]
            : runId;
        return suffix.Replace("-", string.Empty, StringComparison.Ordinal);
    }

    public static ProbeArguments Parse(string[] args)
    {
        string? WorkerValue(string option)
        {
            int index = Array.IndexOf(args, option);
            return index >= 0 && index + 1 < args.Length ? args[index + 1] : null;
        }

        return new ProbeArguments(
            WorkerValue("--worker-name") ?? throw new ArgumentException("--worker-name is required"),
            WorkerValue("--run-id") ?? throw new ArgumentException("--run-id is required"),
            WorkerValue("--ledger") ?? throw new ArgumentException("--ledger is required"),
            args.Contains("--start-run", StringComparer.Ordinal));
    }
}

internal sealed class FileLedger(string path)
{
    private readonly string _path = Path.GetFullPath(path);

    public void Append(
        string type,
        string worker,
        string runId,
        string? activity = null,
        string? effect = null,
        string? details = null)
    {
        Dictionary<string, object?> entry = new()
        {
            ["type"] = type,
            ["worker"] = worker,
            ["runId"] = runId,
            ["pid"] = Environment.ProcessId,
            ["timestampUtc"] = DateTimeOffset.UtcNow.ToString("O"),
        };
        if (activity is not null) entry["activity"] = activity;
        if (effect is not null) entry["effect"] = effect;
        if (details is not null) entry["details"] = details;
        AppendLine(JsonSerializer.Serialize(entry));
    }

    public bool CommitEffectOnce(string effect, string worker, string runId)
    {
        for (int attempt = 0; attempt < 100; attempt++)
        {
            try
            {
                using FileStream stream = new(
                    _path,
                    FileMode.OpenOrCreate,
                    FileAccess.ReadWrite,
                    FileShare.None);
                using StreamReader reader = new(stream, leaveOpen: true);
                bool alreadyCommitted = reader.ReadToEnd()
                    .Split('\n', StringSplitOptions.RemoveEmptyEntries)
                    .Any(line => IsCommittedEffect(line, effect));
                stream.Seek(0, SeekOrigin.End);
                using StreamWriter writer = new(stream, leaveOpen: true);
                Dictionary<string, object?> entry = new()
                {
                    ["type"] = alreadyCommitted ? "duplicate-effect-suppressed" : "effect",
                    ["worker"] = worker,
                    ["runId"] = runId,
                    ["pid"] = Environment.ProcessId,
                    ["timestampUtc"] = DateTimeOffset.UtcNow.ToString("O"),
                    ["effect"] = effect,
                };
                writer.WriteLine(JsonSerializer.Serialize(entry));
                writer.Flush();
                stream.Flush(flushToDisk: true);
                return !alreadyCommitted;
            }
            catch (IOException) when (attempt < 99)
            {
                Thread.Sleep(20);
            }
        }

        throw new IOException($"Could not lock effect ledger {_path}.");
    }

    private void AppendLine(string line)
    {
        for (int attempt = 0; attempt < 100; attempt++)
        {
            try
            {
                using FileStream stream = new(
                    _path,
                    FileMode.Append,
                    FileAccess.Write,
                    FileShare.None);
                using StreamWriter writer = new(stream);
                writer.WriteLine(line);
                writer.Flush();
                stream.Flush(flushToDisk: true);
                return;
            }
            catch (IOException) when (attempt < 99)
            {
                Thread.Sleep(20);
            }
        }

        throw new IOException($"Could not append to effect ledger {_path}.");
    }

    private static bool IsCommittedEffect(string line, string effect)
    {
        try
        {
            using JsonDocument document = JsonDocument.Parse(line);
            JsonElement root = document.RootElement;
            return root.TryGetProperty("type", out JsonElement type)
                && type.GetString() == "effect"
                && root.TryGetProperty("effect", out JsonElement value)
                && value.GetString() == effect;
        }
        catch (JsonException)
        {
            return false;
        }
    }
}

internal sealed class CheckpointOne(FileLedger ledger, string worker, string runId)
    : Executor<string, string>($"CheckpointOne_{ProbeArguments.DurableNameSuffix(runId)}")
{
    public override ValueTask<string> HandleAsync(
        string message,
        IWorkflowContext context,
        CancellationToken cancellationToken = default)
    {
        EnsureRunIdentity(message, runId);
        ledger.Append("activity-enter", worker, message, activity: "checkpoint-one");
        ledger.CommitEffectOnce("checkpoint-one", worker, message);
        ledger.Append("activity-complete", worker, message, activity: "checkpoint-one");
        return ValueTask.FromResult(message);
    }

    private static void EnsureRunIdentity(string message, string expectedRunId)
    {
        if (message != expectedRunId)
        {
            throw new InvalidOperationException($"Expected input {expectedRunId}, got {message}.");
        }
    }
}

internal sealed class CheckpointTwo(FileLedger ledger, string worker, string runId)
    : Executor<string, string>($"CheckpointTwo_{ProbeArguments.DurableNameSuffix(runId)}")
{
    public override async ValueTask<string> HandleAsync(
        string message,
        IWorkflowContext context,
        CancellationToken cancellationToken = default)
    {
        ledger.Append("activity-enter", worker, runId, activity: "checkpoint-two");
        if (worker == "managed-probe-worker-1")
        {
            await Task.Delay(TimeSpan.FromMinutes(5), cancellationToken);
        }

        ledger.CommitEffectOnce("checkpoint-two", worker, runId);
        ledger.Append("activity-complete", worker, runId, activity: "checkpoint-two");
        return message;
    }
}

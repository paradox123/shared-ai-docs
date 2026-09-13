using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using Wpcp.Domain;
using Wpcp.Storage.Postgres;

namespace Wpcp.Worker;

/// <summary>Deterministic admission probe; never routes a real issue to an unqualified runtime.</summary>
internal static class CodexRuntimePreflight
{
    public static async Task ExecuteAsync(PostgresImplementationRunStore store, string runId,
        string configuration, string stateRoot, string python)
    {
        await using var delivery = await store.AcquireAgentDeliveryAsync(runId);
        await using var standalone = await store.AcquireStandaloneAgentAsync(runId);
        var configBytes = await File.ReadAllBytesAsync(configuration);
        var assignment = JsonSerializer.SerializeToUtf8Bytes(new {
            configurationSha256 = Convert.ToHexStringLower(SHA256.HashData(configBytes)),
            stateRoot = Path.GetFullPath(stateRoot), python = Path.GetFullPath(python) });
        var identity = "codex-runtime-gate:" + Convert.ToHexStringLower(SHA256.HashData(assignment));
        var receipt = await store.PrepareAgentAsync(runId, identity, false, kind: "real-codex-preflight");
        if (receipt.State != "running") return;
        AgentAdapterResponse response;
        if (receipt.Session.ObservedResponse is not null)
            response = await store.ReadCapturedAgentResponseAsync(receipt);
        else
        {
            var start = new ProcessStartInfo(python) { RedirectStandardOutput = true,
                RedirectStandardError = true, UseShellExecute = false };
            foreach (var argument in new[] { Path.Combine(AppContext.BaseDirectory, "codex_runtime_gate.py"),
                "--config", Path.GetFullPath(configuration), "--state-dir", Path.Combine(Path.GetFullPath(stateRoot), receipt.AttemptId),
                "--run-id", runId, "--attempt-id", receipt.AttemptId }) start.ArgumentList.Add(argument);
            try
            {
                using var process = Process.Start(start) ?? throw new IOException("Could not start runtime gate.");
                var stdout = process.StandardOutput.ReadToEndAsync();
                var stderr = process.StandardError.ReadToEndAsync();
                using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(120));
                try
                {
                    await process.WaitForExitAsync(timeout.Token);
                    response = new(200, await stdout);
                    await stderr; // Do not persist unredacted interpreter/runtime diagnostics.
                }
                catch (OperationCanceledException)
                {
                    process.Kill(entireProcessTree: true);
                    await process.WaitForExitAsync();
                    await Task.WhenAll(stdout, stderr);
                    response = Failure(runId, receipt.AttemptId, "gate-process-timeout", process.Id);
                }
            }
            catch (System.ComponentModel.Win32Exception)
            {
                response = Failure(runId, receipt.AttemptId, "gate-process-unavailable");
            }
            receipt = await store.CaptureAgentResponseAsync(runId, response);
            response = await store.ReadCapturedAgentResponseAsync(receipt);
        }
        string category;
        try
        {
            using var document = JsonDocument.Parse(response.Body);
            var report = document.RootElement;
            if (report.GetProperty("schemaVersion").GetString() != "codex-runtime-gate/v1" ||
                report.GetProperty("runId").GetString() != runId ||
                report.GetProperty("attemptId").GetString() != receipt.AttemptId ||
                report.GetProperty("decision").GetString() != "no-go" ||
                report.GetProperty("issueWorkStarted").GetBoolean())
                throw new JsonException("Unqualified real runtime report.");
            if (report.TryGetProperty("capabilities", out var capabilities) &&
                capabilities.TryGetProperty("startFresh", out var fresh) && fresh.TryGetProperty("sessionId", out var session))
                await store.BindAgentSessionAsync(runId, session.GetString()!,
                    new(Reason: "isolated-probe-session-disposed; native-client-lease-fencing-unverified"));
            category = "capability-unavailable";
        }
        catch (Exception error) when (error is JsonException or KeyNotFoundException or InvalidOperationException or ArgumentException)
        {
            category = "schema-failure";
        }
        await store.CompleteAgentAsync(runId, category, "not-admitted");
    }

    private static AgentAdapterResponse Failure(string runId, string attemptId, string reason, int? processId = null) =>
        new(200, JsonSerializer.Serialize(new { schemaVersion = "codex-runtime-gate/v1", runId, attemptId,
            decision = "no-go", issueWorkStarted = false, reasons = new[] { reason }, processId }));
}

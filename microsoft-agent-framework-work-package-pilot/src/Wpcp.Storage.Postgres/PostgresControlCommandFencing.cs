using System.Text.Json;
using Npgsql;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    private static async Task<IReadOnlyList<ActiveAgentAttempt>> ReadTransferActiveAttemptsAsync(NpgsqlConnection connection,
        NpgsqlTransaction transaction, StoredRun run, CancellationToken token)
    {
        var attempts = new List<ActiveAgentAttempt>();
        await using (var query = new NpgsqlCommand(
            "SELECT state::text FROM wpcp_live_attempts WHERE run_id=@run ORDER BY activity_key", connection, transaction))
        {
            query.Parameters.AddWithValue("run", Guid.Parse(run.Correlation.RunId));
            await using var reader = await query.ExecuteReaderAsync(token);
            while (await reader.ReadAsync(token)) attempts.Add(Deserialize<ActiveAgentAttempt>(reader.GetString(0)));
        }
        return attempts;
    }

    private async Task FenceQueuedActiveCommandsAsync(NpgsqlConnection connection,
        NpgsqlTransaction transaction, StoredRun run, IReadOnlyList<ActiveAgentAttempt> attempts, CancellationToken token)
    {
        foreach (var attempt in attempts)
        {
            var queued = attempt.Commands.Where(c => c.State == "queued").ToArray();
            if (queued.Length == 0) continue;
            foreach (var command in queued)
                await AppendAgentEventAsync(connection, transaction, run, "ActiveAgentCommandRejected",
                    new { attempt.AttemptId, command.CommandId, reason = "control-lease-changed" }, token);
            await SaveActiveAttemptAsync(connection, transaction, run.Correlation.RunId,
                attempt with { Commands = attempt.Commands.Select(c => c.State == "queued"
                    ? c with { State = "rejected", RejectionReason = "control-lease-changed", QueuePosition = null } : c).ToArray() }, token);
        }
    }

    private async Task<string?> FencePendingSessionWritesAsync(NpgsqlConnection connection,
        NpgsqlTransaction transaction, StoredRun run,
        Func<ContinuationOperation, CancellationToken, Task<JsonElement?>>? fence, CancellationToken token)
    {
        var commands = new List<StoredContinuationCommand>();
        await using (var query = new NpgsqlCommand("""
            SELECT command_id::text FROM wpcp_human_request_commands
            WHERE run_id=@run AND state='pending' AND action<>'open' ORDER BY created_at, command_id
            """, connection, transaction))
        {
            query.Parameters.AddWithValue("run", Guid.Parse(run.Correlation.RunId));
            var ids = new List<string>();
            await using (var reader = await query.ExecuteReaderAsync(token))
                while (await reader.ReadAsync(token)) ids.Add(reader.GetString(0));
            foreach (var id in ids)
                commands.Add((await ReadContinuationCommandAsync(connection, transaction, id, token))!);
        }
        // A durable continuation decision has already allocated/resolved its target.
        // It must settle before a responsibility-only change; do not orphan that attempt.
        if (commands.Any(command => command.Action != "write")) return "control-continuation-pending";
        var fenced = new List<(StoredContinuationCommand Command, JsonElement Receipt)>();
        foreach (var command in commands)
        {
            if (fence is null) return "control-fencing-unavailable";
            var operation = command.ToOperation();
            var receipt = await fence(operation, token);
            if (receipt is null) return "control-fencing-unavailable";
            await transaction.SaveAsync("control_fence_receipt", token);
            try
            {
                RequireReceiptString(receipt.Value, "contractVersion", "AgentSessionAdapter/v1");
                RequireReceiptString(receipt.Value, "operationKey", operation.OperationKey);
                RequireReceiptString(receipt.Value, "sourceSessionId", operation.SourceSessionId);
                RequireReceiptString(receipt.Value, "action", operation.Action);
                var state = receipt.Value.GetProperty("state").GetString();
                if (state == "applied")
                {
                    await CompleteContinuationUnderLockAsync(connection, transaction, run, command,
                        receipt.Value.GetProperty("receipt"), token);
                    return "control-effects-reconciled";
                }
                if (state != "fenced") return "control-fencing-unavailable";
            }
            catch (Exception error) when (error is ArgumentException or KeyNotFoundException or InvalidOperationException)
            {
                await transaction.RollbackAsync("control_fence_receipt", token);
                return "control-fencing-unavailable";
            }
            fenced.Add((command, RedactAgentValue(receipt.Value).Value));
        }
        foreach (var item in fenced)
        {
            var operation = item.Command.ToOperation();
            await UpdateContinuationCommandAsync(connection, transaction, operation with { State = "fenced" },
                item.Receipt, token);
            await AppendAgentEventAsync(connection, transaction, run, "ControlCommandFenced",
                new { operation.CommandId, operation.OperationKey, operation.SourceAttemptId,
                    reason = "control-lease-changing" }, token);
        }
        return null;
    }
}

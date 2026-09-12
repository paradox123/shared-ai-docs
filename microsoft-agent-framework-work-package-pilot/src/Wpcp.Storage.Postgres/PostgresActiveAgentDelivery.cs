using System.Text.Json;
using Npgsql;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    public async Task<IReadOnlyList<ActiveAgentDelivery>> GetActiveAgentDeliveriesAsync(string runId,
        CancellationToken token = default)
    {
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var command = new NpgsqlCommand(
            "SELECT adapter_origin, state::text FROM wpcp_live_attempts WHERE run_id=@run ORDER BY activity_key", connection);
        command.Parameters.AddWithValue("run", Guid.Parse(runId));
        await using var reader = await command.ExecuteReaderAsync(token);
        var result = new List<ActiveAgentDelivery>();
        while (await reader.ReadAsync(token))
            result.Add(new(runId, reader.GetString(0), Deserialize<ActiveAgentAttempt>(reader.GetString(1))));
        return result;
    }

    public async Task<ActiveAgentAttempt> ObserveActiveAgentAsync(ActiveAgentDelivery delivery,
        ActiveAgentOperation operation, JsonElement receipt, CancellationToken token = default)
    {
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        await LockRunAsync(connection, transaction, delivery.RunId, token);
        var run = await FindRunAsync(connection, transaction, delivery.RunId, token)
            ?? throw new InvalidOperationException("Unknown run.");
        var attempt = await ReadActiveAttemptAsync(connection, transaction, delivery.RunId, delivery.Attempt.AttemptId, token)
            ?? throw new InvalidOperationException("Unknown live attempt.");
        var sanitized = await SanitizeEvidenceAsync(connection, transaction, delivery.RunId, receipt, token);
        var safe = sanitized.Value;
        string status;
        try
        {
            status = ValidateActiveReceipt(attempt, operation, safe);
        }
        catch (Exception error) when (error is ArgumentException or InvalidOperationException)
        {
            if (await RecordActiveReceiptAsync(connection, transaction, operation.OperationKey, safe, token))
                await AppendAgentEventAsync(connection, transaction, run, "ActiveAgentReceiptRejected",
                    new { attempt.AttemptId, operation.OperationKey, operation.FenceEpoch,
                        code = "invalid-or-unreconciled-adapter-receipt", receipt }, token);
            await transaction.CommitAsync(token);
            return attempt;
        }
        if (await RecordActiveReceiptAsync(connection, transaction, operation.OperationKey, safe, token))
        {
            if (attempt.CurrentOperation?.OperationKey != operation.OperationKey ||
                attempt.State is "completed" or "cancelled" ||
                attempt.CurrentOperation.ProcessStatus is "completed" or "stopped" ||
                operation.FenceEpoch != attempt.FenceEpoch && !(status == "stopped" && attempt.CurrentOperation.StopRequested))
            {
                await AppendAgentEventAsync(connection, transaction, run, "ActiveAgentLateOutputObserved",
                    new { attempt.AttemptId, operation.OperationKey, operation.FenceEpoch, historyOnly = true, receipt }, token);
                await transaction.CommitAsync(token);
                return attempt;
            }
            if (status == "stopped" && !attempt.CurrentOperation.StopRequested)
                throw new ArgumentException("Unrequested process stop.");
            var updated = operation with { ProcessStatus = status,
                ProcessId = safe.TryGetProperty("processId", out var pid) ? pid.GetString() : null,
                Response = status == "completed" ? await ExternalizeLargeValueAsync(connection, transaction,
                    delivery.RunId, safe.GetProperty("response"), sanitized.Occurred, token) : null };
            await AppendAgentEventAsync(connection, transaction, run,
                status == "completed" ? "ActiveAgentResponseObserved" : "ActiveAgentProcessObserved",
                new { attempt.AttemptId, attempt.SessionId, operation.OperationKey, operation.CommandId,
                    operation.FenceEpoch, processStatus = status, receipt }, token);
            var cancelled = attempt.Commands.Any(c => c.Mode == "cancel" && c.State == "stopping");
            var commandState = status == "stopped" ? (cancelled ? "cancelled" : "interrupted") : status;
            attempt = attempt with { CurrentOperation = updated,
                Commands = attempt.Commands.Select(c => c.CommandId == operation.CommandId
                    ? c with { State = commandState }
                    : c.Mode == "cancel" && c.State == "stopping" && status == "stopped"
                        ? c with { State = "completed" } : c).ToArray() };
            if (status == "stopped")
                await AppendAgentEventAsync(connection, transaction, run, "ActiveAgentEffectsReconciled",
                    new { attempt.AttemptId, operation.OperationKey, operation.FenceEpoch, receipt }, token);
            if (attempt.State == "cancelling" && status == "stopped") attempt = attempt with { State = "cancelled" };
            else if (status is "completed" or "stopped") attempt = await PromoteActiveCommandAsync(connection, transaction, run, attempt, token);
            await SaveActiveAttemptAsync(connection, transaction, delivery.RunId, attempt, token);
        }
        await transaction.CommitAsync(token);
        return attempt;
    }

    public async Task RecordActiveDeliveryUnavailableAsync(ActiveAgentDelivery delivery,
        ActiveAgentOperation operation, string code, CancellationToken token = default)
    {
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        await LockRunAsync(connection, transaction, delivery.RunId, token);
        var run = await FindRunAsync(connection, transaction, delivery.RunId, token)
            ?? throw new InvalidOperationException("Unknown run.");
        var safe = RedactAgentValue(JsonSerializer.SerializeToElement(new { code })).Value;
        if (await RecordActiveReceiptAsync(connection, transaction, operation.OperationKey, safe, token))
            await AppendAgentEventAsync(connection, transaction, run, "ActiveAgentDeliveryUnavailable",
                new { delivery.Attempt.AttemptId, operation.OperationKey, operation.FenceEpoch, diagnostic = safe }, token);
        await transaction.CommitAsync(token);
    }

    private static string ValidateActiveReceipt(ActiveAgentAttempt attempt, ActiveAgentOperation operation, JsonElement safe)
    {
        RequireReceiptString(safe, "contractVersion", "AgentSessionAdapter/v1");
        RequireReceiptString(safe, "operationKey", operation.OperationKey);
        RequireReceiptString(safe, "attemptId", attempt.AttemptId);
        RequireReceiptString(safe, "sessionId", attempt.SessionId);
        RequireReceiptString(safe, "message", operation.Message);
        RequireReceiptString(safe, "commandId", operation.CommandId);
        RequireReceiptString(safe, "effectScope", "none");
        if (!safe.TryGetProperty("fenceEpoch", out var fence) || !fence.TryGetInt64(out var epoch) || epoch != operation.FenceEpoch ||
            !safe.TryGetProperty("processStatus", out var statusField)) throw new ArgumentException("Invalid active receipt.");
        var status = statusField.GetString();
        if (status is not ("running" or "completed" or "stopped")) throw new ArgumentException("Invalid process status.");
        if (!safe.TryGetProperty("processId", out var process) ||
            process.ValueKind is not (JsonValueKind.Null or JsonValueKind.String) ||
            status == "running" && string.IsNullOrWhiteSpace(process.GetString()) ||
            operation.ProcessId is not null && process.GetString() != operation.ProcessId)
            throw new ArgumentException("Conflicting or missing process identity.");
        if (status == "completed" && (!safe.TryGetProperty("response", out var response) || response.ValueKind != JsonValueKind.Object))
            throw new ArgumentException("Missing agent response.");
        if (status is "completed" or "stopped")
        {
            RequireReceiptString(safe, "reconciliation", "reconciled");
            if (!safe.TryGetProperty("effects", out var effects) || effects.ValueKind != JsonValueKind.Array || effects.GetArrayLength() != 0)
                throw new ArgumentException("Active adapter effect reconciliation is unresolved.");
        }
        return status;
    }

    private async Task<ActiveAgentAttempt> PromoteActiveCommandAsync(NpgsqlConnection connection,
        NpgsqlTransaction transaction, StoredRun run, ActiveAgentAttempt attempt, CancellationToken token)
    {
        var next = QueuedActiveCommands(attempt).FirstOrDefault();
        if (next is null) return attempt with { State = "completed" };
        var operation = new ActiveAgentOperation(Guid.NewGuid().ToString(), attempt.FenceEpoch, next.CommandId, next.Message!);
        var commands = attempt.Commands.Select(c => c.CommandId == next.CommandId
            ? c with { State = "delivering", OperationKey = operation.OperationKey, QueuePosition = null } : c).ToArray();
        await AppendAgentEventAsync(connection, transaction, run, "ActiveAgentCommandDeliveryRequested",
            new { attempt.AttemptId, attempt.SessionId, command = next, operation }, token);
        return RepositionActiveQueue(attempt with { CurrentOperation = operation, Commands = commands });
    }

    private static IOrderedEnumerable<ActiveAgentCommand> QueuedActiveCommands(ActiveAgentAttempt attempt) =>
        attempt.Commands.Where(c => c.State == "queued")
            .OrderBy(c => c.Mode == "interrupt" ? 0 : 1).ThenBy(c => c.AcceptancePosition);

    private static ActiveAgentAttempt RepositionActiveQueue(ActiveAgentAttempt attempt)
    {
        var positions = QueuedActiveCommands(attempt)
            .Select((c, i) => (c.CommandId, Position: i + 1)).ToDictionary(c => c.CommandId, c => c.Position);
        return attempt with { Commands = attempt.Commands.Select(c => c with
            { QueuePosition = positions.TryGetValue(c.CommandId, out var position) ? position : null }).ToArray() };
    }

    private static async Task<bool> RecordActiveReceiptAsync(NpgsqlConnection connection, NpgsqlTransaction transaction,
        string operationKey, JsonElement receipt, CancellationToken token)
    {
        await using var insert = new NpgsqlCommand("""
            INSERT INTO wpcp_live_receipts VALUES (@operation, @digest) ON CONFLICT DO NOTHING
            """, connection, transaction);
        insert.Parameters.AddWithValue("operation", Guid.Parse(operationKey));
        insert.Parameters.AddWithValue("digest", Digest(receipt));
        return await insert.ExecuteNonQueryAsync(token) == 1;
    }
}

using System.Text.Json;
using Npgsql;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    private static bool IsTransferAction(string? action) => action is "request-transfer" or "reject-transfer" or "approve-transfer" or "force-takeover";

    private async Task<string> DecideTransferUnderLockAsync(NpgsqlConnection connection,
        NpgsqlTransaction transaction, StoredRun run, RunControlState current, RepositoryAccess access,
        string action, ControlMutation mutation,
        Func<RepositoryBinding, ControlTransferRequest, CancellationToken, Task<RepositoryAccess>>? authorizeRecipient,
        Func<ContinuationOperation, CancellationToken, Task<JsonElement?>>? fenceContinuation,
        CancellationToken token)
    {
        if (string.IsNullOrWhiteSpace(mutation.Reason) ||
            action != "force-takeover" && !Guid.TryParse(mutation.RequestId, out _))
            return "invalid-control-mutation";
        if (action != "force-takeover") mutation = mutation with { RequestId = Guid.Parse(mutation.RequestId!).ToString("D") };
        if (action is "reject-transfer" or "approve-transfer" && current.Holder != access.Actor) return "control-lease-required";
        if (ControlFenceFailure(current, mutation) is { } fenceFailure) return fenceFailure;
        if (current.Holder is null) return "control-lease-unowned";
        var request = current.TransferRequest;
        var reason = _redactionPolicy.Redact(mutation.Reason).Value!;
        if (action == "force-takeover")
        {
            if (current.Holder == access.Actor) return "already-control-holder";
            request = request is null ? null : request with { State = request.State == "pending" ? "superseded" : request.State };
        }
        else if (action == "request-transfer")
        {
            if (current.Holder == access.Actor) return "already-control-holder";
            if (request?.State == "pending") return "control-transfer-pending";
            await using var prior = new NpgsqlCommand("""
                SELECT EXISTS(SELECT 1 FROM wpcp_run_events WHERE run_id=@run
                    AND event_type='ControlTransferRequested'
                    AND payload->'current'->'transferRequest'->>'requestId'=@request)
                """, connection, transaction);
            prior.Parameters.AddWithValue("run", Guid.Parse(run.Correlation.RunId));
            prior.Parameters.AddWithValue("request", mutation.RequestId!);
            if (await prior.ExecuteScalarAsync(token) is true) return "stale-transfer-request";
            if (string.IsNullOrWhiteSpace(access.Login)) return "repository-provider-unavailable";
            request = new(mutation.RequestId!, access.Actor!, access.Login, current.Holder,
                current.LeaseEpoch, DateTimeOffset.UtcNow, reason);
        }
        else
        {
            if (request is null || request.RequestId != mutation.RequestId || request.State != "pending" ||
                request.Holder != current.Holder || request.LeaseEpoch != current.LeaseEpoch)
                return "stale-transfer-request";
            if (action == "approve-transfer")
            {
                if (authorizeRecipient is null || run.Correlation.Repository is null) return "repository-provider-unavailable";
                var recipient = await authorizeRecipient(run.Correlation.Repository, request, token);
                if (recipient.FailureCode is not null) return recipient.FailureCode;
                if (!recipient.IsHuman || !recipient.CanContribute || recipient.Actor != request.Requester)
                    return "transfer-recipient-not-contributor";
            }
            request = request with { State = action == "approve-transfer" ? "approved" : "rejected" };
        }
        if (action is "approve-transfer" or "force-takeover")
        {
            var execution = await ReadRepositoryExecutionAsync(connection, transaction, run.Correlation.RunId, token);
            if (execution?.RequestedAction is not null) return "control-recovery-pending";
            var activeAttempts = await ReadTransferActiveAttemptsAsync(connection, transaction, run, token);
            if (activeAttempts.Any(a => a.CurrentOperation is { CommandId: not null, ProcessStatus: "start-pending" }))
                return "control-active-delivery-pending";
            var fenceCode = await FencePendingSessionWritesAsync(connection, transaction, run, fenceContinuation, token);
            if (fenceCode is not null) return fenceCode;
            await FenceQueuedActiveCommandsAsync(connection, transaction, run, activeAttempts, token);
            run = (await FindRunAsync(connection, transaction, run.Correlation.RunId, token))!;
            current = await ReadControlStateAsync(connection, transaction, run, token);
        }
        var next = current with { RunVersion = current.RunVersion + 1, TransferRequest = request };
        if (action == "approve-transfer")
            next = next with { Holder = request!.Requester, LeaseEpoch = current.LeaseEpoch + 1,
                ClaimedAt = DateTimeOffset.UtcNow };
        if (action == "force-takeover")
            next = next with { Holder = access.Actor, LeaseEpoch = current.LeaseEpoch + 1,
                ClaimedAt = DateTimeOffset.UtcNow };
        await WriteControlTransitionAsync(connection, transaction, run, current, next,
            action == "force-takeover" ? "ControlLeaseForcedTakenOver" : action == "approve-transfer" ? "ControlLeaseTransferred" :
                action == "request-transfer" ? "ControlTransferRequested" : "ControlTransferRejected", access.Actor!, token,
            new { mutation.RequestId, reason = mutation.Reason, mode = action == "force-takeover" ? "forced" : "voluntary" });
        return action == "force-takeover" ? "control-lease-forced-taken-over" : action == "approve-transfer" ? "control-lease-transferred" : action == "request-transfer" ? "control-transfer-requested" : "control-transfer-rejected";
    }
}

using System.IO.Compression;
using System.Text.Json;
using Npgsql;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    private async Task<(ImplementationRunProjection Projection, RunEventsPage History, IReadOnlyList<RunArtifact> Artifacts)>
        ReadDossierSnapshotAsync(string runId, CancellationToken token)
    {
        if (await GetRestoredProjectionAsync(runId, token) is { } restored)
            return (restored, await GetRestoredEventsAsync(restored, 0, int.MaxValue, token),
                (await GetArtifactsAsync(runId, token)).Artifacts);
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(System.Data.IsolationLevel.RepeatableRead, token);
        var run = await FindRunAsync(connection, transaction, runId, token)
            ?? throw new InvalidOperationException("Run unavailable.");
        var projection = await ReadProjectionAsync(connection, transaction, run, token);
        var history = await ReadEventsPageAsync(connection, transaction, run, 0, int.MaxValue, token);
        var artifacts = await ReadArtifactRecordsAsync(connection, transaction, runId, token);
        return (projection, history, artifacts);
    }

    public async Task<object> GetChecksumsAsync(string runId, CancellationToken token = default)
    {
        var snapshot = await ReadDossierSnapshotAsync(runId, token);
        return new { runId, snapshot.History.LastPosition,
            historySha256 = HashBytes(DossierJson.Bytes(snapshot.History.Events)),
            projectionSha256 = HashBytes(DossierJson.Bytes(snapshot.Projection)),
            artifacts = (await GetArtifactsAsync(runId, token)).Artifacts };
    }

    public async Task<byte[]> ExportDossierAsync(string runId, CancellationToken token = default)
    {
        var snapshot = await ReadDossierSnapshotAsync(runId, token);
        var history = DossierJson.Bytes(snapshot.History.Events);
        var projection = DossierJson.Bytes(snapshot.Projection);
        var files = new Dictionary<string, string> {
            ["history.json"] = HashBytes(history), ["projection.json"] = HashBytes(projection) };
        var artifacts = new List<RunArtifact>();
        using var output = new MemoryStream();
        using (var zip = new ZipArchive(output, ZipArchiveMode.Create, leaveOpen: true))
        {
            await WriteZipEntryAsync(zip, "history.json", history, token);
            await WriteZipEntryAsync(zip, "projection.json", projection, token);
            foreach (var artifact in snapshot.Artifacts)
            {
                var verified = await VerifyArtifactAsync(artifact, token);
                artifacts.Add(verified.Artifact);
                if (verified.Bytes is not { } bytes) continue;
                var name = "artifacts/" + artifact.Sha256;
                if (files.TryAdd(name, artifact.Sha256!)) await WriteZipEntryAsync(zip, name, bytes, token);
            }
            var manifest = new RunDossierManifest("wpcp-run-dossier/v1", runId, files, artifacts,
                snapshot.Projection.Provenance,
                snapshot.Projection.Attempts.Where(a => a.Session is not null)
                    .Select(a => a.Session!.ContractVersion)
                    .Concat(snapshot.Projection.Attempts.Any(a => a.LiveOperation is not null) ? ["AgentSessionAdapter/v1"] : [])
                    .Distinct().Order().ToArray(),
                JsonSerializer.SerializeToElement(new {
                    exporter = new { dotnet = Environment.Version.ToString(),
                        storage = typeof(PostgresImplementationRunStore).Assembly.GetName().Version?.ToString() },
                    execution = snapshot.History.Events.Where(e => e.EventType == "AgentPreparationCompleted")
                        .Select(e => e.Payload).ToArray() }, JsonOptions),
                snapshot.Projection.ExecutionEvidence);
            await WriteZipEntryAsync(zip, "manifest.json", DossierJson.Bytes(manifest), token);
        }
        return output.ToArray();
    }

    private static async Task WriteZipEntryAsync(ZipArchive zip, string name, byte[] bytes, CancellationToken token)
    {
        var entry = zip.CreateEntry(name, CompressionLevel.Fastest);
        await using var stream = entry.Open();
        await stream.WriteAsync(bytes, token);
    }
}

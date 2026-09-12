using System.IO.Compression;
using System.Text.Json;
using Npgsql;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    public async Task<string> RestoreDossierAsync(Stream input, CancellationToken token = default)
    {
        // ZIP paths are never extracted. Bound decompressed input before reading it.
        using var zip = new ZipArchive(input, ZipArchiveMode.Read, leaveOpen: true);
        const long maximumBytes = 256L * 1024 * 1024;
        if (zip.Entries.Count > 100000 || zip.Entries.Sum(e => e.Length) > maximumBytes ||
            zip.Entries.Select(e => e.FullName).Distinct(StringComparer.Ordinal).Count() != zip.Entries.Count)
            throw new InvalidDataException("Invalid dossier size or entries.");
        async Task<byte[]> ReadEntry(string name)
        {
            var entry = zip.GetEntry(name) ?? throw new InvalidDataException("Missing dossier core.");
            if (entry.Length > maximumBytes) throw new InvalidDataException("Entry too large.");
            await using var stream = entry.Open();
            using var output = new MemoryStream();
            var buffer = new byte[81920];
            int read;
            while ((read = await stream.ReadAsync(buffer, token)) > 0)
            {
                if (output.Length + read > entry.Length) throw new InvalidDataException("Invalid entry length.");
                output.Write(buffer, 0, read);
            }
            if (output.Length != entry.Length) throw new InvalidDataException("Truncated entry.");
            return output.ToArray();
        }
        var manifestBytes = await ReadEntry("manifest.json");
        var manifest = JsonSerializer.Deserialize<RunDossierManifest>(manifestBytes, JsonOptions)
            ?? throw new InvalidDataException("Invalid manifest.");
        if (manifest.FormatVersion != "wpcp-run-dossier/v1" || !Guid.TryParse(manifest.RunId, out var id) ||
            manifest.Files is null || manifest.Artifacts is null || manifest.Provenance is null ||
            manifest.AdapterContracts is null || manifest.FrameworkCorrelation is null)
            throw new InvalidDataException("Invalid manifest contract.");
        var allowed = new HashSet<string>(StringComparer.Ordinal) { "manifest.json", "history.json", "projection.json" };
        foreach (var artifact in manifest.Artifacts)
        {
            if (!ValidHash(artifact.ArtifactId) || artifact.SizeBytes < 0 || artifact.Redaction is null ||
                string.IsNullOrWhiteSpace(artifact.Redaction.PolicyVersion) ||
                artifact.Availability is not ("available" or "withheld" or "missing" or "corrupt" or "unavailable") ||
                artifact.MediaType is not ("text/plain" or "application/json" or "application/x-ndjson" or "application/octet-stream"))
                throw new InvalidDataException("Invalid artifact metadata.");
            if (artifact.Sha256 is not null)
            {
                if (!ValidHash(artifact.Sha256)) throw new InvalidDataException("Invalid artifact hash.");
                allowed.Add("artifacts/" + artifact.Sha256);
            }
            else if (artifact.Availability == "available") throw new InvalidDataException("Missing artifact hash.");
        }
        if (manifest.Artifacts.Select(a => a.ArtifactId).Distinct().Count() != manifest.Artifacts.Count ||
            zip.Entries.Any(e => !allowed.Contains(e.FullName)) ||
            manifest.Files.Any(f => !allowed.Contains(f.Key) || !ValidHash(f.Value)))
            throw new InvalidDataException("Invalid dossier inventory.");
        var projectionBytes = await ReadEntry("projection.json");
        var historyBytes = await ReadEntry("history.json");
        if (manifest.Files.GetValueOrDefault("projection.json") != HashBytes(projectionBytes) ||
            manifest.Files.GetValueOrDefault("history.json") != HashBytes(historyBytes))
            throw new InvalidDataException("Invalid core checksum.");
        var projection = JsonSerializer.Deserialize<ImplementationRunProjection>(projectionBytes, JsonOptions)
            ?? throw new InvalidDataException("Invalid projection.");
        var history = JsonSerializer.Deserialize<JsonElement>(historyBytes);
        if (projection.RunId != manifest.RunId || projection.Correlation?.RunId != manifest.RunId ||
            projection.Correlation.Repository is null || projection.Authorization is not null ||
            history.ValueKind != JsonValueKind.Array || history.GetArrayLength() != projection.LastPosition ||
            projection.LastPosition < 1 || projection.Control is null || projection.Activities is null ||
            projection.Attempts is null || projection.ExecutionEvidence is null)
            throw new InvalidDataException("Inconsistent dossier correlation.");
        var events = ParseDossierEvents(history);
        if (events.Select(e => e.EventId).Distinct().Count() != events.Count ||
            events.Where((e, index) => e.Position != index + 1 || e.RunId != manifest.RunId ||
                e.Correlation.GetProperty("runId").GetString() != manifest.RunId || !Guid.TryParse(e.EventId, out _)).Any())
            throw new InvalidDataException("Inconsistent history sequence.");
        // The canonical projection must survive materialization without silently discarding fields.
        if (HashBytes(DossierJson.Bytes(projection)) != HashBytes(projectionBytes) ||
            HashBytes(DossierJson.Bytes(events)) != HashBytes(historyBytes))
            throw new InvalidDataException("Unsupported canonical representation.");
        foreach (var bytes in new[] { manifestBytes, projectionBytes, historyBytes })
            RequireSanitizedJson(bytes);

        var inventory = manifest.Artifacts.ToDictionary(a => a.ArtifactId);
        RequireArtifactReferences(history, inventory);
        RequireArtifactReferences(JsonSerializer.Deserialize<JsonElement>(projectionBytes), inventory);
        var artifacts = new List<(RunArtifact Artifact, byte[]? Bytes)>();
        foreach (var artifact in manifest.Artifacts)
        {
            if (artifact.Availability != "available") { artifacts.Add((artifact, null)); continue; }
            var name = "artifacts/" + artifact.Sha256;
            if (manifest.Files.GetValueOrDefault(name) != artifact.Sha256)
                throw new InvalidDataException("Unbound artifact inventory.");
            if (zip.GetEntry(name) is null)
            { artifacts.Add((artifact with { Availability = "missing", Reason = "artifact-not-found" }, null)); continue; }
            var bytes = await ReadEntry(name);
            if (HashBytes(bytes) != artifact.Sha256 || bytes.LongLength != artifact.SizeBytes)
            { artifacts.Add((artifact with { Availability = "corrupt", Reason = "checksum-mismatch" }, null)); continue; }
            if (_redactionPolicy.ContainsControlledCanaryBytes(bytes))
                throw new InvalidDataException("Artifact violates current redaction policy.");
            if (artifact.MediaType == "application/json")
            {
                RequireSanitizedJson(bytes);
                RequireArtifactReferences(JsonSerializer.Deserialize<JsonElement>(bytes), inventory);
            }
            if (artifact.MediaType == "application/x-ndjson")
                foreach (var line in System.Text.Encoding.UTF8.GetString(bytes).Split('\n').Where(line => !string.IsNullOrWhiteSpace(line)))
                    RequireSanitizedJson(System.Text.Encoding.UTF8.GetBytes(line));
            artifacts.Add((artifact, bytes));
        }
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        // Imports cannot race with another import or admission to publish the same identity.
        await using (var tableLock = new NpgsqlCommand(
            "LOCK TABLE wpcp_implementation_runs, wpcp_restored_dossiers IN SHARE ROW EXCLUSIVE MODE", connection, transaction))
            await tableLock.ExecuteNonQueryAsync(token);
        await using (var check = new NpgsqlCommand("""
            SELECT EXISTS (SELECT 1 FROM wpcp_implementation_runs WHERE run_id=@id)
                OR EXISTS (SELECT 1 FROM wpcp_restored_dossiers WHERE run_id=@id)
            """, connection, transaction))
        {
            check.Parameters.AddWithValue("id", id);
            if ((bool)(await check.ExecuteScalarAsync(token))!) throw new InvalidDataException("Run already exists.");
        }
        foreach (var item in artifacts)
        {
            if (item.Bytes is not null) await WriteArtifactBytesAsync(item.Artifact.Sha256!, item.Bytes, token);
            await using var command = new NpgsqlCommand(
                "INSERT INTO wpcp_run_artifacts VALUES (@run, @id, @manifest)", connection, transaction);
            command.Parameters.AddWithValue("run", id);
            command.Parameters.AddWithValue("id", item.Artifact.ArtifactId);
            AddJson(command, "manifest", item.Artifact);
            await command.ExecuteNonQueryAsync(token);
        }
        await using var insert = new NpgsqlCommand(
            "INSERT INTO wpcp_restored_dossiers VALUES (@id, @projection, @history, @manifest)", connection, transaction);
        insert.Parameters.AddWithValue("id", id);
        AddJson(insert, "projection", projection);
        AddJson(insert, "history", history);
        AddJson(insert, "manifest", manifest);
        await insert.ExecuteNonQueryAsync(token);
        await transaction.CommitAsync(token);
        return manifest.RunId;
    }

    private static void RequireArtifactReferences(JsonElement value, IReadOnlyDictionary<string, RunArtifact> inventory)
    {
        if (value.ValueKind == JsonValueKind.Object)
        {
            if (value.TryGetProperty("artifactId", out var id))
            {
                if (id.ValueKind != JsonValueKind.String || !inventory.TryGetValue(id.GetString()!, out var artifact) ||
                    !value.TryGetProperty("sha256", out var hash) || hash.GetString() != artifact.Sha256)
                    throw new InvalidDataException("Unbound artifact reference.");
            }
            foreach (var property in value.EnumerateObject()) RequireArtifactReferences(property.Value, inventory);
        }
        else if (value.ValueKind == JsonValueKind.Array)
            foreach (var item in value.EnumerateArray()) RequireArtifactReferences(item, inventory);
    }

    private static bool ValidHash(string? value) => value is { Length: 64 } &&
        value.All(c => c is >= '0' and <= '9' or >= 'a' and <= 'f');

    private void RequireSanitizedJson(byte[] bytes)
    {
        var value = JsonSerializer.Deserialize<JsonElement>(bytes);
        // Markers are already sanitized. Only a changed value indicates a new raw canary.
        if (!JsonElement.DeepEquals(value, RedactAgentValue(value).Value))
            throw new InvalidDataException("Dossier violates current redaction policy.");
    }

    private static IReadOnlyList<CanonicalRunEvent> ParseDossierEvents(JsonElement history) =>
        history.EnumerateArray().Select(e => new CanonicalRunEvent(
            e.GetProperty("runId").GetString()!, e.GetProperty("position").GetInt64(),
            e.GetProperty("eventId").GetString()!, e.GetProperty("eventType").GetString()!,
            e.GetProperty("occurredAt").GetDateTimeOffset(), e.GetProperty("payload").GetRawText(),
            e.GetProperty("correlation").GetRawText(), e.GetProperty("provenance").GetRawText(),
            e.GetProperty("redaction").Deserialize<RedactionMetadata>(JsonOptions)!)).ToArray();

    public async Task<ImplementationRunProjection?> GetRestoredProjectionAsync(string runId, CancellationToken token = default)
    {
        if (!Guid.TryParse(runId, out var id)) return null;
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var read = new NpgsqlCommand("SELECT projection::text FROM wpcp_restored_dossiers WHERE run_id=@id", connection);
        read.Parameters.AddWithValue("id", id);
        return await read.ExecuteScalarAsync(token) is string value ? Deserialize<ImplementationRunProjection>(value) : null;
    }

    private async Task<RunEventsPage> GetRestoredEventsAsync(ImplementationRunProjection projection, long after,
        int limit, CancellationToken token)
    {
        if (after > projection.LastPosition) throw new ArgumentOutOfRangeException(nameof(after));
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var read = new NpgsqlCommand("""
            SELECT COALESCE(jsonb_agg(event ORDER BY position), '[]'::jsonb)::text FROM (
                SELECT event, position FROM wpcp_restored_dossiers,
                jsonb_array_elements(history) WITH ORDINALITY AS item(event, position)
                WHERE run_id=@id AND position>@after ORDER BY position LIMIT @limit
            ) page
            """, connection);
        read.Parameters.AddWithValue("id", Guid.Parse(projection.RunId));
        read.Parameters.AddWithValue("after", after);
        read.Parameters.AddWithValue("limit", limit);
        var json = (string)(await read.ExecuteScalarAsync(token))!;
        return new(projection.RunId, after, ParseDossierEvents(JsonSerializer.Deserialize<JsonElement>(json)), projection.LastPosition);
    }

    private const string DossierSchema = """
        CREATE TABLE IF NOT EXISTS wpcp_restored_dossiers (
            run_id uuid PRIMARY KEY, projection jsonb NOT NULL, history jsonb NOT NULL, manifest jsonb NOT NULL
        );
        """;
}

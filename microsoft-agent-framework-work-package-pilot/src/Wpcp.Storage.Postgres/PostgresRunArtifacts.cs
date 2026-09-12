using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using Npgsql;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    private string ArtifactPath(string hash)
    {
        if (hash.Length != 64 || hash.Any(c => !char.IsAsciiHexDigit(c)))
            throw new ArgumentException("Invalid artifact hash.");
        var root = Environment.GetEnvironmentVariable("WPCP_ARTIFACT_ROOT")
            ?? throw new InvalidOperationException("WPCP_ARTIFACT_ROOT is required for artifact storage.");
        return Path.Combine(Path.GetFullPath(root), hash.ToLowerInvariant());
    }

    private static string HashBytes(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));

    private async Task WriteArtifactBytesAsync(string hash, byte[] bytes, CancellationToken token)
    {
        var path = ArtifactPath(hash);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        if (File.Exists(path))
        {
            if (HashBytes(await File.ReadAllBytesAsync(path, token)) != hash)
                throw new IOException("Existing artifact checksum mismatch.");
            return;
        }
        var temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            await using (var file = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write,
                FileShare.None, 81920, FileOptions.WriteThrough))
            {
                await file.WriteAsync(bytes, token);
                file.Flush(flushToDisk: true);
            }
            try { File.Move(temporary, path, overwrite: false); }
            catch (IOException) when (File.Exists(path))
            {
                if (HashBytes(await File.ReadAllBytesAsync(path, token)) != hash) throw;
            }
        }
        finally { if (File.Exists(temporary)) File.Delete(temporary); }
    }

    private async Task<RunArtifact> PersistArtifactAsync(NpgsqlConnection connection, NpgsqlTransaction transaction,
        string runId, byte[]? bytes, string mediaType, bool redacted, string? reason, CancellationToken token)
    {
        var hash = bytes is null ? null : HashBytes(bytes);
        var metadata = _redactionPolicy.Metadata(redacted);
        // Identity also binds media/policy: equal bytes in different evidence roles remain unambiguous.
        var identity = HashBytes(JsonSerializer.SerializeToUtf8Bytes(new { hash, mediaType, metadata, reason }, JsonOptions));
        var artifact = new RunArtifact(identity, hash, bytes?.LongLength ?? 0, mediaType,
            bytes is null ? "withheld" : "available", reason, metadata);
        if (bytes is not null) await WriteArtifactBytesAsync(hash!, bytes, token);
        await using var command = new NpgsqlCommand("""
            INSERT INTO wpcp_run_artifacts (run_id, artifact_id, manifest) VALUES (@run, @id, @manifest)
            ON CONFLICT (run_id, artifact_id) DO NOTHING
            """, connection, transaction);
        command.Parameters.AddWithValue("run", Guid.Parse(runId));
        command.Parameters.AddWithValue("id", identity);
        AddJson(command, "manifest", artifact);
        await command.ExecuteNonQueryAsync(token);
        return artifact;
    }

    private async Task<(JsonElement Value, bool Occurred)> SanitizeEvidenceAsync(
        NpgsqlConnection connection, NpgsqlTransaction transaction, string runId, JsonElement value, CancellationToken token, int artifactDepth = 0)
    {
        if (artifactDepth > 16) throw new ArgumentException("Artifact nesting limit exceeded.");
        var occurred = false;
        async Task<JsonNode?> Visit(JsonNode? node)
        {
            if (node is JsonObject obj)
            {
                if (obj.ContainsKey("contentBase64"))
                {
                    byte[]? bytes = null;
                    string? reason = null;
                    var media = obj["mediaType"]?.GetValue<string>() ?? "application/octet-stream";
                    media = media is "text/plain" or "application/json" or "application/x-ndjson"
                        ? media : "application/octet-stream";
                    var redacted = false;
                    try { bytes = Convert.FromBase64String(obj["contentBase64"]!.GetValue<string>()); }
                    catch (FormatException) { reason = "invalid-base64"; }
                    if (bytes is not null && media != "application/octet-stream")
                    {
                        try
                        {
                            var text = new UTF8Encoding(false, true).GetString(bytes);
                            if (media is "application/json")
                            {
                                var safe = await SanitizeEvidenceAsync(connection, transaction, runId,
                                    JsonSerializer.Deserialize<JsonElement>(text), token, artifactDepth + 1);
                                bytes = JsonSerializer.SerializeToUtf8Bytes(safe.Value, JsonOptions);
                                redacted = safe.Occurred;
                            }
                            else if (media == "application/x-ndjson")
                            {
                                var lines = new List<string>();
                                foreach (var line in text.Split('\n').Where(line => !string.IsNullOrWhiteSpace(line)))
                                {
                                    var safe = await SanitizeEvidenceAsync(connection, transaction, runId,
                                        JsonSerializer.Deserialize<JsonElement>(line), token, artifactDepth + 1);
                                    lines.Add(JsonSerializer.Serialize(safe.Value, JsonOptions));
                                    redacted |= safe.Occurred;
                                }
                                bytes = Encoding.UTF8.GetBytes(string.Join('\n', lines) + "\n");
                            }
                            else
                            {
                                var safe = _redactionPolicy.Redact(text);
                                bytes = Encoding.UTF8.GetBytes(safe.Value!);
                                redacted = safe.Occurred;
                            }
                        }
                        catch (DecoderFallbackException) { bytes = null; reason = "invalid-text-encoding"; }
                        catch (JsonException) { bytes = null; reason = "invalid-json"; }
                    }
                    else if (bytes is not null && _redactionPolicy.ContainsControlledCanaryBytes(bytes))
                    { bytes = null; reason = "binary-controlled-canary"; redacted = true; }
                    occurred |= redacted;
                    var artifact = await PersistArtifactAsync(connection, transaction, runId, bytes, media, redacted, reason, token);
                    return JsonSerializer.SerializeToNode(artifact, JsonOptions);
                }
                var result = new JsonObject();
                foreach (var pair in obj)
                {
                    var key = _redactionPolicy.Redact(pair.Key);
                    occurred |= key.Occurred;
                    result[key.Value!] = await Visit(pair.Value);
                }
                if (result["type"] is JsonValue kind && kind.TryGetValue<string>(out var type) && type == "artifact" &&
                    result["data"] is JsonObject descriptor && !descriptor.ContainsKey("artifactId") && !descriptor.ContainsKey("artifact"))
                {
                    var unavailable = await PersistArtifactAsync(connection, transaction, runId, null,
                        "application/octet-stream", occurred, "external-artifact-unavailable", token);
                    descriptor["artifact"] = JsonSerializer.SerializeToNode(unavailable, JsonOptions);
                }
                return result;
            }
            if (node is JsonArray array)
            {
                var result = new JsonArray();
                foreach (var item in array) result.Add(await Visit(item));
                return result;
            }
            if (node is JsonValue v && v.TryGetValue<string>(out var textValue))
            {
                var safe = _redactionPolicy.Redact(textValue);
                occurred |= safe.Occurred || textValue.Contains(_redactionPolicy.Marker, StringComparison.Ordinal);
                return JsonValue.Create(safe.Value);
            }
            return node?.DeepClone();
        }
        return (JsonSerializer.SerializeToElement(await Visit(JsonNode.Parse(value.GetRawText())), JsonOptions), occurred);
    }

    private async Task<JsonElement> ExternalizeLargeValueAsync(NpgsqlConnection connection,
        NpgsqlTransaction transaction, string runId, JsonElement value, bool redacted, CancellationToken token)
    {
        var bytes = JsonSerializer.SerializeToUtf8Bytes(value, JsonOptions);
        if (bytes.Length <= 16384) return value;
        var artifact = await PersistArtifactAsync(connection, transaction, runId, bytes,
            "application/json", redacted, null, token);
        return JsonSerializer.SerializeToElement(artifact, JsonOptions);
    }

    public async Task<AgentAdapterResponse> ReadCapturedAgentResponseAsync(AgentAttemptReceipt receipt,
        CancellationToken token = default)
    {
        var value = receipt.Session.ObservedResponse ?? throw new InvalidOperationException("No captured response.");
        if (value.ValueKind == JsonValueKind.Object && value.TryGetProperty("artifactId", out var id))
        {
            var found = await GetArtifactAsync(receipt.RunId, id.GetString()!, token);
            if (found is not { Bytes: { } bytes }) throw new IOException("Original observation unavailable.");
            return new(receipt.Session.ResponseStatus!.Value, Encoding.UTF8.GetString(bytes));
        }
        return new(receipt.Session.ResponseStatus!.Value, value.GetRawText());
    }

    public async Task<JsonElement?> ReadOriginalAgentResultAsync(AgentAttemptReceipt receipt, CancellationToken token = default)
    {
        if (receipt.Session.OriginalResult is not { } value) return null;
        if (value.ValueKind == JsonValueKind.Object && value.TryGetProperty("artifactId", out var id))
        {
            var found = await GetArtifactAsync(receipt.RunId, id.GetString()!, token);
            if (found is not { Bytes: { } bytes }) throw new IOException("Original result unavailable.");
            return JsonSerializer.Deserialize<JsonElement>(bytes);
        }
        return value;
    }

    private async Task<IReadOnlyList<RunArtifact>> ReadArtifactRecordsAsync(NpgsqlConnection connection,
        NpgsqlTransaction transaction, string runId, CancellationToken token)
    {
        await using var command = new NpgsqlCommand(
            "SELECT manifest::text FROM wpcp_run_artifacts WHERE run_id=@run ORDER BY artifact_id", connection, transaction);
        command.Parameters.AddWithValue("run", Guid.Parse(runId));
        await using var reader = await command.ExecuteReaderAsync(token);
        var result = new List<RunArtifact>();
        while (await reader.ReadAsync(token)) result.Add(Deserialize<RunArtifact>(reader.GetString(0)));
        return result;
    }

    private async Task<(RunArtifact Artifact, byte[]? Bytes)> VerifyArtifactAsync(RunArtifact artifact, CancellationToken token)
    {
        if (artifact.Availability != "available" || artifact.Sha256 is null) return (artifact, null);
        try
        {
            var bytes = await File.ReadAllBytesAsync(ArtifactPath(artifact.Sha256), token);
            return HashBytes(bytes) == artifact.Sha256 && bytes.LongLength == artifact.SizeBytes
                ? (artifact, bytes) : (artifact with { Availability = "corrupt", Reason = "checksum-mismatch" }, null);
        }
        catch (FileNotFoundException) { return (artifact with { Availability = "missing", Reason = "artifact-not-found" }, null); }
        catch (DirectoryNotFoundException) { return (artifact with { Availability = "missing", Reason = "artifact-not-found" }, null); }
        catch (IOException) { return (artifact with { Availability = "unavailable", Reason = "artifact-read-failed" }, null); }
    }

    public async Task<ArtifactManifest> GetArtifactsAsync(string runId, CancellationToken token = default)
    {
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        var records = await ReadArtifactRecordsAsync(connection, transaction, runId, token);
        var verified = new List<RunArtifact>();
        foreach (var record in records) verified.Add((await VerifyArtifactAsync(record, token)).Artifact);
        return new(runId, verified);
    }

    public async Task<(RunArtifact Artifact, byte[]? Bytes)?> GetArtifactAsync(string runId, string artifactId,
        CancellationToken token = default)
    {
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        var artifact = (await ReadArtifactRecordsAsync(connection, transaction, runId, token))
            .SingleOrDefault(a => a.ArtifactId == artifactId);
        return artifact is null ? null : await VerifyArtifactAsync(artifact, token);
    }

    private const string ArtifactSchema = """
        CREATE TABLE IF NOT EXISTS wpcp_run_artifacts (
            run_id uuid NOT NULL, artifact_id text NOT NULL, manifest jsonb NOT NULL,
            PRIMARY KEY (run_id, artifact_id)
        );
        """;
}

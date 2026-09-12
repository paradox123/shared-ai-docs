using System.Text.Encodings.Web;
using System.Text.Json;

namespace Wpcp.Domain;

public sealed record RunDossierManifest(string FormatVersion, string RunId,
    IReadOnlyDictionary<string, string> Files, IReadOnlyList<RunArtifact> Artifacts,
    RunProvenance Provenance, IReadOnlyList<string> AdapterContracts,
    JsonElement Runtime, IReadOnlyList<ExecutionEvidence> FrameworkCorrelation);

/// <summary>Product JSON canonicalization v1: ordinal object keys; unchanged array order.</summary>
public static class DossierJson
{
    private static readonly JsonSerializerOptions Options = new(JsonSerializerDefaults.Web);

    public static byte[] Bytes<T>(T value)
    {
        using var output = new MemoryStream();
        using (var writer = new Utf8JsonWriter(output, new() { Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping }))
            Write(writer, JsonSerializer.SerializeToElement(value, Options));
        return output.ToArray();
    }

    private static void Write(Utf8JsonWriter writer, JsonElement value)
    {
        if (value.ValueKind == JsonValueKind.Object)
        {
            writer.WriteStartObject();
            foreach (var property in value.EnumerateObject().OrderBy(p => p.Name, StringComparer.Ordinal))
            { writer.WritePropertyName(property.Name); Write(writer, property.Value); }
            writer.WriteEndObject();
        }
        else if (value.ValueKind == JsonValueKind.Array)
        {
            writer.WriteStartArray();
            foreach (var item in value.EnumerateArray()) Write(writer, item);
            writer.WriteEndArray();
        }
        else value.WriteTo(writer);
    }
}

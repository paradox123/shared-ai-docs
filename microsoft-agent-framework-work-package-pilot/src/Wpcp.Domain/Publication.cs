using System.Text.Json;

namespace Wpcp.Domain;

public sealed record Publication(string AssignmentHash, string State,
    string? Blocker = null, JsonElement? Report = null, JsonElement? Intent = null,
    bool Dispatched = false);

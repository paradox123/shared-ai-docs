using Wpcp.Domain;

internal static class OperatorHttp
{
    public static string? Credential(HttpContext context)
    {
        var value = context.Request.Headers.Authorization.ToString();
        return value.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase) ? value[7..] : null;
    }

    public static IResult AccessError(RepositoryAccess access, string fallback) =>
        Results.Json(new { code = access.FailureCode ?? fallback }, statusCode:
            access.FailureCode == "repository-provider-unavailable" ? 503 :
            access.FailureCode == "provider-authentication-required" ? 401 : 403);
}

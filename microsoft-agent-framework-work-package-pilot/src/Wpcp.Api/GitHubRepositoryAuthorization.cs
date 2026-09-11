using System.Net;
using System.Net.Http.Headers;
using System.Text.Json;
using Wpcp.Domain;

internal sealed class GitHubRepositoryAuthorization(
    HttpClient client) : IRepositoryAuthorization
{
    public async Task<RepositoryAccess> EvaluateAsync(
        RepositoryBinding binding, string? credential, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(credential))
            return new(null, false, false, "provider-authentication-required");
        try
        {
            using var userResponse = await SendAsync("user", credential, cancellationToken);
            if (userResponse.StatusCode == HttpStatusCode.Unauthorized)
                return new(null, false, false, "provider-authentication-required");
            userResponse.EnsureSuccessStatusCode();
            using var user = JsonDocument.Parse(await userResponse.Content.ReadAsStringAsync(cancellationToken));
            var id = user.RootElement.GetProperty("id").GetInt64();
            if (id <= 0) throw new JsonException();
            var actor = new ActorIdentity(
                user.RootElement.GetProperty("type").GetString() == "User" ? "human" : "service",
                "github", id.ToString(System.Globalization.CultureInfo.InvariantCulture));
            if (actor.Kind != "human")
                return new(actor, false, false, "human-identity-required");

            var path = "repos/" + string.Join('/', binding.FullName.Split('/').Select(Uri.EscapeDataString));
            using var repositoryResponse = await SendAsync(path, credential, cancellationToken);
            if (repositoryResponse.StatusCode == HttpStatusCode.NotFound)
                return new(actor, false, false, "repository-access-denied");
            repositoryResponse.EnsureSuccessStatusCode();
            using var repository = JsonDocument.Parse(await repositoryResponse.Content.ReadAsStringAsync(cancellationToken));
            var root = repository.RootElement;
            if (root.GetProperty("id").GetInt64() != binding.ProviderRepositoryId)
                return new(actor, false, false, "repository-identity-mismatch");
            var permissions = root.GetProperty("permissions");
            var read = permissions.GetProperty("pull").GetBoolean();
            var push = permissions.GetProperty("push").GetBoolean();
            return new(actor, read, read && push);
        }
        catch (Exception error) when (error is HttpRequestException or JsonException or
            InvalidOperationException or KeyNotFoundException or TaskCanceledException or FormatException)
        {
            // Never expose or store upstream bodies, credentials or exception messages.
            return new(null, false, false, "repository-provider-unavailable");
        }
    }

    private async Task<HttpResponseMessage> SendAsync(string path, string credential, CancellationToken cancellationToken)
    {
        using var request = new HttpRequestMessage(HttpMethod.Get, path);
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", credential);
        request.Headers.Accept.ParseAdd("application/vnd.github+json");
        request.Headers.UserAgent.ParseAdd("Wpcp-Pilot/1.0");
        request.Headers.Add("X-GitHub-Api-Version", "2026-03-10");
        return await client.SendAsync(request, cancellationToken);
    }

    public static HttpClient CreateClient()
    {
        var testOrigin = Environment.GetEnvironmentVariable("WPCP_GITHUB_TEST_ORIGIN");
        var origin = new Uri(testOrigin ?? "https://api.github.com/");
        if (testOrigin is not null && (origin.Scheme != "http" ||
            !IPAddress.TryParse(origin.Host, out var address) || !IPAddress.IsLoopback(address) ||
            origin.AbsolutePath != "/" || origin.Query != "" || origin.UserInfo != "" || origin.Fragment != ""))
            throw new ArgumentException("The test provider origin must be a loopback HTTP origin.");
        return new HttpClient(new HttpClientHandler { AllowAutoRedirect = false })
        { BaseAddress = origin, Timeout = TimeSpan.FromSeconds(5) };
    }
}

using System.Net.Http.Headers;

internal static class GitHubRequests
{
    public static async Task<HttpResponseMessage> GetAsync(
        HttpClient client, string path, string credential, CancellationToken token)
    {
        using var request = new HttpRequestMessage(HttpMethod.Get, path);
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", credential);
        request.Headers.Accept.ParseAdd("application/vnd.github+json");
        request.Headers.UserAgent.ParseAdd("Wpcp-Pilot/1.0");
        request.Headers.Add("X-GitHub-Api-Version", "2026-03-10");
        return await client.SendAsync(request, token);
    }
}

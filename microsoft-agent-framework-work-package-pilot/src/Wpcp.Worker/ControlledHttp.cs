namespace Wpcp.Worker;

/// <summary>Shared trust boundary for explicit local pilot providers.</summary>
internal static class ControlledHttp
{
    public static Uri Origin(string origin)
    {
        if (!Uri.TryCreate(origin, UriKind.Absolute, out var uri) || !uri.IsLoopback || uri.Scheme != "http" ||
            uri.AbsolutePath != "/" || uri.UserInfo.Length != 0 || uri.Query.Length != 0 || uri.Fragment.Length != 0)
            throw new ArgumentException("Controlled providers require loopback HTTP origins.");
        return uri;
    }

    public static HttpClient Client(string origin, int timeoutMilliseconds) =>
        new(new HttpClientHandler { AllowAutoRedirect = false })
        {
            BaseAddress = Origin(origin), Timeout = TimeSpan.FromMilliseconds(timeoutMilliseconds),
            MaxResponseContentBufferSize = 64 * 1024 * 1024
        };
}

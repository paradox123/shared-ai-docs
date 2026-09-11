using System.Globalization;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;

return await OperatorCli.RunAsync(args);

internal static class OperatorCli
{
    private const string FixtureAccessHeaderName = "X-Wpcp-Fixture-Access";
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);

    public static async Task<int> RunAsync(string[] arguments)
    {
        if (arguments.Any(argument => argument is "--help" or "-h"))
        {
            return WriteJson(Usage(), exitCode: 0);
        }

        try
        {
            var invocation = ParseInvocation(arguments);
            using var client = new HttpClient(new HttpClientHandler { AllowAutoRedirect = false }) { Timeout = TimeSpan.FromSeconds(30) };
            using var request = CreateRequest(invocation);

            return await SendAsync(client, request);
        }
        catch (ArgumentException)
        {
            return WriteJson(
                new
                {
                    code = "invalid-operator-cli-arguments",
                    message = "Supply --base-url followed by a supported command and its required options.",
                },
                exitCode: 2);
        }
        catch (HttpRequestException)
        {
            return WriteJson(
                new
                {
                    code = "operator-api-unreachable",
                    message = "The Operator API request could not be completed.",
                },
                exitCode: 2);
        }
        catch (TaskCanceledException)
        {
            return WriteJson(
                new
                {
                    code = "operator-api-timeout",
                    message = "The Operator API request timed out.",
                },
                exitCode: 2);
        }
    }

    private static Invocation ParseInvocation(IReadOnlyList<string> arguments)
    {
        var remaining = arguments.ToList();
        var baseUrlIndex = remaining.FindIndex(argument => string.Equals(argument, "--base-url", StringComparison.Ordinal));
        if (baseUrlIndex < 0 || baseUrlIndex == remaining.Count - 1)
        {
            throw new ArgumentException("The global --base-url option is required.");
        }

        var baseUrl = ParseBaseUrl(remaining[baseUrlIndex + 1]);
        var fixtureAccessToken = Environment.GetEnvironmentVariable("WPCP_FIXTURE_ACCESS_TOKEN");
        if (string.IsNullOrWhiteSpace(fixtureAccessToken))
        {
            throw new ArgumentException("WPCP_FIXTURE_ACCESS_TOKEN is required.");
        }
        ValidateHeaderValue(fixtureAccessToken, "WPCP_FIXTURE_ACCESS_TOKEN");
        remaining.RemoveRange(baseUrlIndex, 2);
        if (remaining.Any(argument => string.Equals(argument, "--base-url", StringComparison.Ordinal)) || remaining.Count == 0)
        {
            throw new ArgumentException("Specify --base-url exactly once with a command.");
        }

        var command = remaining[0];
        var options = ParseOptions(remaining.Skip(1));

        return command switch
        {
            "start" => ParseStart(baseUrl, fixtureAccessToken, options),
            "run" => ParseRun(baseUrl, fixtureAccessToken, options),
            "attempt" => ParseAttempt(baseUrl, fixtureAccessToken, options),
            "events" => ParseEvents(baseUrl, fixtureAccessToken, options),
            "audit" => ParseAudit(baseUrl, fixtureAccessToken, options),
            "claim" or "release" => ParseControl(baseUrl, fixtureAccessToken, command, options),
            "--help" or "-h" => throw new ArgumentException("Help does not accept an API base URL."),
            _ => throw new ArgumentException("The command must be start, run, attempt, events, audit, claim, or release."),
        };
    }

    private static Invocation ParseStart(
        Uri baseUrl,
        string fixtureAccessToken,
        IReadOnlyDictionary<string, string> options)
    {
        RequireOnly(
            options,
            "--repository-id",
            "--issue-number",
            "--command-id",
            "--note",
            "--source-revision",
            "--package-revision",
            "--configuration-revision",
            "--contract-revision");

        var repositoryId = Require(options, "--repository-id");
        var issueNumberText = Require(options, "--issue-number");
        if (!long.TryParse(issueNumberText, NumberStyles.None, CultureInfo.InvariantCulture, out var issueNumber) || issueNumber <= 0)
        {
            throw new ArgumentException("--issue-number must be a positive whole number.");
        }

        var commandId = Require(options, "--command-id");
        var note = Require(options, "--note");
        var sourceRevision = Require(options, "--source-revision");
        var packageRevision = Require(options, "--package-revision");
        var configurationRevision = Require(options, "--configuration-revision");
        var contractRevision = Require(options, "--contract-revision");

        return new Invocation(
            baseUrl,
            HttpMethod.Post,
            $"api/v1/issues/{Uri.EscapeDataString(repositoryId)}/{issueNumber.ToString(CultureInfo.InvariantCulture)}/runs",
            new
            {
                commandId,
                note,
                provenance = new
                {
                    sourceRevision,
                    packageRevision,
                    configurationRevision,
                    contractRevision,
                },
            },
            fixtureAccessToken);
    }

    private static Invocation ParseRun(
        Uri baseUrl,
        string fixtureAccessToken,
        IReadOnlyDictionary<string, string> options)
    {
        RequireOnly(options, "--run-id");

        return new Invocation(
            baseUrl,
            HttpMethod.Get,
            $"api/v1/runs/{Uri.EscapeDataString(Require(options, "--run-id"))}",
            null,
            fixtureAccessToken);
    }

    private static Invocation ParseAttempt(Uri baseUrl, string fixtureAccessToken,
        IReadOnlyDictionary<string, string> options)
    {
        RequireOnly(options, "--run-id", "--attempt-id");
        return new Invocation(baseUrl, HttpMethod.Get,
            $"api/v1/runs/{Uri.EscapeDataString(Require(options, "--run-id"))}/attempts/{Uri.EscapeDataString(Require(options, "--attempt-id"))}",
            null, fixtureAccessToken);
    }

    private static Invocation ParseEvents(
        Uri baseUrl,
        string fixtureAccessToken,
        IReadOnlyDictionary<string, string> options)
    {
        RequireOnly(options, "--run-id", "--after");
        var afterText = Require(options, "--after");
        if (!long.TryParse(afterText, NumberStyles.None, CultureInfo.InvariantCulture, out var after) || after < 0)
        {
            throw new ArgumentException("--after must be a non-negative whole number.");
        }


        return new Invocation(
            baseUrl,
            HttpMethod.Get,
            $"api/v1/runs/{Uri.EscapeDataString(Require(options, "--run-id"))}/events?after={after.ToString(CultureInfo.InvariantCulture)}",
            null,
            fixtureAccessToken);
    }

    private static Invocation ParseControl(
        Uri baseUrl, string capability, string action, IReadOnlyDictionary<string, string> options)
    {
        RequireOnly(options, "--run-id", "--target-attempt-id", "--expected-run-version",
            "--expected-head-sha", "--lease-epoch");
        if (!long.TryParse(Require(options, "--expected-run-version"), NumberStyles.None,
                CultureInfo.InvariantCulture, out var version) || version < 1 ||
            !long.TryParse(Require(options, "--lease-epoch"), NumberStyles.None,
                CultureInfo.InvariantCulture, out var epoch) || epoch < 0 ||
            !Guid.TryParse(Require(options, "--target-attempt-id"), out _))
            throw new ArgumentException("Control fences are required.");
        var head = Require(options, "--expected-head-sha");
        return new Invocation(baseUrl, HttpMethod.Post,
            $"api/v1/runs/{Uri.EscapeDataString(Require(options, "--run-id"))}/control/{action}",
            new { targetAttemptId = Require(options, "--target-attempt-id"), expectedRunVersion = version,
                expectedHeadSha = head == "null" ? null : head, leaseEpoch = epoch }, capability);
    }

    private static Invocation ParseAudit(Uri baseUrl, string capability, IReadOnlyDictionary<string, string> options)
    {
        RequireOnly(options, "--run-id");
        return new Invocation(baseUrl, HttpMethod.Get,
            $"api/v1/runs/{Uri.EscapeDataString(Require(options, "--run-id"))}/audit", null, capability);
    }

    private static HttpRequestMessage CreateRequest(Invocation invocation)
    {
        var request = new HttpRequestMessage(invocation.Method, new Uri(invocation.BaseUrl, invocation.RelativePath));
        request.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

        request.Headers.Add(FixtureAccessHeaderName, invocation.FixtureAccessToken);
        var token = Environment.GetEnvironmentVariable("WPCP_PROVIDER_TOKEN");
        if (string.IsNullOrWhiteSpace(token)) throw new ArgumentException("WPCP_PROVIDER_TOKEN is required.");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

        if (invocation.Payload is not null)
        {
            var json = JsonSerializer.Serialize(invocation.Payload, JsonOptions);
            request.Content = new StringContent(json, Encoding.UTF8, "application/json");
        }

        return request;
    }

    private static async Task<int> SendAsync(HttpClient client, HttpRequestMessage request)
    {
        using var response = await client.SendAsync(request);
        var body = await response.Content.ReadAsStringAsync();
        var exitCode = response.IsSuccessStatusCode ? 0 : 1;

        if (!string.IsNullOrWhiteSpace(body))
        {
            try
            {
                using var document = JsonDocument.Parse(body);
                Console.Out.WriteLine(JsonSerializer.Serialize(document.RootElement, JsonOptions));
                return exitCode;
            }
            catch (JsonException)
            {
                // Do not echo a non-JSON response body: it has not passed the
                // public redaction contract and may contain diagnostic data.
            }
        }

        return WriteJson(
            new
            {
                code = "operator-api-non-json-response",
                status = (int)response.StatusCode,
            },
            exitCode);
    }

    private static IReadOnlyDictionary<string, string> ParseOptions(IEnumerable<string> arguments)
    {
        var values = new Dictionary<string, string>(StringComparer.Ordinal);
        using var enumerator = arguments.GetEnumerator();

        while (enumerator.MoveNext())
        {
            var option = enumerator.Current;
            if (!option.StartsWith("--", StringComparison.Ordinal) || !enumerator.MoveNext())
            {
                throw new ArgumentException("Each command option must have a value.");
            }

            // Ticket 02 clients may still send this legacy option; provider credentials
            // are the only identity source and the value is never transported.
            if (option == "--actor-id") continue;
            if (!values.TryAdd(option, enumerator.Current))
            {
                throw new ArgumentException("Command options must not be repeated.");
            }
        }

        return values;
    }

    private static void RequireOnly(IReadOnlyDictionary<string, string> options, params string[] expected)
    {
        foreach (var option in options.Keys)
        {
            if (!expected.Contains(option, StringComparer.Ordinal))
            {
                throw new ArgumentException("An unsupported command option was supplied.");
            }
        }

        foreach (var option in expected)
        {
            _ = Require(options, option);
        }
    }

    private static string Require(IReadOnlyDictionary<string, string> options, string option)
    {
        if (!options.TryGetValue(option, out var value) || string.IsNullOrWhiteSpace(value))
        {
            throw new ArgumentException($"{option} is required.");
        }

        return value;
    }

    private static void ValidateHeaderValue(string value, string option)
    {
        if (value.IndexOf('\r') >= 0 || value.IndexOf('\n') >= 0)
        {
            throw new ArgumentException($"{option} cannot contain a line break.");
        }
    }

    private static Uri ParseBaseUrl(string value)
    {
        if (!Uri.TryCreate(value, UriKind.Absolute, out var parsed)
            || (parsed.Scheme != Uri.UriSchemeHttp && parsed.Scheme != Uri.UriSchemeHttps))
        {
            throw new ArgumentException("--base-url must be an absolute HTTP(S) URL.");
        }

        var builder = new UriBuilder(parsed)
        {
            Query = string.Empty,
            Fragment = string.Empty,
        };
        if (!builder.Path.EndsWith("/", StringComparison.Ordinal))
        {
            builder.Path += "/";
        }

        return builder.Uri;
    }

    private static object Usage() => new
    {
        usage = "Wpcp.OperatorCli --base-url <http-url> <start|run|attempt|events|audit|claim|release> [options]",
        requiredEnvironment = new[] { "WPCP_FIXTURE_ACCESS_TOKEN", "WPCP_PROVIDER_TOKEN" },
        commands = new
        {
            start = new[]
            {
                "--repository-id", "--issue-number", "--command-id", "--note",
                "--source-revision", "--package-revision", "--configuration-revision", "--contract-revision",
            },
            attempt = new[] { "--run-id", "--attempt-id" },
            audit = new[] { "--run-id" },
            control = new[] { "--run-id", "--target-attempt-id", "--expected-run-version",
                "--expected-head-sha", "--lease-epoch" },
            run = new[] { "--run-id" },
            events = new[] { "--run-id", "--after" },
        },
    };

    private static int WriteJson<T>(T value, int exitCode)
    {
        Console.Out.WriteLine(JsonSerializer.Serialize(value, JsonOptions));
        return exitCode;
    }

    private sealed record Invocation(
        Uri BaseUrl,
        HttpMethod Method,
        string RelativePath,
        object? Payload,
        string FixtureAccessToken);
}

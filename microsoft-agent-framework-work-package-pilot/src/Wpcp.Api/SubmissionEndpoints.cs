using System.Net;
using static OperatorHttp;
using System.Text.Json;
using System.Text.RegularExpressions;
using Wpcp.Domain;
using Wpcp.Storage.Postgres;

internal static partial class SubmissionEndpoints
{
    public static void MapSubmissions(this WebApplication app, PostgresSubmissionStore store,
        IReadOnlyList<RepositoryBinding> bindings, IRepositoryAuthorization authorization, HttpClient github)
    {
        app.MapPost("/api/v1/submissions", async (SubmitGitHubIssueRequest request,
            HttpContext context, CancellationToken token) =>
        {
            var match = IssueUrl().Match(request.SourceUrl?.Trim() ?? "");
            if (!match.Success || !int.TryParse(match.Groups[3].Value, out var number))
                return Error("invalid-github-issue-url", 400);
            var name = match.Groups[1].Value + "/" + match.Groups[2].Value;
            var repository = bindings.FirstOrDefault(b => b.FullName.Equals(name, StringComparison.OrdinalIgnoreCase));
            if (repository is null) return Error("repository-not-configured", 403);
            var credential = Credential(context);
            var access = await authorization.EvaluateAsync(repository, credential, token);
            if (!access.CanContribute || !access.IsHuman) return AccessError(access, "repository-contribution-required");
            try
            {
                var url = $"https://github.com/{repository.FullName}/issues/{number}";
                using var response = await GitHubRequests.GetAsync(github,
                    $"repos/{repository.FullName}/issues/{number}", credential!, token);
                if (response.StatusCode == HttpStatusCode.NotFound) return Error("github-issue-not-found", 404);
                response.EnsureSuccessStatusCode();
                using var document = JsonDocument.Parse(await response.Content.ReadAsStringAsync(token));
                var issue = document.RootElement;
                if (issue.TryGetProperty("pull_request", out _)) return Error("github-source-is-pull-request", 422);
                if (issue.GetProperty("number").GetInt32() != number ||
                    !url.Equals(issue.GetProperty("html_url").GetString(), StringComparison.OrdinalIgnoreCase))
                    return Error("github-source-identity-mismatch", 409);
                if (issue.GetProperty("state").GetString() != "open") return Error("github-issue-closed", 422);
                if (!issue.GetProperty("labels").EnumerateArray().Any(l => l.GetProperty("name").GetString() == "ready-for-agent"))
                    return Error("implementation-authorization-required", 422);
                var title = issue.GetProperty("title").GetString();
                var id = issue.GetProperty("id").GetInt64();
                if (id <= 0 || string.IsNullOrWhiteSpace(title)) throw new JsonException();
                var source = new SubmissionSource("github", id, number, url,
                    issue.GetProperty("updated_at").GetDateTimeOffset());
                var result = await store.AdmitAsync(title, issue.GetProperty("body").GetString() ?? "",
                    source, repository, access.Actor!, token);
                return Results.Json(result.Submission, statusCode: result.Created ? 201 : 200);
            }
            catch (RepositoryBindingConflictException) { return Error("repository-identity-mismatch", 409); }
            catch (ArgumentException) { return Error("submission-correlation-rejected", 422); }
            catch (Exception error) when (error is HttpRequestException or JsonException or InvalidOperationException
                or KeyNotFoundException or TaskCanceledException or FormatException)
            { return Error("github-source-unavailable", 503); }
        });

        app.MapGet("/api/v1/submissions/{id:guid}", async (Guid id, HttpContext context, CancellationToken token) =>
        {
            if (Credential(context) is null) return Error("provider-authentication-required", 401);
            var submission = await store.GetAsync(id, token);
            if (submission is null) return Error("submission-not-found", 404);
            var access = await authorization.EvaluateAsync(submission.Repository, Credential(context), token);
            return access.IsHuman && access.CanRead ? Results.Json(submission) : AccessError(access, "repository-access-denied");
        });

        app.MapGet("/api/v1/submissions", async (HttpContext context, CancellationToken token) =>
        {
            if (Credential(context) is null) return Error("provider-authentication-required", 401);
            var submissions = await store.ListAsync(token);
            var allowed = new HashSet<RepositoryBinding>();
            foreach (var repository in bindings.Concat(submissions.Select(s => s.Repository)).Distinct())
            {
                var access = await authorization.EvaluateAsync(repository, Credential(context), token);
                if (access.FailureCode is "provider-authentication-required" or "repository-provider-unavailable" || !access.IsHuman)
                    return AccessError(access, "repository-access-denied");
                if (access.CanRead) allowed.Add(repository);
            }
            return Results.Json(new { submissions = submissions.Where(s => allowed.Contains(s.Repository)) });
        });
    }

    private static IResult Error(string code, int status) => Results.Json(new { code }, statusCode: status);

    [GeneratedRegex(@"\Ahttps://github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9_.-]+)/issues/([1-9][0-9]*)/?(?:\#[^\s]*)?\z", RegexOptions.IgnoreCase)]
    private static partial Regex IssueUrl();
}

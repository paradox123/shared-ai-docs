using System.Diagnostics;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;
using System.Runtime.InteropServices;

try
{
    if (OperatingSystem.IsWindows() || args.Length != 3 || args[1] != "--request")
        throw new Blocked("usage: <verify-sources|git-history|docs-history|prepare-workspace|retire-plan|protect-worktree|restore-worktree|plan-delivery|delivery-status|finalize> --request <private-json>");
    var request = Delivery.Read(Path.GetFullPath(args[2]));
    var result = args[0] switch
    {
        "verify-sources" => Delivery.VerifySources(request),
        "docs-history" => Delivery.DocsHistory(request),
        "git-history" => Delivery.GitHistory(request),
        "prepare-workspace" => Delivery.PrepareWorkspace(request),
        "retire-plan" => Delivery.RetirePlan(request),
        "protect-worktree" => Delivery.ProtectWorktree(request),
        "restore-worktree" => Delivery.RestoreWorktree(request),
        "plan-delivery" => Delivery.Plan(request),
        "delivery-status" => Delivery.Status(request),
        "finalize" => Delivery.Finalize(request),
        _ => throw new Blocked("unknown_command")
    };
    Console.WriteLine(result.ToJsonString());
    return 0;
}
catch (Exception ex) { Console.WriteLine(new JsonObject { ["schema_version"] = 1, ["status"] = "blocked", ["reason"] = ex.Message }.ToJsonString()); return 2; }

sealed class Blocked(string reason) : Exception(reason);

[System.Runtime.Versioning.UnsupportedOSPlatform("windows")]
static class Delivery
{
    static readonly string[] Keys = ["Processed window end", "Last review", "Carry-forward sessions", "Authoritative source tips", "Docs reviewed tip"];
    const UnixFileMode PrivateFile = UnixFileMode.UserRead | UnixFileMode.UserWrite;
    const UnixFileMode PrivateDirectory = PrivateFile | UnixFileMode.UserExecute;
    public static JsonObject Read(string path)
    {
        NoLinks(path);
        return JsonNode.Parse(File.ReadAllBytes(path), documentOptions: new JsonDocumentOptions { AllowDuplicateProperties = false })?.AsObject() ?? throw new Blocked("invalid_json");
    }
    static string S(JsonObject o, string key) => o[key]?.GetValue<string>() is { Length: > 0 } x ? x : throw new Blocked("missing_" + key);
    static string? Optional(JsonObject o, string key) => o[key]?.GetValue<string>();
    static int N(JsonObject o, string key, int fallback) => o[key]?.GetValue<int>() ?? fallback;
    static JsonArray Array(JsonObject o, string key) => o[key]?.AsArray() ?? throw new Blocked("missing_" + key);
    static JsonObject Object(JsonObject o, string key) => o[key]?.AsObject() ?? throw new Blocked("missing_" + key);
    static string[] Strings(JsonObject o, string key) => Array(o, key).Select(x => x!.GetValue<string>()).ToArray();
    static JsonArray List(IEnumerable<string> x) => new(x.Select(x => (JsonNode?)JsonValue.Create(x)).ToArray());
    static string Sha(byte[] x) => Convert.ToHexStringLower(SHA256.HashData(x));
    static string FileSha(string path)
    {
        NoLinks(path);
        return Sha(File.ReadAllBytes(path));
    }
    static JsonNode Canon(JsonNode x) => x switch { JsonObject o => new JsonObject(o.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => new KeyValuePair<string, JsonNode?>(p.Key, p.Value is null ? null : Canon(p.Value)))), JsonArray a => new JsonArray(a.Select(v => v is null ? null : Canon(v)).ToArray()), _ => x.DeepClone() };
    static string Hash(JsonNode x) => Sha(Encoding.UTF8.GetBytes(Canon(x).ToJsonString()));
    static bool Inside(string path, string root) => path == root || path.StartsWith(root.TrimEnd('/') + "/", StringComparison.Ordinal);
    static void NoLinks(string path)
    {
        var current = Path.GetPathRoot(Path.GetFullPath(path))!;
        foreach (var part in Path.GetFullPath(path)[current.Length..].Split('/', StringSplitOptions.RemoveEmptyEntries))
        {
            current = Path.Combine(current, part);
            if ((File.Exists(current) || Directory.Exists(current)) && (File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0)
                throw new Blocked("symlink_not_allowed");
        }
    }
    static string Full(string path)
    {
        if (!Path.IsPathFullyQualified(path) || path.Split('/').Contains(".."))
            throw new Blocked("absolute_canonical_path_required");
        var full = Path.GetFullPath(path);
        NoLinks(full);
        return full;
    }
    static void Dir(string path)
    {
        NoLinks(path);
        if (!Directory.Exists(path))
            Directory.CreateDirectory(path, PrivateDirectory);
        File.SetUnixFileMode(path, PrivateDirectory);
    }
    static void Write(string path, byte[] bytes, bool replace = false)
    {
        NoLinks(path);
        var temp = path + ".tmp-" + Guid.NewGuid().ToString("N");
        try
        {
            using (var f = new FileStream(temp, new FileStreamOptions { Mode = FileMode.CreateNew, Access = FileAccess.Write, Share = FileShare.None, UnixCreateMode = PrivateFile }))
            {
                f.Write(bytes);
                f.Flush(true);
            }
            File.Move(temp, path, replace);
            File.SetUnixFileMode(path, PrivateFile);
        }
        finally { if (File.Exists(temp)) File.Delete(temp); }
    }
    static void WriteJson(string path, JsonObject o, bool replace = false) => Write(path, Encoding.UTF8.GetBytes(o.ToJsonString()), replace);
    static FileStream Lock(JsonObject run)
    {
        var store = Full(S(run, "store"));
        var binding = Object(run, "binding");
        if (Inside(store, Path.GetDirectoryName(S(binding, "memory"))!) || Inside(store, Path.GetDirectoryName(S(binding, "definition"))!) || Inside(store, Path.Combine(S(binding, "codex_home"), "automations")))
            throw new Blocked("unsafe_store");
        Dir(store);
        var path = Path.Combine(store, ".lock");
        NoLinks(path);
        try
        {
            return new FileStream(path, new FileStreamOptions { Mode = FileMode.OpenOrCreate, Access = FileAccess.ReadWrite, Share = FileShare.None, UnixCreateMode = PrivateFile });
        }
        catch (IOException) { throw new Blocked("store_busy_retry"); }
    }
    static JsonObject Result(string status) => new() { ["schema_version"] = 1, ["status"] = status };
    static JsonObject Run(JsonObject request, bool retired = false, bool completionRecovery = false, bool cleanup = false)
    {
        var directory = Full(S(request, "run_directory"));
        var run = Read(Path.Combine(directory, "run.json"));
        if (S(run, "run_directory") != directory || !Inside(directory, Full(S(run, "store"))) || S(run, "state") != "captured" || (!cleanup && run["invalidated"] is not null))
            throw new Blocked("invalid_run");
        // Invalidate only appends this retirement marker. Cleanup must match the
        // originally captured identity, not certify the now-invalidated review.
        if (cleanup) run.Remove("invalidated");
        var b = Object(run, "binding");
        var identity = b.DeepClone().AsObject();
        identity.Remove("memory_sha256");
        if (Hash(identity) != S(run, "binding_sha256"))
            throw new Blocked("corrupt_run_binding");
        foreach (var key in cleanup ? System.Array.Empty<string>() : new[] { "definition", "resolver", "helper" })
        if (FileSha(S(b, key)) != S(b, key + "_sha256"))
            throw new Blocked("current_" + key + "_changed");
        if (!completionRecovery && !cleanup)
        {
            var checkpoint = Bundle(File.ReadAllText(S(b, "memory")));
            if (checkpoint["Processed window end"] is not null)
                checkpoint.Remove("Last review");
            if (Hash(checkpoint) != S(b, "memory_checkpoint_sha256"))
                throw new Blocked("current_memory_checkpoint_changed");
        }
        foreach (var item in Object(run, "files"))
        if (FileSha(Path.Combine(directory, item.Key)) != item.Value!.GetValue<string>())
            throw new Blocked("corrupt_run_evidence");
        if (!retired && !cleanup)
        {
            var active = Read(Path.Combine(S(run, "store"), "active.json"));
            if (S(active, "run_directory") != directory || S(active, "capture_sha256") != Hash(run))
                throw new Blocked("inactive_or_corrupt_run");
        }
        return run;
    }
    static string Folder(JsonObject run)
    {
        var path = Path.Combine(S(run, "run_directory"), "delivery");
        Dir(path);
        return path;
    }
    static JsonObject Save(JsonObject run, string kind, JsonObject body)
    {
        body["schema_version"] = 1;
        body["kind"] = kind;
        body["run_directory"] = S(run, "run_directory");
        body["run_sha256"] = Hash(run);
        body["delivery_helper"] = HelperPath();
        body["delivery_helper_sha256"] = FileSha(HelperPath());
        var receipt = new JsonObject { ["payload"] = body, ["payload_sha256"] = Hash(body) };
        var path = Path.Combine(Folder(run), kind + "-" + Guid.NewGuid().ToString("N") + ".json");
        WriteJson(path, receipt);
        var result = Result(kind);
        result["receipt"] = path;
        result["receipt_sha256"] = Hash(receipt);
        result["payload"] = body.DeepClone();
        return result;
    }
    static JsonObject Receipt(JsonObject run, JsonObject request, string key, string kind, bool cleanup = false)
    {
        var path = Full(S(request, key));
        if (!Inside(path, Folder(run)))
            throw new Blocked("foreign_receipt");
        var envelope = Read(path);
        var body = Object(envelope, "payload");
        if (Hash(body) != S(envelope, "payload_sha256") || S(body, "kind") != kind || S(body, "run_directory") != S(run, "run_directory") || S(body, "run_sha256") != Hash(run) || S(body, "delivery_helper") != HelperPath() || (!cleanup && S(body, "delivery_helper_sha256") != FileSha(HelperPath())))
            throw new Blocked("corrupt_receipt_or_delivery_helper_changed");
        if (Optional(request, key + "_sha256") is string expected && expected != Hash(envelope))
            throw new Blocked("receipt_identity_changed");
        return body;
    }
    static string HelperPath([System.Runtime.CompilerServices.CallerFilePath] string path = "") => Path.GetFullPath(path);
    [DllImport("libc", EntryPoint = "kill", SetLastError = true)] static extern int SignalGroup(int pid, int signal);
    static (int Exit, string Out) Process(JsonObject run, string exe, IEnumerable<string> arguments, string? cwd = null)
    {
        var result = ProcessBounded(run, exe, arguments.ToArray(), cwd).GetAwaiter().GetResult();
        return (result.Exit, result.Out);
    }
    static async Task<(int Exit, string Out, byte[] Bytes)> ProcessBounded(JsonObject run, string exe, string[] arguments, string? cwd)
    {
        var binding = Object(run, "binding");
        var timeout = N(binding, "timeout_seconds", 120);
        var maxBytes = N(binding, "max_output_bytes", 16777216);
        if (timeout < 1 || timeout > 120 || maxBytes < 2000 || maxBytes > 16777216)
            throw new Blocked("invalid_process_bounds");
        // Reuse the required Python runtime only as a Unix session launcher:
        // .NET ProcessStartInfo cannot create an owned process group before exec.
        // C# owns supervision, bounded output, receipts and every workflow decision.
        var start = new ProcessStartInfo(S(binding, "python")) { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true, WorkingDirectory = cwd ?? Environment.CurrentDirectory };
        foreach (var arg in new[] { "-I", "-c", "import os,sys;os.setsid();sys.stderr.buffer.write(b'ncg-wiki-owned-group\\n');sys.stderr.buffer.flush();os.execvp(sys.argv[1],sys.argv[1:])", exe })
            start.ArgumentList.Add(arg);
        foreach (var arg in arguments)
            start.ArgumentList.Add(arg);
        using var p = System.Diagnostics.Process.Start(start) ?? throw new Blocked("process_start_failed");
        using var output = new MemoryStream();
        using var errors = new MemoryStream();
        using var cancel = new CancellationTokenSource();
        var limit = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var ready = 0;
        var captured = 0;
        var marker = Encoding.ASCII.GetBytes("ncg-wiki-owned-group\n");
        void Retain(MemoryStream target, ReadOnlySpan<byte> bytes)
        {
            var previous = Interlocked.Add(ref captured, bytes.Length) - bytes.Length;
            var count = Math.Clamp(maxBytes - previous, 0, bytes.Length);
            if (count > 0)
            lock (target)
                target.Write(bytes[..count]);
            if (count < bytes.Length)
                limit.TrySetResult();
        }
        async Task Drain(Stream input, MemoryStream target, bool handshake)
        {
            try
            {
                if (handshake)
                {
                    var prefix = new byte[marker.Length];
                    var length = 0;
                    while (length < prefix.Length)
                    {
                        var count = await input.ReadAsync(prefix.AsMemory(length), cancel.Token);
                        if (count == 0)
                            break;
                        length += count;
                    }
                    if (length == prefix.Length && prefix.SequenceEqual(marker))
                        Interlocked.Exchange(ref ready, 1);
                    else
                        Retain(target, prefix.AsSpan(0, length));
                }
                var block = new byte[8192];
                int countRead;
                while ((countRead = await input.ReadAsync(block, cancel.Token)) > 0)
                    Retain(target, block.AsSpan(0, countRead));
            }
            catch (OperationCanceledException) { }
            catch (IOException) when (cancel.IsCancellationRequested) { }
            catch (ObjectDisposedException) when (cancel.IsCancellationRequested) { }
        }
        var drain = Task.WhenAll(Drain(p.StandardOutput.BaseStream, output, false), Drain(p.StandardError.BaseStream, errors, true));
        var completion = Task.WhenAll(p.WaitForExitAsync(cancel.Token), drain);
        var winner = await Task.WhenAny(completion, Task.Delay(TimeSpan.FromSeconds(timeout)), limit.Task);
        var failure = limit.Task.IsCompleted ? "process_output_limit" : winner != completion ? "process_timeout" : null;
        if (failure is not null)
        {
            if (Volatile.Read(ref ready) == 1)
                SignalGroup(-p.Id, 9);
            try
            {
                if (!p.HasExited)
                    p.Kill(true);
            }
            catch (InvalidOperationException) { }
            catch (System.ComponentModel.Win32Exception) { }
            if (await Task.WhenAny(completion, Task.Delay(2000)) != completion)
            {
                cancel.Cancel();
                p.StandardOutput.Dispose();
                p.StandardError.Dispose();
                await Task.WhenAny(completion, Task.Delay(1000));
            }
        }
        try
        {
            if (completion.IsCompleted)
                await completion;
        }
        catch (OperationCanceledException) { }
        catch (IOException) { failure = "process_drain_failed"; }
        byte[] stdout, stderr;
        lock (output)
            stdout = output.ToArray();
        lock (errors)
            stderr = errors.ToArray();
        var prefixPath = Path.Combine(Folder(run), "process-" + Guid.NewGuid().ToString("N"));
        Write(prefixPath + ".stdout", stdout);
        Write(prefixPath + ".stderr", stderr);
        var exit = p.HasExited ? p.ExitCode : -1;
        WriteJson(prefixPath + ".json", new JsonObject { ["executable"] = exe, ["arguments"] = List(arguments), ["exit"] = exit, ["failure"] = failure, ["timeout_seconds"] = timeout, ["max_output_bytes"] = maxBytes });
        if (failure is not null)
            throw new Blocked(failure);
        return (exit, Encoding.UTF8.GetString(stdout), stdout);
    }
    static string Git(JsonObject run, string repo, params string[] args)
    {
        var result = Process(run, "git", args, repo);
        if (result.Exit != 0)
            throw new Blocked("git_failed_" + args[0]);
        return result.Out.TrimEnd('\r', '\n');
    }
    static void Sha40(string sha)
    {
        if (!Regex.IsMatch(sha, "^[0-9a-f]{40}$"))
            throw new Blocked("lowercase_sha40_required");
    }
    static bool Ancestor(JsonObject run, string repo, string prior, string tip)
    {
        Sha40(prior);
        Sha40(tip);
        var result = Process(run, "git", ["merge-base", "--is-ancestor", prior, tip], repo);
        if (result.Exit > 1)
            throw new Blocked("missing_history_object");
        return result.Exit == 0;
    }
    static JsonObject Repositories(JsonObject request, JsonObject run)
    {
        var repos = Object(request, "repositories");
        if (repos.Count != 3 || !new[] { "backend", "sts", "docs" }.All(repos.ContainsKey))
            throw new Blocked("exact_three_repositories_required");
        var result = new JsonObject();
        foreach (var key in new[] { "backend", "sts", "docs" })
        {
            var repo = Full(S(repos, key));
            if (Git(run, repo, "rev-parse", "--show-toplevel") != repo)
                throw new Blocked("repository_root_required");
            result[key] = repo;
        }
        if (result.Select(x => x.Value!.GetValue<string>()).Distinct(StringComparer.Ordinal).Count() != 3)
            throw new Blocked("distinct_repositories_required");
        var selection = Read(Path.Combine(S(run, "run_directory"), "selection.json"));
        if (!Strings(Object(selection, "scope"), "cwd_roots").Contains(S(result, "docs"), StringComparer.Ordinal))
            throw new Blocked("docs_root_not_bound_scope");
        return result;
    }
    static JsonObject Fetch(JsonObject run, JsonObject repos)
    {
        var pins = new JsonObject();
        foreach (var key in new[] { "backend", "sts" })
        {
            var repo = S(repos, key);
            Git(run, repo, "fetch", "--quiet", "--no-tags", "--no-write-fetch-head", "origin", "+refs/heads/develop:refs/remotes/origin/develop", "+refs/heads/production:refs/remotes/origin/production");
            foreach (var branch in new[] { "develop", "production" })
            {
                var reference = "refs/remotes/origin/" + branch;
                var sha = Git(run, repo, "rev-parse", reference + "^{commit}");
                Sha40(sha);
                pins[repo + "|" + reference] = sha;
            }
        }
        var docs = S(repos, "docs");
        Git(run, docs, "fetch", "--no-tags", "--no-write-fetch-head", "origin", "+refs/heads/main:refs/remotes/origin/main");
        var tip = Git(run, docs, "rev-parse", "refs/remotes/origin/main^{commit}");
        Sha40(tip);
        return new JsonObject { ["source_pins"] = pins, ["documentation_pin"] = new JsonObject { ["repository"] = docs, ["ref"] = "refs/remotes/origin/main", ["sha"] = tip } };
    }
    static JsonObject Bundle(string text)
    {
        var match = Regex.Match(text, @"^## ", RegexOptions.Multiline);
        var header = match.Success ? text[..match.Index] : text;
        var result = new JsonObject();
        foreach (var key in Keys)
        {
            var values = Regex.Matches(header, "^" + Regex.Escape(key) + @":[^\S\r\n]*([^\r\n]*)$", RegexOptions.Multiline);
            if (values.Count > 1)
                throw new Blocked("duplicate_checkpoint_" + key);
            result[key] = values.Count == 0 ? null : JsonValue.Create(values[0].Groups[1].Value.Trim());
        }
        return result;
    }
    static JsonObject? Parsed(JsonObject bundle, string key) => bundle[key] is null ? null : JsonNode.Parse(bundle[key]!.GetValue<string>(), documentOptions: new JsonDocumentOptions { AllowDuplicateProperties = false })!.AsObject();
    static JsonObject Proof(JsonObject request, JsonObject run)
    {
        var helper = Full(S(request, "review_helper"));
        if (helper != S(Object(run, "binding"), "helper"))
            throw new Blocked("review_helper_must_match_capture");
        var input = Object(request, "review_request").DeepClone().AsObject();
        input["run_directory"] = S(run, "run_directory");
        var path = Path.Combine(Folder(run), "verify-request-" + Guid.NewGuid().ToString("N") + ".json");
        WriteJson(path, input);
        var process = Process(run, "dotnet", ["run", "--file", helper, "--", "verify-pages", "--request", path]);
        if (process.Exit != 0)
            throw new Blocked("current_complete_proof_failed");
        var output = JsonNode.Parse(process.Out.Split('\n', StringSplitOptions.RemoveEmptyEntries).Last())!.AsObject();
        if (S(output, "status") != "complete")
            throw new Blocked("complete_proof_required");
        var proof = Read(Path.Combine(S(run, "run_directory"), "complete.json"));
        if (Hash(proof) != S(output, "receipt_sha256"))
            throw new Blocked("current_proof_changed");
        return proof;
    }
    static JsonArray Commits(JsonObject run, string repo, string range) => List(Git(run, repo, "rev-list", "--reverse", "--topo-order", range).Split('\n', StringSplitOptions.RemoveEmptyEntries));
    public static JsonObject VerifySources(JsonObject request)
    {
        var run = Run(request);
        var proof = Proof(request, run);
        using var mutex = Lock(run);
        if (Hash(Read(Path.Combine(S(run, "run_directory"), "complete.json"))) != Hash(proof))
            throw new Blocked("proof_changed");
        var repos = Repositories(request, run);
        var current = Fetch(run, repos);
        var old = Bundle(File.ReadAllText(Path.Combine(S(run, "run_directory"), "memory.md")));
        var oldPins = Parsed(old, "Authoritative source tips");
        var pins = Object(current, "source_pins");
        if (oldPins is not null && (oldPins.Count != 4 || !pins.All(x => oldPins.ContainsKey(x.Key))))
            throw new Blocked("old_exact_four_source_tips_required");
        var ranges = new JsonObject();
        var candidates = new JsonArray();
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var key in new[] { "backend", "sts" })
        {
            var repo = S(repos, key);
            var develop = repo + "|refs/remotes/origin/develop";
            var production = repo + "|refs/remotes/origin/production";
            var currentDevelop = S(pins, develop);
            var currentProduction = S(pins, production);
            var priorDevelop = oldPins is null ? null : S(oldPins, develop);
            var priorProduction = oldPins is null ? null : S(oldPins, production);
            if (priorDevelop is not null && (!Ancestor(run, repo, priorDevelop, currentDevelop) || !Ancestor(run, repo, priorProduction!, currentProduction)))
                throw new Blocked("code_history_rewritten_or_missing");
            var commits = priorDevelop is null ? new JsonArray() : List(Git(run, repo, "rev-list", "--reverse", "--topo-order", currentDevelop, currentProduction, "--not", priorDevelop, priorProduction!).Split('\n', StringSplitOptions.RemoveEmptyEntries));
            ranges[repo] = new JsonObject { ["prior_develop"] = priorDevelop, ["prior_production"] = priorProduction, ["develop"] = currentDevelop, ["production"] = currentProduction, ["migration_no_backfill"] = priorDevelop is null, ["commits"] = commits.DeepClone() };
            foreach (var node in commits)
            if (seen.Add(repo + "|" + node!.GetValue<string>()))
                candidates.Add((JsonNode)new JsonObject { ["kind"] = "git", ["repository"] = repo, ["sha"] = node!.DeepClone() });
        }
        var docsPin = Object(current, "documentation_pin");
        var priorDocs = Parsed(old, "Docs reviewed tip");
        if (priorDocs is not null && (S(priorDocs, "repository") != S(repos, "docs") || S(priorDocs, "ref") != "refs/remotes/origin/main" || !Ancestor(run, S(repos, "docs"), S(priorDocs, "sha"), S(docsPin, "sha"))))
            throw new Blocked("docs_baseline_invalid_or_nonancestor");
        var result = Save(run, "sources", new JsonObject { ["repositories"] = repos, ["source_pins"] = pins.DeepClone(), ["allow_source_advancement"] = request["allow_source_advancement"]?.GetValue<bool>() ?? false, ["documentation_pin"] = docsPin.DeepClone(), ["code_ranges"] = ranges, ["git_candidates"] = candidates, ["old_bundle"] = old, ["docs_prior"] = priorDocs, ["complete_proof_sha256"] = Hash(proof) });
        // Candidate arrays remain protected; public discovery is paged.
        var emitted = Object(result, "payload");
        emitted.Remove("code_ranges");
        emitted.Remove("git_candidates");
        emitted["git_candidate_count"] = candidates.Count;
        return result;
    }
    static JsonArray DocsCandidates(JsonObject run, JsonObject source)
    {
        var pin = Object(source, "documentation_pin");
        var prior = source["docs_prior"]?.AsObject();
        return Commits(run, S(pin, "repository"), prior is null ? S(pin, "sha") : S(prior, "sha") + ".." + S(pin, "sha"));
    }
    public static JsonObject DocsHistory(JsonObject request)
    {
        var run = Run(request);
        using var mutex = Lock(run);
        var source = Receipt(run, request, "source_receipt", "sources");
        var commits = DocsCandidates(run, source);
        var offset = N(request, "offset", 0);
        var limit = N(request, "limit", 100);
        if (offset < 0 || offset > commits.Count || limit < 1 || limit > 100)
            throw new Blocked("invalid_bounded_history_page");
        var count = Math.Min(limit, commits.Count - offset);
        var page = new JsonArray(commits.Skip(offset).Take(count).Select(x => x!.DeepClone()).ToArray());
        var body = new JsonObject { ["source_receipt_sha256"] = Hash(source), ["docs_pin"] = source["documentation_pin"]!.DeepClone(), ["history_sha256"] = Hash(commits), ["baseline_missing"] = source["docs_prior"] is null, ["offset"] = offset, ["limit"] = limit, ["count"] = count, ["selection_count"] = commits.Count, ["next_offset"] = offset + count, ["has_more"] = offset + count < commits.Count, ["commits"] = page };
        var output = Save(run, "docs-history", body);
        var history = Path.Combine(Folder(run), "docs-history");
        Dir(history);
        WriteJson(Path.Combine(history, offset + ".json"), new JsonObject { ["receipt"] = output["receipt"]!.DeepClone(), ["receipt_sha256"] = output["receipt_sha256"]!.DeepClone() }, true);
        return output;
    }
    public static JsonObject GitHistory(JsonObject request)
    {
        var run = Run(request);
        using var mutex = Lock(run);
        var source = Receipt(run, request, "source_receipt", "sources");
        var candidates = Array(source, "git_candidates");
        var offset = N(request, "offset", 0);
        var limit = N(request, "limit", 100);
        if (offset < 0 || offset > candidates.Count || limit < 1 || limit > 100)
            throw new Blocked("invalid_bounded_history_page");
        var count = Math.Min(limit, candidates.Count - offset);
        var page = new JsonArray(candidates.Skip(offset).Take(count).Select(x => x!.DeepClone()).ToArray());
        var body = new JsonObject { ["source_receipt_sha256"] = Hash(source), ["history_sha256"] = Hash(candidates), ["offset"] = offset, ["limit"] = limit, ["count"] = count, ["selection_count"] = candidates.Count, ["next_offset"] = offset + count, ["has_more"] = offset + count < candidates.Count, ["candidates"] = page };
        var output = Save(run, "git-history", body);
        var history = Path.Combine(Folder(run), "git-history");
        Dir(history);
        WriteJson(Path.Combine(history, offset + ".json"), new JsonObject { ["receipt"] = output["receipt"]!.DeepClone(), ["receipt_sha256"] = output["receipt_sha256"]!.DeepClone() }, true);
        return output;
    }
    static void CompleteGitHistory(JsonObject run, JsonObject source)
    {
        var candidates = Array(source, "git_candidates");
        var offset = 0;
        do
        {
            var pointer = Read(Path.Combine(Folder(run), "git-history", offset + ".json"));
            var request = new JsonObject { ["history_receipt"] = pointer["receipt"]!.DeepClone(), ["history_receipt_sha256"] = pointer["receipt_sha256"]!.DeepClone() };
            var page = Receipt(run, request, "history_receipt", "git-history");
            var count = N(page, "count", -1);
            if (S(page, "source_receipt_sha256") != Hash(source) || S(page, "history_sha256") != Hash(candidates) || N(page, "offset", -1) != offset || N(page, "selection_count", -1) != candidates.Count || count < 0 || Hash(Array(page, "candidates")) != Hash(new JsonArray(candidates.Skip(offset).Take(count).Select(x => x!.DeepClone()).ToArray())))
                throw new Blocked("invalid_git_history_coverage");
            if (page["has_more"]!.GetValue<bool>() && count == 0)
                throw new Blocked("nonprogressing_git_history");
            offset += count;
            if (!page["has_more"]!.GetValue<bool>())
            {
                if (offset != candidates.Count)
                    throw new Blocked("incomplete_git_history");
                break;
            }
        } while (true);
    }
    static void CompleteHistory(JsonObject run, JsonObject source, JsonArray commits)
    {
        var offset = 0;
        do
        {
            var pointer = Read(Path.Combine(Folder(run), "docs-history", offset + ".json"));
            var request = new JsonObject { ["history_receipt"] = pointer["receipt"]!.DeepClone(), ["history_receipt_sha256"] = pointer["receipt_sha256"]!.DeepClone() };
            var page = Receipt(run, request, "history_receipt", "docs-history");
            if (S(page, "source_receipt_sha256") != Hash(source) || S(page, "history_sha256") != Hash(commits) || N(page, "offset", -1) != offset || N(page, "selection_count", -1) != commits.Count)
                throw new Blocked("docs_history_receipt_changed");
            var count = N(page, "count", -1);
            if (count < 0 || !Array(page, "commits").Select(x => x!.GetValue<string>()).SequenceEqual(commits.Skip(offset).Take(count).Select(x => x!.GetValue<string>())))
                throw new Blocked("invalid_docs_history_coverage");
            if (page["has_more"]!.GetValue<bool>() && count == 0)
                throw new Blocked("nonprogressing_docs_history");
            offset += count;
            if (!page["has_more"]!.GetValue<bool>())
            {
                if (offset != commits.Count)
                    throw new Blocked("incomplete_docs_history");
                break;
            }
        } while (true);
    }
    static string Candidate(JsonObject c) => S(c, "kind") switch { "session" => "session|" + S(c, "id"), "git" => "git|" + S(c, "repository") + "|" + S(c, "sha"), _ => throw new Blocked("invalid_candidate_kind") };
    static string Relative(string path)
    {
        if (Path.IsPathFullyQualified(path) || path.Split('/').Any(p => p is "" or "." or "..") || !path.EndsWith(".md", StringComparison.OrdinalIgnoreCase) || path.StartsWith(".git/", StringComparison.Ordinal))
            throw new Blocked("owned_relative_markdown_path_required");
        return path;
    }
    static string WikiRelative(string canonicalDocs, string deliveryDocs, string path)
    {
        var full = Full(path);
        var root = Inside(full, canonicalDocs) ? canonicalDocs : Inside(full, deliveryDocs) ? deliveryDocs : throw new Blocked("wiki_outside_docs");
        return Relative(Path.GetRelativePath(root, full));
    }
    static string? Blob(JsonObject run, string repo, string commit, string path)
    {
        var tree = Process(run, "git", ["ls-tree", "-z", commit, "--", path], repo);
        if (tree.Exit != 0)
            throw new Blocked("git_tree_lookup_failed");
        if (tree.Out.Length == 0)
            return null;
        var entries = tree.Out.Split('\0', StringSplitOptions.RemoveEmptyEntries);
        if (entries.Length != 1)
            throw new Blocked("ambiguous_git_tree_path");
        var separator = entries[0].IndexOf('\t');
        if (separator < 0 || entries[0][(separator + 1)..] != path)
            throw new Blocked("git_tree_path_mismatch");
        var metadata = entries[0][..separator].Split(' ');
        if (metadata.Length != 3 || metadata[1] != "blob" || metadata[0] is not ("100644" or "100755"))
            throw new Blocked("regular_git_blob_required");
        Sha40(metadata[2]);
        return metadata[2];
    }
    static byte[] GitBytes(JsonObject run, string repo, string blob)
    {
        var result = ProcessBounded(run, "git", ["cat-file", "blob", blob], repo).GetAwaiter().GetResult();
        if (result.Exit != 0)
            throw new Blocked("git_blob_unreadable");
        return result.Bytes;
    }
    static void ExactSources(JsonObject run, JsonObject source, JsonObject fresh, bool docsEqual)
    {
        if (Hash(Object(fresh, "source_pins")) != Hash(Object(source, "source_pins")))
        {
            var pins = Object(source, "source_pins");
            var current = Object(fresh, "source_pins");
            if (source["allow_source_advancement"]?.GetValue<bool>() != true)
                throw new Blocked("authoritative_code_pins_changed");
            if (pins.Count != 4 || current.Count != 4 ||
                pins.Any(item => !current.ContainsKey(item.Key) || !Ancestor(run, item.Key[..item.Key.LastIndexOf('|')], item.Value!.GetValue<string>(), S(current, item.Key))))
                throw new Blocked("authoritative_code_pins_changed_or_rewritten");
        }
        if (docsEqual && Hash(Object(fresh, "documentation_pin")) != Hash(Object(source, "documentation_pin")))
            throw new Blocked("docs_pin_changed");
    }
    static string Origin(JsonObject run, string repo)
    {
        var fetch = Git(run, repo, "remote", "get-url", "--all", "origin");
        var push = Git(run, repo, "remote", "get-url", "--push", "--all", "origin");
        if (fetch.Length == 0 || fetch.Contains('\n') || push != fetch)
            throw new Blocked("one_matching_docs_origin_required");
        // Git resolves URL rewrites. Resolve only relative local paths ourselves,
        // so cloning cannot reinterpret them from a different working directory.
        return fetch.Contains(':') ? fetch : Full(Path.GetFullPath(fetch, repo));
    }
    static string Workspace(JsonObject run, JsonObject workspace, JsonObject source, bool cleanBase)
    {
        var root = Full(S(workspace, "workspace_root"));
        var canonical = S(Object(source, "repositories"), "docs");
        if (!Inside(root, Path.Combine(Folder(run), "workspaces")) || root == canonical ||
            S(workspace, "canonical_docs_root") != canonical || S(workspace, "source_payload_sha256") != Hash(source) ||
            S(workspace, "docs_base_sha") != S(Object(source, "documentation_pin"), "sha") ||
            Git(run, root, "rev-parse", "--show-toplevel") != root ||
            Git(run, root, "rev-parse", "--absolute-git-dir") != Path.Combine(root, ".git") ||
            Git(run, root, "symbolic-ref", "--short", "HEAD") != "main" ||
            Origin(run, root) != S(workspace, "origin") || Origin(run, canonical) != S(workspace, "origin"))
            throw new Blocked("owned_workspace_identity_changed");
        NoLinks(Path.Combine(root, ".git"));
        if (cleanBase && (Git(run, root, "rev-parse", "HEAD") != S(workspace, "docs_base_sha") ||
            Git(run, root, "status", "--porcelain=v1", "-z", "--untracked-files=all").Length != 0))
            throw new Blocked("clean_pinned_workspace_main_required");
        return root;
    }
    static void CurrentPointer(JsonObject run, JsonObject request, string name, string receiptKey)
    {
        var path = Path.Combine(Folder(run), name + ".json");
        if (!File.Exists(path)) throw new Blocked("retired_or_unbound_" + name);
        var pointer = Read(path);
        if (S(pointer, "receipt") != S(request, receiptKey) || S(pointer, "receipt_sha256") != Hash(Read(S(request, receiptKey))))
            throw new Blocked("retired_or_unbound_" + name);
    }
    static JsonObject DocsRefresh(JsonObject run, JsonObject source, JsonObject fresh, string? workspace = null)
    {
        var docs = S(Object(source, "repositories"), "docs");
        var prior = S(Object(source, "documentation_pin"), "sha");
        var current = S(Object(fresh, "documentation_pin"), "sha");
        if (prior == current || !Ancestor(run, docs, prior, current)) throw new Blocked("docs_refresh_requires_append_only_main");
        return new JsonObject { ["schema_version"] = 1, ["status"] = "refresh_required", ["reason"] = "docs_main_advanced",
            ["docs_base_sha"] = prior, ["remote_main_sha"] = current, ["workspace_root"] = workspace, ["checkpoint_changed"] = false };
    }
    public static JsonObject PrepareWorkspace(JsonObject request)
    {
        var run = Run(request);
        var proof = Proof(request, run);
        using var mutex = Lock(run);
        var source = Receipt(run, request, "source_receipt", "sources");
        if (Hash(proof) != S(source, "complete_proof_sha256") || Hash(Repositories(request, run)) != Hash(Object(source, "repositories")))
            throw new Blocked("workspace_source_proof_changed");
        CompleteGitHistory(run, source);
        CompleteHistory(run, source, DocsCandidates(run, source));
        var fresh = Fetch(run, Object(source, "repositories"));
        ExactSources(run, source, fresh, false);
        if (Hash(Object(source, "documentation_pin")) != Hash(Object(fresh, "documentation_pin")))
            return DocsRefresh(run, source, fresh);
        if (Protection(run) is not null) throw new Blocked("workspace_and_worktree_protection_are_exclusive");
        var pointerPath = Path.Combine(Folder(run), "workspace.json");
        if (File.Exists(pointerPath))
        {
            var pointer = Read(pointerPath);
            var saved = Receipt(run, new JsonObject { ["workspace_receipt"] = pointer["receipt"]!.DeepClone(), ["workspace_receipt_sha256"] = pointer["receipt_sha256"]!.DeepClone() }, "workspace_receipt", "workspace");
            Workspace(run, saved, source, true);
            return new JsonObject { ["schema_version"] = 1, ["status"] = "workspace_ready", ["receipt"] = pointer["receipt"]!.DeepClone(), ["receipt_sha256"] = pointer["receipt_sha256"]!.DeepClone(), ["payload"] = saved.DeepClone() };
        }
        var preparationPath = Path.Combine(Folder(run), "workspace-preparation.json");
        JsonObject workspace;
        if (File.Exists(preparationPath))
        {
            var saved = Read(preparationPath);
            workspace = Object(saved, "payload");
            if (Hash(workspace) != S(saved, "payload_sha256") || S(workspace, "run_sha256") != Hash(run) ||
                S(workspace, "source_payload_sha256") != Hash(source) || S(workspace, "delivery_helper_sha256") != FileSha(HelperPath()))
                throw new Blocked("workspace_preparation_identity_changed");
        }
        else
        {
            var canonical = S(Object(source, "repositories"), "docs");
            var parent = Path.Combine(Folder(run), "workspaces");
            Dir(parent);
            workspace = new JsonObject { ["workspace_root"] = Path.Combine(parent, "main-" + Guid.NewGuid().ToString("N")),
                ["canonical_docs_root"] = canonical, ["origin"] = Origin(run, canonical),
                ["docs_base_sha"] = S(Object(source, "documentation_pin"), "sha"), ["source_payload_sha256"] = Hash(source),
                ["run_sha256"] = Hash(run), ["delivery_helper_sha256"] = FileSha(HelperPath()) };
            WriteJson(preparationPath, new JsonObject { ["payload"] = workspace, ["payload_sha256"] = Hash(workspace) });
        }
        var root = Full(S(workspace, "workspace_root"));
        if (!Directory.Exists(root))
            Git(run, Folder(run), "-c", "core.hooksPath=/dev/null", "clone", "--quiet", "--no-local", "--no-hardlinks", "--single-branch", "--branch", "main", "--", S(workspace, "origin"), root);
        Dir(root);
        Workspace(run, workspace, source, true);
        var output = Save(run, "workspace", workspace.DeepClone().AsObject());
        WriteJson(pointerPath, new JsonObject { ["receipt"] = output["receipt"]!.DeepClone(), ["receipt_sha256"] = output["receipt_sha256"]!.DeepClone() });
        output["status"] = "workspace_ready";
        return output;
    }
    // Explicitly authorized local docs protection. The journal is mutable, but its
    // original snapshot and exact owned stash are frozen into the delivery plan.
    static string ProtectionPath(JsonObject run) => Path.Combine(Folder(run), "worktree-protection.json");
    static JsonObject? Protection(JsonObject run)
    {
        var path = ProtectionPath(run);
        if (!File.Exists(path)) return null;
        var envelope = Read(path);
        var body = Object(envelope, "payload");
        if (Hash(body) != S(envelope, "payload_sha256") || S(body, "run_sha256") != Hash(run))
            throw new Blocked("corrupt_worktree_protection");
        var docs = Full(S(body, "docs"));
        if (Inside(S(run, "store"), docs) || Git(run, docs, "rev-parse", "--show-toplevel") != docs ||
            Git(run, docs, "rev-parse", "--absolute-git-dir") != S(body, "git_directory") ||
            Git(run, docs, "symbolic-ref", "--short", "HEAD") != "main")
            throw new Blocked("worktree_protection_identity_changed");
        foreach (var item in Object(body, "backup_files"))
            if (!Inside(Full(item.Key), Folder(run)) || FileSha(item.Key) != item.Value!.GetValue<string>())
                throw new Blocked("worktree_backup_changed");
        return body;
    }
    static void SaveProtection(JsonObject run, JsonObject journal) => WriteJson(ProtectionPath(run),
        new JsonObject { ["payload"] = journal.DeepClone(), ["payload_sha256"] = Hash(journal) }, true);
    static string ProtectionIdentity(JsonObject p) => Hash(new JsonObject { ["run_sha256"] = p["run_sha256"]!.DeepClone(),
        ["docs"] = p["docs"]!.DeepClone(), ["base_sha"] = p["base_sha"]!.DeepClone(), ["label"] = p["label"]!.DeepClone(),
        ["initial"] = p["initial"]!.DeepClone(), ["backup_files"] = p["backup_files"]!.DeepClone(), ["stash_sha"] = p["stash_sha"]?.DeepClone() });
    static string[] GitPaths(JsonObject run, string docs, params string[] args)
    {
        var result = ProcessBounded(run, "git", args, docs).GetAwaiter().GetResult();
        if (result.Exit != 0) throw new Blocked("git_path_listing_failed");
        try { return new UTF8Encoding(false, true).GetString(result.Bytes).Split('\0', StringSplitOptions.RemoveEmptyEntries); }
        catch (DecoderFallbackException) { throw new Blocked("non_utf8_worktree_path_unsupported"); }
    }
    static string WorktreePath(string path)
    {
        if (Path.IsPathFullyQualified(path) || path.Split('/').Any(p => p is "" or "." or "..") || path == ".git" || path.StartsWith(".git/", StringComparison.Ordinal))
            throw new Blocked("safe_relative_worktree_path_required");
        return path;
    }
    static JsonObject WorktreeSnapshot(JsonObject run, string docs, JsonObject? backups = null)
    {
        var index = Git(run, docs, "write-tree"); // Rejects unmerged index without changing it.
        var staged = GitPaths(run, docs, "ls-files", "--stage", "-z");
        if (staged.Any(x => x.StartsWith("160000 ", StringComparison.Ordinal) || x.StartsWith("120000 ", StringComparison.Ordinal)) ||
            GitPaths(run, docs, "ls-files", "-v", "-z").Any(x => !x.StartsWith("H ", StringComparison.Ordinal)))
            throw new Blocked("special_index_or_submodule_unsupported");
        var untrackedPaths = GitPaths(run, docs, "ls-files", "--others", "--exclude-standard", "-z");
        var possibleChanges = GitPaths(run, docs, "ls-files", "--modified", "--deleted", "-z")
            .Concat(GitPaths(run, docs, "diff", "--cached", "--name-only", "--no-renames", "-z")).Concat(untrackedPaths).Distinct().ToArray();
        if (backups is not null && possibleChanges.Any(x => Path.GetFileName(x) is ".gitignore" or ".gitattributes"))
            throw new Blocked("changing_ignore_or_attributes_requires_separate_delivery");
        if (possibleChanges.Length > 0)
        {
            var autocrlf = Process(run, "git", ["config", "--get", "core.autocrlf"], docs);
            if (autocrlf.Exit is not (0 or 1) || autocrlf.Out.Trim() is not ("" or "false" or "input")) throw new Blocked("worktree_eol_conversion_unsupported");
            var attributes = GitPaths(run, docs, new[] { "check-attr", "-z", "filter", "working-tree-encoding", "eol", "--" }.Concat(possibleChanges).ToArray());
            if (attributes.Length % 3 != 0 || attributes.Where((_, i) => i % 3 == 2).Any(x => x is not ("unspecified" or "unset")))
                throw new Blocked("worktree_filters_or_eol_attributes_unsupported");
        }
        // stash create is non-destructive: it creates only an unreferenced Git
        // object; no staging, worktree or stash-ref change occurs here.
        var tracked = Git(run, docs, "stash", "create");
        var tree = Git(run, docs, "rev-parse", (tracked.Length == 0 ? "HEAD" : tracked) + "^{tree}");
        var untracked = new JsonObject();
        var total = 0L;
        JsonObject RawFile(string path)
        {
            var full = Full(Path.Combine(docs, WorktreePath(path)));
            if (Process(run, "test", ["-f", full]).Exit != 0) throw new Blocked("worktree_regular_file_required");
            total += new FileInfo(full).Length;
            if (total > N(Object(run, "binding"), "max_output_bytes", 16777216)) throw new Blocked("worktree_backup_output_limit");
            var bytes = File.ReadAllBytes(full);
            var mode = (File.GetUnixFileMode(full) & (UnixFileMode.UserExecute | UnixFileMode.GroupExecute | UnixFileMode.OtherExecute)) != 0 ? "100755" : "100644";
            if (backups is not null)
            {
                var backup = Path.Combine(Folder(run), "prior-file-" + Guid.NewGuid().ToString("N"));
                Write(backup, bytes); backups[backup] = Sha(bytes);
            }
            return new JsonObject { ["sha256"] = Sha(bytes), ["mode"] = mode, ["permissions"] = (int)File.GetUnixFileMode(full) };
        }
        var rawTracked = new JsonObject();
        foreach (var path in ChangedTrackedPaths(run, docs, index, tree))
        {
            var blob = Blob(run, docs, tree, path);
            if (blob is null)
            {
                if (File.Exists(Path.Combine(docs, path))) throw new Blocked("deleted_worktree_path_collision");
                rawTracked[path] = null;
            }
            else
            {
                var raw = RawFile(path);
                if (S(raw, "sha256") != Sha(GitBytes(run, docs, blob))) throw new Blocked("worktree_raw_normalization_unsupported");
                if (GitPaths(run, docs, "ls-tree", "-z", tree, "--", path)[0].Split(' ')[0] != S(raw, "mode"))
                    throw new Blocked("worktree_mode_conversion_unsupported");
                rawTracked[path] = raw;
            }
        }
        foreach (var path in untrackedPaths)
        {
            var raw = RawFile(path);
            var full = Full(Path.Combine(docs, WorktreePath(path)));
            if (Git(run, docs, "hash-object", "--path=" + path, "--", full) != Git(run, docs, "hash-object", "--no-filters", "--", full))
                throw new Blocked("worktree_raw_normalization_unsupported");
            if (S(raw, "mode") == "100755" && Process(run, "git", ["config", "--bool", "--get", "core.filemode"], docs).Out.Trim() == "false")
                throw new Blocked("untracked_mode_conversion_unsupported");
            untracked[path] = raw;
        }
        return new JsonObject { ["index_tree"] = index, ["worktree_tree"] = tree, ["tracked_raw"] = rawTracked, ["untracked"] = untracked };
    }
    static IEnumerable<string> ChangedTrackedPaths(JsonObject run, string docs, string index, string worktree) =>
        GitPaths(run, docs, "diff", "--name-only", "--no-renames", "-z", "HEAD", index)
        .Concat(GitPaths(run, docs, "diff", "--name-only", "--no-renames", "-z", index, worktree)).Distinct().Order(StringComparer.Ordinal);
    static void VerifyOwnedStash(JsonObject run, JsonObject p)
    {
        var docs = S(p, "docs"); var stash = S(p, "stash_sha");
        Sha40(stash);
        var parents = Git(run, docs, "rev-list", "--parents", "-n", "1", stash).Split(' ');
        var initial = Object(p, "initial");
        if (parents.Length is not (3 or 4) || parents[1] != S(p, "base_sha") ||
            Git(run, docs, "rev-parse", parents[2] + "^{tree}") != S(initial, "index_tree") ||
            Git(run, docs, "rev-parse", stash + "^{tree}") != S(initial, "worktree_tree") ||
            Git(run, docs, "show", "-s", "--format=%s", stash) != "On main: " + S(p, "label"))
            throw new Blocked("owned_stash_snapshot_mismatch");
        var entries = parents.Length == 4 ? GitPaths(run, docs, "ls-tree", "-r", "-z", parents[3]) : [];
        var untracked = new JsonObject();
        foreach (var entry in entries)
        {
            var parts = entry.Split('\t', 2); var metadata = parts[0].Split(' ');
            if (parts.Length != 2 || metadata.Length != 3 || metadata[1] != "blob" || metadata[0] is not ("100644" or "100755"))
                throw new Blocked("invalid_stash_untracked_tree");
            untracked[parts[1]] = new JsonObject { ["sha256"] = Sha(GitBytes(run, docs, metadata[2])), ["mode"] = metadata[0] };
        }
        if (Hash(untracked) != Hash(WithoutPermissions(Object(initial, "untracked")))) throw new Blocked("owned_stash_untracked_mismatch");
    }
    static JsonObject WithoutPermissions(JsonObject values)
    {
        var copy = values.DeepClone().AsObject();
        foreach (var item in copy)
            if (item.Value is JsonObject file) file.Remove("permissions");
        return copy;
    }
    static JsonObject WithoutSnapshotPermissions(JsonObject snapshot)
    {
        var copy = snapshot.DeepClone().AsObject();
        foreach (var key in new[] { "tracked_raw", "untracked" }) copy[key] = WithoutPermissions(Object(copy, key));
        return copy;
    }
    static bool AdoptRestoredBytes(JsonObject run, JsonObject p)
    {
        var docs = S(p, "docs"); var expected = Object(p, "expected_restored");
        if (Hash(WithoutSnapshotPermissions(WorktreeSnapshot(run, docs))) != Hash(WithoutSnapshotPermissions(expected))) return false;
        // Git preserves executable mode, but not private 0600 permissions. Set
        // saved permissions only after all actual contents/index are proven owned.
        foreach (var key in new[] { "tracked_raw", "untracked" })
            foreach (var item in Object(expected, key))
                if (item.Value is JsonObject file) File.SetUnixFileMode(Full(Path.Combine(docs, WorktreePath(item.Key))), (UnixFileMode)N(file, "permissions", 0));
        return Hash(WorktreeSnapshot(run, docs)) == Hash(expected);
    }
    static JsonObject ProtectionResult(JsonObject p) => new() { ["schema_version"] = 1,
        ["status"] = S(p, "phase") == "restored" ? "restored" : "protected", ["stash_sha"] = p["stash_sha"]?.DeepClone(),
        ["protection_identity"] = ProtectionIdentity(p), ["safety_backup_retained"] = p["stash_sha"] is not null };
    static string? FindOwnedStash(JsonObject run, JsonObject p)
    {
        var docs = S(p, "docs");
        var matches = Process(run, "git", ["reflog", "show", "--format=%H%x09%gs", "refs/stash"], docs);
        if (matches.Exit != 0 && Process(run, "git", ["rev-parse", "--verify", "refs/stash"], docs).Exit == 0)
            throw new Blocked("stash_ownership_lookup_failed");
        var owned = matches.Out.Split('\n', StringSplitOptions.RemoveEmptyEntries).Where(x => x.EndsWith("\tOn main: " + S(p, "label"), StringComparison.Ordinal)).Select(x => x.Split('\t')[0]).Distinct().ToArray();
        if (owned.Length > 1) throw new Blocked("ambiguous_owned_stash");
        return owned.SingleOrDefault();
    }
    public static JsonObject ProtectWorktree(JsonObject request)
    {
        var run = Run(request); var proof = Proof(request, run);
        using var mutex = Lock(run);
        var source = Receipt(run, request, "source_receipt", "sources");
        if (Hash(proof) != S(source, "complete_proof_sha256")) throw new Blocked("source_complete_proof_changed");
        var repos = Object(source, "repositories"); var docs = S(repos, "docs");
        ExactSources(run, source, Fetch(run, repos), true);
        CompleteHistory(run, source, DocsCandidates(run, source)); CompleteGitHistory(run, source);
        var p = Protection(run);
        if (p is not null && S(p, "phase") != "prepared")
        {
            if (p["stash_sha"] is not null) VerifyOwnedStash(run, p);
            return ProtectionResult(p);
        }
        var baseSha = S(Object(source, "documentation_pin"), "sha");
        if (Inside(S(run, "store"), docs) || Git(run, docs, "symbolic-ref", "--short", "HEAD") != "main" || Git(run, docs, "rev-parse", "HEAD") != baseSha)
            throw new Blocked("aligned_main_required_for_protection");
        if (p is null)
        {
            var backups = new JsonObject(); var initial = WorktreeSnapshot(run, docs, backups);
            p = new JsonObject { ["run_sha256"] = Hash(run), ["docs"] = docs, ["git_directory"] = Git(run, docs, "rev-parse", "--absolute-git-dir"),
                ["base_sha"] = baseSha, ["label"] = "ncg-wiki-protected-" + Guid.NewGuid().ToString("N"), ["initial"] = initial,
                ["backup_files"] = backups, ["phase"] = "prepared", ["prior_stash"] = Process(run, "git", ["rev-parse", "--verify", "refs/stash"], docs).Out.Trim() };
            SaveProtection(run, p); // Must precede the first destructive worktree operation.
        }
        var owned = FindOwnedStash(run, p);
        if (owned is null)
        {
            if (Hash(WorktreeSnapshot(run, docs)) != Hash(Object(p, "initial")) ||
                Process(run, "git", ["rev-parse", "--verify", "refs/stash"], docs).Out.Trim() != SOrEmpty(p, "prior_stash"))
                throw new Blocked("preexisting_work_changed_before_protection");
            if (Git(run, docs, "status", "--porcelain=v1", "-z", "--untracked-files=all").Length != 0)
            {
                var result = Process(run, "git", ["stash", "push", "--include-untracked", "--message", S(p, "label")], docs);
                if (result.Exit != 0) throw new Blocked("worktree_protection_stash_failed");
                p["stash_sha"] = Git(run, docs, "rev-parse", "refs/stash");
            }
        }
        else p["stash_sha"] = owned;
        SaveProtection(run, p);
        if (p["stash_sha"] is not null) VerifyOwnedStash(run, p);
        if (Git(run, docs, "status", "--porcelain=v1", "-z", "--untracked-files=all").Length != 0) throw new Blocked("worktree_not_clean_after_protection");
        p["phase"] = "protected"; SaveProtection(run, p);
        return ProtectionResult(p);
    }
    static string SOrEmpty(JsonObject o, string key) => Optional(o, key) ?? "";
    static void OwnCommit(JsonObject run, string docs, JsonObject plan, string head)
    {
        var baseSha = S(plan, "docs_base_sha"); var owned = Object(plan, "owned_files");
        var parents = Git(run, docs, "rev-list", "--parents", "-n", "1", head).Split(' ');
        if (parents.Length != 2 || parents[1] != baseSha) throw new Blocked("foreign_commit_parent");
        var paths = GitPaths(run, docs, "diff-tree", "--no-commit-id", "--name-only", "-z", "-r", baseSha, head);
        if (!paths.ToHashSet(StringComparer.Ordinal).SetEquals(owned.Select(x => x.Key))) throw new Blocked("foreign_commit_paths");
        foreach (var item in owned)
            if (Blob(run, docs, head, item.Key) != S(item.Value!.AsObject(), "intended_blob")) throw new Blocked("foreign_commit_blob");
    }
    static void SafeOwnedTarget(JsonObject run, string docs, string path, string? baseBlob)
    {
        var full = Full(Path.Combine(docs, Relative(path)));
        if (Directory.Exists(full)) throw new Blocked("owned_target_directory_collision");
        // A clean porcelain result does not imply a vacant new target: ignored
        // and Git-excluded special entries must never be adopted or overwritten.
        if (baseBlob is null && File.Exists(full) && Git(run, docs, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", path).Length == 0)
            throw new Blocked("unowned_delivery_target_collision");
    }
    static JsonObject? VerifiedRestoration(JsonObject run, JsonObject plan, bool required)
    {
        var p = Protection(run);
        if (plan["protection_identity"] is null)
        {
            if (p is not null) throw new Blocked("unbound_worktree_protection");
            return null;
        }
        if (p is null || S(plan, "protection_identity") != ProtectionIdentity(p)) throw new Blocked("worktree_protection_changed");
        if (S(p, "phase") != "restored")
        {
            if (required) throw new Blocked("preexisting_work_restoration_pending");
            return null;
        }
        if (S(p, "restored_head") != Git(run, S(p, "docs"), "rev-parse", "HEAD") || Hash(WorktreeSnapshot(run, S(p, "docs"))) != Hash(Object(p, "expected_restored")))
            throw new Blocked("restored_worktree_changed");
        return new JsonObject { ["identity"] = ProtectionIdentity(p), ["restored_head"] = p["restored_head"]!.DeepClone(), ["snapshot_sha256"] = Hash(Object(p, "expected_restored")), ["stash_sha"] = p["stash_sha"]?.DeepClone() };
    }
    public static JsonObject RestoreWorktree(JsonObject request)
    {
        // Cleanup is deliberately independent of changed remote pins, definition,
        // memory and active pointer. Only exact saved ownership permits it.
        var run = Run(request, cleanup: true); using var mutex = Lock(run);
        var p = Protection(run) ?? throw new Blocked("worktree_protection_missing");
        var docs = S(p, "docs"); var head = Git(run, docs, "rev-parse", "HEAD");
        var pointerPath = Path.Combine(Folder(run), "plan.json");
        JsonObject? plan = null;
        if (File.Exists(pointerPath))
        {
            var pointer = Read(pointerPath);
            var linked = new JsonObject { ["plan_receipt"] = pointer["receipt"]!.DeepClone(), ["plan_receipt_sha256"] = pointer["receipt_sha256"]!.DeepClone() };
            plan = Receipt(run, linked, "plan_receipt", "plan", cleanup: true);
            if (S(plan, "protection_identity") != ProtectionIdentity(p)) throw new Blocked("worktree_protection_changed");
            if (Optional(request, "plan_receipt") is string supplied && supplied != S(linked, "plan_receipt")) throw new Blocked("foreign_cleanup_plan");
        }
        if (head != S(p, "base_sha"))
        {
            if (plan is null) throw new Blocked("unowned_cleanup_commit");
            OwnCommit(run, docs, plan, head);
        }
        if (S(p, "phase") == "prepared")
        {
            // A bounded process failure can occur after Git completed the stash.
            // Recover only the saved nonce's exact object, never issue another push.
            p["stash_sha"] ??= FindOwnedStash(run, p);
            if (p["stash_sha"] is not null)
            {
                VerifyOwnedStash(run, p);
                p["phase"] = "protected"; SaveProtection(run, p);
            }
            else if (head == S(p, "base_sha") && Hash(WorktreeSnapshot(run, docs)) == Hash(Object(p, "initial")))
            {
                p["expected_restored"] = p["initial"]!.DeepClone(); p["restored_head"] = head; p["phase"] = "restored";
                SaveProtection(run, p); return ProtectionResult(p);
            }
            else throw new Blocked("uncertain_protection_state_backup_retained");
        }
        if (p["stash_sha"] is not null) VerifyOwnedStash(run, p);
        if (S(p, "phase") == "restored")
        {
            if (S(p, "restored_head") != head || Hash(WorktreeSnapshot(run, docs)) != Hash(Object(p, "expected_restored"))) throw new Blocked("restored_worktree_changed");
            return ProtectionResult(p);
        }
        if (p["expected_restored"] is null)
        {
            var expected = Object(p, "initial").DeepClone().AsObject();
            if (p["stash_sha"] is not null)
            {
                foreach (var item in new[] { ("index_tree", S(p, "stash_sha") + "^2"), ("worktree_tree", S(p, "stash_sha")) })
                {
                    var merge = Process(run, "git", ["merge-tree", "--write-tree", head, item.Item2], docs);
                    if (merge.Exit != 0) throw new Blocked("preexisting_restore_conflict_backup_retained");
                    var tree = merge.Out.Split('\n')[0]; Sha40(tree); expected[item.Item1] = tree;
                }
            }
            else { var tree = Git(run, docs, "rev-parse", head + "^{tree}"); expected["index_tree"] = tree; expected["worktree_tree"] = tree; }
            var rawTracked = new JsonObject();
            foreach (var path in ChangedTrackedPaths(run, docs, S(expected, "index_tree"), S(expected, "worktree_tree")))
            {
                var blob = Blob(run, docs, S(expected, "worktree_tree"), path);
                var entry = GitPaths(run, docs, "ls-tree", "-z", S(expected, "worktree_tree"), "--", path);
                rawTracked[path] = blob is null ? null : new JsonObject { ["sha256"] = Sha(GitBytes(run, docs, blob)), ["mode"] = entry[0].Split(' ')[0],
                    ["permissions"] = Object(Object(p, "initial"), "tracked_raw")[path] is JsonObject original ? N(original, "permissions", 0) : entry[0].StartsWith("100755 ", StringComparison.Ordinal) ? 493 : 420 };
            }
            expected["tracked_raw"] = rawTracked;
            foreach (var path in Object(expected, "untracked"))
                if (Blob(run, docs, head, path.Key) is not null) throw new Blocked("preexisting_untracked_delivery_collision_backup_retained");
            p["expected_restored"] = expected; p["restored_head"] = head;
        }
        else if (S(p, "restored_head") != head) throw new Blocked("cleanup_head_changed");
        if (S(p, "phase") == "restore_started" && AdoptRestoredBytes(run, p))
        {
            p["phase"] = "restored"; SaveProtection(run, p); return ProtectionResult(p);
        }
        if (Git(run, docs, "status", "--porcelain=v1", "-z", "--untracked-files=all").Length != 0) throw new Blocked("cleanup_requires_owned_clean_delivery_state_backup_retained");
        p["phase"] = "restore_started"; SaveProtection(run, p);
        if (p["stash_sha"] is not null && Process(run, "git", ["stash", "apply", "--index", S(p, "stash_sha")], docs).Exit != 0)
            throw new Blocked("preexisting_restore_failed_backup_retained");
        if (!AdoptRestoredBytes(run, p)) throw new Blocked("restored_worktree_snapshot_mismatch_backup_retained");
        p["phase"] = "restored"; SaveProtection(run, p);
        return ProtectionResult(p);
    }
    public static JsonObject Plan(JsonObject request)
    {
        var run = Run(request);
        var proof = Proof(request, run);
        using var mutex = Lock(run);
        var pointerPath = Path.Combine(Folder(run), "plan.json");
        if (File.Exists(pointerPath))
        {
            var existingPointer = Read(pointerPath);
            var saved = Receipt(run, new JsonObject { ["plan_receipt"] = existingPointer["receipt"]!.DeepClone(), ["plan_receipt_sha256"] = existingPointer["receipt_sha256"]!.DeepClone() }, "plan_receipt", "plan");
            if (S(saved, "request_sha256") != Hash(request) || S(saved, "complete_proof_sha256") != Hash(proof))
                throw new Blocked("existing_delivery_plan_inputs_changed");
            var state = Reconcile(run, saved);
            if (S(state, "status") == "refresh_required") return state;
            return PlanResult("plan_reused", existingPointer, saved);
        }
        var source = Receipt(run, request, "source_receipt", "sources");
        if (Hash(proof) != S(source, "complete_proof_sha256"))
            throw new Blocked("source_complete_proof_changed");
        var repos = Object(source, "repositories");
        var fresh = Fetch(run, repos);
        var docs = S(repos, "docs");
        var workspace = request["workspace_receipt"] is not null ? Receipt(run, request, "workspace_receipt", "workspace") : null;
        if (workspace is not null) CurrentPointer(run, request, "workspace", "workspace_receipt");
        var deliveryDocs = workspace is null ? docs : Workspace(run, workspace, source, true);
        ExactSources(run, source, fresh, workspace is null);
        if (workspace is not null && Hash(Object(source, "documentation_pin")) != Hash(Object(fresh, "documentation_pin")))
            return DocsRefresh(run, source, fresh, deliveryDocs);
        var baseSha = S(Object(source, "documentation_pin"), "sha");
        if (Git(run, deliveryDocs, "symbolic-ref", "--short", "HEAD") != "main" || Git(run, deliveryDocs, "rev-parse", "HEAD") != baseSha)
            throw new Blocked("clean_pinned_main_required");
        var docCommits = DocsCandidates(run, source);
        CompleteHistory(run, source, docCommits);
        CompleteGitHistory(run, source);
        var expected = new HashSet<string>(Strings(proof, "eligible_ids").Select(x => "session|" + x), StringComparer.Ordinal);
        foreach (var c in Array(source, "git_candidates"))
            expected.Add(Candidate(c!.AsObject()));
        foreach (var c in docCommits)
            expected.Add("git|" + docs + "|" + c!.GetValue<string>());
        var candidates = Array(request, "candidates");
        var seen = new HashSet<string>(StringComparer.Ordinal);
        var topics = new JsonObject();
        foreach (var node in candidates)
        {
            var c = node!.AsObject();
            var id = Candidate(c);
            if (!expected.Contains(id) || !seen.Add(id))
                throw new Blocked("foreign_or_duplicate_candidate");
            var disposition = S(c, "disposition");
            if (disposition is not ("irrelevant" or "unproven" or "already_covered" or "update_needed"))
                throw new Blocked("invalid_disposition");
            if (Optional(c, "reason") is not { Length: > 0 })
                throw new Blocked("candidate_reason_required");
            if (disposition == "irrelevant" || (S(c, "kind") == "session" && disposition == "unproven"))
                continue;
            if (S(c, "kind") == "git" && disposition == "unproven")
                throw new Blocked("authoritative_git_candidate_requires_comparison");
            var topicPath = Full(S(c, "topic_receipt"));
            if (!Inside(topicPath, Path.Combine(S(run, "run_directory"), "topics")))
                throw new Blocked("foreign_topic_receipt");
            var topic = Read(topicPath);
            if (Hash(topic) != S(c, "topic_receipt_sha256") || Hash(Object(topic, "context")) != S(topic, "context_sha256"))
                throw new Blocked("corrupt_topic_receipt");
            var context = Object(topic, "context");
            if (S(context, "complete_receipt_sha256") != Hash(proof) || Hash(Object(context, "source_pins")) != Hash(Object(source, "source_pins")) || S(context, "capture_binding_sha256") != S(run, "binding_sha256"))
                throw new Blocked("topic_context_changed");
            if (context["documentation_pin"] is JsonObject topicDocs && Hash(topicDocs) != Hash(Object(source, "documentation_pin")))
                throw new Blocked("topic_documentation_pin_changed");
            if (S(c, "kind") == "session" && !Strings(context, "session_ids").Contains(S(c, "id"), StringComparer.Ordinal) || S(c, "kind") == "git" && !Array(context, "git_candidates").Any(x => S(x!.AsObject(), "repository") == S(c, "repository") && S(x.AsObject(), "sha") == S(c, "sha")))
                throw new Blocked("topic_candidate_mismatch");
            if ((disposition is "already_covered" or "irrelevant" && S(topic, "decision") != "unchanged") || (disposition == "update_needed" && S(topic, "decision") != "update_needed"))
                throw new Blocked("topic_decision_mismatch");
            foreach (var wiki in Object(context, "wiki_sha256"))
            {
                var relative = WikiRelative(docs, deliveryDocs, wiki.Key);
                var blob = Blob(run, docs, baseSha, relative);
                var current = blob is null ? "missing" : Sha(GitBytes(run, docs, blob));
                if (current != wiki.Value!.GetValue<string>())
                    throw new Blocked("topic_wiki_must_match_pinned_blob");
            }
            topics[topicPath] = new JsonObject { ["sha256"] = Hash(topic), ["receipt"] = topic.DeepClone() };
        }
        if (!seen.SetEquals(expected))
            throw new Blocked("candidate_dispositions_incomplete");
        var edits = Array(request, "edits");
        if (edits.Count > 0 && Git(run, deliveryDocs, "status", "--porcelain=v1", "-z", "--untracked-files=all").Length > 0)
            throw new Blocked("foreign_dirty_docs_block_edits");
        var protection = Protection(run);
        if (workspace is not null && protection is not null) throw new Blocked("workspace_and_worktree_protection_are_exclusive");
        if (protection is not null && (S(protection, "phase") != "protected" || S(protection, "base_sha") != baseSha || S(protection, "docs") != docs))
            throw new Blocked("confirmed_worktree_protection_required");
        var owned = new JsonObject();
        foreach (var node in edits)
        {
            var edit = node!.AsObject();
            var path = Relative(S(edit, "path"));
            NoLinks(Path.Combine(deliveryDocs, path));
            if (owned.ContainsKey(path))
                throw new Blocked("duplicate_owned_path");
            var blob = Blob(run, docs, baseSha, path);
            SafeOwnedTarget(run, deliveryDocs, path, blob);
            var desired = S(edit, "content");
            var bytes = Encoding.UTF8.GetBytes(desired);
            var contentPath = Path.Combine(Folder(run), "content-" + Guid.NewGuid().ToString("N") + ".md");
            Write(contentPath, bytes);
            var newBlob = Git(run, deliveryDocs, "hash-object", contentPath);
            if (blob == newBlob)
                throw new Blocked("owned_edit_must_change_blob");
            owned[path] = new JsonObject { ["base_blob"] = blob, ["intended_blob"] = newBlob, ["content_sha256"] = Sha(bytes), ["content_file"] = contentPath };
        }
        var updates = candidates.Select(x => x!.AsObject()).Where(c => S(c, "disposition") == "update_needed").ToArray();
        if ((updates.Length > 0) != (owned.Count > 0))
            throw new Blocked("updates_and_owned_edits_must_match");
        foreach (var update in updates)
        {
            var wiki = Object(Object(Read(S(update, "topic_receipt")), "context"), "wiki_sha256");
            if (!wiki.Any(pair => owned.ContainsKey(WikiRelative(docs, deliveryDocs, pair.Key))))
                throw new Blocked("update_topic_requires_owned_edit");
        }
        var evidence = new JsonObject();
        foreach (var file in Directory.EnumerateFiles(S(run, "run_directory"), "*", SearchOption.AllDirectories).Where(p => !Inside(p, Folder(run))))
            evidence[file] = FileSha(file);
        var linkedPaths = updates.SelectMany(update => Object(Object(Read(S(update, "topic_receipt")), "context"), "wiki_sha256").Select(pair => WikiRelative(docs, deliveryDocs, pair.Key))).ToHashSet(StringComparer.Ordinal);
        if (owned.Any(pair => !linkedPaths.Contains(pair.Key)))
            throw new Blocked("owned_edit_requires_update_topic");
        var body = new JsonObject { ["request_sha256"] = Hash(request), ["sources"] = source.DeepClone(), ["source_receipt"] = request["source_receipt"]!.DeepClone(), ["complete_proof_sha256"] = Hash(proof), ["evidence_files"] = evidence, ["range_pins"] = RangePins(run, proof), ["expected_candidates"] = List(expected.Order(StringComparer.Ordinal)), ["candidates"] = candidates.DeepClone(), ["topics"] = topics, ["docs_base_sha"] = baseSha, ["owned_files"] = owned, ["old_bundle"] = Bundle(File.ReadAllText(S(Object(run, "binding"), "memory"))) };
        if (protection is not null) body["protection_identity"] = ProtectionIdentity(protection);
        if (workspace is not null)
        {
            body["workspace"] = workspace.DeepClone();
            body["workspace_receipt"] = request["workspace_receipt"]!.DeepClone();
            body["workspace_receipt_sha256"] = request["workspace_receipt_sha256"]?.DeepClone();
        }
        var output = Save(run, "plan", body);
        var pointer = new JsonObject { ["receipt"] = output["receipt"]!.DeepClone(), ["receipt_sha256"] = output["receipt_sha256"]!.DeepClone() };
        WriteJson(pointerPath, pointer);
        return PlanResult("plan", pointer, body);
    }
    static JsonObject PlanResult(string status, JsonObject pointer, JsonObject plan) => new() { ["schema_version"] = 1, ["status"] = status, ["receipt"] = pointer["receipt"]!.DeepClone(), ["receipt_sha256"] = pointer["receipt_sha256"]!.DeepClone(), ["payload"] = new JsonObject { ["docs_base_sha"] = plan["docs_base_sha"]!.DeepClone(), ["delivery_root"] = plan["workspace"]?["workspace_root"]?.DeepClone() ?? plan["sources"]!["repositories"]!["docs"]!.DeepClone(), ["owned_files"] = plan["owned_files"]!.DeepClone(), ["expected_candidate_count"] = Array(plan, "expected_candidates").Count, ["request_sha256"] = plan["request_sha256"]!.DeepClone() } };
    static JsonObject RangePins(JsonObject run, JsonObject proof)
    {
        var pins = new JsonObject();
        void Add(JsonObject container)
        {
            foreach (var pair in Object(container, "source_pins"))
            {
                if (pins[pair.Key] is JsonNode existing && Hash(existing) != Hash(pair.Value!))
                    throw new Blocked("inconsistent_raw_range_pin");
                pins[pair.Key] = pair.Value!.DeepClone();
            }
        }
        foreach (var page in Object(proof, "pages"))
        {
            var pointer = Read(Path.Combine(S(run, "run_directory"), "pages", page.Key));
            var envelope = Read(Path.Combine(S(pointer, "folder"), "envelope.json"));
            if (Hash(envelope) != S(pointer, "envelope_sha256"))
                throw new Blocked("page_envelope_changed");
            Add(envelope);
        }
        foreach (var clone in Object(proof, "manual_clone_resolutions"))
        {
            var clones = Path.Combine(S(run, "run_directory"), "clones");
            var pointerPath = Path.Combine(clones, Sha(Encoding.UTF8.GetBytes(clone.Key)) + ".json");
            if (FileSha(pointerPath) != clone.Value!.GetValue<string>())
                throw new Blocked("clone_resolution_pointer_changed");
            var pointer = Read(pointerPath);
            var receiptPath = Full(S(pointer, "receipt"));
            if (!Inside(receiptPath, clones))
                throw new Blocked("foreign_clone_resolution_range_receipt");
            var receipt = Read(receiptPath);
            if (Hash(receipt) != S(pointer, "receipt_sha256") || S(receipt, "session_id") != clone.Key)
                throw new Blocked("clone_resolution_range_receipt_changed");
            Add(receipt);
        }
        if (!pins.Select(p => p.Key).ToHashSet(StringComparer.Ordinal).SetEquals(Strings(proof, "eligible_ids")))
            throw new Blocked("raw_range_coverage_incomplete");
        return pins;
    }
    static string RangeHash(JsonObject pin)
    {
        var path = Full(S(pin, "path"));
        var start = N(pin, "review_line_start", 0);
        var end = N(pin, "review_line_end", -1);
        if (start < 1 || end < start - 1)
            throw new Blocked("invalid_frozen_raw_range");
        using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
        using var digest = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        var buffer = new byte[8192];
        var line = 1;
        var completed = 0;
        var hasBytes = false;
        while (line <= end)
        {
            var read = stream.Read(buffer);
            if (read == 0)
            {
                if (hasBytes)
                    completed = line;
                break;
            }
            var included = -1;
            var consumed = 0;
            for (; consumed < read && line <= end; consumed++)
            {
                if (line >= start && included < 0)
                    included = consumed;
                hasBytes = true;
                if (buffer[consumed] == '\n')
                {
                    completed = line++;
                    hasBytes = false;
                }
            }
            if (included >= 0)
                digest.AppendData(buffer.AsSpan(included, consumed - included));
        }
        if (completed < end)
            throw new Blocked("truncated_frozen_raw_range");
        return Convert.ToHexStringLower(digest.GetHashAndReset());
    }
    static void Evidence(JsonObject plan, bool currentRanges = true)
    {
        foreach (var file in Object(plan, "evidence_files"))
        if (FileSha(file.Key) != file.Value!.GetValue<string>())
            throw new Blocked("completion_evidence_changed");
        if (currentRanges)
        foreach (var range in Object(plan, "range_pins"))
        if (RangeHash(range.Value!.AsObject()) != S(range.Value.AsObject(), "range_sha256"))
            throw new Blocked("completion_rollout_source_changed");
        foreach (var file in Object(plan, "owned_files"))
        {
            var owned = file.Value!.AsObject();
            if (FileSha(S(owned, "content_file")) != S(owned, "content_sha256"))
                throw new Blocked("intended_content_changed");
        }
        foreach (var topic in Object(plan, "topics"))
        if (Hash(Read(topic.Key)) != S(topic.Value!.AsObject(), "sha256"))
            throw new Blocked("topic_receipt_changed");
    }
    static JsonObject Reconcile(JsonObject run, JsonObject plan)
    {
        Evidence(plan);
        var source = Object(plan, "sources");
        var repos = Object(source, "repositories");
        var fresh = Fetch(run, repos);
        ExactSources(run, source, fresh, false);
        var docs = S(repos, "docs");
        if (plan["workspace"] is JsonObject workspace)
        {
            var saved = Receipt(run, plan, "workspace_receipt", "workspace");
            if (Hash(saved) != Hash(workspace)) throw new Blocked("plan_workspace_changed");
            docs = Workspace(run, saved, source, false);
            Git(run, docs, "fetch", "--no-tags", "--no-write-fetch-head", "origin", "+refs/heads/main:refs/remotes/origin/main");
            Object(fresh, "documentation_pin")["sha"] = Git(run, docs, "rev-parse", "refs/remotes/origin/main^{commit}");
        }
        if (Git(run, docs, "symbolic-ref", "--short", "HEAD") != "main")
            throw new Blocked("docs_branch_must_be_main");
        var baseSha = S(plan, "docs_base_sha");
        var head = Git(run, docs, "rev-parse", "HEAD");
        var remote = S(Object(fresh, "documentation_pin"), "sha");
        var owned = Object(plan, "owned_files");
        var dirty = Git(run, docs, "status", "--porcelain=v1", "-z", "--untracked-files=all");
        var isolated = plan["workspace"] is not null;
        JsonObject Refresh(string ownState)
        {
            if (!isolated || !Ancestor(run, docs, baseSha, remote))
                throw new Blocked("foreign_remote_docs_commit");
            return new JsonObject { ["status"] = "refresh_required", ["reason"] = "docs_main_advanced", ["owned_state"] = ownState,
                ["docs_base_sha"] = baseSha, ["remote_main_sha"] = remote, ["workspace_root"] = docs, ["checkpoint_changed"] = false };
        }
        if (head == baseSha)
            foreach (var item in owned) SafeOwnedTarget(run, docs, item.Key, Optional(item.Value!.AsObject(), "base_blob"));
        var restored = VerifiedRestoration(run, plan, false);
        if (owned.Count == 0)
        {
            if (head != baseSha)
                throw new Blocked("unowned_docs_commit");
            if (isolated && dirty.Length != 0) throw new Blocked("foreign_dirty_docs");
            if (remote != baseSha)
            {
                if (!isolated) throw new Blocked("unowned_docs_commit");
                return Refresh("planned");
            }
            if (plan["protection_identity"] is not null && dirty.Length != 0 && restored is null)
                throw new Blocked("foreign_dirty_docs");
            var noChange = new JsonObject { ["status"] = "delivered", ["docs_reviewed_sha"] = baseSha };
            if (restored is not null) noChange["restoration"] = restored;
            return noChange;
        }
        if (head == baseSha)
        {
            if (!isolated && remote != baseSha)
                throw new Blocked("foreign_remote_docs_commit");
            if (dirty.Length == 0)
                return remote == baseSha ? new JsonObject { ["status"] = "planned", ["docs_reviewed_sha"] = baseSha } : Refresh("planned");
            var records = dirty.Split('\0', StringSplitOptions.RemoveEmptyEntries);
            if (records.Any(line => line.Length < 4 || line[..2].Contains('R') || line[..2].Contains('C')))
                throw new Blocked("foreign_rename_or_copy");
            var changed = records.Select(line => line[3..]).ToArray();
            if (changed.Any(p => !owned.ContainsKey(p)))
                throw new Blocked("foreign_dirty_docs");
            foreach (var path in changed)
            {
                var full = Path.Combine(docs, path);
                if (!File.Exists(full) || FileSha(full) != S(owned[path]!.AsObject(), "content_sha256"))
                    throw new Blocked("owned_edit_not_intended_content");
            }
            return remote == baseSha ? new JsonObject { ["status"] = "own_edits", ["docs_reviewed_sha"] = baseSha } : Refresh("own_edits");
        }
        if (dirty.Length != 0 && restored is null)
            throw new Blocked("dirty_docs_after_commit");
        OwnCommit(run, docs, plan, head);
        var delivered = remote == head || (isolated && Ancestor(run, docs, head, remote));
        if (remote != baseSha && !delivered)
            return Refresh("own_commit");
        var result = new JsonObject { ["status"] = delivered ? "delivered" : "own_commit", ["commit"] = head, ["docs_reviewed_sha"] = head };
        if (restored is not null) result["restoration"] = restored;
        return result;
    }
    public static JsonObject Status(JsonObject request)
    {
        var run = Run(request);
        using var mutex = Lock(run);
        var plan = Receipt(run, request, "plan_receipt", "plan");
        CurrentPointer(run, request, "plan", "plan_receipt");
        var result = Reconcile(run, plan);
        result["schema_version"] = 1;
        result["checkpoint_changed"] = false;
        return result;
    }
    public static JsonObject RetirePlan(JsonObject request)
    {
        if (request["plan_receipt"] is null) return RetirePrePlan(request);
        var run = Run(request);
        using var mutex = Lock(run);
        var plan = Receipt(run, request, "plan_receipt", "plan");
        if (File.Exists(Path.Combine(Folder(run), "finalization.json"))) throw new Blocked("finalization_started_cannot_retire_plan");
        if (plan["workspace"] is null) throw new Blocked("isolated_plan_required_for_refresh");
        var journalPath = Path.Combine(Folder(run), "retirement-" + Hash(plan) + ".json");
        JsonObject journal;
        if (File.Exists(journalPath))
        {
            var saved = Read(journalPath);
            journal = Object(saved, "payload");
            if (Hash(journal) != S(saved, "payload_sha256") || S(journal, "plan_sha256") != Hash(plan) ||
                S(journal, "run_sha256") != Hash(run) || S(journal, "delivery_helper_sha256") != FileSha(HelperPath()))
                throw new Blocked("corrupt_plan_retirement");
            if (S(journal, "phase") == "retired") return RetirementResult(journal);
        }
        else
        {
            var current = Reconcile(run, plan);
            if (S(current, "status") == "delivered") return current;
            if (S(current, "status") != "refresh_required") throw new Blocked("docs_refresh_not_required");
            var pointers = new JsonObject();
            foreach (var name in new[] { "plan.json", "workspace.json", "workspace-preparation.json" })
            {
                var path = Path.Combine(Folder(run), name);
                var pointer = Read(path);
                if (name == "plan.json" && (S(pointer, "receipt") != S(request, "plan_receipt") || S(pointer, "receipt_sha256") != Hash(Read(S(request, "plan_receipt")))))
                    throw new Blocked("foreign_plan_pointer");
                if (name == "workspace.json" && S(pointer, "receipt") != S(plan, "workspace_receipt"))
                    throw new Blocked("foreign_workspace_pointer");
                pointers[path] = new JsonObject { ["sha256"] = FileSha(path), ["archived_path"] = Path.Combine(Folder(run), "retired-" + Guid.NewGuid().ToString("N") + "-" + name) };
            }
            journal = new JsonObject { ["run_sha256"] = Hash(run), ["plan_sha256"] = Hash(plan), ["delivery_helper_sha256"] = FileSha(HelperPath()),
                ["phase"] = "prepared", ["refresh"] = current, ["pointers"] = pointers };
            WriteJson(journalPath, new JsonObject { ["payload"] = journal.DeepClone(), ["payload_sha256"] = Hash(journal) });
        }
        return FinishRetirement(run, journalPath, journal);
    }
    static JsonObject RetirePrePlan(JsonObject request)
    {
        var run = Run(request);
        using var mutex = Lock(run);
        var source = Receipt(run, request, "source_receipt", "sources");
        var journalPath = Path.Combine(Folder(run), "retirement-preplan-" + Hash(source) + ".json");
        JsonObject journal;
        if (File.Exists(journalPath))
        {
            var saved = Read(journalPath);
            journal = Object(saved, "payload");
            if (Hash(journal) != S(saved, "payload_sha256") || S(journal, "source_sha256") != Hash(source) ||
                S(journal, "run_sha256") != Hash(run) || S(journal, "delivery_helper_sha256") != FileSha(HelperPath())) throw new Blocked("corrupt_preplan_retirement");
            if (S(journal, "phase") == "retired") return RetirementResult(journal);
        }
        else
        {
            if (File.Exists(Path.Combine(Folder(run), "plan.json"))) throw new Blocked("exact_plan_receipt_required_for_retirement");
            if (Protection(run) is not null) throw new Blocked("isolated_workspace_required_for_refresh");
            var fresh = Fetch(run, Object(source, "repositories"));
            ExactSources(run, source, fresh, false);
            var refresh = DocsRefresh(run, source, fresh);
            var workspacePointer = Path.Combine(Folder(run), "workspace.json");
            var preparationPath = Path.Combine(Folder(run), "workspace-preparation.json");
            var pointers = new JsonObject();
            if (File.Exists(workspacePointer))
            {
                var pointer = Read(workspacePointer);
                if (request["workspace_receipt"] is not null && S(request, "workspace_receipt") != S(pointer, "receipt")) throw new Blocked("foreign_workspace_pointer");
                var body = Receipt(run, new JsonObject { ["workspace_receipt"] = pointer["receipt"]!.DeepClone(), ["workspace_receipt_sha256"] = pointer["receipt_sha256"]!.DeepClone() }, "workspace_receipt", "workspace");
                if (request["workspace_receipt"] is not null && Hash(Receipt(run, request, "workspace_receipt", "workspace")) != Hash(body)) throw new Blocked("foreign_workspace_pointer");
                refresh["workspace_root"] = Workspace(run, body, source, true);
            }
            if (File.Exists(preparationPath))
            {
                var saved = Read(preparationPath);
                var body = Object(saved, "payload");
                if (Hash(body) != S(saved, "payload_sha256") || S(body, "run_sha256") != Hash(run) || S(body, "source_payload_sha256") != Hash(source) ||
                    S(body, "delivery_helper_sha256") != FileSha(HelperPath()) || S(body, "canonical_docs_root") != S(Object(source, "repositories"), "docs")) throw new Blocked("workspace_preparation_identity_changed");
                var root = Full(S(body, "workspace_root"));
                if (!Inside(root, Path.Combine(Folder(run), "workspaces")) || Origin(run, S(body, "canonical_docs_root")) != S(body, "origin")) throw new Blocked("foreign_workspace_preparation");
                if (Directory.Exists(Path.Combine(root, ".git")))
                {
                    NoLinks(Path.Combine(root, ".git"));
                    var head = Git(run, root, "rev-parse", "HEAD");
                    if (Git(run, root, "rev-parse", "--show-toplevel") != root || Git(run, root, "rev-parse", "--absolute-git-dir") != Path.Combine(root, ".git") ||
                        Git(run, root, "symbolic-ref", "--short", "HEAD") != "main" || Origin(run, root) != S(body, "origin") ||
                        Git(run, root, "status", "--porcelain=v1", "-z", "--untracked-files=all").Length != 0 ||
                        !Ancestor(run, root, S(body, "docs_base_sha"), head)) throw new Blocked("clean_owned_preparation_required");
                    // The canonical fetch owns the current main object; fetch it
                    // into this independent clone before proving its exact range.
                    Git(run, root, "fetch", "--no-tags", "--no-write-fetch-head", "origin", "+refs/heads/main:refs/remotes/origin/main");
                    if (!Ancestor(run, root, head, Git(run, root, "rev-parse", "refs/remotes/origin/main^{commit}"))) throw new Blocked("foreign_preparation_commit");
                }
                refresh["workspace_root"] = root;
            }
            foreach (var path in new[] { workspacePointer, preparationPath }.Where(File.Exists))
                pointers[path] = new JsonObject { ["sha256"] = FileSha(path), ["archived_path"] = Path.Combine(Folder(run), "retired-" + Guid.NewGuid().ToString("N") + "-" + Path.GetFileName(path)) };
            journal = new JsonObject { ["run_sha256"] = Hash(run), ["source_sha256"] = Hash(source), ["delivery_helper_sha256"] = FileSha(HelperPath()),
                ["phase"] = "prepared", ["refresh"] = refresh, ["pointers"] = pointers };
            WriteJson(journalPath, new JsonObject { ["payload"] = journal.DeepClone(), ["payload_sha256"] = Hash(journal) });
        }
        return FinishRetirement(run, journalPath, journal);
    }
    static JsonObject FinishRetirement(JsonObject run, string journalPath, JsonObject journal)
    {
        foreach (var item in Object(journal, "pointers"))
        {
            var path = Full(item.Key);
            var archived = Full(S(item.Value!.AsObject(), "archived_path"));
            var expected = S(item.Value.AsObject(), "sha256");
            if (!Inside(path, Folder(run)) || !Inside(archived, Folder(run))) throw new Blocked("foreign_retirement_pointer");
            if (File.Exists(path))
            {
                if (FileSha(path) != expected || File.Exists(archived)) throw new Blocked("retirement_pointer_changed");
                File.Move(path, archived);
            }
            else if (!File.Exists(archived) || FileSha(archived) != expected) throw new Blocked("retirement_pointer_missing");
        }
        journal["phase"] = "retired";
        WriteJson(journalPath, new JsonObject { ["payload"] = journal.DeepClone(), ["payload_sha256"] = Hash(journal) }, true);
        return RetirementResult(journal);
    }
    static JsonObject RetirementResult(JsonObject journal) => new() { ["schema_version"] = 1, ["status"] = "refresh_required", ["reason"] = "docs_main_advanced",
        ["checkpoint_changed"] = false, ["plan_retired"] = journal["plan_sha256"] is not null, ["workspace_retired"] = true, ["preserved_workspace"] = Object(journal, "refresh")["workspace_root"]?.DeepClone(),
        ["archived_pointers"] = Object(journal, "pointers").DeepClone() };
    static string Patch(string memory, JsonObject intended)
    {
        var match = Regex.Match(memory, @"^## ", RegexOptions.Multiline);
        var header = match.Success ? memory[..match.Index] : memory;
        var tail = match.Success ? memory[match.Index..] : "";
        var newline = memory.Contains("\r\n", StringComparison.Ordinal) ? "\r\n" : "\n";
        foreach (var key in Keys)
        {
            var value = S(intended, key);
            var regex = new Regex("^" + Regex.Escape(key) + @":[^\r\n]*(?<ending>\r?\n|$)", RegexOptions.Multiline);
            if (regex.IsMatch(header))
                header = regex.Replace(header, m => key + ": " + value + m.Groups["ending"].Value, 1);
            else
                header += (header.EndsWith('\n') || header.Length == 0 ? "" : newline) + key + ": " + value + newline;
        }
        return header + tail;
    }
    public static JsonObject Finalize(JsonObject request)
    {
        var directory = Full(S(request, "run_directory"));
        var intentPath = Path.Combine(directory, "delivery", "finalization.json");
        var terminalPath = Path.Combine(directory, "delivery", "completed.json");
        var recovering = File.Exists(intentPath);
        var run = Run(request, recovering && File.Exists(terminalPath), recovering);
        var memory = S(Object(run, "binding"), "memory");
        JsonObject? priorIntent = null;
        var needsCurrentProof = true;
        if (recovering)
        {
            var envelope = Read(intentPath);
            priorIntent = Object(envelope, "payload");
            if (Hash(priorIntent) != S(envelope, "payload_sha256") || S(priorIntent, "run_sha256") != Hash(run) || S(priorIntent, "delivery_helper") != HelperPath() || S(priorIntent, "delivery_helper_sha256") != FileSha(HelperPath()))
                throw new Blocked("corrupt_finalization_intent_or_delivery_helper_changed");
            var bundle = Bundle(File.ReadAllText(memory));
            needsCurrentProof = Hash(bundle) == Hash(Object(priorIntent, "old_bundle"));
            if (!needsCurrentProof && Hash(bundle) != Hash(Object(priorIntent, "new_bundle")))
                throw new Blocked("checkpoint_compare_and_swap_failed");
        }
        var currentProof = needsCurrentProof ? Proof(request, run) : null;
        using var mutex = Lock(run);
        var plan = Receipt(run, request, "plan_receipt", "plan");
        CurrentPointer(run, request, "plan", "plan_receipt");
        if (currentProof is not null && Hash(currentProof) != S(plan, "complete_proof_sha256"))
            throw new Blocked("completion_proof_changed");
        var currentText = File.ReadAllText(memory);
        var currentBundle = Bundle(currentText);
        JsonObject intent;
        JsonObject reconciliation;
        if (recovering)
        {
            intent = priorIntent!;
            if (S(intent, "plan_sha256") != Hash(plan) || S(intent, "complete_proof_sha256") != S(plan, "complete_proof_sha256"))
                throw new Blocked("corrupt_finalization_intent");
            var old = Object(intent, "old_bundle");
            var next = Object(intent, "new_bundle");
            if (Hash(currentBundle) == Hash(old))
            {
                if (currentProof is null)
                    throw new Blocked("old_bundle_requires_current_proof");
                reconciliation = Reconcile(run, plan);
                VerifiedRestoration(run, plan, true);
                if (S(reconciliation, "status") != "delivered" || Hash(reconciliation) != Hash(Object(intent, "delivery")))
                    throw new Blocked("delivery_gate_changed");
            }
            else if (Hash(currentBundle) == Hash(next))
            {
                Evidence(plan, false);
                reconciliation = Object(intent, "delivery").DeepClone().AsObject();
                if (S(reconciliation, "status") != "delivered")
                    throw new Blocked("invalid_protected_delivery_gate");
            }
            else
                throw new Blocked("checkpoint_compare_and_swap_failed");
        }
        else
        {
            if (Hash(currentBundle) != Hash(Object(plan, "old_bundle")))
                throw new Blocked("checkpoint_compare_and_swap_failed");
            var manifest = Read(Path.Combine(directory, "manifest.json"));
            var window = Object(manifest, "window");
            var carry = Array(window, "carry_forward_to_persist");
            var approved = Object(run, "binding")["approved_missing_carry_ids"]?.AsArray().Select(x => x!.GetValue<string>()).ToHashSet(StringComparer.Ordinal) ?? [];
            var ignoreMissing = Object(run, "binding")["missing_session_policy"]?.GetValue<string>() == "ignore";
            var missing = Array(manifest, "sessions").Where(x => S(x!.AsObject(), "status") == "missing").Select(x => S(x!.AsObject(), "id")).ToHashSet(StringComparer.Ordinal);
            var persisted = new JsonArray(carry.Where(x => !((ignoreMissing || approved.Contains(S(x!.AsObject(), "id"))) && missing.Contains(S(x!.AsObject(), "id")))).Select(x => x!.DeepClone()).ToArray());
            var source = Object(plan, "sources");
            reconciliation = Reconcile(run, plan);
            if (S(reconciliation, "status") != "delivered")
                throw new Blocked("required_delivery_incomplete");
            VerifiedRestoration(run, plan, true);
            var next = new JsonObject { ["Processed window end"] = S(window, "cursor_to_persist"), ["Last review"] = DateTimeOffset.UtcNow.ToString("O"), ["Carry-forward sessions"] = Canon(persisted).ToJsonString(), ["Authoritative source tips"] = Canon(Object(source, "source_pins")).ToJsonString(), ["Docs reviewed tip"] = new JsonObject { ["repository"] = S(Object(source, "repositories"), "docs"), ["ref"] = "refs/remotes/origin/main", ["sha"] = S(reconciliation, "docs_reviewed_sha") }.ToJsonString() };
            if (request["new_checkpoint"] is JsonObject supplied)
            {
                foreach (var key in Keys.Where(k => k != "Last review"))
                if (supplied[key] is null || supplied[key]!.GetValue<string>() != S(next, key))
                    throw new Blocked("new_checkpoint_must_be_derived");
                if (supplied.Count != 5)
                    throw new Blocked("exact_completion_bundle_required");
                if (!DateTimeOffset.TryParse(S(supplied, "Last review"), out var stamp) || Math.Abs((DateTimeOffset.UtcNow - stamp).TotalMinutes) > 5)
                    throw new Blocked("last_review_must_be_current");
                next["Last review"] = S(supplied, "Last review");
            }
            intent = new JsonObject { ["schema_version"] = 1, ["plan_sha256"] = Hash(plan), ["old_bundle"] = currentBundle.DeepClone(), ["new_bundle"] = next, ["run_sha256"] = Hash(run), ["delivery_helper"] = HelperPath(), ["delivery_helper_sha256"] = FileSha(HelperPath()), ["complete_proof_sha256"] = Hash(currentProof!), ["checked_source_pins"] = Object(source, "source_pins").DeepClone(), ["delivery"] = reconciliation.DeepClone() };
            WriteJson(intentPath, new JsonObject { ["payload"] = intent, ["payload_sha256"] = Hash(intent) });
        }
        // The exact old/new intent is the only recovery exception. Generic Load stays strict.
        if (Hash(currentBundle) == Hash(Object(intent, "old_bundle")))
            Write(memory, Encoding.UTF8.GetBytes(Patch(currentText, Object(intent, "new_bundle"))), true);
        if (Hash(Bundle(File.ReadAllText(memory))) != Hash(Object(intent, "new_bundle")))
            throw new Blocked("checkpoint_replacement_not_confirmed");
        var terminal = new JsonObject { ["schema_version"] = 1, ["status"] = "complete", ["run_directory"] = directory, ["intent_sha256"] = Hash(intent), ["new_bundle_sha256"] = Hash(Object(intent, "new_bundle")), ["delivery"] = reconciliation };
        if (File.Exists(terminalPath))
        {
            if (Hash(Read(terminalPath)) != Hash(terminal))
                throw new Blocked("terminal_receipt_changed");
        }
        else
            WriteJson(terminalPath, terminal);
        var active = Path.Combine(S(run, "store"), "active.json");
        if (File.Exists(active))
        {
            if (S(Read(active), "run_directory") != directory)
                throw new Blocked("foreign_active_run");
            File.Delete(active);
        }
        var result = Result("complete");
        result["receipt"] = terminalPath;
        result["checkpoint_changed"] = true;
        result["active_retired"] = true;
        result["new_checkpoint"] = Object(intent, "new_bundle").DeepClone();
        return result;
    }
}

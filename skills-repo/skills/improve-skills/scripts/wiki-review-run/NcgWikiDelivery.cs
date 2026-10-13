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
        throw new Blocked("usage: <verify-sources|git-history|docs-history|plan-delivery|delivery-status|finalize> --request <private-json>");
    var request = Delivery.Read(Path.GetFullPath(args[2]));
    var result = args[0] switch
    {
        "verify-sources" => Delivery.VerifySources(request),
        "docs-history" => Delivery.DocsHistory(request),
        "git-history" => Delivery.GitHistory(request),
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
    static JsonObject Run(JsonObject request, bool retired = false, bool completionRecovery = false)
    {
        var directory = Full(S(request, "run_directory"));
        var run = Read(Path.Combine(directory, "run.json"));
        if (S(run, "run_directory") != directory || !Inside(directory, Full(S(run, "store"))) || S(run, "state") != "captured" || run["invalidated"] is not null)
            throw new Blocked("invalid_run");
        var b = Object(run, "binding");
        var identity = b.DeepClone().AsObject();
        identity.Remove("memory_sha256");
        if (Hash(identity) != S(run, "binding_sha256"))
            throw new Blocked("corrupt_run_binding");
        foreach (var key in new[] { "definition", "resolver", "helper" })
        if (FileSha(S(b, key)) != S(b, key + "_sha256"))
            throw new Blocked("current_" + key + "_changed");
        if (!completionRecovery)
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
        if (!retired)
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
    static JsonObject Receipt(JsonObject run, JsonObject request, string key, string kind)
    {
        var path = Full(S(request, key));
        if (!Inside(path, Folder(run)))
            throw new Blocked("foreign_receipt");
        var envelope = Read(path);
        var body = Object(envelope, "payload");
        if (Hash(body) != S(envelope, "payload_sha256") || S(body, "kind") != kind || S(body, "run_directory") != S(run, "run_directory") || S(body, "run_sha256") != Hash(run) || S(body, "delivery_helper") != HelperPath() || S(body, "delivery_helper_sha256") != FileSha(HelperPath()))
            throw new Blocked("corrupt_receipt_or_delivery_helper_changed");
        if (Optional(request, key + "_sha256") is string expected && expected != Hash(envelope))
            throw new Blocked("receipt_identity_changed");
        return body;
    }
    static string HelperPath([System.Runtime.CompilerServices.CallerFilePath] string path = "") => Path.GetFullPath(path);
    [DllImport("libc", EntryPoint = "kill", SetLastError = true)] static extern int SignalGroup(int pid, int signal);
    static (int Exit, string Out) Process(JsonObject run, string exe, IEnumerable<string> arguments, string? cwd = null) => ProcessBounded(run, exe, arguments.ToArray(), cwd).GetAwaiter().GetResult();
    static async Task<(int Exit, string Out)> ProcessBounded(JsonObject run, string exe, string[] arguments, string? cwd)
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
        return (exit, Encoding.UTF8.GetString(stdout));
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
        var result = Save(run, "sources", new JsonObject { ["repositories"] = repos, ["source_pins"] = pins.DeepClone(), ["documentation_pin"] = docsPin.DeepClone(), ["code_ranges"] = ranges, ["git_candidates"] = candidates, ["old_bundle"] = old, ["docs_prior"] = priorDocs, ["complete_proof_sha256"] = Hash(proof) });
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
        var result = Process(run, "git", ["cat-file", "blob", blob], repo);
        if (result.Exit != 0)
            throw new Blocked("git_blob_unreadable");
        return Encoding.UTF8.GetBytes(result.Out);
    }
    static void ExactSources(JsonObject run, JsonObject source, JsonObject fresh, bool docsEqual)
    {
        if (Hash(Object(fresh, "source_pins")) != Hash(Object(source, "source_pins")))
            throw new Blocked("authoritative_code_pins_changed");
        if (docsEqual && Hash(Object(fresh, "documentation_pin")) != Hash(Object(source, "documentation_pin")))
            throw new Blocked("docs_pin_changed");
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
            Reconcile(run, saved);
            return PlanResult("plan_reused", existingPointer, saved);
        }
        var source = Receipt(run, request, "source_receipt", "sources");
        if (Hash(proof) != S(source, "complete_proof_sha256"))
            throw new Blocked("source_complete_proof_changed");
        var repos = Object(source, "repositories");
        var fresh = Fetch(run, repos);
        ExactSources(run, source, fresh, true);
        var docs = S(repos, "docs");
        var baseSha = S(Object(source, "documentation_pin"), "sha");
        if (Git(run, docs, "symbolic-ref", "--short", "HEAD") != "main" || Git(run, docs, "rev-parse", "HEAD") != baseSha)
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
                var full = Full(wiki.Key);
                if (!Inside(full, docs))
                    throw new Blocked("wiki_outside_docs");
                var relative = Relative(Path.GetRelativePath(docs, full));
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
        if (edits.Count > 0 && Git(run, docs, "status", "--porcelain=v1", "-z", "--untracked-files=all").Length > 0)
            throw new Blocked("foreign_dirty_docs_block_edits");
        var owned = new JsonObject();
        foreach (var node in edits)
        {
            var edit = node!.AsObject();
            var path = Relative(S(edit, "path"));
            NoLinks(Path.Combine(docs, path));
            if (owned.ContainsKey(path))
                throw new Blocked("duplicate_owned_path");
            var desired = S(edit, "content");
            var bytes = Encoding.UTF8.GetBytes(desired);
            var contentPath = Path.Combine(Folder(run), "content-" + Guid.NewGuid().ToString("N") + ".md");
            Write(contentPath, bytes);
            var blob = Blob(run, docs, baseSha, path);
            var newBlob = Git(run, docs, "hash-object", contentPath);
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
            if (!wiki.Any(pair => owned.ContainsKey(Path.GetRelativePath(docs, pair.Key))))
                throw new Blocked("update_topic_requires_owned_edit");
        }
        var evidence = new JsonObject();
        foreach (var file in Directory.EnumerateFiles(S(run, "run_directory"), "*", SearchOption.AllDirectories).Where(p => !Inside(p, Folder(run))))
            evidence[file] = FileSha(file);
        var linkedPaths = updates.SelectMany(update => Object(Object(Read(S(update, "topic_receipt")), "context"), "wiki_sha256").Select(pair => Path.GetRelativePath(docs, pair.Key))).ToHashSet(StringComparer.Ordinal);
        if (owned.Any(pair => !linkedPaths.Contains(pair.Key)))
            throw new Blocked("owned_edit_requires_update_topic");
        var body = new JsonObject { ["request_sha256"] = Hash(request), ["sources"] = source.DeepClone(), ["source_receipt"] = request["source_receipt"]!.DeepClone(), ["complete_proof_sha256"] = Hash(proof), ["evidence_files"] = evidence, ["range_pins"] = RangePins(run, proof), ["expected_candidates"] = List(expected.Order(StringComparer.Ordinal)), ["candidates"] = candidates.DeepClone(), ["topics"] = topics, ["docs_base_sha"] = baseSha, ["owned_files"] = owned, ["old_bundle"] = Bundle(File.ReadAllText(S(Object(run, "binding"), "memory"))) };
        var output = Save(run, "plan", body);
        var pointer = new JsonObject { ["receipt"] = output["receipt"]!.DeepClone(), ["receipt_sha256"] = output["receipt_sha256"]!.DeepClone() };
        WriteJson(pointerPath, pointer);
        return PlanResult("plan", pointer, body);
    }
    static JsonObject PlanResult(string status, JsonObject pointer, JsonObject plan) => new() { ["schema_version"] = 1, ["status"] = status, ["receipt"] = pointer["receipt"]!.DeepClone(), ["receipt_sha256"] = pointer["receipt_sha256"]!.DeepClone(), ["payload"] = new JsonObject { ["docs_base_sha"] = plan["docs_base_sha"]!.DeepClone(), ["owned_files"] = plan["owned_files"]!.DeepClone(), ["expected_candidate_count"] = Array(plan, "expected_candidates").Count, ["request_sha256"] = plan["request_sha256"]!.DeepClone() } };
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
        if (Git(run, docs, "symbolic-ref", "--short", "HEAD") != "main")
            throw new Blocked("docs_branch_must_be_main");
        var baseSha = S(plan, "docs_base_sha");
        var head = Git(run, docs, "rev-parse", "HEAD");
        var remote = S(Object(fresh, "documentation_pin"), "sha");
        var owned = Object(plan, "owned_files");
        var dirty = Git(run, docs, "status", "--porcelain=v1", "-z", "--untracked-files=all");
        if (owned.Count == 0)
        {
            if (head != baseSha || remote != baseSha)
                throw new Blocked("unowned_docs_commit");
            return new JsonObject { ["status"] = "delivered", ["docs_reviewed_sha"] = baseSha };
        }
        if (head == baseSha)
        {
            if (remote != baseSha)
                throw new Blocked("foreign_remote_docs_commit");
            if (dirty.Length == 0)
                return new JsonObject { ["status"] = "planned", ["docs_reviewed_sha"] = baseSha };
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
            return new JsonObject { ["status"] = "own_edits", ["docs_reviewed_sha"] = baseSha };
        }
        if (dirty.Length != 0)
            throw new Blocked("dirty_docs_after_commit");
        var parents = Git(run, docs, "rev-list", "--parents", "-n", "1", head).Split(' ');
        if (parents.Length != 2 || parents[1] != baseSha)
            throw new Blocked("foreign_commit_parent");
        var paths = Git(run, docs, "diff-tree", "--no-commit-id", "--name-only", "-z", "-r", baseSha, head).Split('\0', StringSplitOptions.RemoveEmptyEntries);
        if (!paths.ToHashSet(StringComparer.Ordinal).SetEquals(owned.Select(x => x.Key)))
            throw new Blocked("foreign_commit_paths");
        foreach (var item in owned)
        if (Blob(run, docs, head, item.Key) != S(item.Value!.AsObject(), "intended_blob"))
            throw new Blocked("foreign_commit_blob");
        if (remote != baseSha && remote != head)
            throw new Blocked("foreign_remote_docs_commit");
        return new JsonObject { ["status"] = remote == head ? "delivered" : "own_commit", ["commit"] = head, ["docs_reviewed_sha"] = head };
    }
    public static JsonObject Status(JsonObject request)
    {
        var run = Run(request);
        using var mutex = Lock(run);
        var plan = Receipt(run, request, "plan_receipt", "plan");
        var result = Reconcile(run, plan);
        result["schema_version"] = 1;
        result["checkpoint_changed"] = false;
        return result;
    }
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
            var missing = Array(manifest, "sessions").Where(x => S(x!.AsObject(), "status") == "missing").Select(x => S(x!.AsObject(), "id")).ToHashSet(StringComparer.Ordinal);
            var persisted = new JsonArray(carry.Where(x => !(approved.Contains(S(x!.AsObject(), "id")) && missing.Contains(S(x.AsObject(), "id")))).Select(x => x!.DeepClone()).ToArray());
            var source = Object(plan, "sources");
            reconciliation = Reconcile(run, plan);
            if (S(reconciliation, "status") != "delivered")
                throw new Blocked("required_delivery_incomplete");
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

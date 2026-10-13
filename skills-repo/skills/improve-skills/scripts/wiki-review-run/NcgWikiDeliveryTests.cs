using System.Diagnostics;
using System.Text;
using System.Text.Json.Nodes;

if (OperatingSystem.IsWindows()) return 2;
var root = Path.Combine(OperatingSystem.IsMacOS() ? "/private/tmp" : Path.GetTempPath(), "ncg-wiki-delivery-tests-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(root);
var helper = Path.GetFullPath("skills-repo/skills/improve-skills/scripts/wiki-review-run/NcgWikiDelivery.cs");
var review = Path.Combine(Path.GetDirectoryName(helper)!, "ReviewRun.cs");
var scripts = Path.GetDirectoryName(Path.GetDirectoryName(helper))!;
try
{
    const int outputCap = 4096;
    var bounded = Fixture("within-output-cap", false, true, maxOutputBytes: outputCap);
    var withinCapContent = new string('p', outputCap - 256) + "\n";
    File.WriteAllText(Path.Combine(bounded.Docs, "a.md"), withinCapContent);
    Git(bounded.Docs, "add", "a.md");
    Git(bounded.Docs, "commit", "-m", "Legitimate pinned blob below configured output cap");
    Git(bounded.Docs, "push", "origin", "main");
    var boundedSource = Sources(bounded);
    History(bounded, boundedSource, 0, 100);
    var boundedCommit = Git(bounded.Docs, "rev-parse", "HEAD");
    var boundedTopic = Topic(bounded, boundedSource, boundedCommit, "unchanged");
    var boundedPlan = Plan(bounded, new JsonArray(Candidate(bounded, boundedCommit, boundedTopic, "already_covered")), [], boundedSource);
    var blobOutput = Directory.EnumerateFiles(Path.Combine(bounded.Run, "delivery"), "process-*.json")
        .Select(path => (Path: path, Body: JsonNode.Parse(File.ReadAllBytes(path))!.AsObject()))
        .Single(item => item.Body["arguments"]!.AsArray().FirstOrDefault()?.GetValue<string>() == "cat-file");
    Check(File.ReadAllBytes(Path.ChangeExtension(blobOutput.Path, ".stdout")).SequenceEqual(Encoding.UTF8.GetBytes(withinCapContent)), "successful in-limit Git blob retains every byte up to the actual configured cap");
    Check(Call(helper, "delivery-status", Completion(bounded, boundedPlan)).Body["status"]!.GetValue<string>() == "delivered", "legitimate pinned Markdown between cap-minus512 and cap permits normal delivery validation");

    var excessive = Fixture("over-output-cap", false, true, maxOutputBytes: outputCap);
    File.WriteAllText(Path.Combine(excessive.Docs, "a.md"), new string('q', outputCap) + "\n");
    Git(excessive.Docs, "add", "a.md");
    Git(excessive.Docs, "commit", "-m", "Quick producer exceeding configured output cap");
    Git(excessive.Docs, "push", "origin", "main");
    var excessiveSource = Sources(excessive);
    History(excessive, excessiveSource, 0, 100);
    var excessiveCommit = Git(excessive.Docs, "rev-parse", "HEAD");
    var excessiveTopic = Topic(excessive, excessiveSource, excessiveCommit, "unchanged");
    var beforeExcessivePlan = File.ReadAllBytes(excessive.Memory);
    var excessivePlan = Call(helper, "plan-delivery", PlanRequest(excessive, new JsonArray(Candidate(excessive, excessiveCommit, excessiveTopic, "already_covered")), [], excessiveSource));
    Check(excessivePlan.Exit == 2 && excessivePlan.Body["reason"]!.GetValue<string>() == "process_output_limit" && File.ReadAllBytes(excessive.Memory).SequenceEqual(beforeExcessivePlan) && !File.Exists(Path.Combine(excessive.Run, "delivery", "plan.json")), "quickly exiting over-cap Git output blocks plan and preserves checkpoint");
    var limitDiagnostic = Directory.EnumerateFiles(Path.Combine(excessive.Run, "delivery"), "process-*.json")
        .Select(path => (Path: path, Body: JsonNode.Parse(File.ReadAllBytes(path))!.AsObject()))
        .Single(item => item.Body["failure"]?.GetValue<string>() == "process_output_limit");
    Check(limitDiagnostic.Body["max_output_bytes"]!.GetValue<int>() == outputCap && File.ReadAllBytes(Path.ChangeExtension(limitDiagnostic.Path, ".stdout")).Length <= outputCap && File.GetUnixFileMode(limitDiagnostic.Path) == (UnixFileMode.UserRead | UnixFileMode.UserWrite), "over-cap failure retains protected bounded diagnostics without reserving payload capacity");
    Console.WriteLine("PASS exact-git-output-cap-full-bytes-and-overflow-blocker");
    if (Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_OUTPUT_CAP") == "1")
    {
        Console.WriteLine("Fixture: " + root);
        return 0;
    }
    var manual = Fixture("manual-clone", true, true, manualClone: true);
    var resolutionRequest = manual.ReviewRequest.DeepClone().AsObject();
    resolutionRequest["run_directory"] = manual.Run;
    resolutionRequest["session_id"] = "discovery-session";
    resolutionRequest["kind"] = "reviewed_suffix";
    resolutionRequest["suffix_start"] = 3;
    resolutionRequest["reason"] = "Actual boundary and structural projections show imported metadata on line2 and the new substantive user suffix on line3.";
    var resolved = Call(review, "resolve-clone", resolutionRequest);
    Check(resolved.Exit == 0, "public manual suffix resolution: " + resolved.Body.ToJsonString());
    var manualProofRequest = manual.ReviewRequest.DeepClone().AsObject();
    manualProofRequest["run_directory"] = manual.Run;
    var manualProof = Call(review, "verify-pages", manualProofRequest);
    Check(manualProof.Exit == 0 && manualProof.Body["resolved_manual_clones"]!.GetValue<int>() == 1, "manual clone has a real successful completeness proof");
    var manualSource = Sources(manual);
    History(manual, manualSource, 0, 100);
    var manualCandidates = new JsonArray(new JsonObject { ["kind"] = "session", ["id"] = "discovery-session", ["disposition"] = "irrelevant", ["reason"] = "Reviewed new user suffix asks only for discovery; imported metadata supplies no durable original-source fact." });
    var cloneReceiptPath = resolved.Body["receipt"]!.GetValue<string>();
    var originalCloneReceipt = File.ReadAllBytes(cloneReceiptPath);
    var corruptCloneReceipt = JsonNode.Parse(originalCloneReceipt)!.AsObject();
    corruptCloneReceipt["reason"] = "Changed pointed receipt without a matching protected pointer hash";
    File.WriteAllText(cloneReceiptPath, corruptCloneReceipt.ToJsonString());
    var beforeCorruptPlan = File.ReadAllBytes(manual.Memory);
    var rejectedClone = Call(helper, "plan-delivery", PlanRequest(manual, manualCandidates, [], manualSource));
    Check(rejectedClone.Exit == 2 && File.ReadAllBytes(manual.Memory).SequenceEqual(beforeCorruptPlan) && !File.Exists(Path.Combine(manual.Run, "delivery", "plan.json")), "corrupt pointed manual-clone receipt is rejected before actionable plan or checkpoint");
    File.WriteAllBytes(cloneReceiptPath, originalCloneReceipt);
    var manualPlan = Plan(manual, manualCandidates, [], manualSource);
    var manualComplete = Call(helper, "finalize", Completion(manual, manualPlan));
    Check(manualComplete.Exit == 0 && manualComplete.Body["active_retired"]!.GetValue<bool>(), "resolved manual clone composes through plan and complete finalization: " + manualComplete.Body.ToJsonString());
    Console.WriteLine("PASS resolved-manual-clone-pointer-plan-and-finalization");
    if (Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_MANUAL_CLONE") == "1")
    {
        Console.WriteLine("Fixture: " + root);
        return 0;
    }
    var promotion = Fixture("promotion", false, true, true);
    Git(promotion.Backend, "update-ref", "refs/heads/production", Git(promotion.Backend, "rev-parse", "develop"));
    Git(promotion.Backend, "push", "origin", "production");
    var promotionSource = Sources(promotion);
    Check(promotionSource.Body["payload"]!["git_candidate_count"]!.GetValue<int>() == 0, "production promotion excludes commits already reviewed on develop");
    Console.WriteLine("PASS reviewed-other-branch-promotion-is-not-reselected");
    var discovery = Fixture("discovery", true, true);
    var discoveryCandidates = new JsonArray(new JsonObject { ["kind"] = "session", ["id"] = "discovery-session", ["disposition"] = "unproven", ["reason"] = "Narrative only; no original source claim or durable wiki fact." });
    var discoveryPlan = Plan(discovery, discoveryCandidates, []);
    var completed = Call(helper, "finalize", Completion(discovery, discoveryPlan));
    Check(completed.Exit == 0, "unproven session discovery may complete without creating a documentation claim: " + completed.Body.ToJsonString());
    Console.WriteLine("PASS unproven-session-negative-gate-completes");

    var own = Fixture("owned", false, true);
    var newCommit = OldDatedDocsChange(own);
    var source = Sources(own);
    var history = History(own, source, 0, 1);
    Check(history.Body["payload"]!["commits"]!.AsArray().Single()!.GetValue<string>() == newCommit, "SHA range includes newly reachable commit whose date is years older");
    const string ownPath = "Page ü space.md";
    var topic = Topic(own, source, newCommit, "update_needed", ownPath);
    var candidates = new JsonArray(Candidate(own, newCommit, topic, "update_needed"));
    var desired = "Reviewed new operational fact\n";
    var ownEdits = new JsonArray(new JsonObject { ["path"] = ownPath, ["content"] = desired });
    var plan = Plan(own, candidates, ownEdits, source);
    var copiedHelper = Path.Combine(own.Folder, "CopiedDelivery.cs");
    File.Copy(helper, copiedHelper);
    Check(Call(copiedHelper, "delivery-status", Completion(own, plan)).Exit == 2, "a same-byte helper at a different source identity cannot reuse the delivery receipt");
    File.AppendAllText(copiedHelper, "\n// Changed fixture helper bytes\n");
    Check(Call(copiedHelper, "delivery-status", Completion(own, plan)).Exit == 2, "changed delivery helper bytes never silently reuse workflow decisions");
    var repeatedPlan = Call(helper, "plan-delivery", PlanRequest(own, candidates, ownEdits, source));
    Check(repeatedPlan.Exit == 0 && repeatedPlan.Body["status"]!.GetValue<string>() == "plan_reused" && repeatedPlan.Body["receipt"]!.GetValue<string>() == plan.Body["receipt"]!.GetValue<string>(), "identical plan request reuses exact actionable intent before edits");
    Check(Call(helper, "delivery-status", Completion(own, plan)).Body["status"]!.GetValue<string>() == "planned", "plan retains desired content before edits");
    File.WriteAllText(Path.Combine(own.Docs, ownPath), desired);
    Check(Call(helper, "delivery-status", Completion(own, plan)).Body["status"]!.GetValue<string>() == "own_edits", "intended own files are recoverable");
    Check(Call(helper, "plan-delivery", PlanRequest(own, candidates, ownEdits, source)).Body["status"]!.GetValue<string>() == "plan_reused", "plan adoption bridges its exact own post-edit wiki bytes");
    Check(Call(helper, "plan-delivery", PlanRequest(own, candidates, new JsonArray(new JsonObject { ["path"] = ownPath, ["content"] = "different\n" }), source)).Exit == 2, "changed requested intended content does not overwrite protected plan");
    File.WriteAllText(Path.Combine(own.Docs, "foreign.md"), "foreign\n");
    Check(Call(helper, "delivery-status", Completion(own, plan)).Exit == 2, "foreign dirty file blocks recovery without cleanup");
    File.Delete(Path.Combine(own.Docs, "foreign.md"));
    Git(own.Docs, "add", ownPath);
    Git(own.Docs, "commit", "-m", "Owned documentation delivery");
    Check(GitExit(own.Docs, "push", Path.Combine(root, "does-not-exist"), "main") != 0, "isolated fixture push fails");
    Check(Call(helper, "delivery-status", Completion(own, plan)).Body["status"]!.GetValue<string>() == "own_commit", "exact own commit remains recoverable after failed push");
    Check(Call(helper, "finalize", Completion(own, plan)).Exit == 2, "undelivered own commit never advances memory");
    Git(own.Docs, "push", "origin", "main");
    Check(Call(helper, "delivery-status", Completion(own, plan)).Body["status"]!.GetValue<string>() == "delivered", "fresh exact origin main proves own delivery");
    var active = File.ReadAllBytes(Path.Combine(own.Store, "active.json"));
    var memoryBefore = File.ReadAllText(own.Memory);
    var final = Call(helper, "finalize", Completion(own, plan));
    Check(final.Exit == 0, "owned delivery finalizes: " + final.Body.ToJsonString());
    var deliveredMemory = File.ReadAllBytes(own.Memory);
    Check(File.ReadAllText(own.Memory).Contains("## Earlier\nHistorical paragraph stays byte-identical\n"), "history is preserved while whole official bundle advances");
    var terminal = final.Body["receipt"]!.GetValue<string>();
    var intentFile = Path.Combine(own.Run, "delivery", "finalization.json");
    var intent = File.ReadAllBytes(intentFile);
    // Interruption after preparing intent, but before replacing old memory.
    File.Delete(terminal);
    File.WriteAllBytes(Path.Combine(own.Store, "active.json"), active);
    File.WriteAllText(own.Memory, memoryBefore);
    var oldRecovery = Call(helper, "finalize", Completion(own, plan));
    Check(oldRecovery.Exit == 0 && File.ReadAllBytes(own.Memory).SequenceEqual(deliveredMemory), "old-bundle intent recovery revalidates current proof and delivery then commits exact intended bundle");
    File.Delete(terminal);
    File.WriteAllBytes(Path.Combine(own.Store, "active.json"), active);
    // A newer source after the checkpoint patch cannot strand historical retirement.
    Git(own.Backend, "commit", "--allow-empty", "-m", "Later source after completed bundle");
    Git(own.Backend, "push", "origin", "develop");
    var recovered = Call(helper, "finalize", Completion(own, plan));
    Check(recovered.Exit == 0 && File.ReadAllBytes(own.Memory).SequenceEqual(deliveredMemory), "restart with intended new bundle completes terminal receipt without advancing twice");
    Check(Call(helper, "finalize", Completion(own, plan)).Exit == 0, "terminal finalization repeats idempotently after active retirement");
    File.AppendAllText(own.Memory, "\nFailure note preserved\n");
    Check(Call(helper, "finalize", Completion(own, plan)).Exit == 0, "noncheckpoint failure prose survives terminal reconciliation");
    File.WriteAllText(own.Memory, File.ReadAllText(own.Memory).Replace("Carry-forward sessions: []", "Carry-forward sessions: [{\"id\":\"foreign\"}]"));
    Check(Call(helper, "finalize", Completion(own, plan)).Exit == 2, "foreign completion bundle blocks narrow recovery");
    Console.WriteLine("PASS old-dated-docs-owned-space-path-plan-reuse-failed-push-finalization-restart");

    var first = Fixture("first-docs-baseline", false, false);
    var firstSource = Sources(first);
    var p0 = History(first, firstSource, 0, 1);
    Check(p0.Body["payload"]!["baseline_missing"]!.GetValue<bool>(), "missing Docs baseline is explicit");
    Check(Call(helper, "plan-delivery", PlanRequest(first, new JsonArray(), new JsonArray(), firstSource)).Exit == 2, "unclassified pinned history cannot become a reviewed Docs tip");
    var initial = Git(first.Docs, "rev-parse", "HEAD");
    var original = File.ReadAllBytes(Path.Combine(first.Docs, "a.md"));
    File.WriteAllText(Path.Combine(first.Docs, "a.md"), "Foreign dirty fact\n");
    var dirtyTopic = Topic(first, firstSource, initial, "unchanged");
    Check(Call(helper, "plan-delivery", PlanRequest(first, new JsonArray(Candidate(first, initial, dirtyTopic, "already_covered")), [], firstSource)).Exit == 2, "local dirty page bytes never certify already-covered against pinned main");
    File.WriteAllBytes(Path.Combine(first.Docs, "a.md"), original);
    var firstTopic = Topic(first, firstSource, initial, "unchanged");
    var completePlan = Plan(first, new JsonArray(Candidate(first, initial, firstTopic, "already_covered")), [], firstSource);
    Check(Call(helper, "finalize", Completion(first, completePlan)).Exit == 0, "fully compared first pinned history permits baseline establishment");
    Console.WriteLine("PASS missing-docs-baseline-and-candidate-completeness");

    var changed = Fixture("changed-source", false, true);
    var changedSource = Sources(changed);
    History(changed, changedSource, 0, 1);
    var changedPlan = Plan(changed, [], [], changedSource);
    File.WriteAllText(Path.Combine(changed.Backend, "new.txt"), "new\n");
    Git(changed.Backend, "add", "new.txt");
    Git(changed.Backend, "commit", "-m", "New source after comparison");
    Git(changed.Backend, "push", "origin", "develop");
    var unchanged = File.ReadAllBytes(changed.Memory);
    Check(Call(helper, "finalize", Completion(changed, changedPlan)).Exit == 2 && File.ReadAllBytes(changed.Memory).SequenceEqual(unchanged), "changed authoritative code pin blocks finalization before checkpoint write");
    Console.WriteLine("PASS changed-source-pins-block-checkpoint");

    var symlink = Fixture("symlink", false, true);
    var outside = Path.Combine(symlink.Folder, "outside.md");
    File.WriteAllText(outside, "Outside bytes must stay unchanged\n");
    File.CreateSymbolicLink(Path.Combine(symlink.Docs, "link.md"), outside);
    Git(symlink.Docs, "add", "link.md");
    Git(symlink.Docs, "commit", "-m", "Tracked symlink fixture");
    Git(symlink.Docs, "push", "origin", "main");
    var symlinkSource = Sources(symlink);
    History(symlink, symlinkSource, 0, 100);
    var symlinkCommit = Git(symlink.Docs, "rev-parse", "HEAD");
    var symlinkTopic = Topic(symlink, symlinkSource, symlinkCommit, "update_needed");
    var symlinkRequest = PlanRequest(symlink, new JsonArray(Candidate(symlink, symlinkCommit, symlinkTopic, "update_needed")), new JsonArray(new JsonObject { ["path"] = "link.md", ["content"] = "Unsafe target\n" }), symlinkSource);
    var rejected = Call(helper, "plan-delivery", symlinkRequest);
    Check(rejected.Exit == 2 && rejected.Body["reason"]!.GetValue<string>() == "symlink_not_allowed" && File.ReadAllText(outside) == "Outside bytes must stay unchanged\n", "actionable symlink intent is rejected before outside bytes can change");
    Console.WriteLine("PASS symlink-owned-target-is-blocked-before-intent");

    var timed = Fixture("owned-process-timeout", false, true, false, 2);
    var launcher = Path.Combine(timed.Folder, "fake-bin");
    Directory.CreateDirectory(launcher);
    var pidFile = Path.Combine(timed.Folder, "child.pid");
    var gitWrapper = Path.Combine(launcher, "git");
    File.WriteAllText(gitWrapper, "#!/usr/bin/env python3\nimport os,sys,subprocess\nif len(sys.argv)>1 and sys.argv[1]=='fetch':\n p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])\n open(" + JsonValue.Create(pidFile)!.ToJsonString() + ",'w').write(str(p.pid))\n sys.exit(0)\nos.execv('/usr/bin/git',['git',*sys.argv[1:]])\n");
    File.SetUnixFileMode(gitWrapper, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute);
    var beforeTimeout = File.ReadAllBytes(timed.Memory);
    var clock = Stopwatch.StartNew();
    var timeout = Call(helper, "verify-sources", Common(timed), launcher + ":" + Environment.GetEnvironmentVariable("PATH"));
    Check(timeout.Exit == 2 && timeout.Body["reason"]!.GetValue<string>() == "process_timeout" && clock.Elapsed.TotalSeconds < 15, "exited fetch parent with open child pipes has a bounded failure");
    var child = int.Parse(File.ReadAllText(pidFile));
    var probe = new ProcessStartInfo("/bin/kill") { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true };
    probe.ArgumentList.Add("-0");
    probe.ArgumentList.Add(child.ToString());
    using (var p = Process.Start(probe)!)
    {
        p.WaitForExit();
        Check(p.ExitCode != 0, "owned process-group termination stops fetch descendants after parent exit");
    }
    Check(File.ReadAllBytes(timed.Memory).SequenceEqual(beforeTimeout), "timeout leaves checkpoint untouched");
    Check(Call(helper, "verify-sources", Common(timed)).Exit == 0, "timeout released shared store lock for an explicit normal retry");
    Console.WriteLine("PASS bounded-git-descendant-timeout-diagnostics-and-lock-release");
    Console.WriteLine("PASS NcgWikiDelivery CLI fixtures (local bare remotes only)");
    Console.WriteLine("Fixture: " + root);
    return 0;
}
catch (Exception ex) { Console.Error.WriteLine("FAIL " + ex.Message + "\nFixture: " + root); return 1; }
finally { if (Environment.GetEnvironmentVariable("NCG_WIKI_KEEP_FIXTURE") != "1") Directory.Delete(root, true); }

FixtureState Fixture(string name, bool session, bool docsBaseline, bool reviewedDevelopAhead = false, int timeoutSeconds = 120, bool manualClone = false, int maxOutputBytes = 16777216)
{
    var folder = Path.Combine(root, name);
    Directory.CreateDirectory(folder);
    var backend = Repository(folder, "backend", "develop");
    var sts = Repository(folder, "sts", "develop");
    var docs = Repository(folder, "docs", "main");
    foreach (var repo in new[] { backend, sts })
    {
        Git(repo, "branch", "production");
        Git(repo, "push", "origin", "production");
    }
    if (reviewedDevelopAhead)
    {
        Git(backend, "commit", "--allow-empty", "-m", "Already reviewed development commit");
        Git(backend, "push", "origin", "develop");
    }
    var home = Path.Combine(folder, "home");
    Directory.CreateDirectory(home);
    var automation = Path.Combine(folder, "automation");
    Directory.CreateDirectory(automation);
    var memory = Path.Combine(automation, "memory.md");
    var definition = Path.Combine(automation, "automation.toml");
    File.WriteAllText(definition, "id = \"keep-ncg-wiki-current\"\n");
    var pins = new JsonObject();
    foreach (var repo in new[] { backend, sts })
    foreach (var branch in new[] { "develop", "production" })
        pins[repo + "|refs/remotes/origin/" + branch] = Git(repo, "rev-parse", branch);
    var docsTip = new JsonObject { ["repository"] = docs, ["ref"] = "refs/remotes/origin/main", ["sha"] = Git(docs, "rev-parse", "HEAD") };
    File.WriteAllText(memory, "Processed window end: 2026-10-12T06:00:00Z\nLast review: 2026-10-12T06:01:00Z\nCarry-forward sessions: []\nAuthoritative source tips: " + pins.ToJsonString() + "\n" + (docsBaseline ? "Docs reviewed tip: " + docsTip.ToJsonString() + "\n" : "") + "\n## Earlier\nHistorical paragraph stays byte-identical\n");
    var index = Path.Combine(home, "session_index.jsonl");
    File.WriteAllText(index, new JsonObject { ["id"] = "before-window", ["updated_at"] = "2001-01-01T00:00:00Z" }.ToJsonString() + "\n");
    if (session)
    {
        var day = Path.Combine(home, "sessions", "2026", "10", "12");
        Directory.CreateDirectory(day);
        File.WriteAllText(index, new JsonObject { ["id"] = "discovery-session", ["updated_at"] = "2026-10-12T07:00:00Z" }.ToJsonString() + "\n");
        var records = new[] { new JsonObject { ["timestamp"] = "2026-10-12T07:00:00Z", ["type"] = "session_meta", ["payload"] = new JsonObject { ["id"] = "discovery-session", ["cwd"] = docs } }, new JsonObject { ["timestamp"] = "2026-10-12T07:00:00Z", ["type"] = "response_item", ["payload"] = new JsonObject { ["type"] = "message", ["role"] = "user", ["content"] = new JsonArray(new JsonObject { ["type"] = "input_text", ["text"] = "Unproven narrative discovery" }) } } };
        var selectedRecords = records.ToList();
        if (manualClone)
            selectedRecords.Insert(1, new JsonObject { ["timestamp"] = "2026-10-12T07:00:00Z", ["type"] = "session_meta", ["payload"] = new JsonObject { ["id"] = "imported-session", ["cwd"] = docs } });
        File.WriteAllText(Path.Combine(day, "rollout-discovery-session.jsonl"), string.Join("\n", selectedRecords.Select(x => x.ToJsonString())) + "\n");
    }
    var store = Path.Combine(folder, "store");
    var capture = Call(review, "capture", new JsonObject { ["store"] = store, ["automation_id"] = "keep-ncg-wiki-current", ["codex_home"] = home, ["memory"] = memory, ["definition"] = definition, ["resolver"] = Path.Combine(scripts, "resolve_codex_sessions.py"), ["python"] = "python3", ["exclude_session_id"] = "maintenance", ["max_sessions"] = 100, ["timeout_seconds"] = timeoutSeconds, ["max_output_bytes"] = maxOutputBytes });
    Check(capture.Exit == 0, "fixture capture: " + capture.Body.ToJsonString());
    var run = capture.Body["run_directory"]!.GetValue<string>();
    var reviewRequest = new JsonObject { ["extractor"] = Path.Combine(scripts, "extract_codex_session_evidence.py"), ["python"] = "python3", ["scope"] = new JsonObject { ["cwd_roots"] = new JsonArray(backend, sts, docs), ["worktree_tails"] = new JsonArray() } };
    var page = reviewRequest.DeepClone().AsObject();
    page["run_directory"] = run;
    page["offset"] = 0;
    page["limit"] = 100;
    Check(Call(review, "page", page).Exit == 0, "fixture zero-or-one summary page");
    var prove = reviewRequest.DeepClone().AsObject();
    prove["run_directory"] = run;
    if (!manualClone)
        Check(Call(review, "verify-pages", prove).Exit == 0, "fixture proof complete");
    return new(folder, backend, sts, docs, memory, store, run, reviewRequest);
}
string Repository(string folder, string name, string branch) { var remote = Path.Combine(folder, name + ".git"); Git(folder, "init", "--bare", remote); var repo = Path.Combine(folder, name); Git(folder, "init", "-b", branch, repo); Git(repo, "config", "user.name", "Fixture"); Git(repo, "config", "user.email", "fixture@example.invalid"); File.WriteAllText(Path.Combine(repo, "a.md"), "Original fact\n"); Git(repo, "add", "a.md"); Git(repo, "commit", "-m", "Initial fixture"); Git(repo, "remote", "add", "origin", remote); Git(repo, "push", "-u", "origin", branch); return repo; }
string OldDatedDocsChange(FixtureState f) { File.WriteAllText(Path.Combine(f.Docs, "a.md"), "New source fact\n"); Git(f.Docs, "add", "a.md"); var start = new ProcessStartInfo("git") { WorkingDirectory = f.Docs, UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true }; foreach (var arg in new[] { "commit", "-m", "Old dated newly reachable fact" }) start.ArgumentList.Add(arg); start.Environment["GIT_AUTHOR_DATE"] = "2001-01-01T00:00:00Z"; start.Environment["GIT_COMMITTER_DATE"] = "2001-01-01T00:00:00Z"; using var p = Process.Start(start)!; var output = p.StandardOutput.ReadToEnd(); var errors = p.StandardError.ReadToEnd(); p.WaitForExit(); Check(p.ExitCode == 0, "old dated fixture commit"); Git(f.Docs, "push", "origin", "main"); return Git(f.Docs, "rev-parse", "HEAD"); }
JsonObject Common(FixtureState f) => new() { ["run_directory"] = f.Run, ["review_helper"] = review, ["review_request"] = f.ReviewRequest.DeepClone(), ["repositories"] = new JsonObject { ["backend"] = f.Backend, ["sts"] = f.Sts, ["docs"] = f.Docs } };
(int Exit, JsonObject Body) Sources(FixtureState f) { var result = Call(helper, "verify-sources", Common(f)); Check(result.Exit == 0, "source verification: " + result.Body.ToJsonString()); var request = new JsonObject { ["run_directory"] = f.Run, ["source_receipt"] = result.Body["receipt"]!.DeepClone(), ["source_receipt_sha256"] = result.Body["receipt_sha256"]!.DeepClone(), ["offset"] = 0, ["limit"] = 100 }; Check(Call(helper, "git-history", request).Exit == 0, "bounded code history page"); return result; }
(int Exit, JsonObject Body) History(FixtureState f, (int Exit, JsonObject Body) source, int offset, int limit) { var r = new JsonObject { ["run_directory"] = f.Run, ["source_receipt"] = source.Body["receipt"]!.DeepClone(), ["source_receipt_sha256"] = source.Body["receipt_sha256"]!.DeepClone(), ["offset"] = offset, ["limit"] = limit }; var result = Call(helper, "docs-history", r); Check(result.Exit == 0, "history: " + result.Body.ToJsonString()); return result; }
(int Exit, JsonObject Body) Topic(FixtureState f, (int Exit, JsonObject Body) source, string commit, string decision, string wikiPath = "a.md") { var payload = source.Body["payload"]!; var request = f.ReviewRequest.DeepClone().AsObject(); request["run_directory"] = f.Run; request["topic_id"] = "docs-topic"; request["source_pins"] = payload["source_pins"]!.DeepClone(); request["documentation_pin"] = payload["documentation_pin"]!.DeepClone(); request["session_ids"] = new JsonArray(); request["git_candidates"] = new JsonArray(new JsonObject { ["repository"] = f.Docs, ["sha"] = commit }); request["wiki_files"] = new JsonArray(Path.Combine(f.Docs, wikiPath)); request["decision"] = decision; request["comparison"] = "Compared fixed authoritative Git change with current pinned main page."; var result = Call(review, "record-topic", request); Check(result.Exit == 0, "topic: " + result.Body.ToJsonString()); return result; }
JsonObject Candidate(FixtureState f, string commit, (int Exit, JsonObject Body) topic, string disposition) => new() { ["kind"] = "git", ["repository"] = f.Docs, ["sha"] = commit, ["disposition"] = disposition, ["reason"] = "Compared pinned current Markdown and exact Git original", ["topic_receipt"] = topic.Body["receipt"]!.DeepClone(), ["topic_receipt_sha256"] = topic.Body["receipt_sha256"]!.DeepClone() };
JsonObject PlanRequest(FixtureState f, JsonArray candidates, JsonArray edits, (int Exit, JsonObject Body) source) { var request = Common(f); request["source_receipt"] = source.Body["receipt"]!.DeepClone(); request["source_receipt_sha256"] = source.Body["receipt_sha256"]!.DeepClone(); request["candidates"] = candidates.DeepClone(); request["edits"] = edits.DeepClone(); return request; }
(int Exit, JsonObject Body) Plan(FixtureState f, JsonArray candidates, JsonArray edits, (int Exit, JsonObject Body)? source = null) { var s = source ?? Sources(f); if (source is null) History(f, s, 0, 100); var result = Call(helper, "plan-delivery", PlanRequest(f, candidates, edits, s)); Check(result.Exit == 0, "delivery plan: " + result.Body.ToJsonString()); return result; }
JsonObject Completion(FixtureState f, (int Exit, JsonObject Body) plan) { var r = Common(f); r["plan_receipt"] = plan.Body["receipt"]!.DeepClone(); r["plan_receipt_sha256"] = plan.Body["receipt_sha256"]!.DeepClone(); return r; }
(int Exit, JsonObject Body) Call(string file, string command, JsonObject request, string? pathOverride = null) { var path = Path.Combine(root, "request-" + Guid.NewGuid().ToString("N") + ".json"); File.WriteAllText(path, request.ToJsonString()); File.SetUnixFileMode(path, UnixFileMode.UserRead | UnixFileMode.UserWrite); var start = new ProcessStartInfo("dotnet") { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true }; if (pathOverride is not null) start.Environment["PATH"] = pathOverride; foreach (var arg in new[] { "run", "--file", file, "--", command, "--request", path }) start.ArgumentList.Add(arg); using var p = Process.Start(start)!; var output = p.StandardOutput.ReadToEnd(); var errors = p.StandardError.ReadToEnd(); p.WaitForExit(); File.AppendAllText(Path.Combine(root, "public-cli.log"), command + " exit=" + p.ExitCode + "\n" + output + errors + "\n"); var line = output.Split('\n', StringSplitOptions.RemoveEmptyEntries).LastOrDefault() ?? "{}"; return (p.ExitCode, JsonNode.Parse(line)!.AsObject()); }
string Git(string cwd, params string[] arguments) { var r = GitRun(cwd, arguments); Check(r.Exit == 0, "git " + arguments[0] + ": " + r.Error); return r.Output.Trim(); }
int GitExit(string cwd, params string[] arguments) => GitRun(cwd, arguments).Exit;
(int Exit, string Output, string Error) GitRun(string cwd, string[] arguments) { var start = new ProcessStartInfo("git") { WorkingDirectory = cwd, UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true }; foreach (var arg in arguments) start.ArgumentList.Add(arg); using var p = Process.Start(start)!; var output = p.StandardOutput.ReadToEnd(); var error = p.StandardError.ReadToEnd(); p.WaitForExit(); return (p.ExitCode, output, error); }
void Check(bool condition, string why) { if (!condition) throw new Exception(why); }
record FixtureState(string Folder, string Backend, string Sts, string Docs, string Memory, string Store, string Run, JsonObject ReviewRequest);

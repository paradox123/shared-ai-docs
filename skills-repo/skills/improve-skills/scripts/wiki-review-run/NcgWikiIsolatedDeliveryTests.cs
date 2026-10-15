using System.Diagnostics;
using System.Text;
using System.Text.Json.Nodes;

if (OperatingSystem.IsWindows()) return 2;
var root = Path.Combine(OperatingSystem.IsMacOS() ? "/private/tmp" : Path.GetTempPath(), "ncg-wiki-delivery-tests-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(root);
Console.WriteLine("Fixture: " + root);
var helper = Path.GetFullPath("skills-repo/skills/improve-skills/scripts/wiki-review-run/NcgWikiDelivery.cs");
var review = Path.Combine(Path.GetDirectoryName(helper)!, "ReviewRun.cs");
var scripts = Path.GetDirectoryName(Path.GetDirectoryName(helper))!;
try
{
    if (Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_PREPLAN_RACE") == "1")
    {
        var early = Fixture("pre-plan-docs-main-refresh", false, true);
        var earlyChange = OldDatedDocsChange(early);
        var earlySource = Sources(early);
        History(early, earlySource, 0, 100);
        var earlyRequest = Common(early);
        earlyRequest["source_receipt"] = earlySource.Body["receipt"]!.DeepClone();
        earlyRequest["source_receipt_sha256"] = earlySource.Body["receipt_sha256"]!.DeepClone();
        var earlyWorkspace = Call(helper, "prepare-workspace", earlyRequest);
        Check(earlyWorkspace.Exit == 0, "pre-plan fixture first prepares its protected main clone");
        var earlyRoot = earlyWorkspace.Body["payload"]!["workspace_root"]!.GetValue<string>();
        var earlyHead = Git(earlyRoot, "rev-parse", "HEAD");
        var earlyMemory = File.ReadAllBytes(early.Memory);
        File.WriteAllText(Path.Combine(early.Docs, "b.md"), "Normal concurrent writer before wiki comparison\n");
        Git(early.Docs, "add", "--", "b.md");
        Git(early.Docs, "commit", "-m", "Append-only docs while no delivery plan exists");
        Git(early.Docs, "push", "origin", "main");
        var earlyOtherCommit = Git(early.Docs, "rev-parse", "HEAD");
        var earlyRefresh = Call(helper, "prepare-workspace", earlyRequest);
        Check(earlyRefresh.Exit == 0 && earlyRefresh.Body["status"]!.GetValue<string>() == "refresh_required", "pre-plan ordinary docs advance requests bounded refresh, not terminal failure: " + earlyRefresh.Body.ToJsonString());
        earlyRequest["workspace_receipt"] = earlyWorkspace.Body["receipt"]!.DeepClone();
        earlyRequest["workspace_receipt_sha256"] = earlyWorkspace.Body["receipt_sha256"]!.DeepClone();
        var earlyRetirement = Call(helper, "retire-plan", earlyRequest);
        Check(earlyRetirement.Exit == 0 && Call(helper, "retire-plan", earlyRequest).Exit == 0 && File.ReadAllBytes(early.Memory).SequenceEqual(earlyMemory) && Git(earlyRoot, "rev-parse", "HEAD") == earlyHead, "pre-plan retirement adopts only the exact owned clean clone and is idempotent without advancing memory");
        var earlyFreshSource = Sources(early);
        History(early, earlyFreshSource, 0, 100);
        var earlyFreshRequest = Common(early);
        earlyFreshRequest["source_receipt"] = earlyFreshSource.Body["receipt"]!.DeepClone();
        earlyFreshRequest["source_receipt_sha256"] = earlyFreshSource.Body["receipt_sha256"]!.DeepClone();
        var earlyFreshWorkspace = Call(helper, "prepare-workspace", earlyFreshRequest);
        Check(earlyFreshWorkspace.Exit == 0, "pre-plan same-run refreshed source admits a distinct owned main clone");
        var earlyFreshRoot = earlyFreshWorkspace.Body["payload"]!["workspace_root"]!.GetValue<string>();
        var earlyFreshTopic = Topic(early, earlyFreshSource, earlyChange, "unchanged", wikiRoot: earlyFreshRoot);
        var earlyCandidates = new JsonArray(Candidate(early, earlyChange, earlyFreshTopic, "already_covered"), new JsonObject { ["kind"] = "git", ["repository"] = early.Docs, ["sha"] = earlyOtherCommit, ["disposition"] = "irrelevant", ["reason"] = "Inspected unrelated fixture-only concurrent review note in exact refreshed main history" });
        var earlyPlanRequest = PlanRequest(early, earlyCandidates, [], earlyFreshSource);
        earlyPlanRequest["workspace_receipt"] = earlyFreshWorkspace.Body["receipt"]!.DeepClone();
        earlyPlanRequest["workspace_receipt_sha256"] = earlyFreshWorkspace.Body["receipt_sha256"]!.DeepClone();
        var earlyPlan = Call(helper, "plan-delivery", earlyPlanRequest);
        Check(earlyPlan.Exit == 0 && Call(helper, "finalize", Completion(early, earlyPlan)).Exit == 0 && earlyFreshRoot != earlyRoot && Git(earlyRoot, "rev-parse", "HEAD") == earlyHead && Git(early.Docs, "rev-parse", "HEAD") == earlyOtherCommit, "full refreshed history/comparison completes same session run without overwriting the original checkout or first clone");
        Console.WriteLine("PASS pre-plan-same-run-docs-main-refresh");
        return 0;
    }
    if (Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_DOCS_RACE") == "1")
    {
        var race = Fixture("same-run-docs-main-refresh", false, true);
        var raceChange = OldDatedDocsChange(race);
        var raceSource = Sources(race);
        History(race, raceSource, 0, 100);
        var raceWorkspaceRequest = Common(race);
        raceWorkspaceRequest["source_receipt"] = raceSource.Body["receipt"]!.DeepClone();
        raceWorkspaceRequest["source_receipt_sha256"] = raceSource.Body["receipt_sha256"]!.DeepClone();
        var raceWorkspace = Call(helper, "prepare-workspace", raceWorkspaceRequest);
        Check(raceWorkspace.Exit == 0, "initial race fixture owns its isolated checkout");
        var raceOldRoot = raceWorkspace.Body["payload"]!["workspace_root"]!.GetValue<string>();
        var raceTopic = Topic(race, raceSource, raceChange, "update_needed");
        var racePlanRequest = PlanRequest(race, new JsonArray(Candidate(race, raceChange, raceTopic, "update_needed")), new JsonArray(new JsonObject { ["path"] = "a.md", ["content"] = "Owned refreshed fact\n" }), raceSource);
        racePlanRequest["workspace_receipt"] = raceWorkspace.Body["receipt"]!.DeepClone();
        racePlanRequest["workspace_receipt_sha256"] = raceWorkspace.Body["receipt_sha256"]!.DeepClone();
        var raceOldPlan = Call(helper, "plan-delivery", racePlanRequest);
        Check(raceOldPlan.Exit == 0, "original race plan is retained before any own edit");
        File.WriteAllText(Path.Combine(raceOldRoot, "a.md"), "Owned refreshed fact\n");
        Git(raceOldRoot, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "add", "--", "a.md");
        Git(raceOldRoot, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "docs: preserved old own attempt");
        var oldOwnCommit = Git(raceOldRoot, "rev-parse", "HEAD");
        File.WriteAllText(Path.Combine(race.Docs, "b.md"), "Another writer's review note\n");
        Git(race.Docs, "add", "--", "b.md");
        Git(race.Docs, "commit", "-m", "Another writer's append-only main commit");
        Git(race.Docs, "push", "origin", "main");
        var otherCommit = Git(race.Docs, "rev-parse", "HEAD");
        var raceMemory = File.ReadAllBytes(race.Memory);
        var raceStatus = Call(helper, "delivery-status", Completion(race, raceOldPlan));
        Check(raceStatus.Exit == 0 && raceStatus.Body["status"]!.GetValue<string>() == "refresh_required", "ordinary main advance requests bounded refresh, not terminal failure: " + raceStatus.Body.ToJsonString());
        var retired = Call(helper, "retire-plan", Completion(race, raceOldPlan));
        Check(retired.Exit == 0 && retired.Body["status"]!.GetValue<string>() == "refresh_required" && File.ReadAllBytes(race.Memory).SequenceEqual(raceMemory) && Git(raceOldRoot, "rev-parse", "HEAD") == oldOwnCommit, "retirement preserves old exact own commit, plan evidence and official checkpoint");
        Check(Call(helper, "retire-plan", Completion(race, raceOldPlan)).Exit == 0, "named plan retirement is restart-idempotent");
        var retiredStatus = Call(helper, "delivery-status", Completion(race, raceOldPlan));
        Check(retiredStatus.Exit == 2 && retiredStatus.Body["reason"]!.GetValue<string>().Contains("retired", StringComparison.Ordinal), "a retired plan cannot certify further delivery through an old receipt: " + retiredStatus.Body.ToJsonString());
        var freshRaceSource = Sources(race);
        History(race, freshRaceSource, 0, 100);
        var freshRaceTopic = Topic(race, freshRaceSource, raceChange, "update_needed");
        var freshRaceCandidates = new JsonArray(Candidate(race, raceChange, freshRaceTopic, "update_needed"), new JsonObject { ["kind"] = "git", ["repository"] = race.Docs, ["sha"] = otherCommit, ["disposition"] = "irrelevant", ["reason"] = "Unrelated writer's fixture-only review note inspected in the refreshed exact main range" });
        var freshRaceWorkspaceRequest = Common(race);
        freshRaceWorkspaceRequest["source_receipt"] = freshRaceSource.Body["receipt"]!.DeepClone();
        freshRaceWorkspaceRequest["source_receipt_sha256"] = freshRaceSource.Body["receipt_sha256"]!.DeepClone();
        var freshRaceWorkspace = Call(helper, "prepare-workspace", freshRaceWorkspaceRequest);
        Check(freshRaceWorkspace.Exit == 0, "same immutable session run can prepare a new pinned main workspace");
        var freshRaceRoot = freshRaceWorkspace.Body["payload"]!["workspace_root"]!.GetValue<string>();
        var freshRacePlanRequest = PlanRequest(race, freshRaceCandidates, new JsonArray(new JsonObject { ["path"] = "a.md", ["content"] = "Owned refreshed fact\n" }), freshRaceSource);
        freshRacePlanRequest["workspace_receipt"] = freshRaceWorkspace.Body["receipt"]!.DeepClone();
        freshRacePlanRequest["workspace_receipt_sha256"] = freshRaceWorkspace.Body["receipt_sha256"]!.DeepClone();
        var freshRacePlan = Call(helper, "plan-delivery", freshRacePlanRequest);
        Check(freshRacePlan.Exit == 0 && freshRaceRoot != raceOldRoot, "refreshed topic/history proof binds a distinct new own main intent");
        File.WriteAllText(Path.Combine(freshRaceRoot, "a.md"), "Owned refreshed fact\n");
        Git(freshRaceRoot, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "add", "--", "a.md");
        Git(freshRaceRoot, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "docs: validated refreshed own review");
        Git(freshRaceRoot, "push", "origin", "main");
        var freshOwnCommit = Git(freshRaceRoot, "rev-parse", "HEAD");
        var laterRoot = Path.Combine(race.Folder, "later-writer");
        Git(race.Folder, "clone", "--quiet", "--branch", "main", Git(race.Docs, "remote", "get-url", "origin"), laterRoot);
        File.WriteAllText(Path.Combine(laterRoot, "c.md"), "Later next-window document\n");
        Git(laterRoot, "add", "--", "c.md");
        Git(laterRoot, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "Later append after verified own push");
        Git(laterRoot, "push", "origin", "main");
        var laterCommit = Git(laterRoot, "rev-parse", "HEAD");
        var actualDelivered = Call(helper, "delivery-status", Completion(race, freshRacePlan));
        Check(actualDelivered.Exit == 0 && actualDelivered.Body["status"]!.GetValue<string>() == "delivered" && actualDelivered.Body["docs_reviewed_sha"]!.GetValue<string>() == freshOwnCommit, "a reachable own pushed commit remains delivered without adopting newer unreviewed docs");
        Check(Call(helper, "finalize", Completion(race, freshRacePlan)).Exit == 0, "refreshed actual own delivery completes the same captured session run");
        var finalRaceMemory = File.ReadAllText(race.Memory);
        Check(finalRaceMemory.Contains(freshOwnCommit, StringComparison.Ordinal) && !finalRaceMemory.Contains(laterCommit, StringComparison.Ordinal) && Git(race.Docs, "rev-parse", "HEAD") == otherCommit && Git(raceOldRoot, "rev-parse", "HEAD") == oldOwnCommit && File.ReadAllText(Path.Combine(race.Docs, "a.md")) == "New source fact\n", "checkpoint covers actual reviewed own commit, and both original checkout and old owned attempt remain unchanged");
        Console.WriteLine("PASS same-run-docs-main-race-refresh-and-delivered-ancestor");
        return 0;
    }
    if (Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_ADVANCEMENT") == "1")
    {
        var advancement = Fixture("opt-in-append-only-source-advancement", false, true, reviewedDevelopAhead: true);
        var advancementRequest = Common(advancement);
        advancementRequest["allow_source_advancement"] = true;
        var advancementSource = Call(helper, "verify-sources", advancementRequest);
        Check(advancementSource.Exit == 0, "opt-in exact source verification succeeds");
        var advancementHistory = new JsonObject { ["run_directory"] = advancement.Run, ["source_receipt"] = advancementSource.Body["receipt"]!.DeepClone(), ["source_receipt_sha256"] = advancementSource.Body["receipt_sha256"]!.DeepClone(), ["offset"] = 0, ["limit"] = 100 };
        Check(Call(helper, "git-history", advancementHistory).Exit == 0 && Call(helper, "docs-history", advancementHistory).Exit == 0, "both empty authoritative chains are fully reviewed before advancement");
        var advancementPlan = Plan(advancement, [], [], advancementSource);
        var reviewedTip = Git(advancement.Backend, "rev-parse", "refs/remotes/origin/develop");
        Git(advancement.Backend, "commit", "--allow-empty", "-m", "Unreviewed next-window append-only fact");
        Git(advancement.Backend, "push", "origin", "develop");
        var appendedTip = Git(advancement.Backend, "rev-parse", "HEAD");
        var advancementStatus = Call(helper, "delivery-status", Completion(advancement, advancementPlan));
        Check(advancementStatus.Exit == 0 && advancementStatus.Body["status"]!.GetValue<string>() == "delivered", "opt-in descendant advancement does not abort the fully reviewed pinned window: " + advancementStatus.Body.ToJsonString());
        Check(Call(helper, "finalize", Completion(advancement, advancementPlan)).Exit == 0, "append-only source advance permits complete pinned-window finalization");
        var advancementMemory = File.ReadAllText(advancement.Memory);
        Check(advancementMemory.Contains(reviewedTip, StringComparison.Ordinal) && !advancementMemory.Contains(appendedTip, StringComparison.Ordinal), "checkpoint persists only reviewed source tips, leaving newer commits for the next window");
        var rewritten = Fixture("opt-in-rewritten-source-still-rejected", false, true, reviewedDevelopAhead: true);
        var rewrittenRequest = Common(rewritten);
        rewrittenRequest["allow_source_advancement"] = true;
        var rewrittenSource = Call(helper, "verify-sources", rewrittenRequest);
        var rewrittenHistory = new JsonObject { ["run_directory"] = rewritten.Run, ["source_receipt"] = rewrittenSource.Body["receipt"]!.DeepClone(), ["source_receipt_sha256"] = rewrittenSource.Body["receipt_sha256"]!.DeepClone(), ["offset"] = 0, ["limit"] = 100 };
        Check(Call(helper, "git-history", rewrittenHistory).Exit == 0 && Call(helper, "docs-history", rewrittenHistory).Exit == 0, "rewritten fixture history is initially complete");
        var rewrittenPlan = Plan(rewritten, [], [], rewrittenSource);
        var rewrittenMemory = File.ReadAllBytes(rewritten.Memory);
        Git(rewritten.Backend, "push", "--force", "origin", "HEAD^:refs/heads/develop");
        var rejected = Call(helper, "finalize", Completion(rewritten, rewrittenPlan));
        Check(rejected.Exit == 2 && rejected.Body["reason"]!.GetValue<string>().Contains("authoritative_code", StringComparison.Ordinal) && File.ReadAllBytes(rewritten.Memory).SequenceEqual(rewrittenMemory), "nonancestor rewrite remains blocked and cannot checkpoint unproven source state: " + rejected.Body.ToJsonString());
        Console.WriteLine("PASS opt-in-monotonic-source-advancement-and-reviewed-only-checkpoint");
        return 0;
    }
        var isolated = Fixture("isolated-main-delivery", false, true, withPriorWork: true);
        var change = OldDatedDocsChange(isolated);
        var isolatedSource = Sources(isolated);
        History(isolated, isolatedSource, 0, 100);
        File.WriteAllText(Path.Combine(isolated.Docs, "prior-work.txt"), "Foreign stash fixture\n");
        Git(isolated.Docs, "stash", "push", "-m", "Unrelated retained stash", "--", "prior-work.txt");
        var stashBefore = Git(isolated.Docs, "stash", "list", "--format=%H");
        File.WriteAllText(Path.Combine(isolated.Docs, "prior-work.txt"), "User staged bytes\n");
        Git(isolated.Docs, "add", "--", "prior-work.txt");
        File.WriteAllText(Path.Combine(isolated.Docs, "prior-work.txt"), "User working bytes\n");
        File.WriteAllBytes(Path.Combine(isolated.Docs, "user-binary.bin"), [0x00, 0xfe, 0x47]);
        File.WriteAllText(Path.Combine(isolated.Docs, "a.md"), "Canonical unrelated guide edit\n");
        var indexBefore = Git(isolated.Docs, "write-tree");
        var initialIndexBytes = File.ReadAllBytes(Path.Combine(isolated.Docs, ".git", "index"));
        var request = Common(isolated);
        request["source_receipt"] = isolatedSource.Body["receipt"]!.DeepClone();
        request["source_receipt_sha256"] = isolatedSource.Body["receipt_sha256"]!.DeepClone();
        var workspace = Call(helper, "prepare-workspace", request);
        Check(workspace.Exit == 0 && workspace.Body["status"]!.GetValue<string>() == "workspace_ready", "a private main workspace is prepared despite mixed canonical dirt: " + workspace.Body.ToJsonString());
        var deliveryRoot = workspace.Body["payload"]!["workspace_root"]!.GetValue<string>();
        Check(deliveryRoot != isolated.Docs && Git(deliveryRoot, "branch", "--show-current") == "main" && Git(deliveryRoot, "rev-parse", "HEAD") == Git(isolated.Docs, "rev-parse", "refs/remotes/origin/main"), "the run-owned workspace is independent and pinned on main");
        Check(File.ReadAllBytes(Path.Combine(isolated.Docs, ".git", "index")).SequenceEqual(initialIndexBytes) && Git(isolated.Docs, "write-tree") == indexBefore && Git(isolated.Docs, "stash", "list", "--format=%H") == stashBefore && File.ReadAllText(Path.Combine(isolated.Docs, "prior-work.txt")) == "User working bytes\n", "preparation leaves literal canonical index, bytes and stashes untouched");
        var repeatedWorkspace = Call(helper, "prepare-workspace", request);
        Check(repeatedWorkspace.Exit == 0 && repeatedWorkspace.Body["receipt"]!.GetValue<string>() == workspace.Body["receipt"]!.GetValue<string>(), "an unchanged prepare request adopts the same protected workspace");
        var isolatedTopic = Topic(isolated, isolatedSource, change, "update_needed", wikiRoot: deliveryRoot);
        var planRequest = PlanRequest(isolated, new JsonArray(Candidate(isolated, change, isolatedTopic, "update_needed")), new JsonArray(new JsonObject { ["path"] = "a.md", ["content"] = "Owned isolated review fact\n" }), isolatedSource);
        planRequest["workspace_receipt"] = workspace.Body["receipt"]!.DeepClone();
        planRequest["workspace_receipt_sha256"] = workspace.Body["receipt_sha256"]!.DeepClone();
        var foreignWorkspaceReceipt = Path.Combine(root, "arbitrary-workspace-receipt.json");
        File.WriteAllBytes(foreignWorkspaceReceipt, File.ReadAllBytes(workspace.Body["receipt"]!.GetValue<string>()));
        File.SetUnixFileMode(foreignWorkspaceReceipt, UnixFileMode.UserRead | UnixFileMode.UserWrite);
        var arbitraryRequest = planRequest.DeepClone().AsObject();
        arbitraryRequest["workspace_receipt"] = foreignWorkspaceReceipt;
        var arbitraryWorkspace = Call(helper, "plan-delivery", arbitraryRequest);
        Check(arbitraryWorkspace.Exit == 2 && arbitraryWorkspace.Body["reason"]!.GetValue<string>() == "foreign_receipt", "a caller-supplied arbitrary workspace receipt outside the protected run cannot authorize delivery");
        var exactOrigin = Git(deliveryRoot, "remote", "get-url", "origin");
        var otherOrigin = Git(isolated.Sts, "remote", "get-url", "origin");
        Git(deliveryRoot, "remote", "set-url", "origin", otherOrigin);
        Check(Call(helper, "plan-delivery", planRequest).Exit == 2, "a wrong workspace fetch origin cannot be used for docs delivery");
        Git(deliveryRoot, "remote", "set-url", "origin", exactOrigin);
        Git(deliveryRoot, "config", "remote.origin.pushurl", otherOrigin);
        Check(Call(helper, "plan-delivery", planRequest).Exit == 2, "the effective workspace push URL must match the exact bound docs origin too");
        Git(deliveryRoot, "config", "--unset", "remote.origin.pushurl");
        var exactWorkspacePath = workspace.Body["receipt"]!.GetValue<string>();
        var exactWorkspaceBytes = File.ReadAllBytes(exactWorkspacePath);
        File.WriteAllText(exactWorkspacePath, "{}\n");
        Check(Call(helper, "plan-delivery", planRequest).Exit == 2, "corrupt owned workspace evidence cannot be adopted");
        File.WriteAllBytes(exactWorkspacePath, exactWorkspaceBytes);
        var isolatedPlan = Call(helper, "plan-delivery", planRequest);
        Check(isolatedPlan.Exit == 0, "own isolated delivery plan ignores ordinary canonical dirt: " + isolatedPlan.Body.ToJsonString());
        var privateForeignPath = Path.Combine(deliveryRoot, "foreign.md");
        File.WriteAllText(privateForeignPath, "Unknown private workspace edit\n");
        var privateForeignMemory = File.ReadAllBytes(isolated.Memory);
        var privateForeignStatus = Call(helper, "delivery-status", Completion(isolated, isolatedPlan));
        Check(privateForeignStatus.Exit == 2 && privateForeignStatus.Body["reason"]!.GetValue<string>() == "foreign_dirty_docs" && File.ReadAllText(privateForeignPath) == "Unknown private workspace edit\n" && File.ReadAllBytes(isolated.Memory).SequenceEqual(privateForeignMemory), "unowned private workspace edits remain intact and cannot certify delivery or checkpoint");
        File.Delete(privateForeignPath);
        // Model another writer's legitimate local commit and fresh dirty work.
        Git(isolated.Docs, "commit", "-m", "Another task's local audit commit");
        File.WriteAllText(Path.Combine(isolated.Docs, "prior-work.txt"), "Concurrent working bytes\n");
        Git(isolated.Docs, "add", "--", "prior-work.txt");
        File.WriteAllText(Path.Combine(isolated.Docs, "prior-work.txt"), "Concurrent later bytes\n");
        var concurrentHead = Git(isolated.Docs, "rev-parse", "HEAD");
        var concurrentIndex = Git(isolated.Docs, "write-tree");
        var concurrentStatus = Git(isolated.Docs, "status", "--porcelain=v1", "--untracked-files=all");
        var concurrentIndexBytes = File.ReadAllBytes(Path.Combine(isolated.Docs, ".git", "index"));
        Check(Call(helper, "delivery-status", Completion(isolated, isolatedPlan)).Body["status"]!.GetValue<string>() == "planned", "concurrent canonical work does not invalidate the private plan");
        File.WriteAllText(Path.Combine(deliveryRoot, "a.md"), "Owned isolated review fact\n");
        Git(deliveryRoot, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "add", "--", "a.md");
        Git(deliveryRoot, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "docs: isolated fixture review");
        Check(Call(helper, "delivery-status", Completion(isolated, isolatedPlan)).Body["status"]!.GetValue<string>() == "own_commit", "only the exact isolated own commit permits its push");
        Git(deliveryRoot, "push", "origin", "main");
        var ownHead = Git(deliveryRoot, "rev-parse", "HEAD");
        var isolatedCompleted = Call(helper, "finalize", Completion(isolated, isolatedPlan));
        Check(isolatedCompleted.Exit == 0 && isolatedCompleted.Body["active_retired"]!.GetValue<bool>(), "actual isolated main delivery completes without unrelated protection/restoration: " + isolatedCompleted.Body.ToJsonString());
        Check(File.ReadAllBytes(Path.Combine(isolated.Docs, ".git", "index")).SequenceEqual(concurrentIndexBytes) && Git(isolated.Docs, "rev-parse", "HEAD") == concurrentHead && Git(isolated.Docs, "write-tree") == concurrentIndex && Git(isolated.Docs, "status", "--porcelain=v1", "--untracked-files=all") == concurrentStatus && Git(isolated.Docs, "stash", "list", "--format=%H") == stashBefore && File.ReadAllText(Path.Combine(isolated.Docs, "prior-work.txt")) == "Concurrent later bytes\n" && File.ReadAllText(Path.Combine(isolated.Docs, "a.md")) == "Canonical unrelated guide edit\n" && File.ReadAllBytes(Path.Combine(isolated.Docs, "user-binary.bin")).SequenceEqual(new byte[] { 0x00, 0xfe, 0x47 }), "delivery/finalization leave all canonical concurrent bytes, literal index, dirty same guide, HEAD and foreign stashes untouched");
        var memoryText = File.ReadAllText(isolated.Memory);
        Check(memoryText.Contains("\"repository\":\"" + isolated.Docs + "\"", StringComparison.Ordinal) && memoryText.Contains(ownHead, StringComparison.Ordinal) && !memoryText.Contains(deliveryRoot, StringComparison.Ordinal), "Docs checkpoint retains canonical repository identity and actually reviewed own SHA");
        Console.WriteLine("PASS isolated-main-delivery-with-concurrent-canonical-work");
        Console.WriteLine("Fixture: " + root);
        return 0;
}
catch (Exception ex) { Console.Error.WriteLine("FAIL " + ex.Message + "\nFixture: " + root); return 1; }
finally { if (Environment.GetEnvironmentVariable("NCG_WIKI_KEEP_FIXTURE") != "1") Directory.Delete(root, true); }

FixtureState Fixture(string name, bool session, bool docsBaseline, bool reviewedDevelopAhead = false, int timeoutSeconds = 120, bool manualClone = false, int maxOutputBytes = 16777216, bool withPriorWork = false)
{
    var folder = Path.Combine(root, name);
    Directory.CreateDirectory(folder);
    var backend = Repository(folder, "backend", "develop");
    var sts = Repository(folder, "sts", "develop");
    var docs = Repository(folder, "docs", "main");
    if (withPriorWork)
    {
        File.WriteAllText(Path.Combine(docs, "prior-work.txt"), "Baseline user work\n");
        Git(docs, "add", "--", "prior-work.txt");
        Git(docs, "commit", "-m", "Initial unrelated tracked user work");
        Git(docs, "push", "origin", "main");
    }
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
(int Exit, JsonObject Body) Topic(FixtureState f, (int Exit, JsonObject Body) source, string commit, string decision, string wikiPath = "a.md", string? wikiRoot = null) { var payload = source.Body["payload"]!; var request = f.ReviewRequest.DeepClone().AsObject(); request["run_directory"] = f.Run; request["topic_id"] = "docs-topic"; request["source_pins"] = payload["source_pins"]!.DeepClone(); request["documentation_pin"] = payload["documentation_pin"]!.DeepClone(); request["session_ids"] = new JsonArray(); request["git_candidates"] = new JsonArray(new JsonObject { ["repository"] = f.Docs, ["sha"] = commit }); request["wiki_files"] = new JsonArray(Path.Combine(wikiRoot ?? f.Docs, wikiPath)); request["decision"] = decision; request["comparison"] = "Compared fixed authoritative Git change with current pinned main page."; var result = Call(review, "record-topic", request); Check(result.Exit == 0, "topic: " + result.Body.ToJsonString()); return result; }
JsonObject Candidate(FixtureState f, string commit, (int Exit, JsonObject Body) topic, string disposition) => new() { ["kind"] = "git", ["repository"] = f.Docs, ["sha"] = commit, ["disposition"] = disposition, ["reason"] = "Compared pinned current Markdown and exact Git original", ["topic_receipt"] = topic.Body["receipt"]!.DeepClone(), ["topic_receipt_sha256"] = topic.Body["receipt_sha256"]!.DeepClone() };
JsonObject PlanRequest(FixtureState f, JsonArray candidates, JsonArray edits, (int Exit, JsonObject Body) source) { var request = Common(f); request["source_receipt"] = source.Body["receipt"]!.DeepClone(); request["source_receipt_sha256"] = source.Body["receipt_sha256"]!.DeepClone(); request["candidates"] = candidates.DeepClone(); request["edits"] = edits.DeepClone(); return request; }
(int Exit, JsonObject Body) Plan(FixtureState f, JsonArray candidates, JsonArray edits, (int Exit, JsonObject Body)? source = null) { var s = source ?? Sources(f); if (source is null) History(f, s, 0, 100); var result = Call(helper, "plan-delivery", PlanRequest(f, candidates, edits, s)); Check(result.Exit == 0, "delivery plan: " + result.Body.ToJsonString()); return result; }
JsonObject Completion(FixtureState f, (int Exit, JsonObject Body) plan) { var r = Common(f); r["plan_receipt"] = plan.Body["receipt"]!.DeepClone(); r["plan_receipt_sha256"] = plan.Body["receipt_sha256"]!.DeepClone(); return r; }
(int Exit, JsonObject Body) Call(string file, string command, JsonObject request, string? pathOverride = null) { var path = Path.Combine(root, "request-" + Guid.NewGuid().ToString("N") + ".json"); File.WriteAllText(path, request.ToJsonString()); File.SetUnixFileMode(path, UnixFileMode.UserRead | UnixFileMode.UserWrite); var start = new ProcessStartInfo("dotnet") { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true }; if (pathOverride is not null) start.Environment["PATH"] = pathOverride; foreach (var arg in new[] { "run", "--file", file, "--", command, "--request", path }) start.ArgumentList.Add(arg); using var p = Process.Start(start)!; var output = p.StandardOutput.ReadToEnd(); var errors = p.StandardError.ReadToEnd(); p.WaitForExit(); File.AppendAllText(Path.Combine(root, "public-cli.log"), command + " exit=" + p.ExitCode + "\n" + output + errors + "\n"); var line = output.Split('\n', StringSplitOptions.RemoveEmptyEntries).LastOrDefault() ?? "{}"; return (p.ExitCode, JsonNode.Parse(line)!.AsObject()); }
string Git(string cwd, params string[] arguments) { var r = GitRun(cwd, arguments); Check(r.Exit == 0, "git " + arguments[0] + ": " + r.Error); return r.Output.Trim(); }
int GitExit(string cwd, params string[] arguments) => GitRun(cwd, arguments).Exit;
bool IsFifo(string path) { var start = new ProcessStartInfo("/bin/test") { UseShellExecute = false }; start.ArgumentList.Add("-p"); start.ArgumentList.Add(path); using var process = Process.Start(start)!; process.WaitForExit(); return process.ExitCode == 0; }
(int Exit, string Output, string Error) GitRun(string cwd, string[] arguments) { var start = new ProcessStartInfo("git") { WorkingDirectory = cwd, UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true }; foreach (var arg in arguments) start.ArgumentList.Add(arg); using var p = Process.Start(start)!; var output = p.StandardOutput.ReadToEnd(); var error = p.StandardError.ReadToEnd(); p.WaitForExit(); return (p.ExitCode, output, error); }
void Check(bool condition, string why) { if (!condition) throw new Exception(why); }
record FixtureState(string Folder, string Backend, string Sts, string Docs, string Memory, string Store, string Run, JsonObject ReviewRequest);

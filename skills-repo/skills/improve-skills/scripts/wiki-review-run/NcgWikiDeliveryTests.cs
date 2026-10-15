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
    if (Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_IGNORED_TARGET") != "1")
    {
    var untrackedNormalization = Fixture("untracked-only-normalization-preflight", false, true);
    var untrackedNormalizationSource = Sources(untrackedNormalization);
    History(untrackedNormalization, untrackedNormalizationSource, 0, 100);
    var untrackedNormalizationMemory = File.ReadAllBytes(untrackedNormalization.Memory);
    var untrackedNormalizationHead = Git(untrackedNormalization.Docs, "rev-parse", "HEAD");
    var untrackedNormalizationIndex = Git(untrackedNormalization.Docs, "rev-parse", "HEAD^{tree}");
    File.WriteAllBytes(Path.Combine(untrackedNormalization.Docs, "raw-crlf-untracked.txt"), Encoding.UTF8.GetBytes("Untracked CRLF bytes\r\nSecond CRLF line\r\n"));
    var untrackedNormalizationRequest = Common(untrackedNormalization);
    untrackedNormalizationRequest["source_receipt"] = untrackedNormalizationSource.Body["receipt"]!.DeepClone();
    untrackedNormalizationRequest["source_receipt_sha256"] = untrackedNormalizationSource.Body["receipt_sha256"]!.DeepClone();
    foreach (var normalization in new[] { (Setting: "true", Reason: "worktree_eol_conversion_unsupported"), (Setting: "input", Reason: "worktree_raw_normalization_unsupported") })
    {
        Git(untrackedNormalization.Docs, "config", "core.autocrlf", normalization.Setting);
        Check(Git(untrackedNormalization.Docs, "diff", "--name-only") == "" && Git(untrackedNormalization.Docs, "diff", "--cached", "--name-only") == "" && Git(untrackedNormalization.Docs, "status", "--porcelain", "--untracked-files=all") == "?? raw-crlf-untracked.txt", "the CRLF preflight fixture has only untracked dirt under core.autocrlf=" + normalization.Setting);
        var normalizationProtection = Call(helper, "protect-worktree", untrackedNormalizationRequest);
        Check(normalizationProtection.Exit == 2 && normalizationProtection.Body["reason"]!.GetValue<string>() == normalization.Reason, "untracked-only CRLF normalization is rejected concretely before protection under core.autocrlf=" + normalization.Setting + ": " + normalizationProtection.Body.ToJsonString());
        Check(File.ReadAllBytes(Path.Combine(untrackedNormalization.Docs, "raw-crlf-untracked.txt")).SequenceEqual(Encoding.UTF8.GetBytes("Untracked CRLF bytes\r\nSecond CRLF line\r\n")) && File.ReadAllBytes(untrackedNormalization.Memory).SequenceEqual(untrackedNormalizationMemory) && Git(untrackedNormalization.Docs, "rev-parse", "HEAD") == untrackedNormalizationHead && Git(untrackedNormalization.Docs, "write-tree") == untrackedNormalizationIndex && GitExit(untrackedNormalization.Docs, "rev-parse", "--verify", "refs/stash") != 0, "rejected untracked normalization preserves literal bytes, memory, HEAD, index and absence of any stash");
    }
    Console.WriteLine("PASS untracked-only-crlf-true-and-input-pre-mutation-rejection");
    }

    var ignoredTarget = Fixture("ignored-owned-target-collisions", false, true);
    var ignoredTargetCommit = OldDatedDocsChange(ignoredTarget);
    var ignoredTargetSource = Sources(ignoredTarget);
    History(ignoredTarget, ignoredTargetSource, 0, 100);
    var ignoredTargetMemory = File.ReadAllBytes(ignoredTarget.Memory);
    var ignoredTargetTopic = Topic(ignoredTarget, ignoredTargetSource, ignoredTargetCommit, "update_needed", "new-page.md");
    var ignoredTargetCandidates = new JsonArray(Candidate(ignoredTarget, ignoredTargetCommit, ignoredTargetTopic, "update_needed"));
    var ignoredTargetEdits = new JsonArray(new JsonObject { ["path"] = "new-page.md", ["content"] = "Own new page content\n" });
    var ignoredTargetRequest = PlanRequest(ignoredTarget, ignoredTargetCandidates, ignoredTargetEdits, ignoredTargetSource);
    var ignoreFile = Path.Combine(ignoredTarget.Docs, ".git", "info", "exclude");
    byte[] originalExclusion = File.Exists(ignoreFile) ? File.ReadAllBytes(ignoreFile) : [];
    File.AppendAllText(ignoreFile, "\nnew-page.md\n");
    File.WriteAllText(Path.Combine(ignoredTarget.Docs, "new-page.md"), "Foreign ignored user content\n");
    Check(Git(ignoredTarget.Docs, "check-ignore", "--", "new-page.md") == "new-page.md" && Git(ignoredTarget.Docs, "status", "--porcelain", "--untracked-files=all") == "", "a real ignored target collision is absent from ordinary Git status");
    var rejectedIgnoredPlan = Call(helper, "plan-delivery", ignoredTargetRequest);
    Check(rejectedIgnoredPlan.Exit == 2 && (rejectedIgnoredPlan.Body["reason"]!.GetValue<string>().Contains("collision", StringComparison.Ordinal) || rejectedIgnoredPlan.Body["reason"]!.GetValue<string>().Contains("target", StringComparison.Ordinal)), "an ignored foreign file cannot become an owned missing-base delivery target: " + rejectedIgnoredPlan.Body.ToJsonString());
    Check(!File.Exists(Path.Combine(ignoredTarget.Run, "delivery", "plan.json")) && File.ReadAllText(Path.Combine(ignoredTarget.Docs, "new-page.md")) == "Foreign ignored user content\n" && File.ReadAllBytes(ignoredTarget.Memory).SequenceEqual(ignoredTargetMemory) && GitExit(ignoredTarget.Docs, "rev-parse", "--verify", "refs/stash") != 0, "ignored pre-plan collision blocks actionable intent while preserving foreign file bytes, memory and stash state");
    File.Delete(Path.Combine(ignoredTarget.Docs, "new-page.md"));
    File.WriteAllBytes(ignoreFile, originalExclusion);
    var missingTargetPlan = Plan(ignoredTarget, ignoredTargetCandidates, ignoredTargetEdits, ignoredTargetSource);
    File.AppendAllText(ignoreFile, "\nnew-page.md\n");
    File.WriteAllText(Path.Combine(ignoredTarget.Docs, "new-page.md"), "New ignored foreign content after plan\n");
    Check(Git(ignoredTarget.Docs, "check-ignore", "--", "new-page.md") == "new-page.md" && Git(ignoredTarget.Docs, "status", "--porcelain", "--untracked-files=all") == "", "the new ignored target remains invisible to Git status after the missing-target plan");
    var ignoredTargetStatus = Call(helper, "delivery-status", Completion(ignoredTarget, missingTargetPlan));
    Check(ignoredTargetStatus.Exit == 2 && (ignoredTargetStatus.Body["reason"]!.GetValue<string>().Contains("collision", StringComparison.Ordinal) || ignoredTargetStatus.Body["reason"]!.GetValue<string>().Contains("target", StringComparison.Ordinal)), "delivery status rejects the ignored foreign target before approving application of the owned plan: " + ignoredTargetStatus.Body.ToJsonString());
    Check(File.ReadAllText(Path.Combine(ignoredTarget.Docs, "new-page.md")) == "New ignored foreign content after plan\n" && File.ReadAllBytes(ignoredTarget.Memory).SequenceEqual(ignoredTargetMemory) && GitExit(ignoredTarget.Docs, "rev-parse", "--verify", "refs/stash") != 0, "post-plan ignored collision preserves the exact new foreign bytes, memory and stash state");
    Console.WriteLine("PASS ignored-target-before-plan-and-after-plan-collision-guards");
    if (Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_STASH_PREFLIGHT") == "1" || Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_IGNORED_TARGET") == "1")
    {
        Console.WriteLine("Fixture: " + root);
        return 0;
    }
    if (Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_STASH_FIFO") != "1")
    {
        var interrupted = Fixture("interrupted-real-stash-operations", false, true, maxOutputBytes: 4096, withPriorWork: true);
        var interruptedSource = Sources(interrupted);
        History(interrupted, interruptedSource, 0, 100);
        var interruptedMemory = File.ReadAllBytes(interrupted.Memory);
        File.WriteAllText(Path.Combine(interrupted.Docs, "prior-work.txt"), "Recovery staged before interruption\n");
        Git(interrupted.Docs, "add", "--", "prior-work.txt");
        File.WriteAllText(Path.Combine(interrupted.Docs, "prior-work.txt"), "Recovery unstaged before interruption\n");
        File.WriteAllBytes(Path.Combine(interrupted.Docs, "interrupted-binary.bin"), [0x08, 0x00, 0xf7, 0x63]);
        var interruptedLauncher = Path.Combine(interrupted.Folder, "fake-bin");
        Directory.CreateDirectory(interruptedLauncher);
        var pushCount = Path.Combine(interrupted.Folder, "push-count.txt");
        var applyCount = Path.Combine(interrupted.Folder, "apply-count.txt");
        var interruptedGit = Path.Combine(interruptedLauncher, "git");
        File.WriteAllText(interruptedGit, $$"""
            #!/usr/bin/env python3
            import os,sys,subprocess
            arguments=sys.argv[1:]
            mutation=arguments[1] if len(arguments)>1 and arguments[0]=='stash' and arguments[1] in ('push','apply') else None
            if mutation:
                result=subprocess.run(['/usr/bin/git',*arguments])
                if result.returncode==0:
                    counter={{JsonValue.Create(pushCount)!.ToJsonString()}} if mutation=='push' else {{JsonValue.Create(applyCount)!.ToJsonString()}}
                    count=int(open(counter).read()) if os.path.exists(counter) else 0
                    open(counter,'w').write(str(count+1))
                    if count==0:
                        sys.stdout.write('x'*8192+'\n')
                        sys.stdout.flush()
                sys.exit(result.returncode)
            os.execv('/usr/bin/git',['git',*arguments])
            """ + "\n");
        File.SetUnixFileMode(interruptedGit, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute);
        var interruptedPath = interruptedLauncher + ":" + Environment.GetEnvironmentVariable("PATH");
        var interruptedProtectRequest = Common(interrupted);
        interruptedProtectRequest["source_receipt"] = interruptedSource.Body["receipt"]!.DeepClone();
        interruptedProtectRequest["source_receipt_sha256"] = interruptedSource.Body["receipt_sha256"]!.DeepClone();
        var interruptedProtection = Call(helper, "protect-worktree", interruptedProtectRequest, interruptedPath);
        Check(interruptedProtection.Exit == 2 && interruptedProtection.Body["reason"]!.GetValue<string>() == "process_output_limit" && File.ReadAllText(pushCount) == "1", "a real successful stash push is interrupted by the bounded-output failure");
        var interruptedStash = Git(interrupted.Docs, "rev-parse", "refs/stash");
        Check(Git(interrupted.Docs, "status", "--porcelain", "--untracked-files=all") == "" && File.Exists(Path.Combine(interrupted.Run, "delivery", "worktree-protection.json")) && File.ReadAllBytes(interrupted.Memory).SequenceEqual(interruptedMemory), "the successful interrupted mutation leaves clean docs, recovery evidence and unchanged memory");
        var interruptedDefinition = Path.Combine(Path.GetDirectoryName(interrupted.Memory)!, "automation.toml");
        File.AppendAllText(interruptedDefinition, "# Definition changed after the protected stash operation\n");
    var invalidation = Call(review, "invalidate", new JsonObject { ["run_directory"] = interrupted.Run, ["reason"] = "Explicit stale fixture review; restore protected work only" });
    Check(invalidation.Exit == 0 && !File.Exists(Path.Combine(interrupted.Folder, "store", "active.json")), "explicit stale-run invalidation retires selection without losing protection ownership");
        var interruptedRestoration = Call(helper, "restore-worktree", Common(interrupted), interruptedPath);
        Check(interruptedRestoration.Exit == 2 && interruptedRestoration.Body["reason"]!.GetValue<string>() == "process_output_limit" && File.ReadAllText(applyCount) == "1", "stale-definition cleanup adopts the nonce-owned stash and a real successful apply is interrupted by output bounds");
        Check(File.ReadAllText(Path.Combine(interrupted.Docs, "prior-work.txt")) == "Recovery unstaged before interruption\n" && GitRun(interrupted.Docs, ["show", ":prior-work.txt"]).Output == "Recovery staged before interruption\n" && File.ReadAllBytes(Path.Combine(interrupted.Docs, "interrupted-binary.bin")).SequenceEqual(new byte[] { 0x08, 0x00, 0xf7, 0x63 }), "interrupted apply already recovered the exact original working, index and binary contents");
        var recoveredRestoration = Call(helper, "restore-worktree", Common(interrupted), interruptedPath);
        Check(recoveredRestoration.Exit == 0 && recoveredRestoration.Body["status"]!.GetValue<string>() == "restored" && recoveredRestoration.Body["stash_sha"]!.GetValue<string>() == interruptedStash, "restart adopts the exact completed restoration despite changed definition: " + recoveredRestoration.Body.ToJsonString());
        Check(File.ReadAllText(pushCount) == "1" && File.ReadAllText(applyCount) == "1" && Git(interrupted.Docs, "stash", "list", "--format=%H") == interruptedStash && File.ReadAllBytes(interrupted.Memory).SequenceEqual(interruptedMemory), "recovery performs neither successful Git mutation twice and retains its exact backup and memory");
        Console.WriteLine("PASS real-stash-push-and-apply-interruption-adoption-after-stale-definition");

        var rawEol = Fixture("protected-raw-eol-preflight", false, true, withPriorWork: true);
        var rawEolSource = Sources(rawEol);
        History(rawEol, rawEolSource, 0, 100);
        var rawEolMemory = File.ReadAllBytes(rawEol.Memory);
        var rawEolHead = Git(rawEol.Docs, "rev-parse", "HEAD");
        Git(rawEol.Docs, "config", "core.autocrlf", "true");
        File.WriteAllBytes(Path.Combine(rawEol.Docs, "prior-work.txt"), Encoding.UTF8.GetBytes("Raw staged fact\r\n"));
        Git(rawEol.Docs, "add", "--", "prior-work.txt");
        Check(GitRun(rawEol.Docs, ["show", ":prior-work.txt"]).Output == "Raw staged fact\n", "EOL fixture genuinely normalizes CRLF staged bytes into LF index bytes");
        File.WriteAllBytes(Path.Combine(rawEol.Docs, "prior-work.txt"), Encoding.UTF8.GetBytes("Raw unstaged fact\n"));
        var rawEolRequest = Common(rawEol);
        rawEolRequest["source_receipt"] = rawEolSource.Body["receipt"]!.DeepClone();
        rawEolRequest["source_receipt_sha256"] = rawEolSource.Body["receipt_sha256"]!.DeepClone();
        var rawEolProtection = Call(helper, "protect-worktree", rawEolRequest);
        if (rawEolProtection.Exit == 0)
        {
            var rawEolRestore = Call(helper, "restore-worktree", Common(rawEol));
            Check(rawEolRestore.Exit == 0 && rawEolRestore.Body["status"]!.GetValue<string>() == "restored", "supported EOL conversion can restore its protected work");
        }
        else
        {
            Check(rawEolProtection.Exit == 2 && rawEolProtection.Body["reason"]!.GetValue<string>() == "worktree_eol_conversion_unsupported" && GitExit(rawEol.Docs, "rev-parse", "--verify", "refs/stash") != 0 && Git(rawEol.Docs, "rev-parse", "HEAD") == rawEolHead, "unsupported EOL conversion is rejected concretely before any stash mutation");
        }
        Check(File.ReadAllBytes(Path.Combine(rawEol.Docs, "prior-work.txt")).SequenceEqual(Encoding.UTF8.GetBytes("Raw unstaged fact\n")) && GitRun(rawEol.Docs, ["show", ":prior-work.txt"]).Output == "Raw staged fact\n" && File.ReadAllBytes(rawEol.Memory).SequenceEqual(rawEolMemory), "normalization never silently changes literal original working bytes, staged bytes or memory");
        Console.WriteLine("PASS raw-working-eol-preservation-or-concrete-pre-mutation-rejection");
    }

    var nonregular = Fixture("protected-untouched-special-file-or-preflight", false, true, withPriorWork: true);
    var nonregularSource = Sources(nonregular);
    History(nonregular, nonregularSource, 0, 100);
    var nonregularMemory = File.ReadAllBytes(nonregular.Memory);
    File.WriteAllText(Path.Combine(nonregular.Docs, "prior-work.txt"), "FIFO fixture original staged bytes\n");
    Git(nonregular.Docs, "add", "--", "prior-work.txt");
    File.WriteAllText(Path.Combine(nonregular.Docs, "prior-work.txt"), "FIFO fixture original working bytes\n");
    File.WriteAllBytes(Path.Combine(nonregular.Docs, "original-binary.bin"), [0x7b, 0x00, 0xee]);
    var fifoPath = Path.Combine(nonregular.Docs, "nonregular.pipe");
    var fifoStart = new ProcessStartInfo("mkfifo") { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true };
    fifoStart.ArgumentList.Add(fifoPath);
    using (var fifo = Process.Start(fifoStart)!)
    {
        fifo.WaitForExit();
        Check(fifo.ExitCode == 0, "the isolated nonregular fixture creates a real FIFO");
    }
    File.SetUnixFileMode(fifoPath, UnixFileMode.UserRead | UnixFileMode.UserWrite);
    var nonregularRequest = Common(nonregular);
    nonregularRequest["source_receipt"] = nonregularSource.Body["receipt"]!.DeepClone();
    nonregularRequest["source_receipt_sha256"] = nonregularSource.Body["receipt_sha256"]!.DeepClone();
    var nonregularProtection = Call(helper, "protect-worktree", nonregularRequest);
    if (nonregularProtection.Exit == 0)
    {
        Check(nonregularProtection.Body["status"]!.GetValue<string>() == "protected" && IsFifo(fifoPath) && File.ReadAllBytes(nonregular.Memory).SequenceEqual(nonregularMemory), "Git-ignored special files remain real FIFOs throughout successful protection");
        var nonregularRestore = Call(helper, "restore-worktree", Common(nonregular));
        Check(nonregularRestore.Exit == 0 && nonregularRestore.Body["status"]!.GetValue<string>() == "restored", "protected regular work restores while the ignored FIFO stays untouched: " + nonregularRestore.Body.ToJsonString());
    }
    else
    {
        Check(nonregularProtection.Exit == 2 && nonregularProtection.Body["reason"]!.GetValue<string>().Contains("regular_file", StringComparison.Ordinal) && GitExit(nonregular.Docs, "rev-parse", "--verify", "refs/stash") != 0, "a listed nonregular FIFO is rejected concretely before stash mutation");
    }
    Check(IsFifo(fifoPath) && File.ReadAllText(Path.Combine(nonregular.Docs, "prior-work.txt")) == "FIFO fixture original working bytes\n" && GitRun(nonregular.Docs, ["show", ":prior-work.txt"]).Output == "FIFO fixture original staged bytes\n" && File.ReadAllBytes(Path.Combine(nonregular.Docs, "original-binary.bin")).SequenceEqual(new byte[] { 0x7b, 0x00, 0xee }) && File.ReadAllBytes(nonregular.Memory).SequenceEqual(nonregularMemory), "special-file handling preserves the actual FIFO, distinct original working/index bytes, binary data and memory");
    Console.WriteLine("PASS untouched-special-file-or-preflight");
    if (Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_STASH_RECOVERY") == "1" || Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_STASH_FIFO") == "1")
    {
        Console.WriteLine("Fixture: " + root);
        return 0;
    }
    var protectedWork = Fixture("protected-mixed-prior-work", false, true, withPriorWork: true);
    var protectedCommit = OldDatedDocsChange(protectedWork);
    var protectedSource = Sources(protectedWork);
    History(protectedWork, protectedSource, 0, 100);
    const string priorPath = "prior-work.txt";
    File.WriteAllText(Path.Combine(protectedWork.Docs, priorPath), "Foreign stash work\n");
    Git(protectedWork.Docs, "stash", "push", "-m", "Foreign fixture stash", "--", priorPath);
    var foreignStash = Git(protectedWork.Docs, "rev-parse", "refs/stash");
    File.WriteAllText(Path.Combine(protectedWork.Docs, priorPath), "User staged version\n");
    Git(protectedWork.Docs, "add", "--", priorPath);
    File.WriteAllText(Path.Combine(protectedWork.Docs, priorPath), "User unstaged version\n");
    File.SetUnixFileMode(Path.Combine(protectedWork.Docs, priorPath), UnixFileMode.UserRead | UnixFileMode.UserWrite);
    const string untrackedPath = "untracked ü data.bin";
    File.WriteAllBytes(Path.Combine(protectedWork.Docs, untrackedPath), [0x00, 0xff, 0x0a, 0x80, 0x42, 0x0d]);
    File.SetUnixFileMode(Path.Combine(protectedWork.Docs, untrackedPath), UnixFileMode.UserRead | UnixFileMode.UserWrite);
    var protectedMemory = File.ReadAllBytes(protectedWork.Memory);
    var protectRequest = Common(protectedWork);
    protectRequest["source_receipt"] = protectedSource.Body["receipt"]!.DeepClone();
    protectRequest["source_receipt_sha256"] = protectedSource.Body["receipt_sha256"]!.DeepClone();
    var protection = Call(helper, "protect-worktree", protectRequest);
    Check(protection.Exit == 0 && protection.Body["status"]!.GetValue<string>() == "protected", "pre-existing mixed work can be protected: " + protection.Body.ToJsonString());
    var ownStash = protection.Body["stash_sha"]!.GetValue<string>();
    Check(ownStash != foreignStash && Git(protectedWork.Docs, "rev-parse", "refs/stash") == ownStash, "protection reports its exact own stash rather than adopting the pre-existing foreign stash");
    Check(Git(protectedWork.Docs, "status", "--porcelain", "--untracked-files=all") == "" && Git(protectedWork.Docs, "diff", "--cached", "--name-only") == "", "protected staged, unstaged and untracked work leaves a clean delivery tree and index");
    Check(File.ReadAllBytes(protectedWork.Memory).SequenceEqual(protectedMemory), "protection does not advance the original memory");
    var protectedTopic = Topic(protectedWork, protectedSource, protectedCommit, "update_needed");
    var protectedPlan = Plan(protectedWork, new JsonArray(Candidate(protectedWork, protectedCommit, protectedTopic, "update_needed")), new JsonArray(new JsonObject { ["path"] = "a.md", ["content"] = "Owned review fact\n" }), protectedSource);
    File.WriteAllText(Path.Combine(protectedWork.Docs, "a.md"), "Owned review fact\n");
    Git(protectedWork.Docs, "add", "--", "a.md");
    Git(protectedWork.Docs, "commit", "-m", "Own review with protected prior work");
    var ownProtectedCommit = Git(protectedWork.Docs, "rev-parse", "HEAD");
    Git(protectedWork.Docs, "push", "origin", "main");
    Check(Git(protectedWork.Docs, "diff-tree", "--no-commit-id", "--name-only", "-r", ownProtectedCommit) == "a.md", "the delivered own commit contains only the planned Markdown page");
    var beforeRestore = Call(helper, "delivery-status", Completion(protectedWork, protectedPlan));
    Check(beforeRestore.Exit == 0 && beforeRestore.Body["status"]!.GetValue<string>() == "delivered", "the exact own pushed commit is recognized while prior work remains protected");
    var prematureCompletion = Call(helper, "finalize", Completion(protectedWork, protectedPlan));
    Check(prematureCompletion.Exit == 2 && File.ReadAllBytes(protectedWork.Memory).SequenceEqual(protectedMemory), "delivery alone cannot finalize before protected work is restored");
    var restoration = Call(helper, "restore-worktree", Completion(protectedWork, protectedPlan));
    Check(restoration.Exit == 0 && restoration.Body["status"]!.GetValue<string>() == "restored", "the exact protected prior work can be restored: " + restoration.Body.ToJsonString());
    Check(File.ReadAllBytes(Path.Combine(protectedWork.Docs, priorPath)).SequenceEqual(Encoding.UTF8.GetBytes("User unstaged version\n")), "restoration recovers the literal original unstaged working bytes");
    var restoredIndex = GitRun(protectedWork.Docs, ["show", ":" + priorPath]);
    Check(restoredIndex.Exit == 0 && restoredIndex.Output == "User staged version\n", "restoration preserves the distinct literal original staged bytes for the same file");
    Check(File.ReadAllBytes(Path.Combine(protectedWork.Docs, untrackedPath)).SequenceEqual(new byte[] { 0x00, 0xff, 0x0a, 0x80, 0x42, 0x0d }), "restoration recovers every original untracked binary byte");
    Check(File.GetUnixFileMode(Path.Combine(protectedWork.Docs, priorPath)) == (UnixFileMode.UserRead | UnixFileMode.UserWrite) && File.GetUnixFileMode(Path.Combine(protectedWork.Docs, untrackedPath)) == (UnixFileMode.UserRead | UnixFileMode.UserWrite), "restoration preserves the literal original 0600 permissions of tracked and untracked prior work");
    Check(Git(protectedWork.Docs, "diff", "--cached", "--name-only") == priorPath && Git(protectedWork.Docs, "diff", "--name-only") == priorPath, "restored prior work retains its staged and further unstaged changes");
    Check(Git(protectedWork.Docs, "stash", "list", "--format=%H").Split('\n').SequenceEqual(new[] { ownStash, foreignStash }), "the owned safety backup and the exact foreign stash both remain intact");
    Check(File.ReadAllText(Path.Combine(protectedWork.Docs, "a.md")) == "Owned review fact\n" && File.ReadAllBytes(protectedWork.Memory).SequenceEqual(protectedMemory), "restoration preserves delivered own content without advancing the memory");
    var protectedFinal = Call(helper, "finalize", Completion(protectedWork, protectedPlan));
    Check(protectedFinal.Exit == 0 && protectedFinal.Body["active_retired"]!.GetValue<bool>(), "verified restored prior dirt permits official completion: " + protectedFinal.Body.ToJsonString());
    var completedProtectedMemory = File.ReadAllBytes(protectedWork.Memory);
    Check(!completedProtectedMemory.SequenceEqual(protectedMemory), "successful completion advances the review bundle after restoration");
    Check(Call(helper, "finalize", Completion(protectedWork, protectedPlan)).Exit == 0 && File.ReadAllBytes(protectedWork.Memory).SequenceEqual(completedProtectedMemory), "completed protected delivery is idempotent despite restored prior dirt");
    Console.WriteLine("PASS protected-mixed-prior-work-own-delivery-restoration-and-finalization");
    if (Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_STASH") == "1")
    {
        Console.WriteLine("Fixture: " + root);
        return 0;
    }

    var cleanProtection = Fixture("protected-clean-tree", false, true);
    var cleanSource = Sources(cleanProtection);
    History(cleanProtection, cleanSource, 0, 100);
    var cleanMemory = File.ReadAllBytes(cleanProtection.Memory);
    var cleanProtectRequest = Common(cleanProtection);
    cleanProtectRequest["source_receipt"] = cleanSource.Body["receipt"]!.DeepClone();
    cleanProtectRequest["source_receipt_sha256"] = cleanSource.Body["receipt_sha256"]!.DeepClone();
    var cleanProtected = Call(helper, "protect-worktree", cleanProtectRequest);
    Check(cleanProtected.Exit == 0 && cleanProtected.Body["status"]!.GetValue<string>() == "protected" && GitExit(cleanProtection.Docs, "rev-parse", "--verify", "refs/stash") != 0, "clean protection is recorded without inventing a stash");
    var cleanPlan = Plan(cleanProtection, [], [], cleanSource);
    Check(Call(helper, "finalize", Completion(cleanProtection, cleanPlan)).Exit == 2 && File.ReadAllBytes(cleanProtection.Memory).SequenceEqual(cleanMemory), "even no-change protection requires confirmed restoration before completion");
    var cleanRestore = Call(helper, "restore-worktree", Completion(cleanProtection, cleanPlan));
    Check(cleanRestore.Exit == 0 && cleanRestore.Body["status"]!.GetValue<string>() == "restored", "no-change protection can be restored without applying a stash");
    var repeatedCleanRestore = Call(helper, "restore-worktree", Completion(cleanProtection, cleanPlan));
    Check(repeatedCleanRestore.Exit == 0 && repeatedCleanRestore.Body["status"]!.GetValue<string>() == "restored" && Git(cleanProtection.Docs, "status", "--porcelain", "--untracked-files=all") == "" && File.ReadAllBytes(cleanProtection.Memory).SequenceEqual(cleanMemory), "confirmed restoration repeats idempotently without introducing dirt or advancing memory");
    File.WriteAllText(Path.Combine(cleanProtection.Docs, "later-user.md"), "New user work after restoration\n");
    Check(Call(helper, "finalize", Completion(cleanProtection, cleanPlan)).Exit == 2 && File.ReadAllBytes(cleanProtection.Memory).SequenceEqual(cleanMemory) && File.ReadAllText(Path.Combine(cleanProtection.Docs, "later-user.md")) == "New user work after restoration\n", "new dirt after verified restoration blocks finalization without overwriting user work");
    Console.WriteLine("PASS no-change-protection-restoration-idempotence-and-later-dirt-gate");

    var overlap = Fixture("protected-nonconflicting-overlap", false, true);
    const string overlapBase = "Source title\nLine 02\nLine 03\nLine 04\nLine 05\nLine 06\nLine 07\nSource middle\nLine 09\nLine 10\nLine 11\nLine 12\nLine 13\nLine 14\nLine 15\nSource ending\n";
    const string overlapStaged = "User staged title\nLine 02\nLine 03\nLine 04\nLine 05\nLine 06\nLine 07\nSource middle\nLine 09\nLine 10\nLine 11\nLine 12\nLine 13\nLine 14\nLine 15\nSource ending\n";
    const string overlapWorking = "User staged title\nLine 02\nLine 03\nLine 04\nLine 05\nLine 06\nLine 07\nUser unstaged middle\nLine 09\nLine 10\nLine 11\nLine 12\nLine 13\nLine 14\nLine 15\nSource ending\n";
    const string overlapOwned = "Source title\nLine 02\nLine 03\nLine 04\nLine 05\nLine 06\nLine 07\nSource middle\nLine 09\nLine 10\nLine 11\nLine 12\nLine 13\nLine 14\nLine 15\nOwned ending\n";
    const string overlapExpectedIndex = "User staged title\nLine 02\nLine 03\nLine 04\nLine 05\nLine 06\nLine 07\nSource middle\nLine 09\nLine 10\nLine 11\nLine 12\nLine 13\nLine 14\nLine 15\nOwned ending\n";
    const string overlapExpectedWorking = "User staged title\nLine 02\nLine 03\nLine 04\nLine 05\nLine 06\nLine 07\nUser unstaged middle\nLine 09\nLine 10\nLine 11\nLine 12\nLine 13\nLine 14\nLine 15\nOwned ending\n";
    File.WriteAllText(Path.Combine(overlap.Docs, "a.md"), overlapBase);
    Git(overlap.Docs, "add", "--", "a.md");
    Git(overlap.Docs, "commit", "-m", "Source with distant independent changes");
    Git(overlap.Docs, "push", "origin", "main");
    var overlapCommit = Git(overlap.Docs, "rev-parse", "HEAD");
    var overlapSource = Sources(overlap);
    History(overlap, overlapSource, 0, 100);
    var overlapMemory = File.ReadAllBytes(overlap.Memory);
    File.WriteAllText(Path.Combine(overlap.Docs, "a.md"), overlapStaged);
    Git(overlap.Docs, "add", "--", "a.md");
    File.WriteAllText(Path.Combine(overlap.Docs, "a.md"), overlapWorking);
    var overlapProtectRequest = Common(overlap);
    overlapProtectRequest["source_receipt"] = overlapSource.Body["receipt"]!.DeepClone();
    overlapProtectRequest["source_receipt_sha256"] = overlapSource.Body["receipt_sha256"]!.DeepClone();
    var overlapProtection = Call(helper, "protect-worktree", overlapProtectRequest);
    Check(overlapProtection.Exit == 0, "nonconflicting overlapping work is protected: " + overlapProtection.Body.ToJsonString());
    var overlapStash = overlapProtection.Body["stash_sha"]!.GetValue<string>();
    var overlapTopic = Topic(overlap, overlapSource, overlapCommit, "update_needed");
    var overlapPlan = Plan(overlap, new JsonArray(Candidate(overlap, overlapCommit, overlapTopic, "update_needed")), new JsonArray(new JsonObject { ["path"] = "a.md", ["content"] = overlapOwned }), overlapSource);
    File.WriteAllText(Path.Combine(overlap.Docs, "a.md"), overlapOwned);
    Git(overlap.Docs, "add", "--", "a.md");
    Git(overlap.Docs, "commit", "-m", "Own distant ending change");
    Git(overlap.Docs, "push", "origin", "main");
    var overlapRestoration = Call(helper, "restore-worktree", Completion(overlap, overlapPlan));
    Check(overlapRestoration.Exit == 0 && overlapRestoration.Body["status"]!.GetValue<string>() == "restored", "nonconflicting staged and unstaged overlap restores: " + overlapRestoration.Body.ToJsonString());
    Check(GitRun(overlap.Docs, ["show", ":a.md"]).Output == overlapExpectedIndex && File.ReadAllText(Path.Combine(overlap.Docs, "a.md")) == overlapExpectedWorking, "literal restored index and working contents combine own delivery with both prior changes");
    Check(GitRun(overlap.Docs, ["show", "HEAD:a.md"]).Output == overlapOwned && Git(overlap.Docs, "stash", "list", "--format=%H") == overlapStash && File.ReadAllBytes(overlap.Memory).SequenceEqual(overlapMemory), "the own committed page excludes prior work while its original safety backup and memory remain intact");
    var overlapRestoredBytes = File.ReadAllBytes(Path.Combine(overlap.Docs, "a.md"));
    Check(Call(helper, "restore-worktree", Completion(overlap, overlapPlan)).Exit == 0 && File.ReadAllBytes(Path.Combine(overlap.Docs, "a.md")).SequenceEqual(overlapRestoredBytes) && GitRun(overlap.Docs, ["show", ":a.md"]).Output == overlapExpectedIndex, "repeating overlapping restoration preserves both already restored states");
    Check(Call(helper, "finalize", Completion(overlap, overlapPlan)).Exit == 0, "verified overlapping prior work permits completion");
    Console.WriteLine("PASS staged-and-unstaged-nonconflicting-own-page-overlap");

    var conflict = Fixture("protected-conflicting-overlap", false, true);
    var conflictCommit = OldDatedDocsChange(conflict);
    var conflictSource = Sources(conflict);
    History(conflict, conflictSource, 0, 100);
    var conflictMemory = File.ReadAllBytes(conflict.Memory);
    File.WriteAllText(Path.Combine(conflict.Docs, "a.md"), "User conflicting staged fact\n");
    Git(conflict.Docs, "add", "--", "a.md");
    File.WriteAllText(Path.Combine(conflict.Docs, "a.md"), "User conflicting working fact\n");
    File.WriteAllBytes(Path.Combine(conflict.Docs, "conflict-backup.bin"), [0x31, 0x00, 0xfe, 0x79]);
    var conflictProtectRequest = Common(conflict);
    conflictProtectRequest["source_receipt"] = conflictSource.Body["receipt"]!.DeepClone();
    conflictProtectRequest["source_receipt_sha256"] = conflictSource.Body["receipt_sha256"]!.DeepClone();
    var conflictProtection = Call(helper, "protect-worktree", conflictProtectRequest);
    Check(conflictProtection.Exit == 0, "conflicting prior work is protected before own delivery");
    var conflictStash = conflictProtection.Body["stash_sha"]!.GetValue<string>();
    var conflictBackups = Directory.EnumerateFiles(conflict.Run, "*", SearchOption.AllDirectories)
        .Where(path => File.ReadAllBytes(path).SequenceEqual(new byte[] { 0x31, 0x00, 0xfe, 0x79 })).ToArray();
    Check(conflictBackups.Length > 0, "the literal original untracked contents have protected run evidence");
    var conflictTopic = Topic(conflict, conflictSource, conflictCommit, "update_needed");
    var conflictPlan = Plan(conflict, new JsonArray(Candidate(conflict, conflictCommit, conflictTopic, "update_needed")), new JsonArray(new JsonObject { ["path"] = "a.md", ["content"] = "Owned incompatible fact\n" }), conflictSource);
    File.WriteAllText(Path.Combine(conflict.Docs, "a.md"), "Owned incompatible fact\n");
    Git(conflict.Docs, "add", "--", "a.md");
    Git(conflict.Docs, "commit", "-m", "Own incompatible same-line change");
    Git(conflict.Docs, "push", "origin", "main");
    var conflictRestore = Call(helper, "restore-worktree", Completion(conflict, conflictPlan));
    Check(conflictRestore.Exit == 2 && File.ReadAllBytes(conflict.Memory).SequenceEqual(conflictMemory), "a conflicting restoration blocks without advancing the official memory");
    Check(Git(conflict.Docs, "stash", "list", "--format=%H") == conflictStash && GitRun(conflict.Docs, ["show", conflictStash + "^2:a.md"]).Output == "User conflicting staged fact\n" && GitRun(conflict.Docs, ["show", conflictStash + ":a.md"]).Output == "User conflicting working fact\n", "the exact conflicting stash preserves both literal prior states");
    Check(conflictBackups.All(path => File.Exists(path) && File.ReadAllBytes(path).SequenceEqual(new byte[] { 0x31, 0x00, 0xfe, 0x79 }) && !OperatingSystem.IsWindows() && File.GetUnixFileMode(path) == (UnixFileMode.UserRead | UnixFileMode.UserWrite)) && File.Exists(Path.Combine(conflict.Run, "delivery", "worktree-protection.json")), "conflicting restoration retains protected original backup bytes and recovery journal");
    Check(File.ReadAllText(Path.Combine(conflict.Docs, "a.md")) == "Owned incompatible fact\n" && GitRun(conflict.Docs, ["show", ":a.md"]).Output == "Owned incompatible fact\n", "a known merge conflict is detected before overwriting the delivered working file or index");
    Check(Call(helper, "finalize", Completion(conflict, conflictPlan)).Exit == 2 && File.ReadAllBytes(conflict.Memory).SequenceEqual(conflictMemory), "a retained conflicting backup never permits completion");
    Console.WriteLine("PASS conflicting-overlap-retains-stash-snapshots-memory-and-own-content");

    var staleCleanup = Fixture("protected-stale-source-cleanup", false, true, withPriorWork: true);
    var staleCleanupSource = Sources(staleCleanup);
    History(staleCleanup, staleCleanupSource, 0, 100);
    var staleCleanupMemory = File.ReadAllBytes(staleCleanup.Memory);
    File.WriteAllText(Path.Combine(staleCleanup.Docs, priorPath), "Protected staged cleanup work\n");
    Git(staleCleanup.Docs, "add", "--", priorPath);
    var staleCleanupRequest = Common(staleCleanup);
    staleCleanupRequest["source_receipt"] = staleCleanupSource.Body["receipt"]!.DeepClone();
    staleCleanupRequest["source_receipt_sha256"] = staleCleanupSource.Body["receipt_sha256"]!.DeepClone();
    var staleCleanupProtection = Call(helper, "protect-worktree", staleCleanupRequest);
    Check(staleCleanupProtection.Exit == 0, "cleanup fixture prior work is protected");
    var staleCleanupStash = staleCleanupProtection.Body["stash_sha"]!.GetValue<string>();
    File.WriteAllText(Path.Combine(staleCleanup.Docs, "a.md"), "Later foreign stash content\n");
    Git(staleCleanup.Docs, "stash", "push", "-m", "Later foreign stash", "--", "a.md");
    var laterForeignStash = Git(staleCleanup.Docs, "rev-parse", "refs/stash");
    Git(staleCleanup.Backend, "commit", "--allow-empty", "-m", "Changed code pin while documentation work is protected");
    Git(staleCleanup.Backend, "push", "origin", "develop");
    var staleCleanupRestoration = Call(helper, "restore-worktree", Common(staleCleanup));
    Check(staleCleanupRestoration.Exit == 0 && staleCleanupRestoration.Body["status"]!.GetValue<string>() == "restored", "narrowly owned cleanup remains available after source pins change, without a delivery plan: " + staleCleanupRestoration.Body.ToJsonString());
    Check(File.ReadAllText(Path.Combine(staleCleanup.Docs, priorPath)) == "Protected staged cleanup work\n" && GitRun(staleCleanup.Docs, ["show", ":" + priorPath]).Output == "Protected staged cleanup work\n" && File.ReadAllText(Path.Combine(staleCleanup.Docs, "a.md")) == "Original fact\n", "cleanup applies only its exact owned stash, preserving the staged prior work");
    Check(Git(staleCleanup.Docs, "stash", "list", "--format=%H").Split('\n').SequenceEqual(new[] { laterForeignStash, staleCleanupStash }) && File.ReadAllBytes(staleCleanup.Memory).SequenceEqual(staleCleanupMemory), "a newer foreign stash and the owned backup remain untouched while cleanup leaves memory unchanged");
    Console.WriteLine("PASS changed-source-cleanup-without-plan-and-newer-foreign-stash");

    var guardedCleanup = Fixture("protected-foreign-cleanup-guards", false, true, withPriorWork: true);
    var guardedSource = Sources(guardedCleanup);
    History(guardedCleanup, guardedSource, 0, 100);
    var guardedMemory = File.ReadAllBytes(guardedCleanup.Memory);
    File.WriteAllText(Path.Combine(guardedCleanup.Docs, priorPath), "Protected prior working bytes\n");
    File.WriteAllBytes(Path.Combine(guardedCleanup.Docs, "prior-binary.bin"), [0x00, 0xf1, 0x55]);
    var guardedProtectRequest = Common(guardedCleanup);
    guardedProtectRequest["source_receipt"] = guardedSource.Body["receipt"]!.DeepClone();
    guardedProtectRequest["source_receipt_sha256"] = guardedSource.Body["receipt_sha256"]!.DeepClone();
    var guardedProtection = Call(helper, "protect-worktree", guardedProtectRequest);
    Check(guardedProtection.Exit == 0, "foreign-state guard fixture is protected");
    var guardedStash = guardedProtection.Body["stash_sha"]!.GetValue<string>();
    File.WriteAllBytes(Path.Combine(guardedCleanup.Docs, "prior-binary.bin"), [0x20, 0x21, 0x22]);
    Check(Call(helper, "restore-worktree", Common(guardedCleanup)).Exit == 2 && File.ReadAllBytes(Path.Combine(guardedCleanup.Docs, "prior-binary.bin")).SequenceEqual(new byte[] { 0x20, 0x21, 0x22 }) && File.ReadAllText(Path.Combine(guardedCleanup.Docs, priorPath)) == "Baseline user work\n", "an untracked-path collision is preserved without restoring over foreign contents");
    File.Delete(Path.Combine(guardedCleanup.Docs, "prior-binary.bin"));
    File.WriteAllText(Path.Combine(guardedCleanup.Docs, "new-foreign.md"), "New foreign untracked work\n");
    Check(Call(helper, "restore-worktree", Common(guardedCleanup)).Exit == 2 && File.ReadAllText(Path.Combine(guardedCleanup.Docs, "new-foreign.md")) == "New foreign untracked work\n" && !File.Exists(Path.Combine(guardedCleanup.Docs, "prior-binary.bin")) && File.ReadAllText(Path.Combine(guardedCleanup.Docs, priorPath)) == "Baseline user work\n", "new unrelated untracked work is retained and blocks restoration before protected files are introduced");
    File.Delete(Path.Combine(guardedCleanup.Docs, "new-foreign.md"));
    File.WriteAllText(Path.Combine(guardedCleanup.Docs, priorPath), "New foreign indexed work\n");
    Git(guardedCleanup.Docs, "add", "--", priorPath);
    Check(Call(helper, "restore-worktree", Common(guardedCleanup)).Exit == 2 && GitRun(guardedCleanup.Docs, ["show", ":" + priorPath]).Output == "New foreign indexed work\n" && File.ReadAllText(Path.Combine(guardedCleanup.Docs, priorPath)) == "New foreign indexed work\n", "foreign index dirt remains exact and is never overwritten by owned cleanup");
    Check(Git(guardedCleanup.Docs, "stash", "list", "--format=%H") == guardedStash && GitRun(guardedCleanup.Docs, ["show", guardedStash + ":" + priorPath]).Output == "Protected prior working bytes\n" && File.ReadAllBytes(guardedCleanup.Memory).SequenceEqual(guardedMemory), "all foreign-state refusals preserve the exact owned backup and original memory");
    Console.WriteLine("PASS untracked-collision-new-untracked-and-foreign-index-restoration-guards");
    if (Environment.GetEnvironmentVariable("NCG_WIKI_ONLY_STASH_BOUNDARIES") == "1")
    {
        Console.WriteLine("Fixture: " + root);
        return 0;
    }
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
(int Exit, JsonObject Body) Topic(FixtureState f, (int Exit, JsonObject Body) source, string commit, string decision, string wikiPath = "a.md") { var payload = source.Body["payload"]!; var request = f.ReviewRequest.DeepClone().AsObject(); request["run_directory"] = f.Run; request["topic_id"] = "docs-topic"; request["source_pins"] = payload["source_pins"]!.DeepClone(); request["documentation_pin"] = payload["documentation_pin"]!.DeepClone(); request["session_ids"] = new JsonArray(); request["git_candidates"] = new JsonArray(new JsonObject { ["repository"] = f.Docs, ["sha"] = commit }); request["wiki_files"] = new JsonArray(Path.Combine(f.Docs, wikiPath)); request["decision"] = decision; request["comparison"] = "Compared fixed authoritative Git change with current pinned main page."; var result = Call(review, "record-topic", request); Check(result.Exit == 0, "topic: " + result.Body.ToJsonString()); return result; }
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

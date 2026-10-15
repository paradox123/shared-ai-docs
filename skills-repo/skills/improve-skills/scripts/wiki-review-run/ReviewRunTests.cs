using System.Diagnostics;
using System.Text.Json.Nodes;

if(OperatingSystem.IsWindows()) return 2;
var helper = Path.GetFullPath("skills-repo/skills/improve-skills/scripts/wiki-review-run/ReviewRun.cs");
var scripts = Path.GetDirectoryName(Path.GetDirectoryName(helper))!;
var root = Path.Combine(Path.GetTempPath(), "wiki-review-test-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(root);
try
{
    var home = Path.Combine(root, "codex-home");
    var repo = Path.Combine(root, "ncg");
    Directory.CreateDirectory(Path.Combine(repo, ".git"));
    var day = Path.Combine(home, "sessions", "2026", "10", "12");
    Directory.CreateDirectory(day);
    var automation=Path.Combine(root,"automation"); Directory.CreateDirectory(automation);
    var definition = Path.Combine(automation, "automation.toml");
    var memory = Path.Combine(automation, "memory.md");
    File.WriteAllText(definition, "id = \"keep-ncg-wiki-current\"\n");
    File.WriteAllText(memory, "Processed window end: 2026-10-12T06:00:00Z\n");
    var resolver=Path.Combine(root,"resolver.py"); File.Copy(Path.Combine(scripts,"resolve_codex_sessions.py"),resolver);
    var stamp = "2026-10-12T07:00:00Z";
    File.WriteAllText(Path.Combine(home, "session_index.jsonl"),
        new JsonObject { ["id"] = "session-1", ["updated_at"] = stamp }.ToJsonString() + "\n");
    var records = new[] {
        new JsonObject { ["timestamp"]=stamp,["type"]="session_meta",["payload"]=new JsonObject { ["id"]="session-1",["cwd"]=repo } },
        new JsonObject { ["timestamp"]=stamp,["type"]="response_item",["payload"]=new JsonObject { ["type"]="message",["role"]="user",["content"]=new JsonArray(new JsonObject { ["type"]="input_text",["text"]="Review NCG deployment docs" }) } },
        new JsonObject { ["timestamp"]=stamp,["type"]="response_item",["payload"]=new JsonObject { ["type"]="message",["role"]="assistant",["phase"]="final",["content"]=new JsonArray(new JsonObject { ["type"]="output_text",["text"]="NCG review completed" }) } }
    };
    File.WriteAllText(Path.Combine(day, "rollout-session-1.jsonl"), string.Join("\n", records.Select(x=>x.ToJsonString())) + "\n");
    var request = new JsonObject {
        ["store"]=Path.Combine(root,"store"),["automation_id"]="keep-ncg-wiki-current",
        ["definition"]=definition,["memory"]=memory,["resolver"]=resolver,
        ["python"]="python3",["codex_home"]=home,["exclude_session_id"]="maintenance-session",["max_sessions"]=500,["prompt_last_run"]="2026-10-12T06:00:00Z"
    };
    var first = Invoke("capture", request);
    Check(first.Exit == 0 && first.Body["status"]?.GetValue<string>() == "captured", "capture emits a protected persisted selection");
    var directory = first.Body["run_directory"]!.GetValue<string>();
    // A changed live index must not be read after an interruption.
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"), "deliberately invalid later index\n");
    var resumed = Invoke("capture", request);
    Check(resumed.Exit==0 && resumed.Body["status"]?.GetValue<string>()=="resumed" && resumed.Body["run_directory"]?.GetValue<string>()==directory && resumed.Body["manifest_sha256"]?.GetValue<string>()==first.Body["manifest_sha256"]?.GetValue<string>(), "separate process resumes the exact snapshot after live index changes");
    Console.WriteLine("PASS capture-and-process-restart");
    request["prompt_last_run"]="2026-10-12T09:00:00Z";
    var ignoredScheduler=Invoke("capture",request);
    Check(ignoredScheduler.Exit==0 && ignoredScheduler.Body["status"]?.GetValue<string>()=="resumed" && ignoredScheduler.Body["run_directory"]?.GetValue<string>()==directory,"new scheduler LastRun is ignored for adoption when Processed is authoritative");
    Console.WriteLine("PASS ignored-scheduler-boundary-resumes-processed-selection");
    var scope=new JsonObject { ["cwd_roots"]=new JsonArray(repo),["worktree_tails"]=new JsonArray() };
    var selection=new JsonObject { ["run_directory"]=directory,["extractor"]=Path.Combine(scripts,"extract_codex_session_evidence.py"),["python"]="python3",["scope"]=scope };
    var pageRequest=selection.DeepClone().AsObject(); pageRequest["offset"]=0; pageRequest["limit"]=1;
    var page=Invoke("page",pageRequest);
    Check(page.Exit==0 && page.Body["status"]?.GetValue<string>()=="page_captured","page captures extractor output bound to the immutable manifest and scope");
    var proof=Invoke("verify-pages",selection);
    Check(proof.Exit==0 && proof.Body["status"]?.GetValue<string>()=="complete" && proof.Body["eligible_sessions"]?.GetValue<int>()==1,"complete same-manifest summary chain receives a versioned receipt");
    Console.WriteLine("PASS complete-extraction-receipt");
    var wiki=Path.Combine(root,"wiki.md"); File.WriteAllText(wiki,"NCG deployment evidence\n");
    var pinKey=repo+"|refs/remotes/origin/develop";
    var topic=selection.DeepClone().AsObject(); topic["topic_id"]="deployment"; topic["source_pins"]=new JsonObject { [pinKey]=new string('a',40) }; topic["session_ids"]=new JsonArray("session-1"); topic["git_candidates"]=new JsonArray(); topic["wiki_files"]=new JsonArray(wiki); topic["decision"]="update_needed"; topic["comparison"]="An explicit documentation update is still required.";
    var recorded=Invoke("record-topic",topic);
    Check(recorded.Exit==0 && recorded.Body["status"]?.GetValue<string>()=="pending_delivery","cached update-needed comparison remains pending delivery");
    var reusable=Invoke("resume-topics",topic);
    Check(reusable.Exit==0 && reusable.Body["status"]?.GetValue<string>()=="reusable" && reusable.Body["delivery_state"]?.GetValue<string>()=="pending_delivery","same current pins and wiki hashes can reuse the provisional comparison");
    Check(Invoke("capture",request).Body["status"]?.GetValue<string>()=="resumed","captured run resumes before repeating its existing page chain");
    var repeatedPage=Invoke("page",pageRequest); var repeatedProof=Invoke("verify-pages",selection); var repeatedTopic=Invoke("resume-topics",topic);
    Check(repeatedProof.Exit==0 && repeatedProof.Body["receipt_sha256"]?.GetValue<string>()==proof.Body["receipt_sha256"]?.GetValue<string>() && repeatedTopic.Body["status"]?.GetValue<string>()=="reusable","identical bounded pages after process restart preserve completeness and reusable topic proof");
    Check(repeatedPage.Body["status"]?.GetValue<string>()=="page_reused" && repeatedPage.Body["output"]?.GetValue<string>()==page.Body["output"]?.GetValue<string>() && repeatedPage.Body["page_receipt"]?.GetValue<string>()==page.Body["page_receipt"]?.GetValue<string>(),"page reuse returns the exact successful output and pointer paths");
    Console.WriteLine("PASS identical-page-chain-resumes-with-stable-topic-proof");
    var largerPageRequest=pageRequest.DeepClone().AsObject(); largerPageRequest["max_total_chars"]=30000;
    var changedBoundPage=Invoke("page",largerPageRequest);
    Check(changedBoundPage.Exit==0 && changedBoundPage.Body["status"]?.GetValue<string>()=="page_captured" && changedBoundPage.Body["output"]?.GetValue<string>()!=page.Body["output"]?.GetValue<string>(),"a changed character bound publishes a distinct page output");
    Check(Invoke("resume-topics",topic).Exit==2,"changed page bounds invalidate the previous completeness proof until it is reverified");
    var changedBoundProof=Invoke("verify-pages",selection);
    Check(changedBoundProof.Exit==0 && changedBoundProof.Body["receipt_sha256"]?.GetValue<string>()!=proof.Body["receipt_sha256"]?.GetValue<string>() && Invoke("resume-topics",topic).Body["status"]?.GetValue<string>()=="stale","new bounded page proof makes the earlier topic comparison stale");
    Check(Invoke("record-topic",topic).Exit==0,"a newly reviewed topic can be recorded against the new bounded proof");
    var pageRollout=Path.Combine(day,"rollout-session-1.jsonl"); var unchangedRollout=File.ReadAllBytes(pageRollout);
    File.WriteAllText(pageRollout,File.ReadAllText(pageRollout).Replace("Review NCG deployment docs","Changed NCG deployment docs"));
    Check(Invoke("page",largerPageRequest).Exit==2,"same-bound page refuses changed advertised source bytes"); File.WriteAllBytes(pageRollout,unchangedRollout);
    var storedOutput=changedBoundPage.Body["output"]!.GetValue<string>(); var unchangedOutput=File.ReadAllBytes(storedOutput); File.AppendAllText(storedOutput,"\n");
    Check(Invoke("page",largerPageRequest).Exit==2,"same-bound page refuses corrupted stored output instead of silently extracting again"); File.WriteAllBytes(storedOutput,unchangedOutput);
    var restoredPage=Invoke("page",largerPageRequest);
    Check(restoredPage.Body["status"]?.GetValue<string>()=="page_reused" && restoredPage.Body["output"]?.GetValue<string>()==storedOutput && Invoke("resume-topics",topic).Body["status"]?.GetValue<string>()=="reusable","restored exact evidence retains its pointer and newly reviewed topic");
    Console.WriteLine("PASS changed-page-bounds-and-corruption-block-reuse");
    File.AppendAllText(wiki,"Changed current wiki context\n");
    var changedWiki=Invoke("resume-topics",topic);
    Check(changedWiki.Exit==0 && changedWiki.Body["status"]?.GetValue<string>()=="stale","changed wiki file makes the cached topic stale");
    File.WriteAllText(wiki,"NCG deployment evidence\n");
    topic["source_pins"]![pinKey]=new string('b',40);
    var changedSource=Invoke("resume-topics",topic);
    Check(changedSource.Exit==0 && changedSource.Body["status"]?.GetValue<string>()=="stale","changed source pin makes the cached topic stale");
    Console.WriteLine("PASS provisional-topic-resumption-and-staleness");
    topic["source_pins"]![pinKey]=new string('a',40);
    var rollout=Path.Combine(day,"rollout-session-1.jsonl"); var originalRollout=File.ReadAllBytes(rollout);
    File.AppendAllText(rollout,new JsonObject { ["timestamp"]="2026-10-12T09:00:00Z",["type"]="event_msg",["payload"]=new JsonObject { ["type"]="task_started" } }.ToJsonString()+"\n");
    Check(Invoke("capture",request).Exit==0,"later live rollout and index changes keep the captured selection");
    var appendedTopic=Invoke("resume-topics",topic); Check(appendedTopic.Exit==0 && appendedTopic.Body["status"]?.GetValue<string>()=="reusable","appending after the advertised range preserves cached evidence");
    File.WriteAllText(rollout,File.ReadAllText(rollout).Replace("Review NCG deployment docs","Mutate NCG deployment docs"));
    Check(Invoke("resume-topics",topic).Exit==2,"mutating an advertised evidence line blocks reuse");
    File.WriteAllBytes(rollout,originalRollout);
    Console.WriteLine("PASS advertised-range-pins-allow-append-and-reject-mutation");
    var missingId="deleted-carried-session";
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),new JsonObject { ["id"]="session-1",["updated_at"]=stamp }.ToJsonString()+"\n");
    File.WriteAllText(memory,"Processed window end: 2026-10-12T06:00:00Z\nCarry-forward sessions: [{\"id\":\""+missingId+"\",\"line_count\":4,\"last_activity_at\":\"2026-10-11T07:00:00Z\"}]\n");
    request["store"]=Path.Combine(root,"carry-store"); request["approved_missing_carry_ids"]=new JsonArray(missingId);
    var approvedCarry=Invoke("capture",request);
    Check(approvedCarry.Exit==0 && approvedCarry.Body["resolver_exit"]?.GetValue<int>()==2 && approvedCarry.Body["extraction_allowed"]?.GetValue<bool>()==true,"exact approved deleted carried row is captured with raw unsafe exit and explicit exception");
    Console.WriteLine("PASS exact-approved-missing-carry-compatibility");
    var missingWindowId="deleted-window-session";
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),new JsonObject { ["id"]="session-1",["updated_at"]=stamp }.ToJsonString()+"\n"+new JsonObject { ["id"]=missingWindowId,["updated_at"]=stamp }.ToJsonString()+"\n");
    var ignoreRequest=request.DeepClone().AsObject(); ignoreRequest["store"]=Path.Combine(root,"ignore-missing-store"); ignoreRequest.Remove("approved_missing_carry_ids"); ignoreRequest["missing_session_policy"]="ignore";
    var ignoredMissing=Invoke("capture",ignoreRequest);
    Check(ignoredMissing.Exit==0 && ignoredMissing.Body["extraction_allowed"]?.GetValue<bool>()==true && ignoredMissing.Body["resolver_exit"]?.GetValue<int>()==2 && ignoredMissing.Body["resolver_safe_to_persist"]?.GetValue<bool>()==false,"ignore policy admits missing window and carry sessions without per-ID approval while preserving raw failure");
    var ignoredIds=ignoredMissing.Body["ignored_missing_session_ids"]!.AsArray().Select(x=>x!.GetValue<string>()).ToHashSet(StringComparer.Ordinal);
    Check(ignoredIds.SetEquals(new[]{missingId,missingWindowId}),"capture reports exactly the ignored missing sessions");
    Console.WriteLine("PASS ignore-missing-window-and-carry");
    var strictMissingRequest=ignoreRequest.DeepClone().AsObject(); strictMissingRequest["store"]=Path.Combine(root,"strict-missing-store"); strictMissingRequest.Remove("missing_session_policy");
    var strictMissing=Invoke("capture",strictMissingRequest);
    Check(strictMissing.Exit==2 && strictMissing.Body["reason"]?.GetValue<string>()=="resolver_unsafe_capture","missing sessions remain blocked when the caller omits the opt-in policy and legacy allowlist");
    Console.WriteLine("PASS missing-session-policy-default-remains-strict");
    var changedMissingPolicy=ignoreRequest.DeepClone().AsObject(); changedMissingPolicy["missing_session_policy"]="block";
    var changedMissingResume=Invoke("capture",changedMissingPolicy);
    Check(changedMissingResume.Exit==2 && changedMissingResume.Body["reason"]?.GetValue<string>()=="active_inputs_changed_explicit_invalidation_required","changing a captured missing-session policy cannot silently adopt its previous ignore decision");
    var missingLiveIndex=File.ReadAllText(Path.Combine(home,"session_index.jsonl"));
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),"invalid live index after ignore capture\n");
    var ignoreResume=Invoke("capture",ignoreRequest);
    Check(ignoreResume.Exit==0 && ignoreResume.Body["status"]?.GetValue<string>()=="resumed" && ignoreResume.Body["run_directory"]?.GetValue<string>()==ignoredMissing.Body["run_directory"]?.GetValue<string>() && ignoreResume.Body["manifest_sha256"]?.GetValue<string>()==ignoredMissing.Body["manifest_sha256"]?.GetValue<string>() && ignoreResume.Body["index_sha256"]?.GetValue<string>()==ignoredMissing.Body["index_sha256"]?.GetValue<string>(),"unchanged ignore policy resumes the exact captured snapshot despite a changed live index");
    Check(ignoreResume.Body["ignored_missing_session_ids"]!.AsArray().Select(x=>x!.GetValue<string>()).ToHashSet(StringComparer.Ordinal).SetEquals(ignoredIds),"snapshot resumption preserves the originally validated ignored IDs");
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),missingLiveIndex);
    Console.WriteLine("PASS ignore-policy-bound-resume-preserves-snapshot");
    var invalidMissingPolicy=ignoreRequest.DeepClone().AsObject(); invalidMissingPolicy["store"]=Path.Combine(root,"invalid-missing-policy-store"); invalidMissingPolicy["missing_session_policy"]="discard";
    var invalidMissingCapture=Invoke("capture",invalidMissingPolicy);
    Check(invalidMissingCapture.Exit==2 && invalidMissingCapture.Body["reason"]?.GetValue<string>()=="missing_session_policy_must_be_block_or_ignore" && !Directory.Exists(invalidMissingPolicy["store"]!.GetValue<string>()),"an unsupported missing-session policy blocks before creating a capture");
    Console.WriteLine("PASS invalid-missing-session-policy-blocks-capture");
    foreach(var badHistory in new[]{("malformed-json","{not-json\n"),("unknown-timestamp",new JsonObject { ["type"]="event_msg",["payload"]=new JsonObject { ["type"]="task_started" } }.ToJsonString()+"\n")}) {
        File.WriteAllText(rollout,System.Text.Encoding.UTF8.GetString(originalRollout)+badHistory.Item2);
        var badHistoryRequest=ignoreRequest.DeepClone().AsObject(); badHistoryRequest["store"]=Path.Combine(root,"ignore-with-"+badHistory.Item1);
        var badHistoryCapture=Invoke("capture",badHistoryRequest);
        Check(badHistoryCapture.Exit==2 && badHistoryCapture.Body["reason"]?.GetValue<string>()=="resolver_unsafe_capture" && badHistoryCapture.Body["resolver_exit"]?.GetValue<int>()==2,"ignore must not admit a resolved "+badHistory.Item1+" history alongside missing sessions");
        File.WriteAllBytes(rollout,originalRollout);
    }
    Console.WriteLine("PASS ignore-missing-does-not-admit-malformed-stored-history");
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),new JsonObject { ["id"]=missingWindowId,["updated_at"]=stamp }.ToJsonString()+"\n");
    var onlyMissingRequest=ignoreRequest.DeepClone().AsObject(); onlyMissingRequest["store"]=Path.Combine(root,"only-missing-store");
    var onlyMissingCapture=Invoke("capture",onlyMissingRequest);
    Check(onlyMissingCapture.Exit==0 && onlyMissingCapture.Body["ignored_missing_session_ids"]!.AsArray().Select(x=>x!.GetValue<string>()).ToHashSet(StringComparer.Ordinal).SetEquals(new[]{missingId,missingWindowId}),"an all-missing capture admits only its validated window and carry IDs");
    var onlyMissingSelection=selection.DeepClone().AsObject(); onlyMissingSelection["run_directory"]=onlyMissingCapture.Body["run_directory"]!.DeepClone();
    Check(Invoke("verify-pages",onlyMissingSelection).Exit==2,"ignoring all missing sessions does not manufacture an empty-scope completeness receipt");
    var onlyMissingPage=onlyMissingSelection.DeepClone().AsObject(); onlyMissingPage["offset"]=0; onlyMissingPage["limit"]=1;
    Check(Invoke("page",onlyMissingPage).Exit==0,"all-missing scope still captures a real offset-zero extraction page");
    var onlyMissingProof=Invoke("verify-pages",onlyMissingSelection);
    Check(onlyMissingProof.Exit==0 && onlyMissingProof.Body["status"]?.GetValue<string>()=="complete" && onlyMissingProof.Body["eligible_sessions"]?.GetValue<int>()==0,"the real empty page proves a complete zero-eligible scope");
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),missingLiveIndex);
    Console.WriteLine("PASS ignore-only-missing-requires-real-empty-scope-page");
    // The production resolver is an external Python CLI. These isolated response
    // fixtures keep its process interface while C# owns the guard scenarios.
    var ignoredManifest=JsonNode.Parse(File.ReadAllText(ignoredMissing.Body["manifest"]!.GetValue<string>()))!.AsObject();
    var resolverGuards=new (string Name,int Exit,Action<JsonObject> Mutate)[] {
        ("missing-with-safe-zero-exit",0,manifest=>manifest["window"]!["safe_to_persist"]=true),
        ("missing-with-safe-two-exit",2,manifest=>manifest["window"]!["safe_to_persist"]=true),
        ("absent-missing-diagnostic",2,manifest=>{
            var diagnostics=manifest["diagnostics"]!.AsArray();
            for(var n=diagnostics.Count-1;n>=0;n--) if(diagnostics[n]?["code"]?.GetValue<string>()=="missing_rollout") diagnostics.RemoveAt(n);
        }),
        ("wrong-missing-diagnostic-id",2,manifest=>manifest["diagnostics"]!.AsArray().First(x=>x?["code"]?.GetValue<string>()=="missing_rollout")!["session_id"]="unselected-session"),
        ("missing-with-storage-path",2,manifest=>manifest["sessions"]!.AsArray().First(x=>x?["status"]?.GetValue<string>()=="missing")!["path"]=rollout),
        ("missing-with-storage-meta",2,manifest=>manifest["sessions"]!.AsArray().First(x=>x?["status"]?.GetValue<string>()=="missing")!["meta"]=new JsonObject { ["cwd"]=repo }),
        ("missing-with-rollout-window",2,manifest=>manifest["sessions"]!.AsArray().First(x=>x?["status"]?.GetValue<string>()=="missing")!["rollout_window"]=new JsonObject { ["state"]="complete" }),
        ("unrelated-unsafe-diagnostic",2,manifest=>manifest["diagnostics"]!.AsArray().Add(new JsonObject { ["code"]="unsafe_rollout_window",["session_id"]="session-1",["state"]="unknown" }))
    };
    foreach(var guard in resolverGuards) {
        var guardManifest=ignoredManifest.DeepClone().AsObject(); guard.Mutate(guardManifest);
        var guardResolver=Path.Combine(root,"resolver-guard-"+guard.Name+".py");
        File.WriteAllText(guardResolver,"import hashlib,json,pathlib,sys\n"+
            "data=(pathlib.Path(sys.argv[sys.argv.index('--codex-home')+1])/'session_index.jsonl').read_bytes()\n"+
            "pathlib.Path(sys.argv[sys.argv.index('--save-index-snapshot')+1]).write_bytes(data)\n"+
            "manifest=json.loads("+JsonValue.Create(guardManifest.ToJsonString())!.ToJsonString()+")\n"+
            "manifest['snapshot']['sha256']=hashlib.sha256(data).hexdigest()\nprint(json.dumps(manifest))\nsys.exit("+guard.Exit+")\n");
        var guardRequest=ignoreRequest.DeepClone().AsObject(); guardRequest["store"]=Path.Combine(root,"resolver-guard-store-"+guard.Name); guardRequest["resolver"]=guardResolver;
        var guarded=Invoke("capture",guardRequest);
        Check(guarded.Exit==2 && guarded.Body["reason"]?.GetValue<string>()=="resolver_unsafe_capture" && guarded.Body["resolver_exit"]?.GetValue<int>()==guard.Exit,"ignore rejects the external resolver's "+guard.Name+" response without treating missing storage as a blanket exception");
    }
    Console.WriteLine("PASS ignore-missing-rejects-contradictory-resolver-responses");
    File.WriteAllText(memory,"Processed window end: 2026-10-12T06:00:00Z\n");
    var cloneRecords=records.Select(x=>x.DeepClone().AsObject()).ToList(); cloneRecords[0]["payload"]!["id"]="session-clone";
    cloneRecords.Insert(1,new JsonObject { ["timestamp"]=stamp,["type"]="session_meta",["payload"]=new JsonObject { ["id"]="imported-session",["cwd"]=repo } });
    File.WriteAllText(Path.Combine(day,"rollout-session-clone.jsonl"),string.Join("\n",cloneRecords.Select(x=>x.ToJsonString()))+"\n");
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),new JsonObject { ["id"]="session-clone",["updated_at"]=stamp }.ToJsonString()+"\n");
    request["store"]=Path.Combine(root,"clone-store"); request.Remove("approved_missing_carry_ids");
    var capturedClone=Invoke("capture",request); Check(capturedClone.Exit==0,"embedded-history capture remains inspectable");
    var cloneSelection=selection.DeepClone().AsObject(); cloneSelection["run_directory"]=capturedClone.Body["run_directory"]!.DeepClone();
    var clonePage=cloneSelection.DeepClone().AsObject(); clonePage["offset"]=0; clonePage["limit"]=1; Invoke("page",clonePage);
    var unresolvedClone=Invoke("verify-pages",cloneSelection); Check(unresolvedClone.Exit==2 && unresolvedClone.Body["reason"]?.GetValue<string>()=="unresolved_manual_clone_session-clone","manual record blocks terminal page proof");
    var suffix=cloneSelection.DeepClone().AsObject(); suffix["session_id"]="session-clone"; suffix["kind"]="reviewed_suffix"; suffix["suffix_start"]=3; suffix["reason"]="Boundary map reviewed: imported metadata ends before the new substantive user turn on line3.";
    var resolvedClone=Invoke("resolve-clone",suffix);
    Check(resolvedClone.Exit==0 && resolvedClone.Body["status"]?.GetValue<string>()=="clone_resolved","real exact suffix output provides a manifest-bound resolution");
    var completeClone=Invoke("verify-pages",cloneSelection); Check(completeClone.Exit==0 && completeClone.Body["status"]?.GetValue<string>()=="complete","matching suffix receipt clears exactly the manual clone");
    Console.WriteLine("PASS bound-clone-suffix-resolution");
    var cloneTopic=cloneSelection.DeepClone().AsObject(); cloneTopic["topic_id"]="clone-review"; cloneTopic["source_pins"]=new JsonObject { [pinKey]=new string('a',40) }; cloneTopic["session_ids"]=new JsonArray("session-clone"); cloneTopic["git_candidates"]=new JsonArray(); cloneTopic["wiki_files"]=new JsonArray(wiki); cloneTopic["decision"]="update_needed"; cloneTopic["comparison"]="The reviewed substantive clone suffix requires a pending documentation update.";
    Check(Invoke("record-topic",cloneTopic).Exit==0 && Invoke("capture",request).Body["status"]?.GetValue<string>()=="resumed","topic with a valid clone resolution is captured for process resumption");
    var replayedClonePage=Invoke("page",clonePage); var replayedCloneProof=Invoke("verify-pages",cloneSelection);
    Check(replayedClonePage.Body["status"]?.GetValue<string>()=="page_reused" && replayedCloneProof.Body["receipt_sha256"]?.GetValue<string>()==completeClone.Body["receipt_sha256"]?.GetValue<string>() && Invoke("resume-topics",cloneTopic).Body["status"]?.GetValue<string>()=="reusable","identical clone page replay validates existing resolution identity without regenerating it or staling the topic");
    Console.WriteLine("PASS page-replay-preserves-valid-clone-and-topic-proof");
    cloneRecords.Insert(3,new JsonObject { ["timestamp"]=stamp,["type"]="event_msg",["payload"]=new JsonObject { ["type"]="task_complete" } });
    File.WriteAllText(Path.Combine(day,"rollout-session-clone.jsonl"),string.Join("\n",cloneRecords.Select(x=>x.ToJsonString()))+"\n"); request["store"]=Path.Combine(root,"late-boundary-store");
    var lateCapture=Invoke("capture",request); Check(lateCapture.Exit==0,"new-user plus late task-complete fixture captures safely");
    var lateSelection=cloneSelection.DeepClone().AsObject(); lateSelection["run_directory"]=lateCapture.Body["run_directory"]!.DeepClone();
    var lateDisposition=lateSelection.DeepClone().AsObject(); lateDisposition["session_id"]="session-clone"; lateDisposition["kind"]="clone_only"; lateDisposition["reviewed_boundary_line"]=4; lateDisposition["reason"]="Explicit caller claim must not hide the genuine new substantive user line3.";
    var hiddenTurn=Invoke("resolve-clone",lateDisposition); Check(hiddenTurn.Exit==2,"a late completion marker cannot prove clone-only when a substantive user turn precedes it");
    Console.WriteLine("PASS clone-only-cannot-hide-new-user-before-completion");
    cloneRecords.RemoveAt(2);
    File.WriteAllText(Path.Combine(day,"rollout-session-clone.jsonl"),string.Join("\n",cloneRecords.Select(x=>x.ToJsonString()))+"\n"); request["store"]=Path.Combine(root,"zero-user-clone-store");
    var zeroUserCapture=Invoke("capture",request); Check(zeroUserCapture.Exit==0,"zero-substantive clone captures safely");
    var zeroUserSelection=cloneSelection.DeepClone().AsObject(); zeroUserSelection["run_directory"]=zeroUserCapture.Body["run_directory"]!.DeepClone();
    var zeroUserPage=zeroUserSelection.DeepClone().AsObject(); zeroUserPage["offset"]=0; zeroUserPage["limit"]=1; Invoke("page",zeroUserPage);
    var zeroUserDisposition=zeroUserSelection.DeepClone().AsObject(); zeroUserDisposition["session_id"]="session-clone"; zeroUserDisposition["kind"]="clone_only"; zeroUserDisposition["reviewed_boundary_line"]=3; zeroUserDisposition["reason"]="Entire advertised boundary and structural projections contain zero substantive user turns.";
    Check(Invoke("resolve-clone",zeroUserDisposition).Exit==0,"zero-substantive clone-only requires actual complete boundary and structural outputs");
    Check(Invoke("verify-pages",zeroUserSelection).Exit==0,"matching zero-substantive resolution clears the selected manual row");
    Console.WriteLine("PASS zero-substantive-clone-only-proof");
    var other=Path.Combine(root,"other-repo"); Directory.CreateDirectory(Path.Combine(other,".git"));
    request["store"]=Path.Combine(root,"git-only-store");
    var gitCapture=Invoke("capture",request); Check(gitCapture.Exit==0,"Git-only scope uses a captured safe manifest");
    var gitSelection=selection.DeepClone().AsObject(); gitSelection["run_directory"]=gitCapture.Body["run_directory"]!.DeepClone(); gitSelection["scope"]=new JsonObject { ["cwd_roots"]=new JsonArray(other),["worktree_tails"]=new JsonArray() };
    var gitPage=gitSelection.DeepClone().AsObject(); gitPage["offset"]=0; gitPage["limit"]=1; Invoke("page",gitPage);
    var zeroProof=Invoke("verify-pages",gitSelection); Check(zeroProof.Exit==0 && zeroProof.Body["eligible_sessions"]?.GetValue<int>()==0,"zero eligible scope has an explicit complete page receipt");
    var newWiki=Path.Combine(root,"new-wiki.md");
    var gitTopic=gitSelection.DeepClone().AsObject(); gitTopic["topic_id"]="git-only"; gitTopic["session_ids"]=new JsonArray(); gitTopic["git_candidates"]=new JsonArray(new JsonObject { ["repository"]=repo,["sha"]=new string('c',40) }); gitTopic["source_pins"]=new JsonObject { [pinKey]=new string('a',40) }; gitTopic["wiki_files"]=new JsonArray(newWiki); gitTopic["decision"]="update_needed"; gitTopic["comparison"]="Reachable Git change needs a new wiki page; ancestry is caller evidence.";
    var gitRecorded=Invoke("record-topic",gitTopic); Check(gitRecorded.Exit==0 && gitRecorded.Body["status"]?.GetValue<string>()=="pending_delivery","Git-only candidate can cache an update for a missing new wiki file");
    Check(Invoke("resume-topics",gitTopic).Body["status"]?.GetValue<string>()=="reusable","Git-only pending comparison survives a new process");
    var relativeGitTopic=gitTopic.DeepClone().AsObject(); relativeGitTopic["git_candidates"]![0]!["repository"]=Path.GetRelativePath(Environment.CurrentDirectory,repo);
    Check(Invoke("record-topic",relativeGitTopic).Exit==2,"relative Git candidate repository is rejected even when it resolves to an allowed source root");
    Console.WriteLine("PASS absolute-git-candidate-repository-contract");
    var stsRepo=Path.Combine(root,"sts-repo"); Directory.CreateDirectory(Path.Combine(stsRepo,".git"));
    var docsTopic=gitTopic.DeepClone().AsObject(); docsTopic["topic_id"]="docs-only";
    docsTopic["source_pins"]=new JsonObject { [repo+"|refs/remotes/origin/develop"]=new string('a',40),[repo+"|refs/remotes/origin/production"]=new string('b',40),[stsRepo+"|refs/remotes/origin/develop"]=new string('c',40),[stsRepo+"|refs/remotes/origin/production"]=new string('d',40) };
    docsTopic["documentation_pin"]=new JsonObject { ["repository"]=other,["ref"]="refs/remotes/origin/main",["sha"]=new string('e',40) };
    docsTopic["git_candidates"]=new JsonArray(new JsonObject { ["repository"]=other,["sha"]=new string('f',40) });
    docsTopic["comparison"]="A reachable docs-only origin/main change needs a wiki update; code source pins remain separate.";
    var docsRecorded=Invoke("record-topic",docsTopic); Check(docsRecorded.Exit==0 && docsRecorded.Body["status"]?.GetValue<string>()=="pending_delivery","docs-only origin/main candidate can be cached with a separately bound documentation pin");
    Check(Invoke("resume-topics",docsTopic).Body["status"]?.GetValue<string>()=="reusable","matching documentation and unchanged four code pins reuse the docs-only comparison");
    docsTopic["documentation_pin"]!["sha"]=new string('9',40); Check(Invoke("resume-topics",docsTopic).Body["status"]?.GetValue<string>()=="stale","changed separate documentation pin makes docs-only comparison stale");
    Console.WriteLine("PASS separate-documentation-main-pin-and-staleness");
    File.WriteAllText(newWiki,"Delivered page content\n"); Check(Invoke("resume-topics",gitTopic).Body["status"]?.GetValue<string>()=="stale","creation of missing wiki input invalidates pending cache");
    File.AppendAllText(memory,"Run time: 2026-10-12T08:00:00Z\n\n## Failed run\nModel capacity interrupted the review.\n");
    var proseResume=Invoke("capture",request); Check(proseResume.Exit==0 && proseResume.Body["status"]?.GetValue<string>()=="resumed","failure prose and run time preserve the exact captured official checkpoint");
    File.WriteAllText(memory,"Processed window end: 2026-10-12T06:30:00Z\n");
    Check(Invoke("capture",request).Exit==2,"changed official processed cursor blocks adoption");
    File.WriteAllText(memory,"Processed window end: 2026-10-12T06:00:00Z\n");
    Console.WriteLine("PASS git-only-zero-scope-new-wiki-and-checkpoint-binding");
    var pointerPath=Path.Combine(gitCapture.Body["run_directory"]!.GetValue<string>(),"pages","page-0000000000.json"); var savedPointer=File.ReadAllBytes(pointerPath); File.Delete(pointerPath);
    Check(Invoke("resume-topics",gitTopic).Exit==2,"missing extraction page blocks cache reuse before stale topic comparison"); File.WriteAllBytes(pointerPath,savedPointer);
    var capturedIndex=gitCapture.Body["index_snapshot"]!.GetValue<string>(); var savedIndex=File.ReadAllBytes(capturedIndex); File.AppendAllText(capturedIndex,"corruption\n"); Check(Invoke("capture",request).Exit==2,"snapshot corruption blocks capture adoption"); File.WriteAllBytes(capturedIndex,savedIndex);
    var savedManifest=File.ReadAllBytes(gitCapture.Body["manifest"]!.GetValue<string>()); File.Delete(gitCapture.Body["manifest"]!.GetValue<string>()); Check(Invoke("capture",request).Exit==2,"missing manifest blocks capture adoption"); File.WriteAllBytes(gitCapture.Body["manifest"]!.GetValue<string>(),savedManifest);
    Console.WriteLine("PASS incomplete-evidence-and-corrupt-capture-blocking");
    File.AppendAllText(definition,"prompt = \"changed definition\"\n"); Check(Invoke("resume-topics",gitTopic).Exit==2,"changed automation definition blocks current topic reuse"); File.WriteAllText(definition,"id = \"keep-ncg-wiki-current\"\n");
    var resolverBytes=File.ReadAllBytes(resolver); File.AppendAllText(resolver,"\n# changed resolver version\n"); Check(Invoke("capture",request).Exit==2,"changed resolver contents block adopting an old run"); File.WriteAllBytes(resolver,resolverBytes);
    var normalHelper=helper; var otherHelper=Path.Combine(root,"OtherReviewRun.cs"); File.Copy(helper,otherHelper); helper=otherHelper;
    Check(Invoke("resume-topics",gitTopic).Exit==2,"different running helper identity cannot reuse old topic proof"); helper=normalHelper;
    Console.WriteLine("PASS current-definition-resolver-and-helper-identity");
    var pageRows=new List<string>();
    for(var n=1;n<=3;n++) {
        var id="paged-"+n;
        pageRows.Add(new JsonObject { ["id"]=id,["updated_at"]=stamp }.ToJsonString());
        var pageRecords=records.Select(x=>x.DeepClone().AsObject()).ToArray(); pageRecords[0]["payload"]!["id"]=id;
        pageRecords[1]["payload"]!["content"]![0]!["text"]=new string('x',1000); pageRecords[2]["payload"]!["content"]![0]!["text"]=new string('y',1000);
        File.WriteAllText(Path.Combine(day,"rollout-"+id+".jsonl"),string.Join("\n",pageRecords.Select(x=>x.ToJsonString()))+"\n");
    }
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),string.Join("\n",pageRows)+"\n"); request["store"]=Path.Combine(root,"page-store");
    var pagedCapture=Invoke("capture",request); Check(pagedCapture.Exit==0,"multi-page fixture captures safe sessions");
    var pagedSelection=selection.DeepClone().AsObject(); pagedSelection["run_directory"]=pagedCapture.Body["run_directory"]!.DeepClone();
    var omittedRequest=pagedSelection.DeepClone().AsObject(); omittedRequest["offset"]=0; omittedRequest["limit"]=3; omittedRequest["max_total_chars"]=2000;
    var omittedPage=Invoke("page",omittedRequest); Check(omittedPage.Exit==0 && omittedPage.Body["extractor_exit"]?.GetValue<int>()==0,"capped terminal extractor exits successfully");
    var rawOmitted=JsonNode.Parse(File.ReadAllText(omittedPage.Body["output"]!.GetValue<string>()))!.AsObject(); Check(rawOmitted["selection_window"]!["has_more"]?.GetValue<bool>()==false && rawOmitted["omitted_sessions"]!["count"]?.GetValue<int>()>0,"fixture reaches terminal page with actual output omissions");
    Check(Invoke("verify-pages",pagedSelection).Exit==2,"successful terminal process with omissions is rejected");
    omittedRequest["limit"]=1; omittedRequest["max_total_chars"]=20000; Invoke("page",omittedRequest);
    omittedRequest["offset"]=2; Invoke("page",omittedRequest);
    var gap=Invoke("verify-pages",pagedSelection); Check(gap.Exit==2 && gap.Body["reason"]?.GetValue<string>()=="missing_page_at_offset_1","missing middle page cannot be healed by a later terminal page");
    omittedRequest["offset"]=1; Invoke("page",omittedRequest); Check(Invoke("verify-pages",pagedSelection).Exit==0,"all contiguous pages with zero omissions receive completeness proof");
    Console.WriteLine("PASS capped-output-and-missing-middle-page");
    foreach(var file in Directory.EnumerateFiles(pagedCapture.Body["run_directory"]!.GetValue<string>(),"*",SearchOption.AllDirectories)) Check((File.GetUnixFileMode(file)&(UnixFileMode.GroupRead|UnixFileMode.GroupWrite|UnixFileMode.GroupExecute|UnixFileMode.OtherRead|UnixFileMode.OtherWrite|UnixFileMode.OtherExecute))==0,"private evidence file has no group/world permissions");
    foreach(var folder in Directory.EnumerateDirectories(pagedCapture.Body["run_directory"]!.GetValue<string>(),"*",SearchOption.AllDirectories)) Check((File.GetUnixFileMode(folder)&(UnixFileMode.GroupRead|UnixFileMode.GroupWrite|UnixFileMode.GroupExecute|UnixFileMode.OtherRead|UnixFileMode.OtherWrite|UnixFileMode.OtherExecute))==0,"private evidence directory has no group/world permissions");
    var invalidate=new JsonObject { ["run_directory"]=pagedCapture.Body["run_directory"]!.DeepClone(),["reason"]="Fixture review completed; retain evidence and explicitly select the next run." };
    Check(Invoke("invalidate",invalidate).Body["status"]?.GetValue<string>()=="invalidated","explicit invalidation preserves prior evidence and frees active capture");
    Check(Invoke("capture",request).Body["status"]?.GetValue<string>()=="captured","explicitly invalidated run can be followed by a new capture");
    Console.WriteLine("PASS private-permissions-and-explicit-invalidation");
    var alias=Path.Combine(root,"automation-alias"); Directory.CreateSymbolicLink(alias,automation);
    request["store"]=Path.Combine(alias,"hidden-run-storage");
    var aliasedStore=Invoke("capture",request); Check(aliasedStore.Exit==2,"a symlinked ancestor cannot move protected evidence into automation memory storage");
    Console.WriteLine("PASS automation-memory-storage-boundary-through-symlink");
    var upperAutomation=Path.Combine(root,"AUTOMATION");
    if(Directory.Exists(upperAutomation)) {
        request["store"]=Path.Combine(upperAutomation,"case-run-storage");
        var caseAlias=Invoke("capture",request);
        Check(caseAlias.Exit==2 && caseAlias.Body["reason"]?.GetValue<string>()=="store_must_be_outside_automation_definition_and_memory_directory" && !Directory.Exists(Path.Combine(automation,"case-run-storage")),"existing uppercase automation alias is blocked before directory, lock, active or resolver artifacts");
        Console.WriteLine("CONTROL case-insensitive alias exercised; distinct-case directories unavailable on this fixture filesystem");
    } else {
        Directory.CreateDirectory(upperAutomation); request["store"]=Path.Combine(upperAutomation,"case-run-storage");
        Check(Invoke("capture",request).Exit==0 && !Directory.Exists(Path.Combine(automation,"case-run-storage")),"an actually distinct uppercase directory on a case-sensitive filesystem remains allowed");
        Console.WriteLine("CONTROL case-sensitive distinct directory exercised; uppercase alias unavailable on this fixture filesystem");
    }
    request["store"]=Path.Combine(root,"automation-sibling","run-evidence");
    Check(Invoke("capture",request).Exit==0,"outside sibling directory sharing the automation name prefix remains allowed");
    Console.WriteLine("PASS filesystem-case-alias-store-boundary-and-sibling-control");
    File.WriteAllText(memory,"Processed window end: malformed\n"); request["store"]=Path.Combine(root,"failed-resolver-store");
    var failedCapture=Invoke("capture",request); Check(failedCapture.Exit==2 && failedCapture.Body["resolver_exit"]?.GetValue<int>()==1 && failedCapture.Body["run_directory"] is not null && File.Exists(failedCapture.Body["resolver_stdout"]!.GetValue<string>()) && File.ReadAllText(failedCapture.Body["resolver_exit_file"]!.GetValue<string>())=="1","failed resolver exposes exact protected artifact paths and numeric status without a fresh invocation");
    var failedResume=Invoke("capture",request); Check(failedResume.Exit==2 && failedResume.Body["run_directory"]?.GetValue<string>()==failedCapture.Body["run_directory"]?.GetValue<string>(),"incomplete failed capture remains a named blocker after process restart");
    Console.WriteLine("PASS inspectable-failed-capture-and-no-silent-recapture");
    File.WriteAllText(memory,"Last review: 2026-10-12T06:00:00Z\n"); request["store"]=Path.Combine(root,"legacy-store"); request["prompt_last_run"]="2026-10-12T06:00:00Z";
    var legacyCapture=Invoke("capture",request); Check(legacyCapture.Exit==0,"absent Processed cursor preserves explicit legacy prompt boundary");
    request["prompt_last_run"]="2026-10-12T09:00:00Z"; Check(Invoke("capture",request).Exit==2,"changed legacy prompt boundary remains selection identity when Processed is absent");
    Console.WriteLine("PASS explicit-legacy-prompt-boundary-remains-bound");
    File.WriteAllText(memory,"Run time: 2026-10-12T08:00:00Z\n\n## Historical review\nLast review: 2026-10-12T06:00:00Z\n"); request["store"]=Path.Combine(root,"historical-only-store"); request["prompt_last_run"]="";
    var historicalOnly=Invoke("capture",request); Check(historicalOnly.Exit==2 && historicalOnly.Body["reason"]?.GetValue<string>()=="historical_last_review_without_header_cutoff","historical Last review without any authoritative header cutoff blocks before capture");
    File.WriteAllText(memory,"Run time: 2026-10-12T08:00:00Z\n\n## Historical review\nLast review: 2026-10-12T06:30:00Z\n");
    var changedHistorical=Invoke("capture",request); Check(changedHistorical.Exit==2 && changedHistorical.Body["reason"]?.GetValue<string>()=="historical_last_review_without_header_cutoff" && !Directory.Exists(request["store"]!.GetValue<string>()),"changed historical timestamp cannot define or resume a selection and creates no run store");
    File.WriteAllText(memory,"## Historical review\nLast review: 2026-10-12T06:30:00Z\n");
    Check(Invoke("capture",request).Body["reason"]?.GetValue<string>()=="historical_last_review_without_header_cutoff","a history heading at the start does not turn its Last review into a current header boundary");
    Console.WriteLine("PASS historical-only-last-review-never-defines-capture");
}
finally { Directory.Delete(root,true); }
return 0;

(int Exit, JsonObject Body) Invoke(string command, JsonObject request)
{
    var path=Path.Combine(root,"request-"+Guid.NewGuid().ToString("N")+".json");
    File.WriteAllText(path,request.ToJsonString());
    var start=new ProcessStartInfo("dotnet") { RedirectStandardOutput=true,RedirectStandardError=true,UseShellExecute=false };
    foreach(var arg in new[]{"run","--file",helper,"--",command,"--request",path}) start.ArgumentList.Add(arg);
    using var process=Process.Start(start)!;
    var stdoutTask=process.StandardOutput.ReadToEndAsync();
    var stderrTask=process.StandardError.ReadToEndAsync();
    process.WaitForExit();
    var stdout=stdoutTask.Result; var stderr=stderrTask.Result;
    if(stderr.Length>0) Console.Error.WriteLine(stderr);
    Console.WriteLine($"CLI {command}: exit={process.ExitCode} {stdout.Trim()}");
    return (process.ExitCode,JsonNode.Parse(stdout)!.AsObject());
}
void Check(bool condition,string message)
{
    if(!condition) throw new Exception("BEHAVIOR FAILURE: "+message);
}

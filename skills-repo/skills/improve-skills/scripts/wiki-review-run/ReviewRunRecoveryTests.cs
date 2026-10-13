using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json.Nodes;

if(OperatingSystem.IsWindows()) return 2;
var scripts=Path.GetFullPath("skills-repo/skills/improve-skills/scripts");
var fixture=Path.Combine(Path.GetTempPath(),"wiki-recovery-"+Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(fixture,UnixFileMode.UserRead|UnixFileMode.UserWrite|UnixFileMode.UserExecute);
// Freeze the tested public entrypoint so concurrent implementation work cannot
// change its capture identity halfway through an isolated fixture.
var helper=Path.Combine(fixture,"ReviewRun.cs");
File.Copy(Path.Combine(scripts,"wiki-review-run","ReviewRun.cs"),helper);
try
{
    var setup=Setup("retry");
    var marker=Path.Combine(setup.Root,"attempted");
    File.WriteAllText(setup.Extractor,
        "import pathlib,sys,runpy\nmarker=pathlib.Path("+JsonValue.Create(marker)!.ToJsonString()+")\n"+
        "if not marker.exists():\n marker.touch()\n sys.stderr.write('fixture first attempt failed\\n')\n sys.exit(7)\n"+
        "runpy.run_path("+JsonValue.Create(Path.Combine(scripts,"extract_codex_session_evidence.py"))!.ToJsonString()+",run_name='__main__')\n");
    var capture=Invoke("capture",setup.Capture); Check(capture.Exit==0,"retry fixture captures safe selection");
    var page=RequestPage(setup,capture.Body);
    var failed=Invoke("page",page);
    Check(failed.Body["extractor_exit"]?.GetValue<int>()==7,"failed extractor status remains inspectable");
    var failedPointer=File.ReadAllBytes(failed.Body["page_receipt"]!.GetValue<string>());
    Check(Invoke("page",page).Exit==2,"failed page is never automatically retried");
    page["retry_failed"]=true;
    var failedErrors=Path.Combine(Path.GetDirectoryName(failed.Body["output"]!.GetValue<string>())!,"stderr.txt");
    var originalErrors=File.ReadAllBytes(failedErrors); File.AppendAllText(failedErrors,"tampering");
    Check(Invoke("page",page).Body["reason"]?.GetValue<string>()=="corrupt_extractor_output","explicit retry cannot adopt corrupt failed evidence");
    File.WriteAllBytes(failedErrors,originalErrors);
    var retryRollout=Path.Combine(setup.Root,"home","sessions","2026","10","12","rollout-session-1.jsonl");
    var originalRollout=File.ReadAllBytes(retryRollout);
    File.WriteAllText(retryRollout,File.ReadAllText(retryRollout).Replace("Review exact NCG evidence","Changed exact NCG evidence",StringComparison.Ordinal));
    Check(Invoke("page",page).Body["reason"]?.GetValue<string>()=="rollout_source_changed_session-1","explicit failed retry cannot adopt changed advertised source bytes");
    File.WriteAllBytes(retryRollout,originalRollout);
    var retried=Invoke("page",page);
    Check(retried.Exit==0 && retried.Body["status"]?.GetValue<string>()=="page_captured","explicit retry supersedes only a known failed page without recapture");
    Check(!failedPointer.SequenceEqual(File.ReadAllBytes(retried.Body["page_receipt"]!.GetValue<string>())) && File.Exists(failed.Body["output"]!.GetValue<string>()),"retry preserves original failed evidence");
    var retryPointer=JsonNode.Parse(File.ReadAllText(retried.Body["page_receipt"]!.GetValue<string>()))!;
    var retryEnvelope=JsonNode.Parse(File.ReadAllText(Path.Combine(retryPointer["folder"]!.GetValue<string>(),"envelope.json")))!;
    Check(retryEnvelope["superseded_failed_attempt"]!["folder"]!.GetValue<string>()==Path.GetDirectoryName(failed.Body["output"]!.GetValue<string>()),"new page receipt retains the named failed attempt");
    Check(Invoke("verify-pages",page).Exit==0,"retried complete page proves the original selection");
    File.AppendAllText(failedErrors,"later tampering");
    Check(Invoke("verify-pages",page).Body["reason"]?.GetValue<string>()=="corrupt_extractor_output","retained failed evidence remains protected after successful retry");
    File.WriteAllBytes(failedErrors,originalErrors);
    Console.WriteLine("PASS known-failed-page-explicit-retry");

    var timeout=Setup("timeout"); var childPidFile=Path.Combine(timeout.Root,"descendant.pid");
    File.WriteAllText(timeout.Extractor,"import subprocess,sys,pathlib\nchild=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])\npathlib.Path("+JsonValue.Create(childPidFile)!.ToJsonString()+").write_text(str(child.pid))\n");
    var timeoutCapture=Invoke("capture",timeout.Capture); Check(timeoutCapture.Exit==0,"timeout fixture captures safe selection");
    var timeoutPage=RequestPage(timeout,timeoutCapture.Body); timeoutPage["timeout_seconds"]=1;
    var elapsed=Stopwatch.StartNew(); var timedOut=Invoke("page",timeoutPage,6);
    Check(timedOut.Exit==2 && timedOut.Body["extractor_exit"]?.GetValue<int>()==124 && elapsed.Elapsed<TimeSpan.FromSeconds(5),"exited extractor parent cannot leave an indefinite descendant pipe wait");
    var childPid=int.Parse(File.ReadAllText(childPidFile));
    Check(!Alive(childPid),"owned orphan descendant is terminated on timeout");
    var timeoutOutput=timedOut.Body["output"]!.GetValue<string>();
    Check(File.ReadAllText(Path.Combine(Path.GetDirectoryName(timeoutOutput)!,"stderr.txt")).Contains("subprocess_timeout",StringComparison.Ordinal),"timeout leaves protected explicit failure diagnostics");
    Check(Invoke("capture",timeout.Capture).Body["status"]?.GetValue<string>()=="resumed","store lock is released after subprocess timeout");
    Console.WriteLine("PASS bounded-timeout-owned-orphan-and-lock-release");

    var capped=Setup("output-cap");
    File.WriteAllText(capped.Extractor,"import sys,time\nsys.stdout.buffer.write(b'x'*500000)\nsys.stdout.flush()\ntime.sleep(60)\n");
    var cappedCapture=Invoke("capture",capped.Capture); var cappedPage=RequestPage(capped,cappedCapture.Body); cappedPage["max_output_bytes"]=4000; cappedPage["timeout_seconds"]=3;
    var cappedResult=Invoke("page",cappedPage,7);
    Check(cappedResult.Exit==2 && cappedResult.Body["extractor_exit"]?.GetValue<int>()==125,"output overflow stops the subprocess with non-success");
    var cappedFolder=Path.GetDirectoryName(cappedResult.Body["output"]!.GetValue<string>())!;
    Check(new FileInfo(Path.Combine(cappedFolder,"stdout.json")).Length+new FileInfo(Path.Combine(cappedFolder,"stderr.txt")).Length<=4000,"combined retained subprocess output includes diagnostics within the byte bound");
    Check(File.ReadAllText(Path.Combine(cappedFolder,"stderr.txt")).Contains("subprocess_output_limit_exceeded",StringComparison.Ordinal),"output overflow leaves explicit protected diagnostics");
    Console.WriteLine("PASS bounded-combined-output-and-diagnostics");
    var within=Setup("within-output-cap");
    File.WriteAllText(within.Extractor,"import sys,time\nsys.stdout.buffer.write(b'x'*3500)\nsys.stdout.flush()\ntime.sleep(0.2)\n");
    var withinCapture=Invoke("capture",within.Capture); var withinPage=RequestPage(within,withinCapture.Body); withinPage["max_output_bytes"]=4000;
    var withinResult=Invoke("page",withinPage);
    Check(withinResult.Exit==0 && new FileInfo(withinResult.Body["output"]!.GetValue<string>()).Length==3500,"output below the configured byte ceiling is not prematurely truncated for reserved diagnostics");
    Console.WriteLine("PASS configured-output-ceiling-retains-complete-success");

    var wiki=Path.Combine(setup.Root,"wiki.md"); File.WriteAllText(wiki,"Existing fixture wiki\n");
    var batch=page.DeepClone().AsObject(); batch["operation"]="record";
    batch["source_pins"]=new JsonObject { [Path.Combine(setup.Root,"ncg")+"|refs/remotes/origin/develop"]=new string('a',40) };
    var topics=new JsonArray();
    for(var n=0;n<12;n++) topics.Add((JsonNode)new JsonObject { ["topic_id"]="topic-"+n,["session_ids"]=new JsonArray("session-1"),["git_candidates"]=new JsonArray(),["wiki_files"]=new JsonArray(wiki),["decision"]="unchanged",["comparison"]="Fixture compared with existing wiki." });
    batch["topics"]=topics;
    var individual=batch.DeepClone().AsObject(); individual.Remove("topics"); individual.Remove("operation");
    foreach(var pair in topics[0]!.AsObject()) individual[pair.Key]=pair.Value?.DeepClone();
    var individualRecorded=Invoke("record-topic",individual);
    var batchRecorded=Invoke("topics-batch",batch);
    Check(batchRecorded.Exit==0 && batchRecorded.Body["status"]?.GetValue<string>()=="topics_complete" && batchRecorded.Body["complete_proof_validations"]?.GetValue<int>()==1,"bounded batch records all topics after one complete-proof validation");
    Check(batchRecorded.Body["results"]!.AsArray().Count==12 && batchRecorded.Body["results"]![0]!["receipt_sha256"]?.GetValue<string>()==individualRecorded.Body["receipt_sha256"]?.GetValue<string>(),"batch preserves individual topic receipt semantics");
    Console.WriteLine("PASS bounded-topic-batch-equivalence");
    batch["operation"]="resume";
    var separateTime=Stopwatch.StartNew(); var separateReceipts=new List<string>();
    foreach(var topic in topics) {
        var one=batch.DeepClone().AsObject(); one.Remove("topics"); one.Remove("operation");
        foreach(var pair in topic!.AsObject()) one[pair.Key]=pair.Value?.DeepClone();
        var resumed=Invoke("resume-topics",one); Check(resumed.Exit==0 && resumed.Body["status"]?.GetValue<string>()=="reusable","individual topic resumes before batch measurement");
        separateReceipts.Add(resumed.Body["receipt_sha256"]!.GetValue<string>());
    }
    separateTime.Stop(); var batchTime=Stopwatch.StartNew(); var batchResumed=Invoke("topics-batch",batch); batchTime.Stop();
    Check(batchResumed.Exit==0 && batchResumed.Body["complete_proof_validations"]?.GetValue<int>()==1 && batchResumed.Body["results"]!.AsArray().Select(x=>x!["receipt_sha256"]!.GetValue<string>()).SequenceEqual(separateReceipts),"one batch resumes the same exact topic receipts as separate invocations");
    Console.WriteLine(FormattableString.Invariant($"MEASURE topic_resume topics=12 separate_cli_calls=12 separate_elapsed_ms={separateTime.Elapsed.TotalMilliseconds:F3} batch_cli_calls=1 batch_elapsed_ms={batchTime.Elapsed.TotalMilliseconds:F3} batch_complete_proof_validations={batchResumed.Body["complete_proof_validations"]} batch_proof_ms={batchResumed.Body["proof_validation_ms"]}"));
    var changedContext=batch.DeepClone().AsObject(); changedContext["topics"]![0]!["source_pins"]=new JsonObject { [Path.Combine(setup.Root,"ncg")+"|refs/remotes/origin/develop"]=new string('b',40) };
    var mixed=Invoke("topics-batch",changedContext);
    Check(mixed.Body["results"]![0]!["status"]?.GetValue<string>()=="stale" && mixed.Body["results"]![1]!["status"]?.GetValue<string>()=="reusable","batch preserves per-topic source-pin staleness");
    File.AppendAllText(wiki,"Changed wiki\n"); var changedWiki=Invoke("topics-batch",batch);
    Check(changedWiki.Body["results"]!.AsArray().All(x=>x!["status"]?.GetValue<string>()=="stale"),"batch preserves current wiki-input staleness");
    File.WriteAllText(wiki,"Existing fixture wiki\n");
    var duplicate=batch.DeepClone().AsObject(); duplicate["topics"]![1]!["topic_id"]="topic-0";
    Check(Invoke("topics-batch",duplicate).Body["reason"]?.GetValue<string>()=="duplicate_topic_batch_id","batch rejects duplicate topic identities");
    var overridden=batch.DeepClone().AsObject(); overridden["topics"]![0]!["run_directory"]="/foreign";
    Check(Invoke("topics-batch",overridden).Body["reason"]?.GetValue<string>()=="topic_common_fields_must_not_be_overridden","batch cannot override its bound selection per topic");
    var oversized=batch.DeepClone().AsObject(); oversized["topics"]=new JsonArray(Enumerable.Range(0,65).Select(n=>(JsonNode)new JsonObject { ["topic_id"]="oversized-"+n }).ToArray());
    Check(Invoke("topics-batch",oversized).Body["reason"]?.GetValue<string>()=="topic_batch_bounds_exceeded","batch enforces topic-count bounds");
    var oversizedBytes=batch.DeepClone().AsObject(); oversizedBytes["topics"]![0]!["comparison"]=new string('x',524288);
    Check(Invoke("topics-batch",oversizedBytes).Body["reason"]?.GetValue<string>()=="topic_batch_bounds_exceeded","batch enforces combined request byte bounds");
    var outcomes=batch.DeepClone().AsObject(); outcomes["operation"]="record"; outcomes["topics"]=new JsonArray((JsonNode)topics[0]!.DeepClone(),(JsonNode)topics[1]!.DeepClone());
    outcomes["topics"]![0]!["topic_id"]="blocked-outcome"; outcomes["topics"]![0]!["decision"]="blocked";
    outcomes["topics"]![1]!["topic_id"]="pending-outcome"; outcomes["topics"]![1]!["decision"]="update_needed";
    Check(Invoke("topics-batch",outcomes).Exit==0,"batch records explicit pending and blocked outcomes"); outcomes["operation"]="resume";
    var resumedOutcomes=Invoke("topics-batch",outcomes);
    Check(resumedOutcomes.Body["results"]![0]!["status"]?.GetValue<string>()=="topic_blocked" && resumedOutcomes.Body["results"]![1]!["delivery_state"]?.GetValue<string>()=="pending_delivery","batch operation completion never clears blocked or pending delivery state");
    var goodOutput=retried.Body["output"]!.GetValue<string>(); var goodBytes=File.ReadAllBytes(goodOutput); File.AppendAllText(goodOutput,"\n");
    Check(Invoke("topics-batch",batch).Exit==2 && Invoke("page",page).Body["reason"]?.GetValue<string>()=="corrupt_extractor_output","one-proof batch and retry both block corrupted successful evidence");
    File.WriteAllBytes(goodOutput,goodBytes);
    Console.WriteLine("PASS topic-batch-staleness-bounds-and-corruption");

    var ranges=Setup("ranges"); var rangePath=Path.Combine(ranges.Root,"home","sessions","2026","10","12","rollout-session-1.jsonl");
    var rangeText=File.ReadAllText(rangePath).Replace("Review exact NCG evidence",new string('x',2097152),StringComparison.Ordinal).Replace("\n","\r\n",StringComparison.Ordinal).TrimEnd('\r','\n');
    File.WriteAllText(rangePath,rangeText); var rangeBytes=File.ReadAllBytes(rangePath);
    var rangeCapture=Invoke("capture",ranges.Capture); var rangePage=RequestPage(ranges,rangeCapture.Body); var rangeResult=Invoke("page",rangePage);
    Check(rangeResult.Exit==0,"multiblock CRLF fixture without terminal newline extracts successfully");
    var rangePointer=JsonNode.Parse(File.ReadAllText(rangeResult.Body["page_receipt"]!.GetValue<string>()))!;
    var rangeEnvelope=JsonNode.Parse(File.ReadAllText(Path.Combine(rangePointer["folder"]!.GetValue<string>(),"envelope.json")))!;
    Check(rangeEnvelope["source_pins"]!["session-1"]!["range_sha256"]!.GetValue<string>()==Convert.ToHexStringLower(SHA256.HashData(rangeBytes)),"advertised range hash retains all exact CRLF and unterminated final-record bytes across blocks");
    var rangeProof=Invoke("verify-pages",rangePage); Check(rangeProof.Exit==0,"multiblock exact range has complete proof");
    var rangeTopic=rangePage.DeepClone().AsObject(); rangeTopic["operation"]="record"; rangeTopic["source_pins"]=new JsonObject { [Path.Combine(ranges.Root,"ncg")+"|refs/remotes/origin/develop"]=new string('a',40) };
    rangeTopic["topics"]=new JsonArray((JsonNode)topics[0]!.DeepClone());
    var rangeMeasured=Invoke("topics-batch",rangeTopic);
    Console.WriteLine($"MEASURE exact_range source_bytes={rangeBytes.Length} proof_validation_ms={rangeMeasured.Body["proof_validation_ms"]}");
    File.WriteAllText(rangePath,rangeText[..rangeText.LastIndexOf("\r\n",StringComparison.Ordinal)]);
    Check(Invoke("verify-pages",rangePage).Body["reason"]?.GetValue<string>()=="truncated_advertised_range","removing the last advertised record blocks proof");
    File.WriteAllBytes(rangePath,rangeBytes);
    File.AppendAllText(retryRollout,"{\"timestamp\":\"2026-10-12T09:00:00Z\",\"type\":\"event_msg\",\"payload\":{\"type\":\"task_started\"}}\n");
    Check(Invoke("topics-batch",batch).Body["results"]!.AsArray().All(x=>x!["status"]?.GetValue<string>()=="reusable"),"bytes appended beyond complete advertised lines retain topic proof");
    Console.WriteLine("PASS exact-multiblock-crlf-eof-truncation-and-append-ranges");

    var suffix=Setup("suffix-range"); var suffixPath=Path.Combine(suffix.Root,"home","sessions","2026","10","12","rollout-session-1.jsonl");
    var suffixText=File.ReadAllText(suffixPath).Replace("Review exact NCG evidence",new string('x',2097152),StringComparison.Ordinal).Replace("\n","\r\n",StringComparison.Ordinal).TrimEnd('\r','\n');
    File.WriteAllText(suffixPath,suffixText);
    File.WriteAllText(suffix.Capture["memory"]!.GetValue<string>(),"Processed window end: 2026-10-12T06:00:00Z\nCarry-forward sessions: [{\"id\":\"session-1\",\"line_count\":2,\"last_activity_at\":\"2026-10-12T05:00:00Z\"}]\n");
    var suffixCapture=Invoke("capture",suffix.Capture); Check(suffixCapture.Exit==0,"carried suffix fixture captures advertised delta");
    var suffixPage=RequestPage(suffix,suffixCapture.Body); var suffixResult=Invoke("page",suffixPage); Check(suffixResult.Exit==0,"carried suffix extracts only its new advertised record");
    var suffixPointer=JsonNode.Parse(File.ReadAllText(suffixResult.Body["page_receipt"]!.GetValue<string>()))!;
    var suffixEnvelope=JsonNode.Parse(File.ReadAllText(Path.Combine(suffixPointer["folder"]!.GetValue<string>(),"envelope.json")))!;
    var expectedSuffix=System.Text.Encoding.UTF8.GetBytes(suffixText[(suffixText.LastIndexOf("\r\n",StringComparison.Ordinal)+2)..]);
    Check(suffixEnvelope["source_pins"]!["session-1"]!["review_line_start"]!.GetValue<int>()==3 && suffixEnvelope["source_pins"]!["session-1"]!["range_sha256"]!.GetValue<string>()==Convert.ToHexStringLower(SHA256.HashData(expectedSuffix)),"multiblock hashing skips the carried prefix and hashes only exact suffix bytes");
    Check(Invoke("verify-pages",suffixPage).Exit==0,"carried multiblock prefix does not disturb complete suffix proof");
    Console.WriteLine("PASS exact-carried-suffix-after-multiblock-prefix");
}
finally {
    foreach(var path in Directory.EnumerateFiles(fixture,"*.pid",SearchOption.AllDirectories))
        if(int.TryParse(File.ReadAllText(path),out var pid)) try { using var child=Process.GetProcessById(pid); if(!child.HasExited) child.Kill(true); } catch(ArgumentException) { }
    Directory.Delete(fixture,true);
}
return 0;

(string Root,string Extractor,JsonObject Capture) Setup(string name)
{
    var root=Path.Combine(fixture,name); Directory.CreateDirectory(root);
    var home=Path.Combine(root,"home"); var day=Path.Combine(home,"sessions","2026","10","12"); Directory.CreateDirectory(day);
    var repo=Path.Combine(root,"ncg"); Directory.CreateDirectory(Path.Combine(repo,".git"));
    var automation=Path.Combine(home,"automations","fixture"); Directory.CreateDirectory(automation);
    var definition=Path.Combine(automation,"automation.toml"); var memory=Path.Combine(automation,"memory.md");
    File.WriteAllText(definition,"id = \"fixture\"\n"); File.WriteAllText(memory,"Processed window end: 2026-10-12T06:00:00Z\n");
    var stamp="2026-10-12T07:00:00Z";
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),new JsonObject { ["id"]="session-1",["updated_at"]=stamp }.ToJsonString()+"\n");
    var records=new[]{
        new JsonObject { ["timestamp"]=stamp,["type"]="session_meta",["payload"]=new JsonObject { ["id"]="session-1",["cwd"]=repo } },
        new JsonObject { ["timestamp"]=stamp,["type"]="response_item",["payload"]=new JsonObject { ["type"]="message",["role"]="user",["content"]=new JsonArray(new JsonObject { ["type"]="input_text",["text"]="Review exact NCG evidence" }) } },
        new JsonObject { ["timestamp"]=stamp,["type"]="response_item",["payload"]=new JsonObject { ["type"]="message",["role"]="assistant",["phase"]="final",["content"]=new JsonArray(new JsonObject { ["type"]="output_text",["text"]="Wiki compared" }) } }
    };
    File.WriteAllText(Path.Combine(day,"rollout-session-1.jsonl"),string.Join("\n",records.Select(x=>x.ToJsonString()))+"\n");
    var extractor=Path.Combine(root,"extractor.py"); File.Copy(Path.Combine(scripts,"extract_codex_session_evidence.py"),extractor);
    var request=new JsonObject { ["store"]=Path.Combine(root,"store"),["automation_id"]="fixture",["codex_home"]=home,["definition"]=definition,["memory"]=memory,["resolver"]=Path.Combine(scripts,"resolve_codex_sessions.py"),["python"]="python3",["exclude_session_id"]="maintenance",["max_sessions"]=100 };
    return(root,extractor,request);
}
JsonObject RequestPage((string Root,string Extractor,JsonObject Capture) setup,JsonObject capture)=>new() {
    ["run_directory"]=capture["run_directory"]!.DeepClone(),["extractor"]=setup.Extractor,["python"]="python3",
    ["scope"]=new JsonObject { ["cwd_roots"]=new JsonArray(Path.Combine(setup.Root,"ncg")),["worktree_tails"]=new JsonArray() },["offset"]=0,["limit"]=1
};
(int Exit,JsonObject Body) Invoke(string command,JsonObject request,int deadlineSeconds=25)
{
    var path=Path.Combine(fixture,"request-"+Guid.NewGuid().ToString("N")+".json");
    File.WriteAllText(path,request.ToJsonString()); File.SetUnixFileMode(path,UnixFileMode.UserRead|UnixFileMode.UserWrite);
    var start=new ProcessStartInfo("dotnet") { UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true };
    start.Environment["PYTHONDONTWRITEBYTECODE"]="1";
    foreach(var argument in new[]{"run","--file",helper,"--",command,"--request",path}) start.ArgumentList.Add(argument);
    using var process=Process.Start(start)!;
    var stdout=process.StandardOutput.ReadToEndAsync(); var stderr=process.StandardError.ReadToEndAsync();
    if(!process.WaitForExit(deadlineSeconds*1000)) { process.Kill(true); throw new Exception("BEHAVIOR FAILURE: public CLI exceeded fixture deadline for "+command); }
    Task.WaitAll(stdout,stderr);
    var body=JsonNode.Parse(stdout.Result)!.AsObject();
    Console.WriteLine($"CLI {command}: exit={process.ExitCode} status={body["status"]} reason={body["reason"]}");
    return(process.ExitCode,body);
}
void Check(bool condition,string message) { if(!condition) throw new Exception("BEHAVIOR FAILURE: "+message); }
bool Alive(int pid) { try { using var process=Process.GetProcessById(pid); return !process.HasExited; } catch(ArgumentException) { return false; } }

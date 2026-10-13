using System.Diagnostics;
using System.Text.Json.Nodes;

if(OperatingSystem.IsWindows()) return;
var helper=Path.GetFullPath("skills-repo/skills/improve-skills/scripts/wiki-review-run/ReviewRun.cs");
var scripts=Path.GetDirectoryName(Path.GetDirectoryName(helper))!;
var root=Path.Combine(Path.GetTempPath(),"wiki-review-batches-"+Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(root);
try {
    var home=Path.Combine(root,"home"); var day=Path.Combine(home,"sessions/2026/10/12"); Directory.CreateDirectory(day);
    var definition=Path.Combine(root,"automation/automation.toml"); Directory.CreateDirectory(Path.GetDirectoryName(definition)!); File.WriteAllText(definition,"id = \"keep-ncg-wiki-current\"\n");
    var memory=Path.Combine(root,"automation/memory.md"); var original="Processed window end: 2026-10-12T06:00:00Z\n"; File.WriteAllText(memory,original);
    var scopedRepository=Path.Combine(root,"ncg"); Directory.CreateDirectory(Path.Combine(scopedRepository,".git"));
    var index=new List<string>();
    for(var n=0;n<501;n++) {
        var id=$"session-{n:D4}"; const string stamp="2026-10-12T07:00:00Z";
        index.Add(new JsonObject { ["id"]=id,["updated_at"]=stamp }.ToJsonString());
        File.WriteAllText(Path.Combine(day,"rollout-"+id+".jsonl"),new JsonObject { ["timestamp"]=stamp,["type"]="session_meta",["payload"]=new JsonObject { ["id"]=id,["cwd"]=n==0 ? scopedRepository : root } }.ToJsonString()+"\n"+new JsonObject { ["timestamp"]=stamp,["type"]="event_msg",["payload"]=new JsonObject { ["type"]="task_complete" } }.ToJsonString()+"\n");
    }
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),string.Join("\n",index)+"\n");
    var request=new JsonObject { ["automation_id"]="keep-ncg-wiki-current",["codex_home"]=home,["definition"]=definition,["memory"]=memory,["resolver"]=Path.Combine(scripts,"resolve_codex_sessions.py"),["python"]="python3",["exclude_session_id"]="maintenance",["store"]=Path.Combine(root,"store"),["batch_size"]=100 };
    var first=Invoke("capture",request); Check(first.Exit==0 && first.Body["status"]?.GetValue<string>()=="resolving" && first.Body["next_offset"]?.GetValue<int>()==100,"501 sessions begin a bounded protected batch capture");
    var run=first.Body["run_directory"]!.GetValue<string>(); var snapshot=first.Body["index_sha256"]!.GetValue<string>();
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),"invalid new live index\n");
    var resumed=Invoke("capture",request); Check(resumed.Exit==0 && resumed.Body["next_offset"]?.GetValue<int>()==100 && resumed.Body["index_sha256"]?.GetValue<string>()==snapshot,"partial capture resumes without reading changed live index");
    JsonObject last=first.Body;
    for(var offset=100;offset<=500;offset+=100) {
        var batch=new JsonObject { ["run_directory"]=run,["offset"]=offset };
        var next=Invoke("resolve-batch",batch); Check(next.Exit==0,"frozen next batch completes: "+next.Body.ToJsonString());
        var repeated=Invoke("resolve-batch",batch); Check(repeated.Exit==0 && repeated.Body["batch_reused"]?.GetValue<bool>()==true,"successful batch repeats reuse its protected output");
        last=next.Body;
    }
    Check(last["extraction_allowed"]?.GetValue<bool>()==true,"complete batch proof permits bounded extraction");
    var manifest=JsonNode.Parse(File.ReadAllText(last["manifest"]!.GetValue<string>()))!.AsObject();
    Check(manifest["sessions"]!.AsArray().Count==501 && manifest["window"]!["safe_to_persist"]!.GetValue<bool>(),"aggregate contains the complete 501-session selection");
    Check(File.ReadAllText(memory)==original,"batch operations never change official memory");
    Check(Invoke("capture",request).Body["manifest_sha256"]?.GetValue<string>()==last["manifest_sha256"]?.GetValue<string>(),"completed capture adopts the exact aggregate manifest");
    Console.WriteLine("PASS 501-session-bounded-capture-and-process-resume");
    var selection=new JsonObject { ["run_directory"]=run,["extractor"]=Path.Combine(scripts,"extract_codex_session_evidence.py"),["python"]="python3",["scope"]=new JsonObject { ["cwd_roots"]=new JsonArray(scopedRepository),["worktree_tails"]=new JsonArray() } };
    var pageRequest=selection.DeepClone().AsObject(); pageRequest["offset"]=0; pageRequest["limit"]=12;
    Check(Invoke("page",pageRequest).Exit==0,"aggregate manifest enters the existing scoped extractor flow");
    var proof=Invoke("verify-pages",selection); Check(proof.Exit==0 && proof.Body["eligible_sessions"]?.GetValue<int>()==1,"same-manifest proof keeps the sole eligible NCG session after global batching");
    Console.WriteLine("PASS aggregate-manifest-scoped-extraction-completeness");
    var output=last["batch_output"]!.GetValue<string>(); File.AppendAllText(output,"\n");
    Check(Invoke("capture",request).Exit==2,"corrupt batch evidence blocks completed-manifest adoption");
    Console.WriteLine("PASS corrupted-batch-blocks-adoption");
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),string.Join("\n",index)+"\n");
    request["store"]=Path.Combine(root,"skip-store");
    var pending=Invoke("capture",request); var pendingRun=pending.Body["run_directory"]!.GetValue<string>();
    Check(Invoke("resolve-batch",new JsonObject { ["run_directory"]=pendingRun,["offset"]=200 }).Exit==2,"missing middle batch cannot be skipped");
    Check(Invoke("capture",request).Body["next_offset"]?.GetValue<int>()==100,"rejected gap preserves successful prior batch and next offset");
    var docs=Path.Combine(root,"ncg-docs"); Directory.CreateDirectory(Path.Combine(docs,".git"));
    File.AppendAllText(memory,"Docs reviewed tip: "+new JsonObject { ["repository"]=docs,["ref"]="refs/remotes/origin/main",["sha"]=new string('a',40) }.ToJsonString()+"\n");
    Check(Invoke("capture",request).Exit==2,"changed separate Docs reviewed tip invalidates captured checkpoint identity");
    Console.WriteLine("PASS missing-middle-batch-and-docs-checkpoint-binding");
    File.WriteAllText(memory,original+"Carry-forward sessions: [{\"id\":\"deleted-carried\",\"line_count\":2,\"last_activity_at\":\"2026-10-11T07:00:00Z\"}]\n");
    request["store"]=Path.Combine(root,"carry-store"); request["approved_missing_carry_ids"]=new JsonArray("deleted-carried");
    var carried=Invoke("capture",request); Check(carried.Exit==0,"exact approved deleted carry admits bounded resolution");
    var carryRun=carried.Body["run_directory"]!.GetValue<string>(); var carriedLast=carried.Body;
    for(var offset=100;offset<=500;offset+=100) { var step=Invoke("resolve-batch",new JsonObject { ["run_directory"]=carryRun,["offset"]=offset }); Check(step.Exit==0,"remaining carry-bound slices complete"); carriedLast=step.Body; }
    Check(carriedLast["extraction_allowed"]?.GetValue<bool>()==true && carriedLast["resolver_exit"]?.GetValue<int>()==2 && carriedLast["resolver_safe_to_persist"]?.GetValue<bool>()==false,"aggregate preserves raw unsafe carry status with the exact approved exception");
    request["store"]=Path.Combine(root,"unapproved-store"); request.Remove("approved_missing_carry_ids");
    var denied=Invoke("capture",request); Check(denied.Exit==2 && denied.Body["reason"]?.GetValue<string>()=="resolver_unsafe_batch","unapproved deleted carry blocks partial review");
    Console.WriteLine("PASS exact-approved-deleted-carry-and-rejection");
    File.WriteAllText(memory,original); request.Remove("approved_missing_carry_ids");
    var marker=Path.Combine(root,"hang-next-batch"); File.WriteAllText(marker,"hang");
    var retryResolver=Path.Combine(root,"retry-resolver.py");
    File.WriteAllText(retryResolver,"import sys,time,pathlib,runpy\nif '--batch-offset' in sys.argv and sys.argv[sys.argv.index('--batch-offset')+1]=='100' and pathlib.Path("+JsonValue.Create(marker)!.ToJsonString()+").exists(): time.sleep(10)\nrunpy.run_path("+JsonValue.Create(Path.Combine(scripts,"resolve_codex_sessions.py"))!.ToJsonString()+",run_name='__main__')\n");
    request["store"]=Path.Combine(root,"retry-store"); request["resolver"]=retryResolver; request["timeout_seconds"]=1;
    var beforeTimeout=Invoke("capture",request); Check(beforeTimeout.Exit==0,"initial bounded batch captures before transient replay timeout");
    var retryRun=beforeTimeout.Body["run_directory"]!.GetValue<string>();
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),"invalid later live index\n");
    var nextRequest=new JsonObject { ["run_directory"]=retryRun,["offset"]=100 };
    var timedOut=Invoke("resolve-batch",nextRequest); Check(timedOut.Exit==2 && timedOut.Body["resolver_exit"]?.GetValue<int>()==124,"replay timeout records a failed owned batch");
    var failedOutput=timedOut.Body["resolver_stdout"]!.GetValue<string>(); var failedBytes=File.ReadAllBytes(failedOutput);
    Check(Invoke("resolve-batch",nextRequest).Exit==2,"failed batch requires an explicit retry");
    File.Delete(marker); nextRequest["retry_failed"]=true;
    var retried=Invoke("resolve-batch",nextRequest); Check(retried.Exit==0 && retried.Body["next_offset"]?.GetValue<int>()==200 && retried.Body["preserved_failed_batches"]?.GetValue<int>()==1 && File.ReadAllBytes(failedOutput).SequenceEqual(failedBytes),"explicit retry retains failed receipt while resolving only the same next snapshot slice");
    Check(File.ReadAllText(memory)==original,"failed and retried replay keep official checkpoint unchanged");
    Console.WriteLine("PASS timed-out-batch-explicit-retry-preserves-evidence");
}
finally { Directory.Delete(root,true); }

void Check(bool value,string message) { if(!value) throw new Exception(message); }
(int Exit,JsonObject Body) Invoke(string command,JsonObject request) {
    var file=Path.Combine(root,"request-"+Guid.NewGuid().ToString("N")+".json"); File.WriteAllText(file,request.ToJsonString()); File.SetUnixFileMode(file,UnixFileMode.UserRead|UnixFileMode.UserWrite);
    var info=new ProcessStartInfo("dotnet") { RedirectStandardOutput=true,RedirectStandardError=true,UseShellExecute=false };
    foreach(var value in new[]{"run","--file",helper,"--",command,"--request",file}) info.ArgumentList.Add(value);
    using var process=Process.Start(info)!; var output=process.StandardOutput.ReadToEndAsync(); var errors=process.StandardError.ReadToEndAsync(); process.WaitForExit(); Task.WaitAll(output,errors);
    var line=output.Result.Split('\n',StringSplitOptions.RemoveEmptyEntries).LastOrDefault(x=>x.StartsWith('{')) ?? throw new Exception(errors.Result+output.Result);
    return (process.ExitCode,JsonNode.Parse(line)!.AsObject());
}

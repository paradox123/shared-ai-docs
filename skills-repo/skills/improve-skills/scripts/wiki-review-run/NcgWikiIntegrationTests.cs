using System.Diagnostics;
using System.Text;
using System.Text.Json.Nodes;

// Public workflow fixture: dotnet run --file <this file> from shared-ai-docs.
// Requires SDK10, Python3 and Git; uses only private temporary repositories with
// local bare origins. It retains a 0600 CLI log below .scratch and removes its
// fixture unless NCG_WIKI_KEEP_FIXTURE=1. --compile-only skips all fixture work.
if(OperatingSystem.IsWindows()) return 2;
if(args.SequenceEqual(new[]{"--compile-only"})) { Console.WriteLine("PASS integration fixture compiles; workflow was not executed"); return 0; }
var ignoreMissing=args.SequenceEqual(new[]{"--ignore-missing"});
if(args.Length!=0 && !ignoreMissing) { Console.Error.WriteLine("Usage: dotnet run --file NcgWikiIntegrationTests.cs [-- --compile-only|--ignore-missing]"); return 2; }

var identity=Guid.NewGuid().ToString("N");
var root=Path.Combine(OperatingSystem.IsMacOS()?"/private/tmp":Path.GetTempPath(),"ncg-wiki-integration-"+identity);
Directory.CreateDirectory(root);File.SetUnixFileMode(root,UnixFileMode.UserRead|UnixFileMode.UserWrite|UnixFileMode.UserExecute);
var log=Path.GetFullPath(Path.Combine(".scratch","ncg-wiki-review-followup","verification","integration-"+identity+".log"));
Directory.CreateDirectory(Path.GetDirectoryName(log)!);
using(var created=new FileStream(log,new FileStreamOptions{Mode=FileMode.CreateNew,Access=FileAccess.Write,UnixCreateMode=UnixFileMode.UserRead|UnixFileMode.UserWrite})) {}
var review=Path.GetFullPath("skills-repo/skills/improve-skills/scripts/wiki-review-run/ReviewRun.cs");
var delivery=Path.Combine(Path.GetDirectoryName(review)!,"NcgWikiDelivery.cs");
var scripts=Path.GetDirectoryName(Path.GetDirectoryName(review))!;
try {
    var backend=Repository("backend","develop");var sts=Repository("sts","develop");var docs=Repository("docs","main");
    foreach(var repository in new[]{backend,sts}) {Git(repository,"branch","production");Git(repository,"push","origin","production");}
    var sourcePins=new JsonObject();
    foreach(var repository in new[]{backend,sts}) foreach(var branch in new[]{"develop","production"}) sourcePins[repository+"|refs/remotes/origin/"+branch]=Git(repository,"rev-parse",branch);
    var priorDocs=Git(docs,"rev-parse","HEAD");
    var home=Path.Combine(root,"home");var automation=Path.Combine(root,"automation");Directory.CreateDirectory(home);Directory.CreateDirectory(automation);
    var definition=Path.Combine(automation,"automation.toml");File.WriteAllText(definition,"id = \"keep-ncg-wiki-current\"\n");
    var memory=Path.Combine(automation,"memory.md");
    var oldMemory="Processed window end: 2026-10-12T06:00:00Z\nLast review: 2026-10-12T06:01:00Z\nCarry-forward sessions: []\nAuthoritative source tips: "+sourcePins.ToJsonString()+"\nDocs reviewed tip: "+new JsonObject{["repository"]=docs,["ref"]="refs/remotes/origin/main",["sha"]=priorDocs}.ToJsonString()+"\n\n## Earlier\nHistorical fixture paragraph stays unchanged\n";
    if(ignoreMissing) oldMemory=oldMemory.Replace("Carry-forward sessions: []","Carry-forward sessions: [{\"id\":\"deleted-carry\",\"line_count\":4,\"last_activity_at\":\"2026-10-11T07:00:00Z\"},{\"id\":\"deleted-window-carry\",\"line_count\":4,\"last_activity_at\":\"2026-10-11T08:00:00Z\"}]");
    File.WriteAllText(memory,oldMemory);
    var sessions=new[]{"session-backend","session-sts","session-docs"};var roots=new[]{backend,sts,docs};
    var day=Path.Combine(home,"sessions","2026","10","12");Directory.CreateDirectory(day);var index=new List<string>();
    for(var n=0;n<sessions.Length;n++) {
        var stamp=$"2026-10-12T07:0{n}:00Z";
        index.Add(new JsonObject{["id"]=sessions[n],["updated_at"]=stamp}.ToJsonString());
        JsonObject[] records=[
            new(){["timestamp"]=stamp,["type"]="session_meta",["payload"]=new JsonObject{["id"]=sessions[n],["cwd"]=roots[n]}},
            new(){["timestamp"]=stamp,["type"]="response_item",["payload"]=new JsonObject{["type"]="message",["role"]="user",["content"]=new JsonArray(new JsonObject{["type"]="input_text",["text"]="Fixture narrative without implementation provenance"})}},
            new(){["timestamp"]=stamp,["type"]="event_msg",["payload"]=new JsonObject{["type"]="task_complete"}}
        ];
        File.WriteAllText(Path.Combine(day,"rollout-"+sessions[n]+".jsonl"),string.Join("\n",records.Select(x=>x.ToJsonString()))+"\n");
    }
    if(ignoreMissing) {
        index.Add(new JsonObject{["id"]="deleted-window-carry",["updated_at"]="2026-10-12T07:03:00Z"}.ToJsonString());
        index.Add(new JsonObject{["id"]="deleted-window",["updated_at"]="2026-10-12T07:04:00Z"}.ToJsonString());
    }
    File.WriteAllText(Path.Combine(home,"session_index.jsonl"),string.Join("\n",index)+"\n");
    var docsCommits=new List<string>();
    for(var n=1;n<=3;n++) {
        File.WriteAllText(Path.Combine(docs,"fixture-notes.md"),$"Synthetic fixture bookkeeping revision {n}\n");
        Git(docs,"add","fixture-notes.md");Git(docs,"commit","-m",$"Fixture bookkeeping {n}");Git(docs,"push","origin","main");docsCommits.Add(Git(docs,"rev-parse","HEAD"));
    }
    var store=Path.Combine(root,"store");
    var captureRequest=new JsonObject{["store"]=store,["automation_id"]="keep-ncg-wiki-current",["codex_home"]=home,["memory"]=memory,["definition"]=definition,["resolver"]=Path.Combine(scripts,"resolve_codex_sessions.py"),["python"]="python3",["exclude_session_id"]="maintenance",["batch_size"]=1};
    if(ignoreMissing) {
        captureRequest["missing_session_policy"]="ignore";
        // External Python resolver fixture retains missing carry checkpoints, so
        // public finalization must perform the authorized pruning itself.
        var fixtureResolver=Path.Combine(root,"carry-reporting-resolver.py");
        File.WriteAllText(fixtureResolver,"import contextlib,io,json,runpy\nbuffer=io.StringIO()\ncode=0\ntry:\n with contextlib.redirect_stdout(buffer): runpy.run_path("+JsonValue.Create(Path.Combine(scripts,"resolve_codex_sessions.py"))!.ToJsonString()+",run_name='__main__')\nexcept SystemExit as ex: code=ex.code\nmanifest=json.loads(buffer.getvalue())\nmissing={s['id'] for s in manifest['sessions'] if s['status']=='missing'}\nmanifest['window']['carry_forward_to_persist'] += [c for c in manifest['window']['carry_forward_from_memory'] if c['id'] in missing]\nprint(json.dumps(manifest))\nraise SystemExit(code)\n");
        captureRequest["resolver"]=fixtureResolver;
    }
    var capture=Call(review,"capture",captureRequest);Check(capture.Exit==0&&capture.Body["status"]?.GetValue<string>()=="resolving"&&capture.Body["next_offset"]?.GetValue<int>()==1,"three-session capture starts one-session bounded resolution");
    var run=capture.Body["run_directory"]!.GetValue<string>();var resolution=capture.Body;
    while(resolution["extraction_allowed"]?.GetValue<bool>()!=true) {
        var next=Call(review,"resolve-batch",new JsonObject{["run_directory"]=run,["offset"]=resolution["next_offset"]!.DeepClone()});Check(next.Exit==0,"next frozen selection slice resolves");resolution=next.Body;
    }
    Check(resolution["selection_count"]?.GetValue<int>()==(ignoreMissing?6:3),"complete aggregate retains the original full selection including ignored missing rows");
    if(ignoreMissing) Check(resolution["ignored_missing_session_ids"]!.AsArray().Select(x=>x!.GetValue<string>()).ToHashSet(StringComparer.Ordinal).SetEquals(new[]{"deleted-carry","deleted-window-carry","deleted-window"}),"all three missing selection forms are reported across bounded batches");
    Check(File.ReadAllText(memory)==oldMemory,"batch capture never advances official memory");
    Pass("three-session-batch-selection");
    var reviewRequest=new JsonObject{["extractor"]=Path.Combine(scripts,"extract_codex_session_evidence.py"),["python"]="python3",["scope"]=new JsonObject{["cwd_roots"]=new JsonArray(backend,sts,docs),["worktree_tails"]=new JsonArray()}};
    var offset=0;var emitted=new List<string>();
    while(true) {
        var page=reviewRequest.DeepClone().AsObject();page["run_directory"]=run;page["offset"]=offset;page["limit"]=1;page["max_total_chars"]=20000;
        var extracted=Call(review,"page",page);Check(extracted.Exit==0,"bounded aggregate summary page succeeds");
        var output=JsonNode.Parse(File.ReadAllText(extracted.Body["output"]!.GetValue<string>()))!.AsObject();
        Check(output["omitted_sessions"]?["count"]?.GetValue<int>()==0,"summary page omits no eligible session");
        foreach(var session in output["sessions"]!.AsArray()) emitted.Add(session!["id"]!.GetValue<string>());
        var window=output["selection_window"]!.AsObject();
        if(!window["has_more"]!.GetValue<bool>()) break;
        var next=window["next_offset"]!.GetValue<int>();Check(next>offset,"bounded summary chain makes progress");offset=next;
    }
    Check(emitted.SequenceEqual(sessions),"summary chain covers the original ordered session selection");
    var proofRequest=reviewRequest.DeepClone().AsObject();proofRequest["run_directory"]=run;
    var proof=Call(review,"verify-pages",proofRequest);Check(proof.Exit==0&&proof.Body["status"]?.GetValue<string>()=="complete"&&proof.Body["eligible_sessions"]?.GetValue<int>()==3,"summary completeness proof covers all aggregate sessions");
    Pass("aggregate-bounded-summary-completeness");
    var common=new JsonObject{["run_directory"]=run,["review_helper"]=review,["review_request"]=reviewRequest.DeepClone(),["repositories"]=new JsonObject{["backend"]=backend,["sts"]=sts,["docs"]=docs}};
    var sources=Call(delivery,"verify-sources",common);Check(sources.Exit==0,"current exact source verification succeeds");
    Check(sources.Body["payload"]!["git_candidate_count"]!.GetValue<int>()==0,"already reviewed code tips generate an explicit empty Git pass");
    var historyRequest=new JsonObject{["run_directory"]=run,["source_receipt"]=sources.Body["receipt"]!.DeepClone(),["source_receipt_sha256"]=sources.Body["receipt_sha256"]!.DeepClone(),["offset"]=0,["limit"]=1};
    var codeHistory=Call(delivery,"git-history",historyRequest);Check(codeHistory.Exit==0&&codeHistory.Body["payload"]!["count"]!.GetValue<int>()==0&&!codeHistory.Body["payload"]!["has_more"]!.GetValue<bool>(),"empty authoritative code history has a true final offset-zero page");
    var discoveredDocs=new List<string>();offset=0;
    while(true) {
        historyRequest["offset"]=offset;var history=Call(delivery,"docs-history",historyRequest);Check(history.Exit==0,"bounded docs SHA-history page succeeds");
        var page=history.Body["payload"]!.AsObject();foreach(var commit in page["commits"]!.AsArray()) discoveredDocs.Add(commit!.GetValue<string>());
        if(!page["has_more"]!.GetValue<bool>()) break;
        var next=page["next_offset"]!.GetValue<int>();Check(next>offset,"bounded docs history chain makes progress");offset=next;
    }
    Check(discoveredDocs.SequenceEqual(docsCommits),"docs history covers all three newly reachable commits in order");
    Pass("exact-code-source-and-paged-docs-history");
    var candidates=new JsonArray();
    foreach(var id in sessions) candidates.Add((JsonNode)new JsonObject{["kind"]="session",["id"]=id,["disposition"]="unproven",["reason"]="Synthetic user narrative has no Git-backed implementation evidence and establishes no durable NCG fact."});
    foreach(var commit in discoveredDocs) {
        Check(Git(docs,"show","--format=","--name-only",commit)=="fixture-notes.md","irrelevant docs candidate changes only fixture bookkeeping");
        candidates.Add((JsonNode)new JsonObject{["kind"]="git",["repository"]=docs,["sha"]=commit,["disposition"]="irrelevant",["reason"]="The inspected commit changes only synthetic fixture-notes.md bookkeeping; no product or runbook behavior is affected."});
    }
    var planRequest=common.DeepClone().AsObject();planRequest["source_receipt"]=sources.Body["receipt"]!.DeepClone();planRequest["source_receipt_sha256"]=sources.Body["receipt_sha256"]!.DeepClone();planRequest["candidates"]=candidates;planRequest["edits"]=new JsonArray();
    var plan=Call(delivery,"plan-delivery",planRequest);Check(plan.Exit==0,"complete negative dispositions form a no-change delivery plan");
    Check(File.ReadAllText(memory)==oldMemory,"completed evidence and no-change plan still leave official memory untouched");
    var completion=common.DeepClone().AsObject();completion["plan_receipt"]=plan.Body["receipt"]!.DeepClone();completion["plan_receipt_sha256"]=plan.Body["receipt_sha256"]!.DeepClone();
    var final=Call(delivery,"finalize",completion);Check(final.Exit==0&&final.Body["status"]?.GetValue<string>()=="complete","no-change full review finalizes across both helpers");
    var completedMemory=File.ReadAllBytes(memory);var newText=Encoding.UTF8.GetString(completedMemory);
    Check(newText.Contains("Processed window end: "+(ignoreMissing?"2026-10-12T07:04:00Z":"2026-10-12T07:02:00Z")+"\n")&&newText.Contains("## Earlier\nHistorical fixture paragraph stays unchanged\n"),"atomic completion advances the captured ceiling and preserves history");
    var newBundle=final.Body["new_checkpoint"]!.AsObject();
    if(ignoreMissing) {
        var expectedCarry=new JsonArray(new JsonObject{["id"]="session-backend",["line_count"]=3,["last_activity_at"]="2026-10-12T07:00:00Z"},new JsonObject{["id"]="session-sts",["line_count"]=3,["last_activity_at"]="2026-10-12T07:01:00Z"},new JsonObject{["id"]="session-docs",["line_count"]=3,["last_activity_at"]="2026-10-12T07:02:00Z"});
        Check(JsonNode.DeepEquals(JsonNode.Parse(newBundle["Carry-forward sessions"]!.GetValue<string>()),expectedCarry),"successful finalization removes ignored missing carries and preserves remaining checkpoint objects and order");
        Pass("ignored-missing-carry-atomic-pruning");
    }
    Check(JsonNode.Parse(newBundle["Authoritative source tips"]!.GetValue<string>())!.AsObject().Count==4&&JsonNode.Parse(newBundle["Docs reviewed tip"]!.GetValue<string>())!["sha"]!.GetValue<string>()==docsCommits.Last(),"completed bundle retains four code pins and advances its separate reviewed Docs tip");
    Check(!File.Exists(Path.Combine(store,"active.json")),"successful full completion retires the exact active run");
    var repeated=Call(delivery,"finalize",completion);Check(repeated.Exit==0&&File.ReadAllBytes(memory).SequenceEqual(completedMemory),"terminal repeated finalization is idempotent after retirement");
    Check(Git(docs,"status","--porcelain=v1","--untracked-files=all")==""&&Git(docs,"rev-parse","HEAD")==docsCommits.Last(),"no-change completion creates no documentation edit or commit");
    Pass("no-change-finalization-and-idempotent-repeat");
    Console.WriteLine("PASS composed NCG wiki review public CLI workflow");Console.WriteLine("Artifact log: "+log);return 0;
} catch(Exception ex) {File.AppendAllText(log,"FAIL "+ex+"\n");Console.Error.WriteLine("FAIL "+ex.Message+"\nArtifact log: "+log+"\nFixture: "+root);return 1;}
finally {if(Environment.GetEnvironmentVariable("NCG_WIKI_KEEP_FIXTURE")!="1")Directory.Delete(root,true);}

string Repository(string name,string branch) {
    var remote=Path.Combine(root,name+".git");Git(root,"-c","init.templateDir=","init","--bare",remote);Git(remote,"config","core.hooksPath","/dev/null");
    var repository=Path.Combine(root,name);Git(root,"-c","init.templateDir=","init","-b",branch,repository);Git(repository,"config","user.name","Fixture");Git(repository,"config","user.email","fixture@example.invalid");Git(repository,"config","core.hooksPath","/dev/null");
    File.WriteAllText(Path.Combine(repository,"a.md"),"Synthetic original fixture fact\n");Git(repository,"add","a.md");Git(repository,"commit","-m","Initial fixture");Git(repository,"remote","add","origin",remote);Git(repository,"push","-u","origin",branch);return repository;
}
(int Exit,JsonObject Body) Call(string file,string command,JsonObject request) {
    var path=Path.Combine(root,"request-"+Guid.NewGuid().ToString("N")+".json");File.WriteAllText(path,request.ToJsonString());File.SetUnixFileMode(path,UnixFileMode.UserRead|UnixFileMode.UserWrite);
    var start=new ProcessStartInfo("dotnet"){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};foreach(var arg in new[]{"run","--file",file,"--",command,"--request",path})start.ArgumentList.Add(arg);
    using var process=Process.Start(start)!;var output=process.StandardOutput.ReadToEndAsync();var error=process.StandardError.ReadToEndAsync();process.WaitForExit();Task.WaitAll(output,error);
    File.AppendAllText(log,Path.GetFileName(file)+" "+command+" exit="+process.ExitCode+"\n"+output.Result+error.Result+"\n");
    var line=output.Result.Split('\n',StringSplitOptions.RemoveEmptyEntries).LastOrDefault(x=>x.StartsWith('{'))??throw new Exception("CLI produced no JSON: "+error.Result+output.Result);return(process.ExitCode,JsonNode.Parse(line)!.AsObject());
}
string Git(string cwd,params string[] arguments) {
    var start=new ProcessStartInfo("git"){WorkingDirectory=cwd,UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};start.Environment["GIT_TERMINAL_PROMPT"]="0";
    foreach(var arg in new[]{"-c","core.hooksPath=/dev/null"}.Concat(arguments))start.ArgumentList.Add(arg);
    using var process=Process.Start(start)!;var output=process.StandardOutput.ReadToEndAsync();var error=process.StandardError.ReadToEndAsync();process.WaitForExit();Task.WaitAll(output,error);
    File.AppendAllText(log,"git "+string.Join(' ',arguments)+" exit="+process.ExitCode+"\n"+output.Result+error.Result+"\n");Check(process.ExitCode==0,"fixture Git operation failed: "+error.Result);return output.Result.TrimEnd('\r','\n');
}
void Pass(string name) {Console.WriteLine("PASS "+name);File.AppendAllText(log,"PASS "+name+"\n");}
void Check(bool condition,string reason) {if(!condition)throw new Exception(reason);}

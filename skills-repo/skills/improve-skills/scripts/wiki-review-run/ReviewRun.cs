using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

try
{
    if(OperatingSystem.IsWindows()) throw new ReviewBlocked("unix_private_permissions_required");
    if(args.Length!=3 || args[1]!="--request") throw new ReviewBlocked("usage: <capture|resolve-batch|page|verify-pages|resolve-clone|record-topic|resume-topics|topics-batch|invalidate> --request <json-file>");
    var request=Review.ReadJson(Path.GetFullPath(args[2]));
    var result=args[0] switch {
        "capture" => Review.Capture(request),
        "resolve-batch" => Review.ResolveBatch(request),
        "page" => Review.Page(request),
        "verify-pages" => Review.VerifyPages(request),
        "resolve-clone" => Review.ResolveClone(request),
        "record-topic" => Review.RecordTopic(request),
        "resume-topics" => Review.ResumeTopics(request),
        "topics-batch" => Review.TopicsBatch(request),
        "invalidate" => Review.Invalidate(request),
        _ => throw new ReviewBlocked("command_not_implemented")
    };
    Console.WriteLine(result.ToJsonString());
    return 0;
}
catch(Exception ex)
{
    var error=new JsonObject { ["schema_version"]=1,["status"]="blocked",["reason"]=ex.Message };
    foreach(var key in new[]{"run_directory","resolver_stdout","resolver_stderr","resolver_exit_file","output","page_receipt"}) if(ex.Data[key] is string value) error[key]=value;
    if(ex.Data["resolver_exit"] is int exit) error["resolver_exit"]=exit;
    if(ex.Data["extractor_exit"] is int extractorExit) error["extractor_exit"]=extractorExit;
    Console.WriteLine(error.ToJsonString());
    return 2;
}

sealed class ReviewBlocked(string message):Exception(message);

[System.Runtime.Versioning.UnsupportedOSPlatform("windows")]
static class Review
{
    const UnixFileMode DirectoryMode=UnixFileMode.UserRead|UnixFileMode.UserWrite|UnixFileMode.UserExecute;
    const UnixFileMode FileModePrivate=UnixFileMode.UserRead|UnixFileMode.UserWrite;
    public static JsonObject ReadJson(string path) { NoLink(path); return JsonNode.Parse(File.ReadAllBytes(path),documentOptions:new JsonDocumentOptions { AllowDuplicateProperties=false })?.AsObject() ?? throw new ReviewBlocked("invalid_json_object"); }
    public static string Text(JsonObject obj,string name) => obj[name]?.GetValue<string>() is { Length:>0 } value ? value : throw new ReviewBlocked("missing_or_empty_"+name);
    static string Full(JsonObject obj,string name) => Path.GetFullPath(Text(obj,name));
    static string Hash(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    static string FileHash(string path) { NoLink(path); return Hash(File.ReadAllBytes(path)); }
    static string JsonHash(JsonNode node) => Hash(Encoding.UTF8.GetBytes(Canonical(node).ToJsonString()));
    static JsonNode Canonical(JsonNode node) => node switch {
        JsonObject obj => new JsonObject(obj.OrderBy(x=>x.Key,StringComparer.Ordinal).Select(x=>new KeyValuePair<string,JsonNode?>(x.Key,x.Value is null ? null : Canonical(x.Value)))),
        JsonArray array => new JsonArray(array.Select(x=>x is null ? null : Canonical(x)).ToArray()),
        _ => node.DeepClone()
    };
    static JsonArray Strings(IEnumerable<string> values) => new(values.Select(x=>(JsonNode?)JsonValue.Create(x)).ToArray());
    static string[] StringArray(JsonObject obj,string key) => obj[key] is JsonArray array ? array.Select(x=>x?.GetValue<string>() ?? throw new ReviewBlocked("invalid_"+key)).ToArray() : [];
    static int Number(JsonObject obj,string key,int fallback) => obj[key]?.GetValue<int>() ?? fallback;
    static bool Within(string path,string root) => path==root || path.StartsWith(root.TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,StringComparison.Ordinal);
    static string RealPath(string path)
    {
        path=Path.GetFullPath(path); var root=Path.GetPathRoot(path)!; var resolved=root;
        foreach(var part in path[root.Length..].Split(Path.DirectorySeparatorChar,StringSplitOptions.RemoveEmptyEntries)) {
            var next=Path.Combine(resolved,part);
            var exists=File.Exists(next) || Directory.Exists(next);
            if(exists) {
                var matches=Directory.EnumerateFileSystemEntries(resolved).Where(entry=>string.Equals(Path.GetFileName(entry),part,StringComparison.OrdinalIgnoreCase)).ToArray();
                var exact=matches.Where(entry=>string.Equals(Path.GetFileName(entry),part,StringComparison.Ordinal)).ToArray();
                if(exact.Length==1) next=exact[0];
                else if(exact.Length==0 && matches.Length==1) next=matches[0];
                else throw new ReviewBlocked("unresolved_or_ambiguous_filesystem_case_alias");
            }
            if(exists && (File.GetAttributes(next)&FileAttributes.ReparsePoint)!=0) {
                FileSystemInfo info=Directory.Exists(next) ? new DirectoryInfo(next) : new FileInfo(next);
                resolved=RealPath(info.ResolveLinkTarget(true)?.FullName ?? throw new ReviewBlocked("unresolved_symlink_ancestor"));
            } else resolved=next;
        }
        return Path.GetFullPath(resolved);
    }
    static void CheckStore(string store,JsonObject binding)
    {
        var target=RealPath(store);
        if(Within(target,RealPath(Path.Combine(Text(binding,"codex_home"),"automations"))) || Within(target,RealPath(Path.GetDirectoryName(Text(binding,"memory"))!)) || Within(target,RealPath(Path.GetDirectoryName(Text(binding,"definition"))!))) throw new ReviewBlocked("store_must_be_outside_automation_definition_and_memory_directory");
    }
    static FileStream LockRun(JsonObject run) { var store=Text(run,"store"); CheckStore(store,run["binding"]!.AsObject()); return Lock(store); }
    static void NoLink(string path)
    {
        if(File.Exists(path) || Directory.Exists(path))
            if((File.GetAttributes(path)&FileAttributes.ReparsePoint)!=0) throw new ReviewBlocked("symlink_not_allowed: "+path);
    }
    static void PrivateDirectory(string path)
    {
        NoLink(path);
        if(!Directory.Exists(path)) Directory.CreateDirectory(path,DirectoryMode);
        File.SetUnixFileMode(path,DirectoryMode);
    }
    static void WriteBytes(string path,byte[] bytes,bool replace=false)
    {
        NoLink(path);
        var temporary=path+".tmp-"+Guid.NewGuid().ToString("N");
        try {
            using(var stream=new FileStream(temporary,new FileStreamOptions { Mode=FileMode.CreateNew,Access=FileAccess.Write,Share=FileShare.None,UnixCreateMode=FileModePrivate })) { stream.Write(bytes); stream.Flush(true); }
            File.Move(temporary,path,replace);
            File.SetUnixFileMode(path,FileModePrivate);
        } finally { if(File.Exists(temporary)) File.Delete(temporary); }
    }
    static void WriteJson(string path,JsonObject obj,bool replace=false) => WriteBytes(path,Encoding.UTF8.GetBytes(obj.ToJsonString()),replace);
    static FileStream Lock(string store)
    {
        PrivateDirectory(store);
        var path=Path.Combine(store,".lock"); NoLink(path);
        try { var stream=new FileStream(path,new FileStreamOptions { Mode=FileMode.OpenOrCreate,Access=FileAccess.ReadWrite,Share=FileShare.None,UnixCreateMode=FileModePrivate }); File.SetUnixFileMode(path,FileModePrivate); return stream; }
        catch(IOException) { throw new ReviewBlocked("store_busy_retry"); }
    }
    static JsonObject NewResult(string status) => new() { ["schema_version"]=1,["status"]=status };
    [DllImport("libc",EntryPoint="kill",SetLastError=true)]
    static extern int SignalProcessGroup(int pid,int signal);
    static (int Exit,byte[] Out,byte[] Error) Run(string executable,IEnumerable<string> args,int timeoutSeconds=120,int maxOutputBytes=16777216)
        => RunBounded(executable,args,timeoutSeconds,maxOutputBytes).GetAwaiter().GetResult();
    static async Task<(int Exit,byte[] Out,byte[] Error)> RunBounded(string executable,IEnumerable<string> args,int timeoutSeconds,int maxOutputBytes)
    {
        if(timeoutSeconds<1 || timeoutSeconds>120 || maxOutputBytes<2000 || maxOutputBytes>16777216) throw new ReviewBlocked("invalid_process_bounds");
        var start=new ProcessStartInfo(executable) { UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true };
        // ProcessStartInfo has no Unix session option. This startup shim uses the
        // already required Python runtime, creates an owned group, then execs the
        // original invocation. C# owns all supervision and record processing.
        var readyBytes=Encoding.ASCII.GetBytes("wiki-review-owned-group\n");
        start.ArgumentList.Add("-I"); start.ArgumentList.Add("-c");
        start.ArgumentList.Add("import os,sys;os.setsid();sys.stderr.buffer.write(b'wiki-review-owned-group\\n');sys.stderr.buffer.flush();os.execv(sys.executable,[sys.executable,*sys.argv[1:]])");
        foreach(var arg in args) start.ArgumentList.Add(arg);
        using var process=Process.Start(start) ?? throw new ReviewBlocked("process_start_failed");
        using var output=new MemoryStream(); using var errors=new MemoryStream();
        using var cancellation=new CancellationTokenSource();
        var outputLimit=new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var groupReady=0; var captured=0; var retention=maxOutputBytes;
        void Retain(MemoryStream target,ReadOnlySpan<byte> bytes) {
            var previous=Interlocked.Add(ref captured,bytes.Length)-bytes.Length;
            var count=Math.Clamp(retention-previous,0,bytes.Length);
            if(count>0) lock(target) target.Write(bytes[..count]);
            if(count<bytes.Length) outputLimit.TrySetResult();
        }
        async Task Copy(Stream source,MemoryStream target,bool handshake) {
            try {
                if(handshake) {
                    var header=new byte[readyBytes.Length]; var length=0;
                    while(length<header.Length) { var read=await source.ReadAsync(header.AsMemory(length),cancellation.Token); if(read==0) break; length+=read; }
                    if(length==header.Length && header.SequenceEqual(readyBytes)) Interlocked.Exchange(ref groupReady,1);
                    else Retain(target,header.AsSpan(0,length));
                }
                var buffer=new byte[8192];
                while(true) { var read=await source.ReadAsync(buffer,cancellation.Token); if(read==0) break; Retain(target,buffer.AsSpan(0,read)); if(outputLimit.Task.IsCompleted) return; }
            } catch(OperationCanceledException) { } catch(IOException) when(cancellation.IsCancellationRequested) { } catch(ObjectDisposedException) when(cancellation.IsCancellationRequested) { }
        }
        var stdout=Copy(process.StandardOutput.BaseStream,output,false);
        var stderr=Copy(process.StandardError.BaseStream,errors,true);
        var completion=Task.WhenAll(process.WaitForExitAsync(cancellation.Token),stdout,stderr);
        var deadline=Task.Delay(TimeSpan.FromSeconds(timeoutSeconds));
        var winner=await Task.WhenAny(completion,deadline,outputLimit.Task);
        var exit=outputLimit.Task.IsCompleted ? 125 : winner==deadline ? 124 : 0;
        if(exit!=0) {
            // The session handshake proves this negative process-group ID belongs
            // to our invocation, including when its original parent already exited.
            if(Volatile.Read(ref groupReady)==1) SignalProcessGroup(-process.Id,9);
            try { if(!process.HasExited) process.Kill(true); } catch(InvalidOperationException) { } catch(System.ComponentModel.Win32Exception) { }
            if(await Task.WhenAny(completion,Task.Delay(2000))!=completion) {
                cancellation.Cancel(); process.StandardOutput.Dispose(); process.StandardError.Dispose();
                await Task.WhenAny(completion,Task.Delay(1000));
            }
        }
        try { if(completion.IsCompleted) await completion; } catch(OperationCanceledException) { } catch(IOException) { exit=126; }
        byte[] outBytes,errorBytes; lock(output) outBytes=output.ToArray(); lock(errors) errorBytes=errors.ToArray();
        if(exit!=0) {
            var reason=exit==124 ? "subprocess_timeout" : exit==125 ? "subprocess_output_limit_exceeded" : "subprocess_drain_failed";
            var diagnostic=Encoding.UTF8.GetBytes("\n"+new JsonObject { ["status"]="blocked",["reason"]=reason,["timeout_seconds"]=timeoutSeconds,["max_output_bytes"]=maxOutputBytes }.ToJsonString()+"\n");
            // Keep complete successful output up to the actual configured cap.
            // Only a failed invocation trades some retained tail for diagnostics.
            var excess=Math.Max(0,outBytes.Length+errorBytes.Length+diagnostic.Length-maxOutputBytes);
            var trimOut=Math.Min(excess,outBytes.Length); if(trimOut>0) Array.Resize(ref outBytes,outBytes.Length-trimOut);
            excess-=trimOut; if(excess>0) Array.Resize(ref errorBytes,errorBytes.Length-excess);
            errorBytes=[..errorBytes,..diagnostic];
        }
        if(exit==0) exit=process.ExitCode;
        return(exit,outBytes,errorBytes);
    }
    static JsonObject CaptureBinding(JsonObject request)
    {
        var memory=Full(request,"memory"); var definition=Full(request,"definition"); var resolver=Full(request,"resolver");
        var max=Number(request,"max_sessions",100); if(max<1 || max>500) throw new ReviewBlocked("max_sessions_must_be_1_to_500");
        var batch=request["batch_size"] is null ? 0 : Number(request,"batch_size",0);
        if(batch<0 || batch>100 || (request["batch_size"] is not null && batch==0)) throw new ReviewBlocked("batch_size_must_be_1_to_100");
        var timeout=Number(request,"timeout_seconds",120); var output=Number(request,"max_output_bytes",16777216);
        if(timeout<1 || timeout>120 || output<2000 || output>16777216) throw new ReviewBlocked("invalid_process_bounds");
        var approved=StringArray(request,"approved_missing_carry_ids");
        var missingPolicy=request["missing_session_policy"] is null ? "block" : Text(request,"missing_session_policy");
        if(missingPolicy is not ("block" or "ignore")) throw new ReviewBlocked("missing_session_policy_must_be_block_or_ignore");
        var (memoryHeader,memoryHistory)=MemoryParts(memory);
        if(!System.Text.RegularExpressions.Regex.IsMatch(memoryHeader,@"^(Processed window end|Last review):",System.Text.RegularExpressions.RegexOptions.Multiline)
            && System.Text.RegularExpressions.Regex.IsMatch(memoryHistory,@"^Last review:",System.Text.RegularExpressions.RegexOptions.Multiline)) throw new ReviewBlocked("historical_last_review_without_header_cutoff");
        // A present Processed cursor owns selection. The resolver validates it;
        // an ignored scheduler boundary must not invalidate an existing run.
        var prompt=System.Text.RegularExpressions.Regex.IsMatch(memoryHeader,@"^Processed window end:",System.Text.RegularExpressions.RegexOptions.Multiline)
            ? JsonValue.Create("") : request["prompt_last_run"]?.DeepClone() ?? JsonValue.Create("");
        return new JsonObject {
            ["automation_id"]=Text(request,"automation_id"),["definition"]=definition,["definition_sha256"]=FileHash(definition),
            ["memory"]=memory,["memory_sha256"]=FileHash(memory),["resolver"]=resolver,["resolver_sha256"]=FileHash(resolver),
            ["memory_checkpoint_sha256"]=CheckpointHash(memory),
            ["helper"]=HelperPath(),["helper_sha256"]=FileHash(HelperPath()),["codex_home"]=Full(request,"codex_home"),
            ["python"]=Text(request,"python"),["exclude_session_id"]=Text(request,"exclude_session_id"),["max_sessions"]=max,
            ["batch_size"]=batch,["timeout_seconds"]=timeout,["max_output_bytes"]=output,
            ["prompt_last_run"]=prompt,["approved_missing_carry_ids"]=Strings(approved),["missing_session_policy"]=missingPolicy
        };
    }
    // CallerFilePath keeps source identity available in ordinary file-based runs.
    static string HelperPath([System.Runtime.CompilerServices.CallerFilePath]string path="") => Path.GetFullPath(path);
    static (string Header,string History) MemoryParts(string path)
    {
        var text=File.ReadAllText(path).Replace("\r\n","\n");
        var history=System.Text.RegularExpressions.Regex.Match(text,@"^## ",System.Text.RegularExpressions.RegexOptions.Multiline);
        return history.Success ? (text[..history.Index],text[history.Index..]) : (text,"");
    }
    static string CheckpointHash(string path)
    {
        var header=MemoryParts(path).Header;
        var fields=new JsonObject();
        foreach(var key in new[]{"Processed window end","Carry-forward sessions","Authoritative source tips","Docs reviewed tip"}) {
            var values=System.Text.RegularExpressions.Regex.Matches(header,"^"+System.Text.RegularExpressions.Regex.Escape(key)+@":\s*([^\r\n]*)$",System.Text.RegularExpressions.RegexOptions.Multiline);
            if(values.Count>1) throw new ReviewBlocked("ambiguous_checkpoint_"+key);
            fields[key]=values.Count==1 ? JsonValue.Create(values[0].Groups[1].Value.Trim()) : null;
        }
        if(fields["Docs reviewed tip"] is not null) {
            var value=JsonNode.Parse(fields["Docs reviewed tip"]!.GetValue<string>(),documentOptions:new JsonDocumentOptions { AllowDuplicateProperties=false })?.AsObject() ?? throw new ReviewBlocked("invalid_docs_reviewed_tip");
            if(value.Count!=3 || !value.ContainsKey("repository") || !value.ContainsKey("ref") || !value.ContainsKey("sha") || !Path.IsPathFullyQualified(Text(value,"repository")) || Path.GetFullPath(Text(value,"repository"))!=Text(value,"repository") || Text(value,"ref")!="refs/remotes/origin/main" || !System.Text.RegularExpressions.Regex.IsMatch(Text(value,"sha"),"^[0-9a-f]{40}$")) throw new ReviewBlocked("invalid_docs_reviewed_tip");
        }
        if(fields["Processed window end"] is null) {
            var values=System.Text.RegularExpressions.Regex.Matches(header,@"^Last review:\s*([^\r\n]*)$",System.Text.RegularExpressions.RegexOptions.Multiline);
            if(values.Count>1) throw new ReviewBlocked("ambiguous_legacy_checkpoint");
            fields["Last review"]=values.Count==1 ? JsonValue.Create(values[0].Groups[1].Value.Trim()) : null;
        }
        return JsonHash(fields);
    }
    static string BindingHash(JsonObject binding) { var identity=binding.DeepClone().AsObject(); identity.Remove("memory_sha256"); return JsonHash(identity); }
    public static JsonObject Capture(JsonObject request)
    {
        var binding=CaptureBinding(request);
        var store=request["store"] is null ? Path.Combine(Text(binding,"codex_home"),"automation-runs","keep-ncg-wiki-current") : Full(request,"store");
        CheckStore(store,binding);
        using var mutex=Lock(store);
        var activePath=Path.Combine(store,"active.json");
        if(File.Exists(activePath)) {
            var active=ReadJson(activePath);
            var existingDirectory=Text(active,"run_directory");
            if(Text(active,"binding_sha256")!=BindingHash(binding)) throw CaptureError("active_inputs_changed_explicit_invalidation_required",existingDirectory);
            try { var existing=Load(existingDirectory,false); return CaptureResult(existing,"resumed"); }
            catch(Exception ex) { if(ex.Data["run_directory"] is not null) throw; throw CaptureError(ex.Message,existingDirectory); }
        }
        var directory=Path.Combine(store,"run-"+Guid.NewGuid().ToString("N")); PrivateDirectory(directory);
        var run=new JsonObject { ["schema_version"]=1,["run_directory"]=directory,["store"]=store,["binding"]=binding,["binding_sha256"]=BindingHash(binding),["state"]="capturing" };
        WriteJson(Path.Combine(directory,"run.json"),run);
        WriteJson(activePath,new JsonObject { ["schema_version"]=1,["binding_sha256"]=BindingHash(binding),["run_directory"]=directory });
        Console.Error.WriteLine(new JsonObject { ["schema_version"]=1,["status"]="capture_started",["run_directory"]=directory,["active_receipt"]=activePath }.ToJsonString());
        WriteBytes(Path.Combine(directory,"resolver.py"),File.ReadAllBytes(Text(binding,"resolver")));
        WriteBytes(Path.Combine(directory,"memory.md"),File.ReadAllBytes(Text(binding,"memory")));
        WriteBytes(Path.Combine(directory,"definition.toml"),File.ReadAllBytes(Text(binding,"definition")));
        if(Number(binding,"batch_size",0)>0) {
            run["batch_receipts"]=new JsonArray(); run["state"]="resolving";
            ExecuteBatch(run,0,true);
            return CaptureResult(Load(directory,false),"captured");
        }
        var index=Path.Combine(directory,"index.jsonl");
        var arguments=new List<string> { Path.Combine(directory,"resolver.py"),"--codex-home",Text(binding,"codex_home"),"--memory",Path.Combine(directory,"memory.md"),"--exclude-session-id",Text(binding,"exclude_session_id"),"--max-sessions",Number(binding,"max_sessions",100).ToString(),"--compact","--recent","0","--save-index-snapshot",index };
        if(TextOrEmpty(binding,"prompt_last_run") is { Length:>0 } cutoff) { arguments.Add("--prompt-last-run"); arguments.Add(cutoff); }
        var process=Run(Text(binding,"python"),arguments,Number(binding,"timeout_seconds",120),Number(binding,"max_output_bytes",16777216));
        WriteBytes(Path.Combine(directory,"resolver.stdout"),process.Out);
        WriteBytes(Path.Combine(directory,"resolver.stderr"),process.Error);
        WriteBytes(Path.Combine(directory,"manifest.json"),process.Out);
        WriteBytes(Path.Combine(directory,"resolver.exit"),Encoding.UTF8.GetBytes(process.Exit.ToString()));
        if(File.Exists(index)) File.SetUnixFileMode(index,FileModePrivate);
        var files=new JsonObject();
        foreach(var file in new[]{"resolver.py","memory.md","definition.toml","resolver.stdout","resolver.stderr","manifest.json","resolver.exit","index.jsonl"})
            if(File.Exists(Path.Combine(directory,file))) files[file]=FileHash(Path.Combine(directory,file));
        run["files"]=files; run["resolver_exit"]=process.Exit; run["state"]="captured";
        WriteJson(Path.Combine(directory,"run.json"),run,true);
        WriteJson(activePath,new JsonObject { ["schema_version"]=1,["binding_sha256"]=BindingHash(binding),["run_directory"]=directory,["capture_sha256"]=JsonHash(run) },true);
        if(process.Exit is not (0 or 2)) throw CaptureError("resolver_failed_exit_"+process.Exit,directory,process.Exit);
        try { var loaded=Load(directory); return CaptureResult(loaded,"captured"); }
        catch(Exception ex) { throw CaptureError(ex.Message,directory,process.Exit); }
    }
    static ReviewBlocked CaptureError(string reason,string directory,int? exit=null)
    {
        var error=new ReviewBlocked(reason); error.Data["run_directory"]=directory;
        error.Data["resolver_stdout"]=Path.Combine(directory,"resolver.stdout"); error.Data["resolver_stderr"]=Path.Combine(directory,"resolver.stderr"); error.Data["resolver_exit_file"]=Path.Combine(directory,"resolver.exit");
        if(exit.HasValue) error.Data["resolver_exit"]=exit.Value; return error;
    }
    static string TextOrEmpty(JsonObject obj,string key)=>obj[key]?.GetValue<string>() ?? "";
    static JsonObject Load(string directory,bool requireComplete=true)
    {
        directory=Path.GetFullPath(directory); NoLink(directory);
        var run=ReadJson(Path.Combine(directory,"run.json"));
        if(Number(run,"schema_version",0)!=1 || Text(run,"run_directory")!=directory || (Text(run,"state")!="captured" && (requireComplete || Text(run,"state")!="resolving"))) throw new ReviewBlocked("incomplete_or_invalid_capture");
        if(run["invalidated"] is not null) throw new ReviewBlocked("capture_invalidated");
        var binding=run["binding"]!.AsObject();
        if(Text(binding,"helper")!=HelperPath()) throw new ReviewBlocked("current_helper_identity_changed");
        var store=Text(run,"store"); if(!Within(directory,store)) throw new ReviewBlocked("foreign_capture_store");
        var active=ReadJson(Path.Combine(store,"active.json"));
        if(Text(active,"run_directory")!=directory || Text(active,"capture_sha256")!=JsonHash(run) || Text(active,"binding_sha256")!=Text(run,"binding_sha256")) throw new ReviewBlocked("corrupt_or_inactive_capture_descriptor");
        if(BindingHash(binding)!=Text(run,"binding_sha256")) throw new ReviewBlocked("corrupt_capture_binding");
        foreach(var name in new[]{"definition","resolver","helper"})
            if(FileHash(Text(binding,name))!=Text(binding,name+"_sha256")) throw new ReviewBlocked("current_"+name+"_changed");
        if(CheckpointHash(Text(binding,"memory"))!=Text(binding,"memory_checkpoint_sha256")) throw new ReviewBlocked("current_memory_checkpoint_changed");
        var files=run["files"]!.AsObject();
        if(Number(binding,"batch_size",0)>0) {
            foreach(var name in new[]{"resolver.py","memory.md","definition.toml","index.jsonl"})
                if(files[name] is null || FileHash(Path.Combine(directory,name))!=Text(files,name)) throw new ReviewBlocked("missing_or_corrupt_snapshot_"+name);
            foreach(var pair in new[]{("resolver.py","resolver_sha256"),("memory.md","memory_sha256"),("definition.toml","definition_sha256")}) if(Text(files,pair.Item1)!=Text(binding,pair.Item2)) throw new ReviewBlocked("snapshot_input_hash_mismatch");
            ValidateBatches(run);
            if(Text(run,"state")=="captured") {
                if(files["manifest.json"] is null || FileHash(Path.Combine(directory,"manifest.json"))!=Text(files,"manifest.json") || JsonHash(ReadJson(Path.Combine(directory,"manifest.json")))!=JsonHash(AggregateBatches(run))) throw new ReviewBlocked("corrupt_aggregate_manifest");
                if(!ExtractionAllowed(run,ReadJson(Path.Combine(directory,"manifest.json")))) throw new ReviewBlocked("resolver_unsafe_capture");
            }
            return run;
        }
        foreach(var name in new[]{"resolver.py","memory.md","definition.toml","resolver.stdout","resolver.stderr","manifest.json","resolver.exit","index.jsonl"})
            if(files[name] is null || FileHash(Path.Combine(directory,name))!=Text(files,name)) throw new ReviewBlocked("missing_or_corrupt_snapshot_"+name);
        foreach(var pair in new[]{("resolver.py","resolver_sha256"),("memory.md","memory_sha256"),("definition.toml","definition_sha256")}) if(Text(files,pair.Item1)!=Text(binding,pair.Item2)) throw new ReviewBlocked("snapshot_input_hash_mismatch");
        var manifest=ReadJson(Path.Combine(directory,"manifest.json"));
        if(manifest["snapshot"]?["sha256"]?.GetValue<string>()!=Text(files,"index.jsonl")) throw new ReviewBlocked("manifest_index_hash_mismatch");
        if(!ExtractionAllowed(run,manifest)) throw new ReviewBlocked("resolver_unsafe_capture");
        return run;
    }
    static bool ExtractionAllowed(JsonObject run,JsonObject manifest)
    {
        var exit=Number(run,"resolver_exit",-1); var safe=manifest["window"]?["safe_to_persist"]?.GetValue<bool>();
        var sessions=manifest["sessions"]?.AsArray(); if(sessions is null) return false;
        if(exit==0 && safe==true) return sessions.All(x=>x is JsonObject session && Text(session,"status")=="resolved" && session["rollout_window"]?["state"]?.GetValue<string>() is not ("unknown" or "unreadable"));
        if(exit!=2 || safe!=false) return false;
        var approved=StringArray(run["binding"]!.AsObject(),"approved_missing_carry_ids");
        var ignoreMissing=TextOrEmpty(run["binding"]!.AsObject(),"missing_session_policy")=="ignore";
        if((!ignoreMissing && approved.Length==0) || approved.Distinct(StringComparer.Ordinal).Count()!=approved.Length) return false;
        var missing=new HashSet<string>(StringComparer.Ordinal);
        var carriedMissing=new HashSet<string>(StringComparer.Ordinal);
        foreach(var node in sessions) {
            var session=node!.AsObject(); var status=Text(session,"status");
            if(status=="resolved") {
                if(session["rollout_window"]?["state"]?.GetValue<string>() is "unknown" or "unreadable") return false;
                continue;
            }
            var id=Text(session,"id");
            // Deleted sessions have no storage metadata; malformed or unreadable
            // stored histories remain blockers and cannot enter scope pagination.
            if(status!="missing" || session["path"] is not null || session["meta"] is not null || session["rollout_window"] is not null) return false;
            var reasons=StringArray(session,"selection_reasons");
            var carryOnly=reasons.SequenceEqual(new[]{"carry_forward"},StringComparer.Ordinal);
            if(ignoreMissing) {
                if(!carryOnly && !reasons.SequenceEqual(new[]{"window"},StringComparer.Ordinal) && !reasons.SequenceEqual(new[]{"window","carry_forward"},StringComparer.Ordinal)) return false;
            }
            else if(!carryOnly || !approved.Contains(id,StringComparer.Ordinal)) return false;
            if(!missing.Add(id)) return false;
            if(reasons.Contains("carry_forward",StringComparer.Ordinal)) carriedMissing.Add(id);
        }
        if(missing.Count==0) return false;
        var carries=manifest["window"]?["carry_forward_from_memory"]?.AsArray().Select(x=>Text(x!.AsObject(),"id")).ToHashSet(StringComparer.Ordinal);
        if(carries is null || !carriedMissing.IsSubsetOf(carries)) return false;
        var diagnosed=new HashSet<string>(StringComparer.Ordinal);
        foreach(var node in manifest["diagnostics"]!.AsArray()) {
            var diagnostic=node!.AsObject();
            switch(Text(diagnostic,"code")) {
                case "missing_rollout":
                    if(!missing.Contains(Text(diagnostic,"session_id")) || !diagnosed.Add(Text(diagnostic,"session_id"))) return false;
                    break;
                case "carry_forward_index_row_missing_recovered":
                    if(StringArray(diagnostic,"session_ids").Any(id=>!(ignoreMissing ? carries : missing).Contains(id))) return false;
                    break;
                case "duplicate_index_rows_collapsed": break;
                case "embedded_session_history_detected":
                    if(!manifest["sessions"]!.AsArray().Any(x=>Text(x!.AsObject(),"id")==Text(diagnostic,"session_id") && Text(x.AsObject(),"status")=="resolved")) return false;
                    break;
                default: return false;
            }
        }
        return diagnosed.SetEquals(missing);
    }
    static JsonObject CaptureResult(JsonObject run,string status)
    {
        var result=NewResult(status); var directory=Text(run,"run_directory");
        if(Number(run["binding"]!.AsObject(),"batch_size",0)>0) {
            if(run["batch_failure"] is JsonObject failure) throw BatchError(run,failure);
            result["preserved_failed_batches"]=run["failed_batch_receipts"]?.AsArray().Count ?? 0;
            result["selection_count"]=run["selection_count"]?.DeepClone(); result["next_offset"]=run["next_offset"]?.DeepClone();
            result["selection_plan_sha256"]=run["selection_plan_sha256"]?.DeepClone();
            if(Text(run,"state")=="resolving") {
                result["status"]="resolving"; result["run_directory"]=directory; result["index_snapshot"]=Path.Combine(directory,"index.jsonl"); result["index_sha256"]=run["files"]?["index.jsonl"]?.DeepClone();
                result["extraction_allowed"]=false; result["checkpoint_permission"]="none_incomplete_resolution"; return result;
            }
        }
        result["run_directory"]=directory; result["manifest"]=Path.Combine(directory,"manifest.json"); result["index_snapshot"]=Path.Combine(directory,"index.jsonl");
        result["manifest_sha256"]=run["files"]?["manifest.json"]?.DeepClone(); result["index_sha256"]=run["files"]?["index.jsonl"]?.DeepClone(); result["resolver_exit"]=run["resolver_exit"]?.DeepClone();
        result["extraction_allowed"]=true;
        var manifest=ReadJson(Path.Combine(directory,"manifest.json"));
        result["resolver_safe_to_persist"]=manifest["window"]?["safe_to_persist"]?.DeepClone();
        result["missing_session_policy"]=TextOrEmpty(run["binding"]!.AsObject(),"missing_session_policy") is "ignore" ? "ignore" : "block";
        result["ignored_missing_session_ids"]=Strings(manifest["sessions"]!.AsArray().Where(x=>Text(x!.AsObject(),"status")=="missing").Select(x=>Text(x!.AsObject(),"id")));
        result["checkpoint_permission"]="none_final_review_and_delivery_required";
        return result;
    }

    public static JsonObject ResolveBatch(JsonObject request)
    {
        var directory=Full(request,"run_directory"); var descriptor=ReadJson(Path.Combine(directory,"run.json"));
        using var lease=Lock(Text(descriptor,"store"));
        var run=Load(directory,false); var binding=run["binding"]!.AsObject();
        if(Number(binding,"batch_size",0)==0) throw new ReviewBlocked("batch_resolution_not_enabled");
        var offset=Number(request,"offset",-1);
        var existing=run["batch_receipts"]!.AsArray().FirstOrDefault(x=>Number(x!.AsObject(),"offset",-1)==offset);
        if(existing is not null) { var reused=CaptureResult(run,Text(run,"state")=="captured" ? "resumed" : "resolving"); reused["batch_reused"]=true; reused["batch_output"]=existing["output"]!.DeepClone(); return reused; }
        if(offset!=Number(run,"next_offset",0) || Text(run,"state")=="captured") throw new ReviewBlocked("batch_offset_not_next");
        if(run["batch_failure"] is JsonObject failure) {
            if(request["retry_failed"]?.GetValue<bool>()!=true || Number(failure,"exit",-1) is not (124 or 125 or 126)) throw BatchError(run,failure);
            var history=run["failed_batch_receipts"] as JsonArray;
            if(history is null) { history=new JsonArray(); run["failed_batch_receipts"]=history; }
            history.Add(failure.DeepClone());
            run.Remove("batch_failure");
        }
        ExecuteBatch(run,offset,false);
        var completed=Load(directory,false); var result=CaptureResult(completed,"captured"); result["batch_output"]=completed["batch_receipts"]!.AsArray().Last()!["output"]!.DeepClone(); return result;
    }
    static void SaveCapture(JsonObject run)
    {
        WriteJson(Path.Combine(Text(run,"run_directory"),"run.json"),run,true);
        WriteJson(Path.Combine(Text(run,"store"),"active.json"),new JsonObject { ["schema_version"]=1,["binding_sha256"]=run["binding_sha256"]!.DeepClone(),["run_directory"]=run["run_directory"]!.DeepClone(),["capture_sha256"]=JsonHash(run) },true);
    }
    static ReviewBlocked BatchError(JsonObject run,JsonObject failure)
    {
        var error=CaptureError(Text(failure,"reason"),Text(run,"run_directory"),Number(failure,"exit",-1));
        error.Data["resolver_stdout"]=Text(failure,"output"); error.Data["resolver_stderr"]=Text(failure,"stderr"); error.Data["resolver_exit_file"]=Text(failure,"exit_file"); return error;
    }
    static void ExecuteBatch(JsonObject run,int offset,bool live)
    {
        var directory=Text(run,"run_directory"); var binding=run["binding"]!.AsObject(); var index=Path.Combine(directory,"index.jsonl");
        var attempts=Path.Combine(directory,"batches"); Directory.CreateDirectory(attempts); File.SetUnixFileMode(attempts,DirectoryMode);
        var prefix=Path.Combine(attempts,$"{offset:D8}-"+Guid.NewGuid().ToString("N"));
        var arguments=new List<string> { Path.Combine(directory,"resolver.py"),"--codex-home",Text(binding,"codex_home"),"--memory",Path.Combine(directory,"memory.md"),"--exclude-session-id",Text(binding,"exclude_session_id"),"--max-sessions",Number(binding,"batch_size",0).ToString(),"--batch-offset",offset.ToString(),"--compact","--recent","0" };
        if(live) { arguments.Add("--save-index-snapshot"); arguments.Add(index); }
        else { arguments.Add("--index-snapshot"); arguments.Add(index); arguments.Add("--expected-index-sha256"); arguments.Add(Text(run["files"]!.AsObject(),"index.jsonl")); }
        if(TextOrEmpty(binding,"prompt_last_run") is { Length:>0 } cutoff) { arguments.Add("--prompt-last-run"); arguments.Add(cutoff); }
        var process=Run(Text(binding,"python"),arguments,Number(binding,"timeout_seconds",120),Number(binding,"max_output_bytes",16777216));
        WriteBytes(prefix+".stdout",process.Out); WriteBytes(prefix+".stderr",process.Error); WriteBytes(prefix+".exit",Encoding.UTF8.GetBytes(process.Exit.ToString()));
        var receipt=new JsonObject { ["offset"]=offset,["output"]=prefix+".stdout",["output_sha256"]=FileHash(prefix+".stdout"),["stderr"]=prefix+".stderr",["stderr_sha256"]=FileHash(prefix+".stderr"),["exit_file"]=prefix+".exit",["exit_sha256"]=FileHash(prefix+".exit"),["exit"]=process.Exit };
        var files=run["files"] as JsonObject ?? new JsonObject(); run["files"]=files;
        foreach(var name in new[]{"resolver.py","memory.md","definition.toml","index.jsonl"}) if(File.Exists(Path.Combine(directory,name))) files[name]=FileHash(Path.Combine(directory,name));
        try {
            if(process.Exit is not (0 or 2)) throw new ReviewBlocked("resolver_failed_exit_"+process.Exit);
            var manifest=ReadJson(prefix+".stdout"); ValidateBatch(run,receipt,manifest,offset);
            run["batch_receipts"]!.AsArray().Add((JsonNode)receipt); run["next_offset"]=manifest["batch"]!["next_offset"]!.DeepClone();
            if(manifest["batch"]!["has_more"]!.GetValue<bool>()==false) {
                var aggregate=AggregateBatches(run); WriteJson(Path.Combine(directory,"manifest.json"),aggregate); files["manifest.json"]=FileHash(Path.Combine(directory,"manifest.json")); run["state"]="captured";
                run["resolver_exit"]=run["batch_receipts"]!.AsArray().Any(x=>Number(x!.AsObject(),"exit",-1)==2) ? 2 : 0;
            }
            SaveCapture(run);
        }
        catch(Exception ex) {
            receipt["reason"]=ex.Message; run["batch_failure"]=receipt; SaveCapture(run); throw BatchError(run,receipt);
        }
    }
    static void ValidateBatch(JsonObject run,JsonObject receipt,JsonObject manifest,int offset)
    {
        var batch=manifest["batch"]?.AsObject() ?? throw new ReviewBlocked("missing_resolution_batch"); var binding=run["binding"]!.AsObject();
        var size=Number(binding,"batch_size",0); var total=Number(batch,"selection_count",-1); var sessions=manifest["sessions"]?.AsArray() ?? throw new ReviewBlocked("missing_batch_sessions");
        if(total<0 || Number(batch,"offset",-1)!=offset || Number(batch,"limit",-1)!=size || sessions.Count!=Math.Min(size,total-offset) || Number(batch,"next_offset",-1)!=offset+sessions.Count || batch["has_more"]?.GetValue<bool>()!=(offset+sessions.Count<total) || manifest["window"]?["safe_to_persist"]?.GetValue<bool>()!=false) throw new ReviewBlocked("invalid_resolution_batch_progress");
        var plan=Text(batch,"selection_plan_sha256"); if(!System.Text.RegularExpressions.Regex.IsMatch(plan,"^[0-9a-f]{64}$")) throw new ReviewBlocked("invalid_selection_plan_digest");
        var snapshot=Text(run["files"]!.AsObject(),"index.jsonl");
        if(manifest["snapshot"]?["sha256"]?.GetValue<string>()!=snapshot) throw new ReviewBlocked("batch_snapshot_changed");
        if(run["selection_count"] is null) {
            run["selection_count"]=total; run["selection_plan_sha256"]=plan;
            run["batch_window_binding"]=BatchWindowBinding(manifest);
        }
        if(Number(run,"selection_count",-1)!=total || Text(run,"selection_plan_sha256")!=plan || JsonHash(run["batch_window_binding"]!)!=JsonHash(BatchWindowBinding(manifest))) throw new ReviewBlocked("batch_selection_or_window_changed");
        var local=manifest.DeepClone().AsObject(); local["window"]!["safe_to_persist"]=batch["safe_for_extraction"]?.DeepClone();
        var localRun=run.DeepClone().AsObject(); localRun["resolver_exit"]=Number(receipt,"exit",-1);
        if(!ExtractionAllowed(localRun,local)) throw new ReviewBlocked("resolver_unsafe_batch");
    }
    static JsonObject BatchWindowBinding(JsonObject manifest) => new() {
        ["snapshot"]=manifest["snapshot"]?.DeepClone(),["cutoff"]=manifest["cutoff"]?.DeepClone(),["excluded_sessions"]=manifest["excluded_sessions"]?.DeepClone(),
        ["start_exclusive"]=manifest["window"]?["start_exclusive"]?.DeepClone(),["end_inclusive"]=manifest["window"]?["end_inclusive"]?.DeepClone(),["cursor_to_persist"]=manifest["window"]?["cursor_to_persist"]?.DeepClone(),["carry_forward_from_memory"]=manifest["window"]?["carry_forward_from_memory"]?.DeepClone()
    };
    static void ValidateBatchFiles(JsonObject receipt)
    {
        foreach(var pair in new[]{("output","output_sha256"),("stderr","stderr_sha256"),("exit_file","exit_sha256")}) if(FileHash(Text(receipt,pair.Item1))!=Text(receipt,pair.Item2)) throw new ReviewBlocked("corrupt_batch_"+pair.Item1);
        if(File.ReadAllText(Text(receipt,"exit_file"))!=Number(receipt,"exit",-1).ToString()) throw new ReviewBlocked("batch_exit_disagrees");
    }
    static void ValidateBatches(JsonObject run)
    {
        var offset=0; var final=false; var ids=new HashSet<string>(StringComparer.Ordinal);
        foreach(var node in run["batch_receipts"]!.AsArray()) {
            if(final) throw new ReviewBlocked("batch_after_terminal"); var receipt=node!.AsObject(); ValidateBatchFiles(receipt); var manifest=ReadJson(Text(receipt,"output")); ValidateBatch(run,receipt,manifest,offset);
            foreach(var session in manifest["sessions"]!.AsArray()) if(!ids.Add(Text(session!.AsObject(),"id"))) throw new ReviewBlocked("duplicate_batch_session");
            offset=Number(manifest["batch"]!.AsObject(),"next_offset",-1); final=manifest["batch"]!["has_more"]!.GetValue<bool>()==false;
        }
        if(offset!=Number(run,"next_offset",0) || (Text(run,"state")=="captured")!=final) throw new ReviewBlocked("incomplete_batch_chain");
        if(run["batch_failure"] is JsonObject failure) ValidateBatchFiles(failure);
        if(run["failed_batch_receipts"] is JsonArray history) foreach(var failureNode in history) ValidateBatchFiles(failureNode!.AsObject());
    }
    static JsonObject AggregateBatches(JsonObject run)
    {
        var sessions=new JsonArray(); var carry=new JsonArray(); var diagnostics=new JsonArray(); var seenDiagnostics=new HashSet<string>(StringComparer.Ordinal); JsonObject? result=null; var offset=0; var complete=false;
        using var plan=IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        foreach(var node in run["batch_receipts"]!.AsArray()) {
            var receipt=node!.AsObject(); ValidateBatchFiles(receipt); var manifest=ReadJson(Text(receipt,"output")); ValidateBatch(run,receipt,manifest,offset);
            result ??= manifest.DeepClone().AsObject();
            foreach(var session in manifest["sessions"]!.AsArray()) {
                var encoded=Encoding.UTF8.GetBytes(Text(session!.AsObject(),"id")); var length=new byte[8]; System.Buffers.Binary.BinaryPrimitives.WriteUInt64BigEndian(length,(ulong)encoded.Length); plan.AppendData(length); plan.AppendData(encoded); sessions.Add(session.DeepClone());
            }
            foreach(var item in manifest["window"]!["carry_forward_to_persist"]!.AsArray()) carry.Add(item?.DeepClone());
            foreach(var item in manifest["diagnostics"]!.AsArray()) if(item is not null && seenDiagnostics.Add(JsonHash(item))) diagnostics.Add(item.DeepClone());
            offset=Number(manifest["batch"]!.AsObject(),"next_offset",-1); complete=manifest["batch"]!["has_more"]!.GetValue<bool>()==false;
        }
        if(result is null || !complete || offset!=Number(run,"selection_count",-1) || Convert.ToHexStringLower(plan.GetHashAndReset())!=Text(run,"selection_plan_sha256")) throw new ReviewBlocked("incomplete_or_changed_selection_plan");
        result.Remove("batch"); result["sessions"]=sessions; result["diagnostics"]=diagnostics; result["window"]!["carry_forward_to_persist"]=carry;
        result["window"]!["safe_to_persist"]=!run["batch_receipts"]!.AsArray().Any(x=>Number(x!.AsObject(),"exit",-1)!=0);
        return result;
    }

    // Summary selection and extraction form one vertical slice. Only the existing
    // extractor reads rollout records; this helper checks its bounded output.
    static (JsonObject Run,JsonObject Selection,string Folder) Selection(JsonObject request)
    {
        var run=Load(Full(request,"run_directory"));
        var directory=Text(run,"run_directory");
        var extractor=Full(request,"extractor");
        var scope=request["scope"]?.AsObject() ?? throw new ReviewBlocked("scope_required");
        var roots=StringArray(scope,"cwd_roots").Select(Path.GetFullPath).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();
        foreach(var root in roots) {
            if(!Path.IsPathFullyQualified(root) || root==Path.GetPathRoot(root) || root.Split(Path.DirectorySeparatorChar).Length<3 || Within(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),root) || (!Directory.Exists(Path.Combine(root,".git")) && !File.Exists(Path.Combine(root,".git")))) throw new ReviewBlocked("scope_root_must_be_concrete_existing_repository");
        }
        foreach(var raw in StringArray(scope,"cwd_roots")) if(!Path.IsPathFullyQualified(raw) || raw.Split(Path.DirectorySeparatorChar).Contains("..")) throw new ReviewBlocked("invalid_scope_root");
        var tails=StringArray(scope,"worktree_tails").Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();
        foreach(var tail in tails) if(tail is "." or ".." || !System.Text.RegularExpressions.Regex.IsMatch(tail,@"^[A-Za-z0-9][A-Za-z0-9._-]*$")) throw new ReviewBlocked("invalid_worktree_tail");
        if(roots.Length+tails.Length==0) throw new ReviewBlocked("bounded_path_scope_required");
        var normalized=new JsonObject { ["cwd_roots"]=Strings(roots),["worktree_tails"]=Strings(tails) };
        var manifest=ReadJson(Path.Combine(directory,"manifest.json"));
        var sessions=manifest["sessions"]?.AsArray() ?? throw new ReviewBlocked("manifest_sessions_required");
        var ids=new List<string>(); var allIds=new HashSet<string>(StringComparer.Ordinal);
        var worktrees=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),".codex","worktrees");
        foreach(var node in sessions) {
            var session=node!.AsObject(); var id=Text(session,"id"); if(!allIds.Add(id)) throw new ReviewBlocked("duplicate_manifest_session_id");
            var raw=session["meta"]?["cwd"]?.GetValue<string>();
            if(raw is null || !Path.IsPathFullyQualified(raw) || raw.Split(Path.DirectorySeparatorChar).Contains("..")) continue;
            var cwd=Path.GetFullPath(raw); var relative=Path.GetRelativePath(worktrees,cwd).Split(Path.DirectorySeparatorChar);
            if(roots.Any(root=>Within(cwd,root)) || (Within(cwd,worktrees) && relative.Length>=2 && tails.Contains(relative[1],StringComparer.Ordinal))) ids.Add(id);
        }
        var selection=new JsonObject {
            ["schema_version"]=1,["manifest_sha256"]=run["files"]?["manifest.json"]?.DeepClone(),
            ["scope"]=normalized,["eligible_ids"]=Strings(ids),["extractor"]=extractor,["extractor_sha256"]=FileHash(extractor),
            ["python"]=request["python"]?.DeepClone() ?? run["binding"]?["python"]?.DeepClone()
        };
        if(Text(selection,"python")!=Text(run["binding"]!.AsObject(),"python")) throw new ReviewBlocked("python_must_match_capture");
        var selectionPath=Path.Combine(directory,"selection.json");
        if(File.Exists(selectionPath)) { if(JsonHash(ReadJson(selectionPath))!=JsonHash(selection)) throw new ReviewBlocked("selection_or_extractor_changed"); }
        else WriteJson(selectionPath,selection);
        var folder=Path.Combine(directory,"pages"); PrivateDirectory(folder);
        return (run,selection,folder);
    }
    static JsonObject SourcePins(JsonObject run,IEnumerable<string> ids)
    {
        var directory=Text(run,"run_directory");
        var sessions=ReadJson(Path.Combine(directory,"manifest.json"))["sessions"]!.AsArray();
        var pins=new JsonObject();
        foreach(var id in ids) {
            var session=sessions.Select(x=>x!.AsObject()).Single(x=>Text(x,"id")==id);
            if(Text(session,"status")!="resolved") throw new ReviewBlocked("unresolved_selected_session_"+id);
            var path=Text(session,"path"); if(!Path.IsPathFullyQualified(path)) path=Path.Combine(directory,path);
            var window=session["rollout_window"]!.AsObject(); var start=Number(window,"review_line_start",0); var end=Number(window,"review_line_end",-1);
            pins[id]=new JsonObject { ["path"]=Path.GetFullPath(path),["review_line_start"]=start,["review_line_end"]=end,["range_sha256"]=RangeHash(path,start,end) };
        }
        return pins;
    }
    static void CheckPins(JsonObject pins)
    {
        foreach(var pair in pins) { var pin=pair.Value!.AsObject(); if(RangeHash(Text(pin,"path"),Number(pin,"review_line_start",0),Number(pin,"review_line_end",-1))!=Text(pin,"range_sha256")) throw new ReviewBlocked("rollout_source_changed_"+pair.Key); }
    }
    static string RangeHash(string path,int start,int end)
    {
        if(start<1 || end<0 || end<start-1) throw new ReviewBlocked("invalid_advertised_range");
        NoLink(path);
        using var stream=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.ReadWrite);
        using var digest=IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        var buffer=new byte[8192]; var line=1; var completed=0; var hasBytes=false;
        // Raw bytes only: skip the prefix, hash exactly the advertised lines and
        // stop at end. The existing Python extractor owns JSON interpretation.
        while(line<=end) {
            var read=stream.Read(buffer);
            if(read==0) { if(hasBytes) completed=line; break; }
            var included=-1; var consumed=0;
            for(;consumed<read && line<=end;consumed++) {
                if(line>=start && included<0) included=consumed;
                hasBytes=true;
                if(buffer[consumed]=='\n') { completed=line++; hasBytes=false; }
            }
            if(included>=0) digest.AppendData(buffer.AsSpan(included,consumed-included));
        }
        if(completed<end) throw new ReviewBlocked("truncated_advertised_range");
        return Convert.ToHexStringLower(digest.GetHashAndReset());
    }
    static JsonObject Extract(JsonObject run,JsonObject selection,string folder,IEnumerable<string> arguments,JsonObject pins,int timeoutSeconds=120,int maxOutputBytes=16777216)
    {
        PrivateDirectory(folder);
        var snapshot=Path.Combine(folder,"extractor.py"); WriteBytes(snapshot,File.ReadAllBytes(Text(selection,"extractor")));
        if(FileHash(snapshot)!=Text(selection,"extractor_sha256")) throw new ReviewBlocked("extractor_changed_during_capture");
        var command=new List<string> { snapshot,"--manifest",Path.Combine(Text(run,"run_directory"),"manifest.json") }; command.AddRange(arguments);
        var process=Run(Text(selection,"python"),command,timeoutSeconds,maxOutputBytes);
        var stdout=Path.Combine(folder,"stdout.json"); var stderr=Path.Combine(folder,"stderr.txt");
        WriteBytes(stdout,process.Out); WriteBytes(stderr,process.Error); WriteBytes(Path.Combine(folder,"exit.txt"),Encoding.UTF8.GetBytes(process.Exit.ToString()));
        CheckPins(pins);
        var envelope=new JsonObject {
            ["schema_version"]=1,["manifest_sha256"]=selection["manifest_sha256"]!.DeepClone(),["selection_sha256"]=JsonHash(selection),
            ["extractor_sha256"]=selection["extractor_sha256"]!.DeepClone(),["arguments"]=Strings(command.Skip(3)),
            ["exit"]=process.Exit,["stdout_sha256"]=Hash(process.Out),["stderr_sha256"]=Hash(process.Error),["source_pins"]=pins.DeepClone(),["timeout_seconds"]=timeoutSeconds,["max_output_bytes"]=maxOutputBytes
        };
        WriteJson(Path.Combine(folder,"envelope.json"),envelope);
        return envelope;
    }
    static string PagePointer(string folder,int offset)=>Path.Combine(folder,"page-"+offset.ToString("D10")+".json");
    public static JsonObject Page(JsonObject request)
    {
        var directory=Full(request,"run_directory"); var rawRun=ReadJson(Path.Combine(directory,"run.json")); using var mutex=LockRun(rawRun);
        var (run,selection,pages)=Selection(request);
        var offset=Number(request,"offset",-1); var limit=Number(request,"limit",0); var max=Number(request,"max_total_chars",20000);
        var ids=StringArray(selection,"eligible_ids");
        if(offset<0 || offset>ids.Length || limit<1 || max<2000 || max>2000000) throw new ReviewBlocked("invalid_page_bounds");
        var pageIds=ids.Skip(offset).Take(limit).ToArray(); var pins=SourcePins(run,pageIds);
        var pointerPath=PagePointer(pages,offset);
        JsonObject? failedAttempt=null;
        if(File.Exists(pointerPath)) {
            var existingPointer=ReadJson(pointerPath); var retry=request["retry_failed"]?.GetValue<bool>()==true;
            var (previous,_)=ReadExtraction(existingPointer,selection,pages,retry);
            Count(previous,"offset",offset);
            var previousLimit=Number(previous,"limit",0); var previousMax=Number(previous,"max_total_chars",0);
            if(previousLimit<1 || previousMax<2000 || previousMax>2000000) throw new ReviewBlocked("invalid_stored_page_bounds");
            var previousIds=ids.Skip(offset).Take(previousLimit).ToArray();
            if(!StringArray(previous,"expected_ids").SequenceEqual(previousIds,StringComparer.Ordinal) || JsonHash(previous["source_pins"]!)!=JsonHash(SourcePins(run,previousIds))) throw new ReviewBlocked("stored_page_inputs_changed");
            failedAttempt=Number(previous,"exit",-1)!=0 ? existingPointer.DeepClone().AsObject() : previous["superseded_failed_attempt"]?.DeepClone().AsObject();
            if(Number(previous,"exit",-1)==0 && previousLimit==limit && previousMax==max) {
                if(!StringArray(previous,"expected_ids").SequenceEqual(pageIds,StringComparer.Ordinal) || JsonHash(previous["source_pins"]!)!=JsonHash(pins)) throw new ReviewBlocked("stored_page_inputs_changed");
                return PageResult("page_reused",Text(existingPointer,"folder"),pointerPath,previous,offset);
            }
        }
        var folder=Path.Combine(pages,"output-"+Guid.NewGuid().ToString("N"));
        var arguments=new List<string>(); var scope=selection["scope"]!.AsObject();
        foreach(var value in StringArray(scope,"cwd_roots")) { arguments.Add("--cwd-root"); arguments.Add(value); }
        foreach(var value in StringArray(scope,"worktree_tails")) { arguments.Add("--worktree-tail"); arguments.Add(value); }
        arguments.AddRange(["--session-offset",offset.ToString(),"--session-limit",limit.ToString(),"--max-total-chars",max.ToString()]);
        var envelope=Extract(run,selection,folder,arguments,pins,Number(request,"timeout_seconds",120),Number(request,"max_output_bytes",16777216));
        envelope["offset"]=offset; envelope["limit"]=limit; envelope["max_total_chars"]=max; envelope["expected_ids"]=Strings(pageIds);
        if(failedAttempt is not null) envelope["superseded_failed_attempt"]=failedAttempt;
        WriteJson(Path.Combine(folder,"envelope.json"),envelope,true);
        var pointer=new JsonObject { ["folder"]=folder,["envelope_sha256"]=JsonHash(envelope) };
        WriteJson(pointerPath,pointer,true);
        if(Number(envelope,"exit",-1)!=0) {
            var failure=new ReviewBlocked("extractor_failed_exit_"+Number(envelope,"exit",-1));
            failure.Data["output"]=Path.Combine(folder,"stdout.json"); failure.Data["page_receipt"]=pointerPath; failure.Data["extractor_exit"]=Number(envelope,"exit",-1);
            throw failure;
        }
        return PageResult("page_captured",folder,pointerPath,envelope,offset);
    }
    static JsonObject PageResult(string status,string folder,string pointerPath,JsonObject envelope,int offset)
    {
        var result=NewResult(status); result["output"]=Path.Combine(folder,"stdout.json"); result["page_receipt"]=pointerPath; result["extractor_exit"]=envelope["exit"]!.DeepClone(); result["offset"]=offset;
        return result;
    }
    static (JsonObject Envelope,JsonObject Output) ReadExtraction(JsonObject pointer,JsonObject selection,string allowedFolder,bool allowFailed=false,int failedHistoryDepth=0)
    {
        if(failedHistoryDepth>64) throw new ReviewBlocked("failed_page_history_limit_exceeded");
        var folder=Text(pointer,"folder"); if(!Within(folder,allowedFolder)) throw new ReviewBlocked("foreign_output_folder"); NoLink(folder);
        var envelope=ReadJson(Path.Combine(folder,"envelope.json"));
        if(Number(envelope,"schema_version",0)!=1 || Text(pointer,"envelope_sha256")!=JsonHash(envelope) || Text(envelope,"manifest_sha256")!=Text(selection,"manifest_sha256") || Text(envelope,"selection_sha256")!=JsonHash(selection) || Text(envelope,"extractor_sha256")!=Text(selection,"extractor_sha256")) throw new ReviewBlocked("foreign_or_corrupt_page_binding");
        var exit=Number(envelope,"exit",-1);
        if(File.ReadAllText(Path.Combine(folder,"exit.txt"))!=exit.ToString()) throw new ReviewBlocked("corrupt_extractor_exit");
        if(FileHash(Path.Combine(folder,"stdout.json"))!=Text(envelope,"stdout_sha256") || FileHash(Path.Combine(folder,"stderr.txt"))!=Text(envelope,"stderr_sha256") || FileHash(Path.Combine(folder,"extractor.py"))!=Text(selection,"extractor_sha256")) throw new ReviewBlocked("corrupt_extractor_output");
        CheckPins(envelope["source_pins"]!.AsObject());
        if(envelope["superseded_failed_attempt"] is JsonObject failed) {
            var (historical,_)=ReadExtraction(failed,selection,allowedFolder,true,failedHistoryDepth+1);
            if(Number(historical,"exit",0)<1) throw new ReviewBlocked("superseded_attempt_must_have_failed");
        }
        if(exit!=0) {
            if(!allowFailed || exit<1) throw new ReviewBlocked("extractor_exit_failed");
            return(envelope,new JsonObject());
        }
        return (envelope,ReadJson(Path.Combine(folder,"stdout.json")));
    }
    static void Count(JsonObject obj,string name,int expected)
    {
        if(Number(obj,name,-1)!=expected) throw new ReviewBlocked("inconsistent_"+name);
    }
    static JsonObject ValidatePages(JsonObject run,JsonObject selection,string pages)
    {
        var expected=StringArray(selection,"eligible_ids"); var offset=0; var seen=new HashSet<string>(StringComparer.Ordinal); var pagePins=new JsonObject(); var resolutions=new JsonObject();
        var manifestCount=ReadJson(Path.Combine(Text(run,"run_directory"),"manifest.json"))["sessions"]!.AsArray().Count;
        do {
            var pointerPath=PagePointer(pages,offset); if(!File.Exists(pointerPath)) throw new ReviewBlocked("missing_page_at_offset_"+offset);
            var pointer=ReadJson(pointerPath); var (envelope,output)=ReadExtraction(pointer,selection,pages);
            Count(envelope,"offset",offset); var limit=Number(envelope,"limit",0); if(limit<1) throw new ReviewBlocked("invalid_page_limit");
            var pageIds=expected.Skip(offset).Take(limit).ToArray();
            if(!StringArray(envelope,"expected_ids").SequenceEqual(pageIds,StringComparer.Ordinal)) throw new ReviewBlocked("unexpected_page_ids");
            var window=output["selection_window"]?.AsObject() ?? throw new ReviewBlocked("missing_selection_window");
            Count(window,"offset",offset); Count(window,"limit",limit); Count(window,"eligible_sessions",expected.Length); Count(window,"page_sessions",pageIds.Length);
            var counts=output["counts"]?.AsObject() ?? throw new ReviewBlocked("missing_counts");
            Count(counts,"manifest_sessions",manifestCount); Count(counts,"selected_sessions",pageIds.Length); Count(counts,"filtered_out_sessions",manifestCount-pageIds.Length); Count(counts,"resolved_sessions",pageIds.Length); Count(counts,"skipped_unresolved_sessions",0); Count(counts,"emitted_sessions",pageIds.Length); Count(counts,"omitted_sessions",0);
            Count(output["omitted_sessions"]!.AsObject(),"count",0);
            var sessions=output["sessions"]!.AsArray();
            if(!sessions.Select(x=>Text(x!.AsObject(),"id")).SequenceEqual(pageIds,StringComparer.Ordinal)) throw new ReviewBlocked("unexpected_or_duplicate_emitted_session_ids");
            foreach(var node in sessions) {
                var session=node!.AsObject(); var id=Text(session,"id"); if(!seen.Add(id)) throw new ReviewBlocked("duplicate_emitted_session_id");
                if(session["manual_suffix_selection_required"]?.GetValue<bool>()==true) {
                    var resolution=ResolutionPath(Text(run,"run_directory"),id);
                    if(!File.Exists(resolution)) throw new ReviewBlocked("unresolved_manual_clone_"+id);
                    ValidateResolution(ReadJson(resolution),run,selection,id);
                    resolutions[id]=FileHash(resolution);
                } else if(session["manual_suffix_selection_required"]?.GetValue<bool>()!=false) throw new ReviewBlocked("missing_manual_clone_state_"+id);
            }
            var next=offset+pageIds.Length; var more=next<expected.Length;
            if(window["has_more"]?.GetValue<bool>()!=more || (more ? Number(window,"next_offset",-1)!=next : window["next_offset"] is not null)) throw new ReviewBlocked("inconsistent_pagination");
            pagePins[Path.GetFileName(pointerPath)]=FileHash(pointerPath);
            offset=next;
            if(!more) break;
            if(pageIds.Length==0) throw new ReviewBlocked("nonprogressing_pagination");
        } while(true);
        if(seen.Count!=expected.Length) throw new ReviewBlocked("incomplete_eligible_session_coverage");
        return new JsonObject { ["schema_version"]=1,["status"]="complete",["manifest_sha256"]=selection["manifest_sha256"]!.DeepClone(),["selection_sha256"]=JsonHash(selection),["eligible_ids"]=Strings(expected),["eligible_sessions"]=expected.Length,["pages"]=pagePins,["manual_clone_resolutions"]=resolutions,["checkpoint_permission"]="none_final_review_and_delivery_required" };
    }
    public static JsonObject VerifyPages(JsonObject request)
    {
        var directory=Full(request,"run_directory"); var rawRun=ReadJson(Path.Combine(directory,"run.json")); using var mutex=LockRun(rawRun);
        var (run,selection,pages)=Selection(request); var proof=ValidatePages(run,selection,pages);
        var path=Path.Combine(directory,"complete.json"); WriteJson(path,proof,true);
        var result=NewResult("complete"); result["manifest_sha256"]=proof["manifest_sha256"]!.DeepClone(); result["selection_sha256"]=proof["selection_sha256"]!.DeepClone(); result["eligible_sessions"]=proof["eligible_sessions"]!.DeepClone(); result["page_count"]=proof["pages"]!.AsObject().Count; result["resolved_manual_clones"]=proof["manual_clone_resolutions"]!.AsObject().Count; result["receipt"]=path; result["receipt_sha256"]=JsonHash(proof); result["checkpoint_permission"]="none_final_review_and_delivery_required"; return result;
    }
    static string ResolutionPath(string directory,string id)=>Path.Combine(directory,"clones",Hash(Encoding.UTF8.GetBytes(id))+".json");
    public static JsonObject ResolveClone(JsonObject request)
    {
        var directory=Full(request,"run_directory"); var rawRun=ReadJson(Path.Combine(directory,"run.json")); using var mutex=LockRun(rawRun);
        var (run,selection,_)=Selection(request); var id=Text(request,"session_id");
        if(!StringArray(selection,"eligible_ids").Contains(id,StringComparer.Ordinal)) throw new ReviewBlocked("clone_must_belong_to_selection_scope");
        var session=ReadJson(Path.Combine(directory,"manifest.json"))["sessions"]!.AsArray().Select(x=>x!.AsObject()).Single(x=>Text(x,"id")==id);
        if(session["rollout_window"]?["embedded_session_metas"] is not JsonArray embedded || embedded.Count==0) throw new ReviewBlocked("session_has_no_manual_clone_history");
        var pins=SourcePins(run,[id]); var kind=Text(request,"kind"); var reason=Text(request,"reason");
        if(kind is not ("reviewed_suffix" or "clone_only")) throw new ReviewBlocked("clone_resolution_kind_required");
        var max=Number(request,"max_total_chars",200000); if(max<2000 || max>2000000) throw new ReviewBlocked("invalid_clone_output_bound");
        var clones=Path.Combine(directory,"clones"); PrivateDirectory(clones); var folder=Path.Combine(clones,"resolution-"+Guid.NewGuid().ToString("N")); PrivateDirectory(folder);
        var outputs=new JsonObject();
        foreach(var mode in new[]{"boundaries","structural"}) {
            var target=Path.Combine(folder,mode); var flag=mode=="boundaries" ? "--list-clone-boundaries" : "--structural-projection";
            var envelope=Extract(run,selection,target,["--session-id",id,flag,"--max-total-chars",max.ToString()],pins);
            outputs[mode]=new JsonObject { ["folder"]=target,["envelope_sha256"]=JsonHash(envelope) };
        }
        var receipt=new JsonObject { ["schema_version"]=1,["manifest_sha256"]=selection["manifest_sha256"]!.DeepClone(),["selection_sha256"]=JsonHash(selection),["session_id"]=id,["kind"]=kind,["reason"]=reason,["source_pins"]=pins,["outputs"]=outputs };
        if(kind=="reviewed_suffix") {
            var line=Number(request,"suffix_start",0); if(line<1) throw new ReviewBlocked("suffix_start_required");
            receipt["suffix_start"]=line;
            var target=Path.Combine(folder,"suffix"); var envelope=Extract(run,selection,target,["--session-id",id,"--clone-suffix-start",id+"="+line,"--max-total-chars",max.ToString()],pins);
            outputs["suffix"]=new JsonObject { ["folder"]=target,["envelope_sha256"]=JsonHash(envelope) };
        } else receipt["reviewed_boundary_line"]=Number(request,"reviewed_boundary_line",0);
        WriteJson(Path.Combine(folder,"resolution.json"),receipt);
        var pointer=new JsonObject { ["receipt"]=Path.Combine(folder,"resolution.json"),["receipt_sha256"]=JsonHash(receipt) };
        ValidateResolution(pointer,run,selection,id);
        WriteJson(ResolutionPath(directory,id),pointer,true);
        var result=NewResult("clone_resolved"); result["kind"]=kind; result["session_id"]=id; result["receipt"]=Text(pointer,"receipt"); result["receipt_sha256"]=JsonHash(receipt);
        foreach(var output in outputs) result[output.Key+"_output"]=Path.Combine(Text(output.Value!.AsObject(),"folder"),"stdout.json");
        result["checkpoint_permission"]="none_final_review_and_delivery_required"; return result;
    }
    static void ValidateResolution(JsonObject pointer,JsonObject run,JsonObject selection,string id)
    {
        var clones=Path.Combine(Text(run,"run_directory"),"clones"); var path=Text(pointer,"receipt");
        if(!Within(path,clones)) throw new ReviewBlocked("foreign_clone_resolution");
        var receipt=ReadJson(path);
        if(Number(receipt,"schema_version",0)!=1 || JsonHash(receipt)!=Text(pointer,"receipt_sha256") || Text(receipt,"manifest_sha256")!=Text(selection,"manifest_sha256") || Text(receipt,"selection_sha256")!=JsonHash(selection) || Text(receipt,"session_id")!=id || Text(receipt,"reason").Length==0) throw new ReviewBlocked("foreign_or_corrupt_clone_resolution");
        var pins=receipt["source_pins"]!.AsObject(); if(JsonHash(pins)!=JsonHash(SourcePins(run,[id]))) throw new ReviewBlocked("clone_resolution_source_changed");
        var outputs=receipt["outputs"]!.AsObject();
        var (_,boundary)=ReadExtraction(outputs["boundaries"]!.AsObject(),selection,clones);
        CheckSingleSummary(boundary,id);
        var boundarySession=boundary["sessions"]![0]!.AsObject();
        if(boundarySession["manual_suffix_selection_required"]?.GetValue<bool>()!=true) throw new ReviewBlocked("clone_boundary_proof_required");
        var map=boundarySession["clone_boundary_map"]!.AsObject();
        foreach(var item in map) Count(item.Value!.AsObject(),"omitted",0);
        var (_,structural)=ReadExtraction(outputs["structural"]!.AsObject(),selection,clones);
        if(Text(structural,"mode")!="structural_projection" || structural["sessions"]!.AsArray().Count!=1 || Text(structural["sessions"]![0]!.AsObject(),"id")!=id) throw new ReviewBlocked("clone_structural_proof_required");
        Count(structural["counts"]!.AsObject(),"selected_sessions",1); Count(structural["counts"]!.AsObject(),"resolved_sessions",1); Count(structural["counts"]!.AsObject(),"omitted_records",0);
        var structure=structural["sessions"]![0]!.AsObject(); var structureCounts=structure["counts"]!.AsObject();
        Count(structureCounts,"omitted_records",0); Count(structureCounts,"inspected_lines",Number(structureCounts,"advertised_lines",-1)); Count(structureCounts,"emitted_records",Number(structureCounts,"advertised_lines",-1));
        var start=Number(boundarySession,"review_line_start",0); var end=Number(boundarySession,"review_line_end",0);
        Count(structure,"review_line_start",start); Count(structure,"review_line_end",end);
        var userLines=map["substantive_user"]?["lines"]?.AsArray().Select(x=>x!.GetValue<int>()).ToArray() ?? [];
        if(Text(receipt,"kind")=="reviewed_suffix") {
            var line=Number(receipt,"suffix_start",0); if(line<start || line>end || !userLines.Contains(line)) throw new ReviewBlocked("suffix_must_start_at_reviewed_substantive_user_line");
            var (_,suffix)=ReadExtraction(outputs["suffix"]!.AsObject(),selection,clones); CheckSingleSummary(suffix,id);
            var projection=suffix["sessions"]![0]!.AsObject();
            if(projection["manual_suffix_selection_required"]?.GetValue<bool>()!=false || Number(projection["counts"]!.AsObject(),"substantive_user_messages",0)<1 || projection["embedded_history_excluded"]?.GetValue<bool>()!=true) throw new ReviewBlocked("actual_reviewed_suffix_summary_required");
            Count(projection,"review_line_start",line); Count(projection,"review_line_end",end);
        } else if(Text(receipt,"kind")=="clone_only") {
            var line=Number(receipt,"reviewed_boundary_line",0);
            var boundaries=new[]{"outer_session_meta","embedded_session_meta","task_complete"}.SelectMany(key=>map[key]?["lines"]?.AsArray().Select(x=>x!.GetValue<int>()) ?? []).ToArray();
            if(line<start || line>end || !boundaries.Contains(line) || userLines.Length!=0) throw new ReviewBlocked("clone_only_requires_zero_substantive_users_and_reviewed_boundary");
        } else throw new ReviewBlocked("invalid_clone_resolution_kind");
    }
    static void CheckSingleSummary(JsonObject output,string id)
    {
        var counts=output["counts"]!.AsObject(); foreach(var name in new[]{"selected_sessions","resolved_sessions","emitted_sessions"}) Count(counts,name,1);
        Count(counts,"skipped_unresolved_sessions",0); Count(counts,"omitted_sessions",0); Count(output["omitted_sessions"]!.AsObject(),"count",0);
        if(output["sessions"]!.AsArray().Count!=1 || Text(output["sessions"]![0]!.AsObject(),"id")!=id) throw new ReviewBlocked("clone_output_session_mismatch");
    }
    static JsonObject CurrentProof(JsonObject run,JsonObject selection,string pages)
    {
        var path=Path.Combine(Text(run,"run_directory"),"complete.json");
        if(!File.Exists(path)) throw new ReviewBlocked("successful_completeness_receipt_required");
        var proof=ReadJson(path);
        if(JsonHash(proof)!=JsonHash(ValidatePages(run,selection,pages))) throw new ReviewBlocked("completeness_receipt_changed_or_stale");
        return proof;
    }
    static JsonObject TopicContext(JsonObject request,JsonObject run,JsonObject selection,JsonObject proof)
    {
        var pins=request["source_pins"]?.AsObject() ?? throw new ReviewBlocked("source_pins_required");
        if(pins.Count==0) throw new ReviewBlocked("nonempty_source_pins_required");
        var repositories=new HashSet<string>(StringComparer.Ordinal);
        foreach(var pin in pins) {
            var separator=pin.Key.LastIndexOf('|');
            if(separator<1 || !Path.IsPathFullyQualified(pin.Key[..separator]) || pin.Key[(separator+1)..] is not ("refs/remotes/origin/develop" or "refs/remotes/origin/production") || pin.Value is null || !System.Text.RegularExpressions.Regex.IsMatch(pin.Value.GetValue<string>(),"^[0-9a-f]{40}$")) throw new ReviewBlocked("source_pins_require_repository_origin_ref_and_lowercase_sha40");
            repositories.Add(Path.GetFullPath(pin.Key[..separator]));
        }
        JsonObject? documentationPin=null;
        if(request["documentation_pin"] is not null) {
            var supplied=request["documentation_pin"]!.AsObject();
            if(!Path.IsPathFullyQualified(Text(supplied,"repository"))) throw new ReviewBlocked("documentation_pin_repository_must_be_absolute");
            var repository=Full(supplied,"repository"); var reference=Text(supplied,"ref"); var sha=Text(supplied,"sha");
            if(reference!="refs/remotes/origin/main" || !System.Text.RegularExpressions.Regex.IsMatch(sha,"^[0-9a-f]{40}$")) throw new ReviewBlocked("documentation_pin_requires_origin_main_and_lowercase_sha40");
            if(!StringArray(selection["scope"]!.AsObject(),"cwd_roots").Contains(repository,StringComparer.Ordinal) || (!Directory.Exists(Path.Combine(repository,".git")) && !File.Exists(Path.Combine(repository,".git")))) throw new ReviewBlocked("documentation_pin_requires_exact_bound_repository_root");
            if(repositories.Contains(repository)) throw new ReviewBlocked("documentation_pin_must_be_separate_from_code_repositories");
            documentationPin=new JsonObject { ["repository"]=repository,["ref"]=reference,["sha"]=sha };
            repositories.Add(repository);
        }
        var ids=StringArray(request,"session_ids");
        if(ids.Distinct(StringComparer.Ordinal).Count()!=ids.Length || ids.Any(id=>!StringArray(selection,"eligible_ids").Contains(id,StringComparer.Ordinal))) throw new ReviewBlocked("session_ids_must_be_unique_eligible_manifest_ids");
        var git=request["git_candidates"]?.AsArray() ?? new JsonArray(); var gitIdentities=new HashSet<string>(StringComparer.Ordinal); var gitCandidates=new List<JsonObject>();
        foreach(var node in git) {
            var candidate=node!.AsObject(); if(!Path.IsPathFullyQualified(Text(candidate,"repository"))) throw new ReviewBlocked("git_candidate_repository_must_be_absolute");
            var repository=Full(candidate,"repository"); var sha=Text(candidate,"sha");
            if(!repositories.Contains(repository) || !System.Text.RegularExpressions.Regex.IsMatch(sha,"^[0-9a-f]{40}$") || !gitIdentities.Add(repository+"|"+sha)) throw new ReviewBlocked("git_candidates_require_unique_repository_and_lowercase_sha40");
            gitCandidates.Add(new JsonObject { ["repository"]=repository,["sha"]=sha });
        }
        if(ids.Length+gitCandidates.Count==0) throw new ReviewBlocked("session_or_git_candidate_required");
        var wiki=StringArray(request,"wiki_files"); if(wiki.Any(path=>!Path.IsPathFullyQualified(path))) throw new ReviewBlocked("absolute_wiki_files_required");
        var disposition=TextOrEmpty(request,"no_durable_doc_disposition"); if(wiki.Length==0 && disposition.Length==0) throw new ReviewBlocked("wiki_inputs_or_explicit_no_durable_doc_disposition_required");
        var wikiHashes=new JsonObject();
        foreach(var path in wiki.Select(Path.GetFullPath).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal)) wikiHashes[path]=File.Exists(path) ? FileHash(path) : "missing";
        return new JsonObject {
            ["schema_version"]=1,["topic_id"]=Text(request,"topic_id"),["manifest_sha256"]=selection["manifest_sha256"]!.DeepClone(),
            ["capture_binding_sha256"]=run["binding_sha256"]!.DeepClone(),["selection_sha256"]=JsonHash(selection),["complete_receipt_sha256"]=JsonHash(proof),
            ["source_pins"]=Canonical(pins),["documentation_pin"]=documentationPin,["session_ids"]=Strings(ids.Order(StringComparer.Ordinal)),["git_candidates"]=new JsonArray(gitCandidates.OrderBy(x=>Text(x,"repository")+"|"+Text(x,"sha"),StringComparer.Ordinal).Select(x=>(JsonNode)x).ToArray()),["wiki_sha256"]=wikiHashes,["no_durable_doc_disposition"]=disposition
        };
    }
    static string TopicPath(string directory,string id) => Path.Combine(directory,"topics",Hash(Encoding.UTF8.GetBytes(id))+".json");
    public static JsonObject RecordTopic(JsonObject request)
    {
        var directory=Full(request,"run_directory"); var rawRun=ReadJson(Path.Combine(directory,"run.json")); using var mutex=LockRun(rawRun);
        var (run,selection,pages)=Selection(request); var proof=CurrentProof(run,selection,pages); var context=TopicContext(request,run,selection,proof);
        return PublishTopic(directory,TopicReceipt(request,context));
    }
    static JsonObject TopicReceipt(JsonObject request,JsonObject context)
    {
        var decision=Text(request,"decision"); if(decision is not ("unchanged" or "update_needed" or "blocked")) throw new ReviewBlocked("invalid_topic_decision");
        if(decision=="unchanged" && TextOrEmpty(context,"no_durable_doc_disposition").Length==0 && !context["wiki_sha256"]!.AsObject().Any(pair=>pair.Value?.GetValue<string>()!="missing")) throw new ReviewBlocked("unchanged_requires_existing_wiki_or_explicit_no_durable_doc_disposition");
        var state=decision switch { "update_needed"=>"pending_delivery", "blocked"=>"blocked", _=>"comparison_only" };
        return new JsonObject { ["schema_version"]=1,["context"]=context,["context_sha256"]=JsonHash(context),["decision"]=decision,["delivery_state"]=state,["comparison"]=Text(request,"comparison"),["checkpoint_permission"]="none_final_review_and_delivery_required" };
    }
    static JsonObject PublishTopic(string directory,JsonObject receipt)
    {
        var context=receipt["context"]!.AsObject(); var decision=Text(receipt,"decision"); var state=Text(receipt,"delivery_state");
        var topics=Path.Combine(directory,"topics"); PrivateDirectory(topics);
        var evidence=Path.Combine(topics,"receipt-"+Guid.NewGuid().ToString("N")+".json"); WriteJson(evidence,receipt);
        var pointer=new JsonObject { ["receipt"]=evidence,["receipt_sha256"]=JsonHash(receipt) }; WriteJson(TopicPath(directory,Text(context,"topic_id")),pointer,true);
        var result=NewResult(decision=="blocked" ? "topic_blocked" : decision=="update_needed" ? "pending_delivery" : "recorded"); result["receipt"]=evidence; result["receipt_sha256"]=JsonHash(receipt); result["delivery_state"]=state; result["checkpoint_permission"]="none_final_review_and_delivery_required"; return result;
    }
    public static JsonObject ResumeTopics(JsonObject request)
    {
        var directory=Full(request,"run_directory"); var rawRun=ReadJson(Path.Combine(directory,"run.json")); using var mutex=LockRun(rawRun);
        var (run,selection,pages)=Selection(request); var proof=CurrentProof(run,selection,pages); var context=TopicContext(request,run,selection,proof);
        return ResumeTopicContext(directory,context);
    }
    static JsonObject ResumeTopicContext(string directory,JsonObject context)
    {
        var path=TopicPath(directory,Text(context,"topic_id")); if(!File.Exists(path)) return NewResult("missing");
        var pointer=ReadJson(path); var evidence=Text(pointer,"receipt"); if(!Within(evidence,Path.Combine(directory,"topics"))) throw new ReviewBlocked("foreign_topic_receipt");
        var receipt=ReadJson(evidence);
        if(Number(receipt,"schema_version",0)!=1 || JsonHash(receipt)!=Text(pointer,"receipt_sha256") || JsonHash(receipt["context"]!)!=Text(receipt,"context_sha256")) throw new ReviewBlocked("corrupt_topic_receipt");
        if(JsonHash(context)!=Text(receipt,"context_sha256")) { var stale=NewResult("stale"); stale["reason"]="source_pins_candidates_wiki_or_receipt_changed"; return stale; }
        var decision=Text(receipt,"decision"); var expectedState=decision switch { "unchanged"=>"comparison_only","update_needed"=>"pending_delivery","blocked"=>"blocked",_=>throw new ReviewBlocked("invalid_stored_topic_decision") };
        if(Text(receipt,"delivery_state")!=expectedState) throw new ReviewBlocked("invalid_delivery_claim");
        var result=receipt.DeepClone().AsObject(); result["status"]=decision=="blocked" ? "topic_blocked" : "reusable"; result["receipt"]=evidence; result["receipt_sha256"]=JsonHash(receipt); return result;
    }
    public static JsonObject TopicsBatch(JsonObject request)
    {
        var operation=Text(request,"operation"); if(operation is not ("record" or "resume")) throw new ReviewBlocked("invalid_topic_batch_operation");
        var topics=request["topics"]?.AsArray() ?? throw new ReviewBlocked("topics_required");
        if(topics.Count<1 || topics.Count>64 || Encoding.UTF8.GetByteCount(request.ToJsonString())>524288) throw new ReviewBlocked("topic_batch_bounds_exceeded");
        var directory=Full(request,"run_directory"); var rawRun=ReadJson(Path.Combine(directory,"run.json")); using var mutex=LockRun(rawRun);
        var (run,selection,pages)=Selection(request);
        var measured=Stopwatch.StartNew(); var proof=CurrentProof(run,selection,pages); measured.Stop();
        var contexts=new List<(string Id,JsonObject Context,JsonObject? Receipt)>(); var ids=new HashSet<string>(StringComparer.Ordinal);
        // Validate the entire bounded request before publishing any topic. All
        // contexts share this one fresh proof, never a cross-process hash cache.
        foreach(var node in topics) {
            var item=node?.AsObject() ?? throw new ReviewBlocked("invalid_topic_batch_item");
            if(new[]{"run_directory","extractor","python","scope","operation","topics"}.Any(item.ContainsKey)) throw new ReviewBlocked("topic_common_fields_must_not_be_overridden");
            var id=Text(item,"topic_id"); if(!ids.Add(id)) throw new ReviewBlocked("duplicate_topic_batch_id");
            var merged=request.DeepClone().AsObject(); merged.Remove("topics"); merged.Remove("operation");
            foreach(var pair in item) merged[pair.Key]=pair.Value?.DeepClone();
            var context=TopicContext(merged,run,selection,proof);
            contexts.Add((id,context,operation=="record" ? TopicReceipt(merged,context) : null));
        }
        var results=new JsonArray();
        foreach(var topic in contexts) {
            var result=operation=="record" ? PublishTopic(directory,topic.Receipt!) : ResumeTopicContext(directory,topic.Context);
            result["topic_id"]=topic.Id; results.Add((JsonNode)result);
        }
        var response=NewResult("topics_complete"); response["operation"]=operation; response["complete_proof_validations"]=1;
        response["proof_validation_ms"]=Math.Round(measured.Elapsed.TotalMilliseconds,3); response["topic_count"]=contexts.Count; response["results"]=results;
        response["checkpoint_permission"]="none_final_review_and_delivery_required"; return response;
    }
    public static JsonObject Invalidate(JsonObject request)
    {
        var directory=Full(request,"run_directory"); var run=ReadJson(Path.Combine(directory,"run.json")); var store=Text(run,"store"); using var mutex=LockRun(run);
        if(Text(run,"run_directory")!=directory || !Within(directory,store)) throw new ReviewBlocked("foreign_run_directory");
        var activePath=Path.Combine(store,"active.json"); var active=ReadJson(activePath);
        if(Text(active,"run_directory")!=directory) throw new ReviewBlocked("run_is_not_active");
        run["invalidated"]=new JsonObject { ["reason"]=Text(request,"reason"),["at"]=DateTimeOffset.UtcNow.ToString("O") };
        WriteJson(Path.Combine(directory,"run.json"),run,true); NoLink(activePath); File.Delete(activePath);
        var result=NewResult("invalidated"); result["run_directory"]=directory; result["evidence_preserved"]=true; result["checkpoint_changed"]=false; return result;
    }
}

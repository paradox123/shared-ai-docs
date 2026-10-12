using System.Diagnostics;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

try
{
    if(OperatingSystem.IsWindows()) throw new ReviewBlocked("unix_private_permissions_required");
    if(args.Length!=3 || args[1]!="--request") throw new ReviewBlocked("usage: <capture|page|verify-pages|record-topic|resume-topics|invalidate> --request <json-file>");
    var request=Review.ReadJson(Path.GetFullPath(args[2]));
    var result=args[0] switch {
        "capture" => Review.Capture(request),
        "page" => Review.Page(request),
        "verify-pages" => Review.VerifyPages(request),
        "resolve-clone" => Review.ResolveClone(request),
        "record-topic" => Review.RecordTopic(request),
        "resume-topics" => Review.ResumeTopics(request),
        "invalidate" => Review.Invalidate(request),
        _ => throw new ReviewBlocked("command_not_implemented")
    };
    Console.WriteLine(result.ToJsonString());
    return 0;
}
catch(Exception ex)
{
    var error=new JsonObject { ["schema_version"]=1,["status"]="blocked",["reason"]=ex.Message };
    foreach(var key in new[]{"run_directory","resolver_stdout","resolver_stderr","resolver_exit_file"}) if(ex.Data[key] is string value) error[key]=value;
    if(ex.Data["resolver_exit"] is int exit) error["resolver_exit"]=exit;
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
    static (int Exit,byte[] Out,byte[] Error) Run(string executable,IEnumerable<string> args)
    {
        var start=new ProcessStartInfo(executable) { UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true };
        foreach(var arg in args) start.ArgumentList.Add(arg);
        using var process=Process.Start(start) ?? throw new ReviewBlocked("process_start_failed");
        using var output=new MemoryStream(); using var errors=new MemoryStream();
        var stdout=process.StandardOutput.BaseStream.CopyToAsync(output); var stderr=process.StandardError.BaseStream.CopyToAsync(errors);
        process.WaitForExit(); Task.WaitAll(stdout,stderr);
        return (process.ExitCode,output.ToArray(),errors.ToArray());
    }
    static JsonObject CaptureBinding(JsonObject request)
    {
        var memory=Full(request,"memory"); var definition=Full(request,"definition"); var resolver=Full(request,"resolver");
        var max=Number(request,"max_sessions",100); if(max<1 || max>500) throw new ReviewBlocked("max_sessions_must_be_1_to_500");
        var approved=StringArray(request,"approved_missing_carry_ids");
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
            ["prompt_last_run"]=prompt,["approved_missing_carry_ids"]=Strings(approved)
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
        foreach(var key in new[]{"Processed window end","Carry-forward sessions","Authoritative source tips"}) {
            var values=System.Text.RegularExpressions.Regex.Matches(header,"^"+System.Text.RegularExpressions.Regex.Escape(key)+@":\s*([^\r\n]*)$",System.Text.RegularExpressions.RegexOptions.Multiline);
            if(values.Count>1) throw new ReviewBlocked("ambiguous_checkpoint_"+key);
            fields[key]=values.Count==1 ? JsonValue.Create(values[0].Groups[1].Value.Trim()) : null;
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
            try { var existing=Load(existingDirectory); return CaptureResult(existing,"resumed"); }
            catch(Exception ex) { throw CaptureError(ex.Message,existingDirectory); }
        }
        var directory=Path.Combine(store,"run-"+Guid.NewGuid().ToString("N")); PrivateDirectory(directory);
        var run=new JsonObject { ["schema_version"]=1,["run_directory"]=directory,["store"]=store,["binding"]=binding,["binding_sha256"]=BindingHash(binding),["state"]="capturing" };
        WriteJson(Path.Combine(directory,"run.json"),run);
        WriteJson(activePath,new JsonObject { ["schema_version"]=1,["binding_sha256"]=BindingHash(binding),["run_directory"]=directory });
        Console.Error.WriteLine(new JsonObject { ["schema_version"]=1,["status"]="capture_started",["run_directory"]=directory,["active_receipt"]=activePath }.ToJsonString());
        WriteBytes(Path.Combine(directory,"resolver.py"),File.ReadAllBytes(Text(binding,"resolver")));
        WriteBytes(Path.Combine(directory,"memory.md"),File.ReadAllBytes(Text(binding,"memory")));
        WriteBytes(Path.Combine(directory,"definition.toml"),File.ReadAllBytes(Text(binding,"definition")));
        var index=Path.Combine(directory,"index.jsonl");
        var arguments=new List<string> { Path.Combine(directory,"resolver.py"),"--codex-home",Text(binding,"codex_home"),"--memory",Path.Combine(directory,"memory.md"),"--exclude-session-id",Text(binding,"exclude_session_id"),"--max-sessions",Number(binding,"max_sessions",100).ToString(),"--compact","--recent","0","--save-index-snapshot",index };
        if(TextOrEmpty(binding,"prompt_last_run") is { Length:>0 } cutoff) { arguments.Add("--prompt-last-run"); arguments.Add(cutoff); }
        var process=Run(Text(binding,"python"),arguments);
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
    static JsonObject Load(string directory)
    {
        directory=Path.GetFullPath(directory); NoLink(directory);
        var run=ReadJson(Path.Combine(directory,"run.json"));
        if(Number(run,"schema_version",0)!=1 || Text(run,"run_directory")!=directory || Text(run,"state")!="captured") throw new ReviewBlocked("incomplete_or_invalid_capture");
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
        if(exit==0 && safe==true) return true;
        if(exit!=2 || safe!=false) return false;
        var approved=StringArray(run["binding"]!.AsObject(),"approved_missing_carry_ids");
        if(approved.Length==0 || approved.Distinct(StringComparer.Ordinal).Count()!=approved.Length) return false;
        var missing=new HashSet<string>(StringComparer.Ordinal);
        foreach(var node in manifest["sessions"]!.AsArray()) {
            var session=node!.AsObject(); var status=Text(session,"status");
            if(status=="resolved") {
                if(session["rollout_window"]?["state"]?.GetValue<string>() is "unknown" or "unreadable") return false;
                continue;
            }
            var id=Text(session,"id");
            if(status!="missing" || session["path"] is not null || !StringArray(session,"selection_reasons").SequenceEqual(new[]{"carry_forward"},StringComparer.Ordinal) || !approved.Contains(id,StringComparer.Ordinal)) return false;
            missing.Add(id);
        }
        if(missing.Count==0) return false;
        var carries=manifest["window"]?["carry_forward_from_memory"]?.AsArray().Select(x=>Text(x!.AsObject(),"id")).ToHashSet(StringComparer.Ordinal);
        if(carries is null || !missing.IsSubsetOf(carries)) return false;
        var diagnosed=new HashSet<string>(StringComparer.Ordinal);
        foreach(var node in manifest["diagnostics"]!.AsArray()) {
            var diagnostic=node!.AsObject();
            switch(Text(diagnostic,"code")) {
                case "missing_rollout":
                    if(!missing.Contains(Text(diagnostic,"session_id")) || !diagnosed.Add(Text(diagnostic,"session_id"))) return false;
                    break;
                case "carry_forward_index_row_missing_recovered":
                    if(StringArray(diagnostic,"session_ids").Any(id=>!missing.Contains(id))) return false;
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
        result["run_directory"]=directory; result["manifest"]=Path.Combine(directory,"manifest.json"); result["index_snapshot"]=Path.Combine(directory,"index.jsonl");
        result["manifest_sha256"]=run["files"]?["manifest.json"]?.DeepClone(); result["index_sha256"]=run["files"]?["index.jsonl"]?.DeepClone(); result["resolver_exit"]=run["resolver_exit"]?.DeepClone();
        result["extraction_allowed"]=true;
        result["resolver_safe_to_persist"]=ReadJson(Path.Combine(directory,"manifest.json"))["window"]?["safe_to_persist"]?.DeepClone();
        result["checkpoint_permission"]="none_final_review_and_delivery_required";
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
        var buffer=new byte[8192]; var buffered=0; var line=1; var completed=0; var hasBytes=false;
        // Raw bytes only: skip the prefix, hash exactly the advertised lines and
        // stop at end. The existing Python extractor owns JSON interpretation.
        while(line<=end) {
            var value=stream.ReadByte();
            if(value<0) { if(hasBytes) completed=line; break; }
            hasBytes=true;
            if(line>=start) { buffer[buffered++]=(byte)value; if(buffered==buffer.Length) { digest.AppendData(buffer); buffered=0; } }
            if(value=='\n') { completed=line++; hasBytes=false; }
        }
        if(completed<end) throw new ReviewBlocked("truncated_advertised_range");
        if(buffered>0) digest.AppendData(buffer.AsSpan(0,buffered));
        return Convert.ToHexStringLower(digest.GetHashAndReset());
    }
    static JsonObject Extract(JsonObject run,JsonObject selection,string folder,IEnumerable<string> arguments,JsonObject pins)
    {
        PrivateDirectory(folder);
        var snapshot=Path.Combine(folder,"extractor.py"); WriteBytes(snapshot,File.ReadAllBytes(Text(selection,"extractor")));
        if(FileHash(snapshot)!=Text(selection,"extractor_sha256")) throw new ReviewBlocked("extractor_changed_during_capture");
        var command=new List<string> { snapshot,"--manifest",Path.Combine(Text(run,"run_directory"),"manifest.json") }; command.AddRange(arguments);
        var process=Run(Text(selection,"python"),command);
        var stdout=Path.Combine(folder,"stdout.json"); var stderr=Path.Combine(folder,"stderr.txt");
        WriteBytes(stdout,process.Out); WriteBytes(stderr,process.Error); WriteBytes(Path.Combine(folder,"exit.txt"),Encoding.UTF8.GetBytes(process.Exit.ToString()));
        CheckPins(pins);
        var envelope=new JsonObject {
            ["schema_version"]=1,["manifest_sha256"]=selection["manifest_sha256"]!.DeepClone(),["selection_sha256"]=JsonHash(selection),
            ["extractor_sha256"]=selection["extractor_sha256"]!.DeepClone(),["arguments"]=Strings(command.Skip(3)),
            ["exit"]=process.Exit,["stdout_sha256"]=Hash(process.Out),["stderr_sha256"]=Hash(process.Error),["source_pins"]=pins.DeepClone()
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
        if(File.Exists(pointerPath)) {
            var existingPointer=ReadJson(pointerPath); var (previous,_)=ReadExtraction(existingPointer,selection,pages);
            Count(previous,"offset",offset);
            var previousLimit=Number(previous,"limit",0); var previousMax=Number(previous,"max_total_chars",0);
            if(previousLimit<1 || previousMax<2000 || previousMax>2000000) throw new ReviewBlocked("invalid_stored_page_bounds");
            if(previousLimit==limit && previousMax==max) {
                if(!StringArray(previous,"expected_ids").SequenceEqual(pageIds,StringComparer.Ordinal) || JsonHash(previous["source_pins"]!)!=JsonHash(pins)) throw new ReviewBlocked("stored_page_inputs_changed");
                return PageResult("page_reused",Text(existingPointer,"folder"),pointerPath,previous,offset);
            }
        }
        var folder=Path.Combine(pages,"output-"+Guid.NewGuid().ToString("N"));
        var arguments=new List<string>(); var scope=selection["scope"]!.AsObject();
        foreach(var value in StringArray(scope,"cwd_roots")) { arguments.Add("--cwd-root"); arguments.Add(value); }
        foreach(var value in StringArray(scope,"worktree_tails")) { arguments.Add("--worktree-tail"); arguments.Add(value); }
        arguments.AddRange(["--session-offset",offset.ToString(),"--session-limit",limit.ToString(),"--max-total-chars",max.ToString()]);
        var envelope=Extract(run,selection,folder,arguments,pins);
        envelope["offset"]=offset; envelope["limit"]=limit; envelope["max_total_chars"]=max; envelope["expected_ids"]=Strings(pageIds);
        WriteJson(Path.Combine(folder,"envelope.json"),envelope,true);
        var pointer=new JsonObject { ["folder"]=folder,["envelope_sha256"]=JsonHash(envelope) };
        WriteJson(pointerPath,pointer,true);
        return PageResult("page_captured",folder,pointerPath,envelope,offset);
    }
    static JsonObject PageResult(string status,string folder,string pointerPath,JsonObject envelope,int offset)
    {
        var result=NewResult(status); result["output"]=Path.Combine(folder,"stdout.json"); result["page_receipt"]=pointerPath; result["extractor_exit"]=envelope["exit"]!.DeepClone(); result["offset"]=offset;
        return result;
    }
    static (JsonObject Envelope,JsonObject Output) ReadExtraction(JsonObject pointer,JsonObject selection,string allowedFolder)
    {
        var folder=Text(pointer,"folder"); if(!Within(folder,allowedFolder)) throw new ReviewBlocked("foreign_output_folder"); NoLink(folder);
        var envelope=ReadJson(Path.Combine(folder,"envelope.json"));
        if(Number(envelope,"schema_version",0)!=1 || Text(pointer,"envelope_sha256")!=JsonHash(envelope) || Text(envelope,"manifest_sha256")!=Text(selection,"manifest_sha256") || Text(envelope,"selection_sha256")!=JsonHash(selection) || Text(envelope,"extractor_sha256")!=Text(selection,"extractor_sha256")) throw new ReviewBlocked("foreign_or_corrupt_page_binding");
        if(Number(envelope,"exit",-1)!=0 || File.ReadAllText(Path.Combine(folder,"exit.txt"))!="0") throw new ReviewBlocked("extractor_exit_failed");
        if(FileHash(Path.Combine(folder,"stdout.json"))!=Text(envelope,"stdout_sha256") || FileHash(Path.Combine(folder,"stderr.txt"))!=Text(envelope,"stderr_sha256") || FileHash(Path.Combine(folder,"extractor.py"))!=Text(selection,"extractor_sha256")) throw new ReviewBlocked("corrupt_extractor_output");
        CheckPins(envelope["source_pins"]!.AsObject());
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
        var decision=Text(request,"decision"); if(decision is not ("unchanged" or "update_needed" or "blocked")) throw new ReviewBlocked("invalid_topic_decision");
        if(decision=="unchanged" && TextOrEmpty(context,"no_durable_doc_disposition").Length==0 && !context["wiki_sha256"]!.AsObject().Any(pair=>pair.Value?.GetValue<string>()!="missing")) throw new ReviewBlocked("unchanged_requires_existing_wiki_or_explicit_no_durable_doc_disposition");
        var state=decision switch { "update_needed"=>"pending_delivery", "blocked"=>"blocked", _=>"comparison_only" };
        var receipt=new JsonObject { ["schema_version"]=1,["context"]=context,["context_sha256"]=JsonHash(context),["decision"]=decision,["delivery_state"]=state,["comparison"]=Text(request,"comparison"),["checkpoint_permission"]="none_final_review_and_delivery_required" };
        var topics=Path.Combine(directory,"topics"); PrivateDirectory(topics);
        var evidence=Path.Combine(topics,"receipt-"+Guid.NewGuid().ToString("N")+".json"); WriteJson(evidence,receipt);
        var pointer=new JsonObject { ["receipt"]=evidence,["receipt_sha256"]=JsonHash(receipt) }; WriteJson(TopicPath(directory,Text(context,"topic_id")),pointer,true);
        var result=NewResult(decision=="blocked" ? "topic_blocked" : decision=="update_needed" ? "pending_delivery" : "recorded"); result["receipt"]=evidence; result["receipt_sha256"]=JsonHash(receipt); result["delivery_state"]=state; result["checkpoint_permission"]="none_final_review_and_delivery_required"; return result;
    }
    public static JsonObject ResumeTopics(JsonObject request)
    {
        var directory=Full(request,"run_directory"); var rawRun=ReadJson(Path.Combine(directory,"run.json")); using var mutex=LockRun(rawRun);
        var (run,selection,pages)=Selection(request); var proof=CurrentProof(run,selection,pages); var context=TopicContext(request,run,selection,proof);
        var path=TopicPath(directory,Text(context,"topic_id")); if(!File.Exists(path)) return NewResult("missing");
        var pointer=ReadJson(path); var evidence=Text(pointer,"receipt"); if(!Within(evidence,Path.Combine(directory,"topics"))) throw new ReviewBlocked("foreign_topic_receipt");
        var receipt=ReadJson(evidence);
        if(Number(receipt,"schema_version",0)!=1 || JsonHash(receipt)!=Text(pointer,"receipt_sha256") || JsonHash(receipt["context"]!)!=Text(receipt,"context_sha256")) throw new ReviewBlocked("corrupt_topic_receipt");
        if(JsonHash(context)!=Text(receipt,"context_sha256")) { var stale=NewResult("stale"); stale["reason"]="source_pins_candidates_wiki_or_receipt_changed"; return stale; }
        var decision=Text(receipt,"decision"); var expectedState=decision switch { "unchanged"=>"comparison_only","update_needed"=>"pending_delivery","blocked"=>"blocked",_=>throw new ReviewBlocked("invalid_stored_topic_decision") };
        if(Text(receipt,"delivery_state")!=expectedState) throw new ReviewBlocked("invalid_delivery_claim");
        var result=receipt.DeepClone().AsObject(); result["status"]=decision=="blocked" ? "topic_blocked" : "reusable"; result["receipt"]=evidence; result["receipt_sha256"]=JsonHash(receipt); return result;
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

const http=require('node:http'), fs=require('node:fs'), path=require('node:path');
const {chromium}=require(process.env.HOME+'/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright-core');
// Controlled HTTP/SSE fault cases supplement the persisted-data browser tests.
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../src/Wpcp.Api/wwwroot');
let state='running', position=0, available=true; const streams=new Set();
const record={submissionId:'sub1',title:'Saved requirement',runId:'r1',body:'Requirement body',repository:{fullName:'o/r'},source:{url:'https://github.com/o/r/issues/1',updatedAt:'2026-09-14T10:00:00Z',issueNumber:1,providerIssueId:1},admittedAt:'2026-09-14T10:00:00Z',redaction:{occurred:false,policyVersion:'1'},submittedBy:{provider:'github',subjectId:'1'},contentSha256:'sha'};
const run=()=>({runId:'r1',state:state==='completed'?'analysis-completed':state,lastPosition:position,activities:[{activityId:'a1',activityType:'submission-analysis',state}],attempts:[{activityId:'a1',attemptId:'t1',attemptNumber:1,state,session:{sessionId:'s1',originalResult:{artifactId:'f1'}}}]});
const server=http.createServer((req,res)=>{
 const url=new URL(req.url,'http://localhost'), pathname=url.pathname;
 const json=(value,status=200)=>{res.writeHead(status,{'Content-Type':'application/json'});res.end(JSON.stringify(value));};
 if(pathname==='/api/v1/submissions'&&req.method==='POST')return json({code:'github-issue-not-found'},404);
 if(pathname==='/api/v1/submissions')return json({submissions:[record]});
 if(pathname==='/api/v1/submissions/sub1')return json(record);
 if(pathname==='/api/v1/submissions/sub1/execution')return json({submissionId:'sub1',runId:'r1',state});
 if(pathname==='/api/v1/runs/r1')return json(run());
 if(pathname==='/api/v1/runs/r1/artifacts')return json({artifacts:[{artifactId:'f1',mediaType:'application/json',sizeBytes:60,redaction:{occurred:false},availability:available?'available':'missing'}]});
 if(pathname==='/api/v1/runs/r1/artifacts/f1')return available ? json({summary:'Current result',findings:[]}) : json({code:'artifact-unavailable',availability:'missing'},410);
 if(pathname==='/api/v1/runs/r1/events')return json({events:[],nextAfter:Number(url.searchParams.get('after')||0),lastPosition:position,hasMore:false});
 if(pathname==='/api/v1/runs/r1/events/stream'){res.writeHead(200,{'Content-Type':'text/event-stream'});res.write(': connected\n\n');streams.add(res);req.on('close',()=>streams.delete(res));return;}
 const file=path.join(root,pathname==='/operator/'?'operator/index.html':pathname);
 try{res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(file));}catch{res.statusCode=404;res.end();}
});
function advance(){position++;const event={eventId:'e'+position,position,runId:'r1',eventType:'SubmissionExecutionStateChanged',payload:{attemptId:'t1'}};for(const stream of streams)stream.write('event: run-event\ndata: '+JSON.stringify(event)+'\n\n');}
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
 const page=await browser.newPage();page.setDefaultTimeout(5000);
 await page.goto('http://127.0.0.1:'+server.address().port+'/operator/');
 await page.getByLabel('GitHub-Zugangstoken').fill('test-credential');
 await page.getByRole('button',{name:'Verbinden',exact:true}).click();
 await page.getByText('Mit GitHub verbunden',{exact:true}).waitFor();
 const results=[];
 await page.getByRole('tab',{name:'Verlauf',exact:true}).click();
 await page.locator('#history-status').filter({hasText:'Live verbunden'}).waitFor();
 await page.locator('#session-detail > details > summary').click();
 const summary=await page.locator('#session-detail > details > summary').elementHandle();
 results.push({case:'session_before',focused:await page.evaluate(()=>document.activeElement.textContent),expanded:await page.locator('#session-detail > details').getAttribute('open')!==null});
 state='reconciling';advance();await page.waitForTimeout(900);
 results.push({case:'session_after',focusedTag:await page.evaluate(()=>document.activeElement.tagName),nodeStillConnected:await summary.evaluate(n=>n.isConnected),expanded:await page.locator('#session-detail > details').getAttribute('open')!==null});
 await page.getByRole('tab',{name:'Dateien',exact:true}).click();
 await page.locator('#artifact-list button').focus();
 const artifact=await page.locator('#artifact-list button').elementHandle();
 available=false;advance();await page.waitForTimeout(900);
 results.push({case:'artifact_after',focusedTag:await page.evaluate(()=>document.activeElement.tagName),nodeStillConnected:await artifact.evaluate(n=>n.isConnected),selectedTab:await page.locator('[role=tab][aria-selected=true]').textContent()});
 await page.locator('.intake-disclosure > summary').click();
 await page.getByLabel('GitHub-Issue-URL').fill('https://github.com/o/r/issues/999');
 await page.getByRole('button',{name:'Aufnehmen',exact:true}).click();
 await page.locator('#error').filter({hasText:'nicht gefunden'}).waitFor();
 state='completed';
 await page.locator('.submission-row .badge').filter({hasText:'Analyse abgeschlossen'}).waitFor();
 await page.waitForTimeout(1500);
 results.push({case:'rejected_intake_then_state_change',header:await page.locator('[data-execution=state]').textContent(),row:await page.locator('.submission-row .badge').textContent(),freshness:await page.locator('[data-execution=freshness]').textContent()});
 console.log(JSON.stringify(results));
 if (process.argv[2] === 'rejection') {
   assert.equal(results[3].header, 'Analyse abgeschlossen', 'Rejected intake froze the selected header');
 } else {
   assert.equal(results[1].nodeStillConnected, true, 'Live update replaced focused session disclosure');
   assert.equal(results[1].expanded, true, 'Live update closed session disclosure');
   assert.equal(results[1].focusedTag, 'SUMMARY');
   assert.equal(results[2].nodeStillConnected, true, 'Live update replaced focused artifact control');
   assert.equal(results[2].focusedTag, 'BUTTON');
 }

 }finally{await browser.close();server.closeAllConnections();server.close();}
})().catch(error=>{console.error(error);server.closeAllConnections();server.close();process.exitCode=1;});

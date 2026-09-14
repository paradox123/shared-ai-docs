// Presentation of retained observations. Transport, authorization and replay stay in workflow-view.
export function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
export function disclosure(title, child, className = '') {
  const node = element('details', undefined, className);
  node.append(element('summary', title), child);
  return node;
}
export function rawDetails(title, value, className = 'technical-details') {
  return disclosure(title, element('pre', JSON.stringify(value, null, 2)), className);
}
export function duration(start, end) {
  const milliseconds = new Date(end).getTime() - new Date(start).getTime();
  return start && end && Number.isFinite(milliseconds) && milliseconds >= 0
    ? new Intl.NumberFormat('de-DE', {maximumFractionDigits: 1}).format(milliseconds / 1000) + ' s' : null;
}
function parsed(value) {
  if (typeof value !== 'string') return value;
  try { const result = JSON.parse(value); return result && typeof result === 'object' ? result : value; } catch { return value; }
}
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);

// A small safe text renderer: no HTML insertion, links, scripts or remote assets.
export function prose(text) {
  const block = element('div', undefined, 'readable-text');
  let list, code;
  for (const line of String(text).split('\n')) {
    if (line.startsWith('```')) {
      if (code) code = null;
      else { code = element('pre', ''); block.append(code); }
      list = null; continue;
    }
    if (code) { code.textContent += line + '\n'; continue; }
    if (!line.trim()) { list = null; continue; }
    const heading = line.match(/^#{1,6}\s+(.+)/);
    const bullet = line.match(/^\s*(?:[-*]|\d+\.)\s+(.+)/);
    if (heading) { block.append(element('h5', heading[1])); list = null; }
    else if (bullet) {
      if (!list) { list = element('ul'); block.append(list); }
      list.append(element('li', bullet[1]));
    } else { block.append(element('p', line)); list = null; }
  }
  return block;
}
const fieldLabels = {
  command: 'Befehl', body: 'Inhalt', title: 'Titel', summary: 'Zusammenfassung',
  findings: 'Erkenntnisse', outcome: 'Ergebnis', error: 'Fehler', message: 'Meldung',
  exitCode: 'Exit-Code', stdout: 'Ausgabe', stderr: 'Fehlerausgabe', reason: 'Grund',
  parameters: 'Parameter', arguments: 'Parameter', result: 'Ergebnis', content: 'Inhalt',
  durationMs: 'Dauer (ms)', text: 'Text', status: 'Status', name: 'Name',
};
export function readable(value) {
  value = parsed(value);
  if (value == null) return element('p', 'Nicht aufgezeichnet.', 'muted');
  if (typeof value !== 'object') return prose(value);
  if (Array.isArray(value)) {
    const list = element('ul', undefined, 'readable-list');
    for (const item of value) { const li = element('li'); li.append(readable(item)); list.append(li); }
    if (!value.length) list.append(element('li', 'Keine Einträge.'));
    return list;
  }
  const block = element('div', undefined, 'structured-content');
  if (value.contractVersion === 'AgentSessionAdapter/v1' && Array.isArray(value.events)
    && value.events.every(event => object(event) && typeof event.type === 'string' && object(event.data))) {
    block.append(element('h4', 'Sessionereignisse · ' + value.events.length));
    for (const event of value.events) {
      const d = describe({payload: event, eventType: event.type});
      block.append(disclosure(d.title, readable(d.value ?? d.data)));
    }
    return block;
  }
  if (typeof value.summary === 'string' && Array.isArray(value.findings)) {
    block.append(prose(value.summary));
    if (value.findings.length) block.append(disclosure('Erkenntnisse · ' + value.findings.length, readable(value.findings), 'findings-details'));
    return block;
  }
  const source = value.submission || value;
  if (typeof source.title === 'string' && typeof source.body === 'string') {
    block.append(element('h4', source.title), prose(source.body));
    return block;
  }
  if (Array.isArray(value.content) && value.content.every(part => object(part) && typeof part.type === 'string')) {
    for (const part of value.content) block.append(typeof part.text === 'string' ? readable(part.text) : readable(part));
    if (value.structuredContent != null) block.append(readable(value.structuredContent));
    return block;
  }
  const fields = element('dl', undefined, 'readable-fields');
  for (const [key, child] of Object.entries(value)) {
    const dd = element('dd'); dd.append(readable(child));
    fields.append(element('dt', fieldLabels[key] || key), dd);
  }
  block.append(fields);
  return block;
}

const systemLabels = {
  ImplementationRunStarted: 'Run gestartet', SubmissionExecutionQueued: 'Analyse eingeplant',
  SubmissionExecutionStateChanged: 'Ausführungsstatus aktualisiert', AgentPreparationCompleted: 'Agent vorbereitet',
  AgentSessionStartRequested: 'Agentensession angefordert', AgentAdapterResponseObserved: 'Agentenantwort gespeichert',
  AgentSessionStarted: 'Agentensession gestartet', AgentAttemptCompleted: 'Versuch abgeschlossen',
  AgentAttemptFailed: 'Versuch fehlgeschlagen',
};
const roleLabels = {user: 'Auftrag an den Agenten', assistant: 'Agent', system: 'Systemnachricht'};
function contentText(item) {
  return typeof item.text === 'string' ? item.text : Array.isArray(item.content)
    ? item.content.filter(c => object(c) && typeof c.text === 'string').map(c => c.text).join('\n') : undefined;
}
function toolObservation(item, data) {
  if (item?.type === 'commandExecution') return {...item, tool: item.command || 'Terminal',
    arguments: item.command == null ? null : {command: item.command}, result: item.aggregatedOutput};
  if (item?.type === 'dynamicToolCall') return {...item, result: item.contentItems == null ? null : {content: item.contentItems}, isError: item.success === false};
  return item || data;
}
export function describe(event) {
  const p = event.payload, data = p.data ?? p;
  const runtime = data.runtimeEvent, item = runtime?.params?.item;
  const base = {event, data, kind: 'system', title: systemLabels[event.eventType] || 'Weiteres Ereignis', visible: false};
  if (p.type === 'result') return {...base, kind: 'result', title: data.outcome === 'failed' ? 'Analyse fehlgeschlagen' : 'Analyseergebnis', visible: true, value: data};
  if (p.type === 'artifact') return {...base, kind: 'artifact', title: 'Datei gespeichert', visible: true, value: data.name || 'Artefakt'};
  if (p.type?.startsWith('tool-')) {
    const tool = toolObservation(item, data);
    const command = tool.arguments?.command ?? tool.parameters?.command;
    const name = Array.isArray(command) ? command.join(' ') : tool.tool || tool.name || 'Werkzeug';
    const finished = p.type === 'tool-result';
    return {...base, kind: 'tool', title: name === 'read-admitted-issue' ? 'Aufgenommene Anforderungen lesen' : name,
      visible: true, tool, finished, failed: tool.status === 'failed' || tool.error != null || tool.isError === true || tool.result?.isError === true || (tool.exitCode != null && tool.exitCode !== 0),
      value: finished ? tool.result ?? (item ? null : data.body ?? data.output) : tool.arguments ?? tool.parameters};
  }
  if (p.type === 'process-exit') return {...base, kind: 'error', title: 'Agentenprozess beendet', visible: true, value: data};
  if (data.assignment) return {...base, kind: 'assignment', title: 'Aufgenommener Auftrag', visible: true, value: data.assignment};
  if (p.type === 'message' && typeof data.text === 'string') return {...base, kind: 'message', title: roleLabels[data.role] || 'Nachricht', visible: true, value: data.text, role: data.role};
  if (runtime && ['userMessage', 'agentMessage'].includes(item?.type)) {
    const text = contentText(item);
    return {...base, kind: 'message', title: item.type === 'agentMessage' ? 'Agent' : 'Auftrag an den Agenten',
      visible: runtime.method === 'item/completed' && Boolean(text), value: text,
      role: item.type === 'agentMessage' ? 'assistant' : 'user', native: true};
  }
  if (runtime) {
    const error = runtime.params?.error ?? runtime.params?.turn?.error;
    if (runtime.method === 'error' || error != null || runtime.params?.turn?.status === 'failed') {
      return {...base, kind: 'error', title: 'Fehler während der Agentenarbeit', visible: true,
        value: error ?? runtime.params?.message ?? 'Keine Fehlerbeschreibung aufgezeichnet.'};
    }
    if (['wpcp/runtimeExited', 'wpcp/processStopped'].includes(runtime.method)) return {...base, kind: 'error', title: 'Agentenprozess beendet', visible: true, value: runtime.params};
    return {...base, title: {'turn/started': 'Agent beginnt die Bearbeitung', 'turn/completed': 'Agent hat die Bearbeitung beendet'}[runtime.method] || 'Agentenprotokoll'};
  }
  if (data.phase === 'analysis-finished') return {...base, title: 'Analyse beendet'};
  if (p.type === 'message') return {...base, title: 'Weitere Sessionbeobachtung', visible: true};
  return base;
}

export function conversation(descriptions) {
  // Only remove repeated representations within the same attempt, never repeated authored messages.
  return descriptions.filter(d => {
    if (!d.visible) return false;
    if (d.kind === 'tool' && !d.finished && d.tool.id && descriptions.some(other => other.kind === 'tool' && other.finished
      && other.tool.id === d.tool.id && other.event.payload.attemptId === d.event.payload.attemptId
      && other.tool.arguments != null)) return false;
    if (!d.native) return true;
    const sameAttempt = other => other.event.payload.attemptId === d.event.payload.attemptId;
    if (descriptions.some(other => sameAttempt(other) && !other.native && other.kind === 'message' && other.role === d.role && other.value === d.value)) return false;
    const value = parsed(d.value);
    return !(value && typeof value === 'object' && descriptions.some(other => sameAttempt(other) && other.kind === 'result'
      && value.summary === other.value.summary && JSON.stringify(value.findings) === JSON.stringify(other.value.findings)));
  });
}

export function eventCard(d, openStored) {
  const entry = element('article', undefined, 'history-entry event-' + d.kind);
  entry.dataset.eventId = d.event.eventId; entry.dataset.position = d.event.position;
  const header = element('header', undefined, 'event-heading');
  header.append(element('h4', d.title), element('time', new Date(d.event.occurredAt).toLocaleTimeString('de-DE', {hour: '2-digit', minute: '2-digit', second: '2-digit'})));
  entry.append(header);
  if (d.event.redaction?.occurred) entry.append(element('p', 'Inhalt redigiert', 'redaction-note'));
  if (typeof d.data.artifactId === 'string' && typeof d.data.mediaType === 'string') {
    entry.append(element('p', 'Der vollständige Inhalt ist als Datei gespeichert.'));
    const button = element('button', 'Vollständigen Inhalt öffnen', 'quiet');
    button.onclick = () => openStored(d.data);
    entry.append(button);
  } else if (d.kind === 'tool') {
    const status = d.failed ? 'Fehler' : d.finished ? 'Beendet' : 'Aufgerufen';
    const timing = Number.isFinite(d.tool.durationMs) ? d.tool.durationMs + ' ms' : 'Dauer nicht aufgezeichnet';
    entry.dataset.state = d.failed ? 'failed' : 'completed';
    entry.append(element('p', status + (d.finished ? ' · ' + timing : ''), 'tool-status'));
    const body = element('div');
    if (d.finished && d.tool.arguments != null) body.append(element('h5', 'Parameter'), readable(d.tool.arguments));
    body.append(element('h5', d.finished ? 'Ergebnis' : 'Parameter'), readable(d.value));
    if (d.tool.error != null) body.append(element('h5', 'Fehler'), readable(d.tool.error));
    if (d.tool.exitCode != null) body.append(element('p', 'Exit-Code: ' + d.tool.exitCode));
    entry.append(disclosure(d.finished ? 'Ergebnis und Fehler ansehen' : 'Parameter ansehen', body, 'tool-details'));
  } else if (d.kind === 'assignment' || (d.kind === 'message' && d.role === 'user')) {
    entry.append(disclosure(d.kind === 'assignment' ? 'Vollständigen Auftrag lesen' : 'Anweisung lesen', readable(d.value), 'assignment-details'));
  } else if (d.value !== undefined) entry.append(readable(d.value));
  else entry.append(disclosure('Gespeicherte Angaben ansehen', readable(d.data)));
  entry.append(rawDetails('Technische Details · Ereignis ' + d.event.position, d.event, 'technical-details event-raw'));
  return entry;
}

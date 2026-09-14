const $ = id => document.getElementById(id);
const labels = {
  admission: 'Aufnahme', 'submission-analysis': 'Anforderungen analysieren',
  completed: 'Abgeschlossen', running: 'Läuft', queued: 'Wartend', failed: 'Fehlgeschlagen',
  'analysis-completed': 'Analyse abgeschlossen', 'process-failure': 'Prozessfehler',
  message: 'Nachricht / Auftrag', 'tool-call': 'Toolaufruf · Parameter',
  'tool-result': 'Toolergebnis · Dauer / Fehler', result: 'Erkenntnisse / Ergebnis',
  artifact: 'Artefakt', 'process-exit': 'Prozessende',
};
const label = value => labels[value] || value;
const json = value => JSON.stringify(value, null, 2);
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function details(title, value) {
  const node = element('details');
  node.append(element('summary', title), element('pre', json(value)));
  return node;
}

export async function showWorkflow(submission, signal, api, reportError, selectRun) {
  const read = (suffix, format = 'json') => api('/' + submission.runId + suffix, signal, null, '/api/v1/runs', format);
  let run, selected = null, cursor = 0, highWater = 0, hasMore = false, streaming = false;
  let timer, refreshTimer, artifacts = [], artifactGeneration = 0;
  const events = new Map();
  signal.addEventListener('abort', () => {
    clearTimeout(timer); clearTimeout(refreshTimer);
    events.clear(); artifacts = []; run = null; artifactGeneration++;
    $('history-filter').onchange = null;
    $('history-more').onclick = null;
    $('all-history').onclick = null;
  }, {once: true});
  const active = () => !signal.aborted;
  function failed(error) {
    if (!active()) return;
    if (error.status === 401 || error.status === 403) { reportError(error); return; }
    $('history-status').textContent = 'Verbindung unterbrochen · Erneuter Versuch ab Position ' + cursor + '. ' + error.message;
  }

  function renderGraph() {
    $('workflow-state').textContent = label(run.state);
    const graph = $('workflow-graph');
    graph.replaceChildren();
    for (const activity of run.activities) {
      const group = element('section', undefined, 'activity-node');
      group.dataset.activityId = activity.activityId;
      group.append(element('h3', label(activity.activityType)), element('span', label(activity.state), 'badge'));
      for (const attempt of run.attempts.filter(a => a.activityId === activity.activityId)) {
        const node = element('button', undefined, 'attempt-node');
        node.dataset.attemptId = attempt.attemptId;
        node.setAttribute('aria-pressed', String(selected === attempt.attemptId));
        node.append(element('strong', 'Versuch ' + attempt.attemptNumber + ' · ' + label(attempt.state)),
          element('code', attempt.attemptId), element('span', attempt.session?.sessionId
            ? 'Session · ' + attempt.session.sessionId : 'Keine bestätigte Agentensession'));
        node.addEventListener('click', () => select(attempt.attemptId));
        group.append(node);
      }
      graph.append(group);
    }
  }
  function renderSelection() {
    const target = run.attempts.find(a => a.attemptId === selected);
    const content = $('session-detail'); content.replaceChildren();
    content.append(element('h3', target ? 'Versuch ' + target.attemptNumber + ' · ' + label(target.state) : 'Gemeinsame Run History'));
    content.append(element('p', target?.session?.sessionId ? 'Session · ' + target.session.sessionId
      : target ? 'Keine bestätigte Agentensession für diesen Versuch.' : 'Alle Aktivitäten und Sessions dieses Runs.'));
    content.append(details(target ? 'Versuch, Session und Herkunft' : 'Run und Herkunft', target || {
      runId: run.runId, correlation: run.correlation, provenance: run.provenance, executionEvidence: run.executionEvidence}));
  }
  function select(id) {
    selected = id;
    $('artifact-content').hidden = true;
    $('artifact-content').replaceChildren();
    artifactGeneration++;
    renderGraph(); renderSelection(); renderHistory(); renderArtifacts();
  }
  function selectedEvents() {
    return [...events.values()].filter(event => !selected || event.payload.attemptId === selected);
  }
  function renderHistory() {
    const filter = $('history-filter').value;
    const list = $('history-list');
    const relevant = selectedEvents().filter(event => filter === 'all' ||
      (filter === 'tool' ? event.payload.type?.startsWith('tool-') : event.payload.type === filter));
    // Retain existing nodes (and their expanded detail) while appending live events.
    const visible = new Set(relevant.map(event => event.eventId));
    for (const node of [...list.children]) if (!visible.has(node.dataset.eventId)) node.remove();
    let index = 0;
    for (const event of relevant) {
      const existing = list.querySelector(`[data-event-id="${event.eventId}"]`);
      if (existing) {
        if (list.children[index] !== existing) list.insertBefore(existing, list.children[index] || null);
        index++;
        continue;
      }
      const entry = element('article', undefined, 'history-entry');
      entry.dataset.eventId = event.eventId; entry.dataset.position = event.position;
      entry.append(element('h4', `${event.position} · ${label(event.payload.type || event.eventType)}`),
        element('time', new Date(event.occurredAt).toLocaleString('de-DE')));
      if (event.redaction.occurred) entry.append(element('p', 'Inhalt redigiert · ' + event.redaction.policyVersion, 'redaction-note'));
      entry.append(element('pre', json(event.payload.data ?? event.payload)));
      if (event.payload.type?.startsWith('tool-')) entry.append(element('small',
        'Nur erfasste Parameter, Ergebnisse, Dauer und Fehler sind enthalten; fehlende Felder wurden nicht aufgezeichnet.'));
      entry.append(details('Identität, Sessionreihenfolge und Herkunft', event));
      list.insertBefore(entry, list.children[index] || null);
      index++;
    }
    if (!relevant.length) list.append(element('p', 'Keine passenden Ereignisse in den bisher geladenen Seiten.', 'history-empty'));
  }
  function artifactIds(value, ids = new Set()) {
    if (!value || typeof value !== 'object') return ids;
    if (typeof value.artifactId === 'string') ids.add(value.artifactId);
    for (const child of Object.values(value)) artifactIds(child, ids);
    return ids;
  }
  function renderArtifacts() {
    const ids = artifactIds([selectedEvents(), run.attempts.find(a => a.attemptId === selected)?.session]);
    const visible = artifacts.filter(artifact => !selected || ids.has(artifact.artifactId));
    const list = $('artifact-list'); list.replaceChildren();
    for (const artifact of visible) {
      const row = element('div', undefined, 'artifact-row'); row.dataset.artifactId = artifact.artifactId;
      const button = element('button', 'Inhalt öffnen', 'quiet');
      button.onclick = () => openArtifact(artifact);
      row.append(element('code', artifact.artifactId),
        element('p', `${artifact.mediaType} · ${artifact.sizeBytes} Bytes · ${artifact.availability}`));
      if (artifact.redaction.occurred) row.append(element('p', 'Inhalt redigiert · ' + artifact.redaction.policyVersion, 'redaction-note'));
      if (artifact.availability !== 'available') row.append(element('p', 'Inhalt nicht verfügbar · ' + (artifact.reason || artifact.availability)));
      row.append(button); list.append(row);
    }
    if (!visible.length) list.append(element('p', 'Keine Artefaktreferenzen in der geladenen Auswahl. Weitere History-Seiten oder den gesamten Run öffnen.'));
  }
  async function openArtifact(artifact) {
    const generation = ++artifactGeneration;
    const content = $('artifact-content');
    content.hidden = false; content.textContent = 'Artefakt wird geladen …';
    try {
      const response = await read('/artifacts/' + encodeURIComponent(artifact.artifactId), 'response');
      const bytes = new Uint8Array(await response.arrayBuffer());
      signal.throwIfAborted();
      if (generation !== artifactGeneration) return;
      // Never navigate to a source URI or interpret artifact text as HTML/script.
      const text = artifact.mediaType === 'application/octet-stream'
        ? 'Binärinhalt (Hexadezimal):\n' + Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join(' ')
        : new TextDecoder().decode(bytes);
      content.textContent = artifact.mediaType === 'application/json' ? json(JSON.parse(text)) : text;
      content.focus();
    } catch (error) {
      if (!active() || generation !== artifactGeneration) return;
      if (error.status === 404 || error.status === 410) {
        content.textContent = 'Inhalt nicht verfügbar · ' + (error.payload?.reason || error.payload?.availability || 'artifact-not-found');
      } else { content.textContent = 'Artefakt konnte nicht geladen werden.'; failed(error); }
    }
  }
  function status(text) {
    $('history-status').textContent = `${text} · ${cursor} von mindestens ${highWater} Positionen geladen`;
    $('history-more').hidden = !hasMore;
  }
  function accept(entry) {
    if (entry.position <= cursor && events.has(entry.eventId)) return;
    if (entry.runId !== submission.runId || entry.position !== cursor + 1 || events.has(entry.eventId))
      throw new Error('Die History-Reihenfolge konnte nicht bestätigt werden. Bitte Anforderungen aktualisieren.');
    events.set(entry.eventId, entry);
    cursor = entry.position;
    highWater = Math.max(highWater, cursor);
  }
  async function projection() {
    const current = await read('');
    signal.throwIfAborted();
    const manifest = await read('/artifacts');
    signal.throwIfAborted();
    const changed = !run || run.lastPosition !== current.lastPosition;
    run = current; artifacts = manifest.artifacts;
    if (changed) { renderGraph(); renderSelection(); }
    renderArtifacts();
  }
  async function more() {
    $('history-more').disabled = true;
    try {
      const page = await read('/events?after=' + cursor + '&limit=100');
      signal.throwIfAborted();
      for (const entry of page.events) accept(entry);
      if (cursor !== page.nextAfter) throw new Error('Unbestätigte History-Position.');
      highWater = page.lastPosition; hasMore = page.hasMore;
      renderHistory(); renderArtifacts(); status(hasMore ? 'History teilweise geladen' : 'Verbinde Live-Verlauf');
      if (!hasMore) void stream();
    } catch (error) { failed(error); }
    finally { if (active()) $('history-more').disabled = false; }
  }
  async function stream() {
    if (streaming || !active()) return;
    streaming = true;
    let reader;
    try {
      const response = await read('/events/stream?after=' + cursor, 'response');
      signal.throwIfAborted();
      reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      status('Live verbunden');
      while (active()) {
        const chunk = await reader.read();
        signal.throwIfAborted();
        if (chunk.done) throw new Error('Ereignisverbindung beendet.');
        const before = cursor;
        buffer += decoder.decode(chunk.value, {stream: true});
        let boundary;
        while ((boundary = buffer.indexOf('\n\n')) !== -1) {
          const frame = buffer.slice(0, boundary); buffer = buffer.slice(boundary + 2);
          if (frame.includes('event: access-revoked')) {
            const error = new Error('Dein Repository-Zugriff konnte nicht mehr bestätigt werden. Bitte erneut verbinden.');
            error.status = 403; throw error;
          }
          const data = frame.split('\n').find(line => line.startsWith('data: '));
          if (data) accept(JSON.parse(data.slice(6)));
        }
        renderHistory(); status('Live verbunden');
        if (cursor !== before && !refreshTimer) refreshTimer = setTimeout(async () => {
          try {
            do { await projection(); } while (active() && run.lastPosition < cursor);
          } catch (error) { failed(error); }
          finally { refreshTimer = undefined; }
        }, 500);
      }
    } catch (error) {
      failed(error);
      if (active()) timer = setTimeout(stream, 1200);
    } finally {
      streaming = false;
      if (reader) await reader.cancel().catch(() => {});
    }
  }
  $('history-filter').value = 'all';
  $('history-filter').onchange = renderHistory;
  $('history-more').onclick = more;
  $('all-history').onclick = () => select(null);
  await projection();
  const submissions = await api('', signal);
  signal.throwIfAborted();
  for (const record of submissions.submissions.filter(s => s.runId)) {
    const button = element('button', record.title, 'quiet');
    button.dataset.runId = record.runId;
    button.setAttribute('aria-current', String(record.runId === submission.runId));
    button.onclick = () => selectRun(record.submissionId);
    $('run-list').append(button);
  }
  $('workflow').hidden = false;
  await more();
}

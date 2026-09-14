import {element, disclosure, rawDetails, duration, readable, describe, conversation, eventCard} from './session-content.js';
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

export async function showWorkflow(submission, signal, api, reportError, selectRun) {
  const read = (suffix, format = 'json') => api('/' + submission.runId + suffix, signal, null, '/api/v1/runs', format);
  let run, selected = null, cursor = 0, highWater = 0, hasMore = false, streaming = false;
  let selectionChosen = false, renderedSelection;
  let timer, refreshTimer, artifacts = [], artifactGeneration = 0;
  let projectionPending = false, projectionRefreshing = false;
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
    $('workflow-state').dataset.state = run.state;
    const graph = $('workflow-graph');
    const focusedAttempt = graph.contains(document.activeElement) ? document.activeElement.dataset.attemptId : null;
    graph.replaceChildren();
    for (const activity of run.activities) {
      const group = element('section', undefined, 'activity-node');
      group.dataset.activityId = activity.activityId;
      const badge = element('span', label(activity.state), 'badge'); badge.dataset.state = activity.state;
      group.append(element('h3', label(activity.activityType)), badge);
      for (const attempt of run.attempts.filter(a => a.activityId === activity.activityId)) {
        const node = element('button', undefined, 'attempt-node');
        node.dataset.attemptId = attempt.attemptId;
        node.setAttribute('aria-pressed', String(selected === attempt.attemptId));
        node.append(element('strong', 'Versuch ' + attempt.attemptNumber + ' · ' + label(attempt.state)),
          element('span', (attempt.session ? 'Agentensession' : 'Ohne Agentensession')
            + (duration(attempt.startedAt, attempt.completedAt) ? ' · ' + duration(attempt.startedAt, attempt.completedAt) : '')));
        node.dataset.state = attempt.state;
        node.addEventListener('click', () => select(attempt.attemptId));
        group.append(node);
      }
      graph.append(group);
    }
    if (focusedAttempt) graph.querySelector(`[data-attempt-id="${focusedAttempt}"]`)?.focus({preventScroll: true});
  }
  function renderSelection() {
    const target = run.attempts.find(a => a.attemptId === selected);
    const activity = run.activities.find(a => a.activityId === target?.activityId);
    const signature = JSON.stringify([selected, target || run.runId]);
    if (signature === renderedSelection) return;
    renderedSelection = signature;
    const host = $('session-detail');
    const focusedOutcome = host.querySelector('.outcome-summary button') === document.activeElement;
    const sameSelection = host.dataset.selection === (selected || 'all');
    host.dataset.selection = selected || 'all';
    const content = element('div');
    content.append(element('span', target ? 'AUSGEWÄHLTER SCHRITT' : 'GESAMTER RUN', 'section-number'),
      element('h3', activity ? label(activity.activityType) : 'Gemeinsamer Verlauf'));
    content.append(element('p', target ? 'Versuch ' + target.attemptNumber + ' · ' + label(target.state)
      + (duration(target.startedAt, target.completedAt) ? ' · ' + duration(target.startedAt, target.completedAt) : '')
      : 'Alle Aktivitäten und Sessions dieses Runs.'));
    const actor = element('p', undefined, 'session-actor'); actor.id = 'session-actor'; content.append(actor);
    const result = target?.session?.originalResult;
    if (result) {
      const outcome = element('div', undefined, 'outcome-summary'); outcome.dataset.state = result.outcome || target.state;
      outcome.append(element('span', 'ERGEBNIS', 'section-number'));
      if (typeof result.summary === 'string') outcome.append(readable(result.summary));
      else if (result.artifactId) {
        const open = element('button', 'Vollständiges Ergebnis öffnen', 'quiet'); open.onclick = () => openArtifact(result); outcome.append(open);
      } else outcome.append(element('p', 'Ergebnis ohne Zusammenfassung. Details im Verlauf.'));
      content.append(outcome);
    }
    const metadata = element('dl', undefined, 'readable-fields');
    const fields = target ? {'Session': target.session?.sessionId || 'Keine bestätigte Agentensession',
      'Versuch': target.attemptId, 'Gestartet': target.startedAt ? new Date(target.startedAt).toLocaleString('de-DE') : 'Nicht aufgezeichnet'} : {'Run': run.runId};
    for (const [key, value] of Object.entries(fields)) metadata.append(element('dt', key), element('dd', value));
    metadata.append(rawDetails('Originaldaten', target || {
      runId: run.runId, correlation: run.correlation, provenance: run.provenance, executionEvidence: run.executionEvidence}));
    const details = disclosure('Session und Herkunft', metadata, 'technical-details');
    const retained = sameSelection && host.querySelector(':scope > details');
    if (retained) {
      // Keep the actual focused disclosures connected while updating their values.
      const values = retained.querySelectorAll('dd');
      metadata.querySelectorAll('dd').forEach((value, index) => { values[index].textContent = value.textContent; });
      retained.querySelector('pre').textContent = metadata.querySelector('pre').textContent;
      for (const child of [...host.children]) if (child !== retained) child.remove();
      for (const child of [...content.children]) host.insertBefore(child, retained);
    } else {
      content.append(details);
      host.replaceChildren(...content.children);
    }
    if (sameSelection && focusedOutcome) host.querySelector('.outcome-summary button')?.focus({preventScroll: true});
  }
  function select(id) {
    selectionChosen = true;
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
    list.dataset.view = filter;
    const descriptions = selectedEvents().map(describe);
    const provenance = descriptions.find(d => d.data.assignment && (d.data.actor || d.data.host))?.data;
    if ($('session-actor')) $('session-actor').textContent = !selected ? '' : provenance
      ? [provenance.actor?.provider === 'codex' ? 'Codex' : provenance.actor?.provider || 'Agent nicht angegeben', provenance.host || 'Ausführungsort nicht angegeben'].join(' · ')
      : 'Agent und Ausführungsort in der geladenen Historie nicht angegeben.';
    const readableEvents = conversation(descriptions);
    const relevant = (filter === 'all' ? descriptions : readableEvents.filter(d => filter === 'conversation' ||
      (filter === 'message' ? ['message', 'assignment'].includes(d.kind) : d.kind === filter))).map(d => d.event);
    $('history-note').textContent = filter === 'all'
      ? 'Alle gespeicherten Ereignisse. Technische Details lassen sich einzeln öffnen.'
      : 'Aufträge, Nachrichten und Werkzeuge in zeitlicher Folge. Protokollmeldungen findest du unter „Alle Ereignisse“.';
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
      const entry = eventCard(describe(event), openArtifact);
      list.insertBefore(entry, list.children[index] || null);
      index++;
    }
    if (!relevant.length) list.append(element('p', 'Noch keine passenden Inhalte geladen.', 'history-empty'));
  }
  function artifactName(artifact) {
    const record = [...events.values()].find(e => e.payload.data?.artifact?.artifactId === artifact.artifactId);
    if (record?.payload.data?.name) return record.payload.data.name;
    if ([...events.values()].some(e => e.payload.type === 'result' && e.payload.data?.artifactId === artifact.artifactId)) return 'Analyseergebnis';
    return ([...events.values()].some(e => e.eventType === 'AgentAdapterResponseObserved'
      && e.payload.body?.artifactId === artifact.artifactId) ? 'Gespeicherte Agentenantwort' : 'Gespeicherte Datei');
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
    const list = $('artifact-list');
    const visibleIds = new Set(visible.map(artifact => artifact.artifactId));
    for (const node of [...list.children]) if (!visibleIds.has(node.dataset.artifactId)) node.remove();
    for (const artifact of visible) {
      let row = list.querySelector(`[data-artifact-id="${artifact.artifactId}"]`);
      const signature = JSON.stringify([artifact, artifactName(artifact)]);
      if (row?.dataset.content === signature) continue;
      const button = row?.querySelector('button') || element('button', 'Inhalt öffnen', 'quiet');
      if (!row) {
        row = element('div', undefined, 'artifact-row');
        row.dataset.artifactId = artifact.artifactId;
        row.append(button); list.append(row);
      }
      row.dataset.content = signature;
      for (const child of [...row.children]) if (child !== button) child.remove();
      const description = element('div');
      button.onclick = () => openArtifact(artifact);
      description.append(element('strong', artifactName(artifact)),
        element('p', `${artifact.mediaType} · ${new Intl.NumberFormat('de-DE', {maximumFractionDigits: 1}).format(artifact.sizeBytes / 1024)} KB`));
      if (artifact.redaction.occurred) description.append(element('p', 'Inhalt redigiert · ' + artifact.redaction.policyVersion, 'redaction-note'));
      if (artifact.availability !== 'available') description.append(element('p', 'Inhalt nicht verfügbar · ' + (artifact.reason || artifact.availability)));
      row.insertBefore(description, button);
    }
    if (!visible.length) list.append(element('p', 'Keine Artefaktreferenzen in der geladenen Auswahl. Weitere History-Seiten oder den gesamten Run öffnen.'));
  }
  async function openArtifact(artifact) {
    document.getElementById('run-tab-files').click();
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
      content.replaceChildren(element('h4', artifactName(artifact)), readable(artifact.mediaType === 'application/json' ? JSON.parse(text) : text),
        rawDetails('Originalinhalt', artifact.mediaType === 'application/json' ? JSON.parse(text) : text, 'technical-details artifact-raw'));
      content.focus();
    } catch (error) {
      if (!active() || generation !== artifactGeneration) return;
      if (error.status === 404 || error.status === 410) {
        content.textContent = 'Inhalt nicht verfügbar · ' + (error.payload?.reason || error.payload?.availability || 'artifact-not-found');
      } else { content.textContent = 'Artefakt konnte nicht geladen werden.'; failed(error); }
    }
  }
  function status(text) {
    $('history-status').textContent = `${text}${projectionPending ? ' · Workflowstand wird abgeglichen' : ''} · ${cursor} von ${highWater} gespeicherten Ereignissen geladen`;
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
    if (!selectionChosen) selected = run.attempts.findLast(a => a.session)?.attemptId || run.attempts.at(-1)?.attemptId || null;
    if (changed) { renderGraph(); renderSelection(); }
    renderArtifacts();
  }
  function scheduleProjection() {
    projectionPending = true;
    if (!refreshTimer && !projectionRefreshing) refreshTimer = setTimeout(refreshProjection, 500);
  }
  async function refreshProjection() {
    refreshTimer = undefined;
    projectionRefreshing = true;
    let succeeded = false;
    try {
      await projection();
      projectionPending = run.lastPosition < Math.max(cursor, highWater);
      succeeded = true;
      status(hasMore ? 'History teilweise geladen' : streaming ? 'Live verbunden' : 'Verbinde Live-Verlauf');
    } catch (error) { failed(error); }
    finally {
      projectionRefreshing = false;
      if (active() && projectionPending) refreshTimer = setTimeout(refreshProjection, succeeded ? 500 : 1200);
    }
  }
  async function more() {
    $('history-more').disabled = true;
    try {
      const page = await read('/events?after=' + cursor + '&limit=100');
      signal.throwIfAborted();
      for (const entry of page.events) accept(entry);
      if (cursor !== page.nextAfter) throw new Error('Unbestätigte History-Position.');
      highWater = page.lastPosition; hasMore = page.hasMore;
      if (run.lastPosition < highWater) scheduleProjection();
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
          const fields = frame.split('\n');
          const eventType = fields.find(line => line.startsWith('event:'))?.slice(6).trim();
          if (eventType === 'access-revoked') {
            const error = new Error('Dein Repository-Zugriff konnte nicht mehr bestätigt werden. Bitte erneut verbinden.');
            error.status = 403; throw error;
          }
          const data = fields.find(line => line.startsWith('data: '));
          if (eventType === 'run-event' && data) accept(JSON.parse(data.slice(6)));
        }
        renderHistory(); status('Live verbunden');
        if (cursor !== before) scheduleProjection();
      }
    } catch (error) {
      failed(error);
      if (active()) timer = setTimeout(stream, 1200);
    } finally {
      streaming = false;
      if (reader) await reader.cancel().catch(() => {});
    }
  }
  $('history-filter').value = 'conversation';
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
  await more();
}

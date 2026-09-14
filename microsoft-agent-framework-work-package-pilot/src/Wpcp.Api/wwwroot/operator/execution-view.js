const states = {
  queued: ['Wartend', 'Der Auftrag ist dauerhaft vorgemerkt und wartet auf einen Worker.'],
  running: ['Läuft', 'Der Worker verarbeitet die Anforderungen.'],
  reconciling: ['Ergebnis wird abgeglichen', 'Der Ausgang ist noch unbestätigt. Der Worker fragt dieselbe Operation erneut ab und übernimmt ihr gespeichertes Ergebnis.'],
  completed: ['Abgeschlossen', 'Die Anforderungsanalyse ist abgeschlossen.'],
  failed: ['Fehlgeschlagen', 'Der erste Schritt konnte nicht erfolgreich abgeschlossen werden.'],
};
const failures = {
  'artifact-storage-unavailable': 'Der Worker kann den gemeinsamen Ergebnisspeicher nicht lesen und beschreiben.',
  'transport-failure': 'Die Verbindung zum Agentendienst ist fehlgeschlagen.',
  timeout: 'Der Agentendienst hat nicht innerhalb der HTTP-Antwortfrist geantwortet.',
  'process-failure': 'Der Agentenprozess ist mit einem Fehler beendet worden.',
  'schema-failure': 'Die Agentenantwort entspricht nicht dem vereinbarten Ergebnisformat.',
  'infrastructure-failure': 'Der Agentendienst meldet einen Infrastrukturfehler.',
  'execution-configuration-changed': 'Die Ausführungskonfiguration wurde seit dem Start geändert.',
  'repository-execution-required': 'Dieses Repository benötigt den bestehenden verwalteten Ausführungspfad.',
  'worker-execution-failed': 'Der Worker konnte den Auftrag nicht ausführen.',
  'agent-failed': 'Der Agent hat einen Ausführungsfehler protokolliert.',
};

export async function showExecution(container, submission, signal, api) {
  const field = name => container.querySelector(`[data-execution="${name}"]`);
  field('start').hidden = true;
  field('detail').hidden = false;
  field('run-id').textContent = submission.runId;
  let timer;
  signal.addEventListener('abort', () => clearTimeout(timer), {once: true});

  async function refresh() {
    const execution = await api('/' + submission.submissionId + '/execution', signal);
    const run = await api('/' + submission.runId, signal, null, '/api/v1/runs');
    const activity = run.activities.find(a => a.activityType === 'submission-analysis');
    const attempt = run.attempts.find(a => a.activityId === activity?.activityId);
    let result = attempt?.session?.originalResult;
    if (result?.artifactId) {
      try {
        result = await api('/' + submission.runId + '/artifacts/' + encodeURIComponent(result.artifactId), signal, null, '/api/v1/runs');
      } catch (error) {
        if (error.status !== 410 && error.status !== 404) throw error;
        result = {summary: 'Das gespeicherte Ergebnisartefakt ist nicht verfügbar. Der Run behält den Nachweis seiner fehlenden Inhalte.', findings: []};
      }
    }
    signal.throwIfAborted();
    if (!container.isConnected) return;
    const [label, hint] = states[execution.state] || ['Unbekannt', 'Der Zustand kann nicht sicher bestimmt werden.'];
    field('state').textContent = label;
    field('state').dataset.state = execution.state;
    field('hint').textContent = hint;
    field('activity-id').textContent = activity?.activityId || 'Noch nicht angelegt';
    field('attempt-id').textContent = attempt?.attemptId || 'Noch nicht angelegt';
    field('session-id').textContent = attempt?.session?.sessionId || 'Noch keine bestätigte Session';
    field('result').textContent = result?.summary || (execution.code
      ? `${failures[execution.code] || 'Die Verarbeitung wurde mit einem Fehler beendet.'} (${execution.code})` : '');
    field('findings').replaceChildren();
    for (const finding of result?.findings || []) {
      const item = document.createElement('li'); item.textContent = finding;
      field('findings').append(item);
    }
    if (['queued', 'running', 'reconciling'].includes(execution.state)) {
      timer = setTimeout(() => refresh().catch(error => {
        if (signal.aborted || !container.isConnected) return;
        field('state').textContent = 'Verbindung unterbrochen';
        field('hint').textContent = error.message + ' Anforderungen aktualisieren, um den Zustand erneut zu lesen.';
        field('result').textContent = '';
        field('findings').replaceChildren();
      }), 1200);
    }
  }
  await refresh();
}

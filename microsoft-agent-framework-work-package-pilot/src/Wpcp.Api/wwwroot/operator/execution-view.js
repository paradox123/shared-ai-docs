import {analysisState, statusLabel} from './analysis-state.js';
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

export function showExecution(container, submission, signal, api, reportError) {
  const field = name => container.querySelector(`[data-execution="${name}"]`);
  let refreshing = false, renderedResult, latest;
  const active = () => !signal.aborted && container.isConnected;

  return async snapshot => {
    if (!active()) return;
    latest = snapshot;
    const execution = snapshot.execution;
    field('state').textContent = statusLabel(snapshot);
    field('state').dataset.state = execution?.state || 'unknown';
    field('state').dataset.stale = String(snapshot.stale);
    field('freshness').textContent = snapshot.stale ? 'Verbindung unterbrochen · Erneuter Versuch läuft.' : '';
    field('hint').textContent = (snapshot.stale ? 'Zuletzt bestätigter Stand: ' : '') + analysisState(execution?.state)[1];
    field('start').hidden = Boolean(execution?.runId || submission.runId);
    field('detail').hidden = !execution?.runId;
    if (snapshot.stale || !execution?.runId || refreshing) return;
    field('run-id').textContent = execution.runId;
    refreshing = true;
    try {
      const run = await api('/' + execution.runId, signal, null, '/api/v1/runs');
      const activity = run.activities.find(a => a.activityType === 'submission-analysis');
      const attempt = run.attempts.findLast(a => a.activityId === activity?.activityId);
      let result = attempt?.session?.originalResult;
      if (result?.artifactId) {
        try {
          result = await api('/' + execution.runId + '/artifacts/' + encodeURIComponent(result.artifactId), signal, null, '/api/v1/runs');
        } catch (error) {
          if (error.status !== 410 && error.status !== 404) throw error;
          result = {summary: 'Das gespeicherte Ergebnisartefakt ist nicht verfügbar. Der Run behält den Nachweis seiner fehlenden Inhalte.', findings: []};
        }
      }
      if (!active() || latest.stale || latest.execution?.state !== execution.state) return;
      field('result-status').textContent = '';
      field('activity-id').textContent = activity?.activityId || 'Noch nicht angelegt';
      field('attempt-id').textContent = attempt?.attemptId || 'Noch nicht angelegt';
      field('session-id').textContent = attempt?.session?.sessionId || 'Noch keine bestätigte Session';
      const signature = JSON.stringify([result, execution.code, execution.state]);
      if (signature === renderedResult) return;
      renderedResult = signature;
      const diagnostic = execution.code
        ? `${failures[execution.code] || 'Gemeldeter Diagnosecode:'} (${execution.code})` : '';
      field('result').textContent = execution.state === 'failed'
        ? diagnostic || 'Die Verarbeitung wurde mit einem Fehler beendet.'
        : result?.summary || diagnostic || 'Noch kein Analyseergebnis gespeichert.';
      field('findings').replaceChildren();
      for (const finding of result?.findings || []) {
        const item = document.createElement('li'); item.textContent = finding;
        field('findings').append(item);
      }
      field('findings').parentElement.hidden = !field('findings').children.length;
    } catch (error) {
      if (!active()) return;
      if (error.status === 401 || error.status === 403) { reportError(error); return; }
      field('result-status').textContent = 'Ergebnis derzeit nicht lesbar · Ein vorhandener Inhalt zeigt den zuletzt geladenen Stand. Erneuter Versuch läuft.';
    } finally { refreshing = false; }
  };
}

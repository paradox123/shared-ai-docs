export const states = {
  admitted: ['Aufgenommen', 'Der Auftrag ist aufgenommen. Die Analyse wurde noch nicht gestartet.'],
  queued: ['Wartend', 'Der Auftrag ist dauerhaft vorgemerkt und wartet auf einen Worker.'],
  running: ['Läuft', 'Der Worker verarbeitet die Anforderungen.'],
  reconciling: ['Ergebnisabgleich', 'Der Ausgang ist noch unbestätigt. Der Worker fragt dieselbe Operation erneut ab und übernimmt ihr gespeichertes Ergebnis.'],
  completed: ['Analyse abgeschlossen', 'Die Anforderungsanalyse ist abgeschlossen.'],
  failed: ['Fehlgeschlagen', 'Der erste Schritt konnte nicht erfolgreich abgeschlossen werden.'],
};

export const analysisState = state => (Object.hasOwn(states, state) ? states[state] : null) || ['Unbekannt', 'Der Zustand kann nicht sicher bestimmt werden.'];

export function statusLabel(snapshot) {
  return analysisState(snapshot.execution?.state)[0] + (snapshot.stale && snapshot.execution ? ' · zuletzt bestätigt' : '');
}

// One confirmed snapshot feeds both the list row and the selected run header.
export async function watchAnalysis(submission, signal, api, update, reportError) {
  let execution, timer;
  signal.addEventListener('abort', () => clearTimeout(timer), {once: true});
  async function refresh() {
    try {
      try { execution = await api('/' + submission.submissionId + '/execution', AbortSignal.any([signal, AbortSignal.timeout(5000)])); }
      catch (error) {
        if (error.status !== 409 || error.payload?.code !== 'submission-not-started') throw error;
        execution = {submissionId: submission.submissionId, runId: null, state: 'admitted'};
      }
      signal.throwIfAborted();
      update({execution, stale: false});
    } catch (error) {
      if (signal.aborted) return;
      if (error.status === 401 || error.status === 403) { reportError(error); return; }
      update({execution, stale: true});
    } finally {
      if (!signal.aborted) timer = setTimeout(refresh, 1200);
    }
  }
  await refresh();
}

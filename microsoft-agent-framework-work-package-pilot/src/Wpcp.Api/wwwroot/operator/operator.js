import {showExecution} from './execution-view.js';
const $ = id => document.getElementById(id);
const errors = {
  'invalid-github-issue-url': 'Bitte eine GitHub-Issue-URL im Format https://github.com/owner/repository/issues/123 eingeben.',
  'repository-not-configured': 'Dieses Repository ist auf dem Server noch nicht eingerichtet.',
  'provider-authentication-required': 'Der GitHub-Zugang fehlt oder ist abgelaufen. Bitte erneut verbinden.',
  'repository-contribution-required': 'Zum Aufnehmen brauchst du Schreibzugriff auf dieses Repository.',
  'repository-access-denied': 'Deine GitHub-Identität hat keinen Lesezugriff auf dieses Repository.',
  'human-identity-required': 'Bitte den GitHub-Zugang einer menschlichen Identität verwenden.',
  'repository-identity-mismatch': 'Die Repository-ID stimmt nicht mit der gespeicherten Zuordnung überein.',
  'repository-provider-unavailable': 'GitHub konnte deine Repository-Rechte nicht bestätigen. Bitte erneut versuchen.',
  'github-source-unavailable': 'GitHub konnte das Issue nicht zuverlässig liefern. Bitte erneut versuchen.',
  'github-issue-not-found': 'Das GitHub-Issue wurde nicht gefunden oder dein Zugang darf es nicht lesen.',
  'github-source-is-pull-request': 'Diese Quelle ist ein Pull Request. Bitte Anforderungen aus einem Issue aufnehmen.',
  'github-source-identity-mismatch': 'Die GitHub-Antwort gehört nicht zum angefragten Issue.',
  'github-issue-closed': 'Das Issue ist geschlossen. Nur offene Issues können aufgenommen werden.',
  'implementation-authorization-required': 'Dem Issue fehlt die Implementierungsfreigabe „ready-for-agent“.',
  'submission-correlation-rejected': 'Die Herkunft enthält einen durch die Redaktionsregel gesperrten Wert.',
  'submission-not-found': 'Diese Anforderungen wurden nicht gefunden.',
  'run-store-unavailable': 'Der Server kann die Anforderungen gerade nicht speichern oder lesen. Bitte erneut versuchen.',
  'background-execution-not-configured': 'Der Server ist noch nicht für Hintergrundanalysen eingerichtet. Die gespeicherten Anforderungen bleiben erhalten.',
  'agent-credentials-unavailable': 'Dem Server fehlt der Zugang zum Agentendienst. Die Analyse wurde nicht gestartet.',
  'artifact-storage-unavailable': 'Der gemeinsame Ergebnisspeicher ist nicht verfügbar. Bitte die Serverkonfiguration prüfen lassen; es wurde kein Run gestartet.',
  'agent-readiness-unavailable': 'Der Agentendienst ist nicht ausführungsbereit. Bitte dessen Runtime und Zugang prüfen lassen; es wurde kein Run gestartet.',
  'issue-already-has-run': 'Für dieses Issue existiert bereits ein Run aus einem anderen Startweg. Er wird nicht durch einen neuen Auftrag ersetzt.',
};
let credential = '';
let operation;
const date = value => new Date(value).toLocaleString('de-DE', {dateStyle: 'medium', timeStyle: 'short'});

function clearRecords() {
  $('submission-list').replaceChildren();
  $('detail').replaceChildren();
  $('count').textContent = '0';
}

function disconnect() {
  operation?.abort();
  credential = '';
  $('github-token').value = '';
  clearRecords();
  $('workspace').hidden = true;
  $('sign-in').hidden = false;
  $('disconnect').hidden = true;
  $('connection-label').textContent = 'Nicht verbunden';
  $('notice').textContent = '';
  $('error').hidden = true;
}

async function api(path, signal, body, resource = '/api/v1/submissions') {
  const response = await fetch(resource + path, {
    method: body ? 'POST' : 'GET', signal, cache: 'no-store',
    headers: {Authorization: `Bearer ${credential}`, ...(body ? {'Content-Type': 'application/json'} : {})},
    ...(body ? {body: JSON.stringify(body)} : {}),
  });
  const payload = await response.json();
  if (!response.ok) {
    const error = new Error(errors[payload.code] || 'Die Anfrage konnte nicht verarbeitet werden. Bitte erneut versuchen.');
    error.status = response.status;
    throw error;
  }
  return payload;
}

async function perform(work) {
  operation?.abort();
  const current = operation = new AbortController();
  $('error').hidden = true;
  $('notice').textContent = '';
  for (const button of document.querySelectorAll('button[type="submit"], [data-execution="start"], #refresh')) button.disabled = true;
  try { await work(current.signal); }
  catch (error) {
    if (current.signal.aborted) return;
    if (error.status === 401) disconnect();
    $('error').textContent = error.message === 'Failed to fetch'
      ? 'Der Server ist nicht erreichbar. Bitte Verbindung prüfen und erneut versuchen.' : error.message;
    $('error').hidden = false;
  } finally {
    if (operation === current) for (const button of document.querySelectorAll('button[type="submit"], [data-execution="start"], #refresh')) button.disabled = false;
  }
}

async function showDetail(id, signal, focus = false) {
  $('detail').replaceChildren();
  const record = await api('/' + encodeURIComponent(id), signal);
  signal.throwIfAborted();
  const content = $('detail-template').content.cloneNode(true);
  const fields = {
    title: record.title, repository: record.repository.fullName,
    admitted: date(record.admittedAt), revision: date(record.source.updatedAt),
    id: record.submissionId, body: record.body || 'Das Issue enthält keinen Beschreibungstext.',
    redaction: record.redaction.occurred ? 'Inhalt redigiert' : '',
    'issue-id': String(record.source.providerIssueId), actor: `${record.submittedBy.provider}:${record.submittedBy.subjectId}`,
    sha: record.contentSha256, policy: record.redaction.policyVersion,
  };
  for (const [field, value] of Object.entries(fields)) content.querySelector(`[data-field="${field}"]`).textContent = value;
  const source = content.querySelector('[data-field="source"]');
  source.textContent = record.source.url;
  source.href = record.source.url;
  $('detail').append(content);
  history.replaceState(null, '', '#' + record.submissionId);
  for (const row of $('submission-list').children) row.setAttribute('aria-current', String(row.dataset.id === id));
  if (focus) $('detail').querySelector('h2').focus();
  const start = $('detail').querySelector('[data-execution="start"]');
  start.addEventListener('click', () => perform(async next => {
    await api('/' + record.submissionId + '/start', next, {});
    await overview(next, record.submissionId);
    $('notice').textContent = 'Gestartet · Der Server übernimmt die Analyse. Du kannst dieses Fenster schließen.';
  }));
  if (record.runId) {
    $('detail').querySelector('.execution-note').textContent = 'Der Server bearbeitet die Analyse unabhängig von diesem Fenster. Implementierung und Review folgen in späteren Schritten.';
    $('detail').querySelector('.detail-kicker .badge').textContent = '● Gestartet';
    await showExecution($('detail').querySelector('.execution'), record, signal, api);
  }
}

async function overview(signal, selected = location.hash.slice(1)) {
  clearRecords();
  const result = await api('', signal);
  signal.throwIfAborted();
  $('count').textContent = String(result.submissions.length);
  for (const record of result.submissions) {
    const row = document.createElement('button');
    row.className = 'submission-row';
    row.dataset.id = record.submissionId;
    const source = document.createElement('span'); source.className = 'row-source';
    source.textContent = `${record.repository.fullName} / #${record.source.issueNumber}`;
    const title = document.createElement('strong'); title.textContent = record.title;
    const bottom = document.createElement('span'); bottom.className = 'row-bottom';
    const status = document.createElement('span'); status.className = 'badge'; status.textContent = record.runId ? '● Gestartet' : '● Aufgenommen';
    const time = document.createElement('span'); time.textContent = date(record.admittedAt);
    bottom.append(status, time); row.append(source, title, bottom);
    row.addEventListener('click', () => perform(signal => showDetail(record.submissionId, signal, true)));
    $('submission-list').append(row);
  }
  if (result.submissions.length) {
    const id = result.submissions.some(s => s.submissionId === selected) ? selected : result.submissions[0].submissionId;
    await showDetail(id, signal);
  } else {
    const empty = document.createElement('div'); empty.className = 'empty';
    empty.textContent = 'Noch keine sichtbaren Anforderungen. Nimm oben dein erstes freigegebenes GitHub-Issue auf.';
    $('submission-list').append(empty);
    $('detail').textContent = 'Die gespeicherte Fassung erscheint hier nach der Aufnahme.';
  }
}

$('connect-form').addEventListener('submit', event => {
  event.preventDefault();
  credential = $('github-token').value.trim();
  $('github-token').value = '';
  clearRecords();
  perform(async signal => {
    await overview(signal);
    $('sign-in').hidden = true; $('workspace').hidden = false; $('disconnect').hidden = false;
    $('connection-label').textContent = 'Mit GitHub verbunden';
  });
});
$('submission-form').addEventListener('submit', event => {
  event.preventDefault();
  const sourceUrl = $('source-url').value.trim();
  const start = event.submitter?.value === 'start';
  perform(async signal => {
    const record = await api('', signal, {sourceUrl, start});
    await overview(signal, record.submissionId);
    $('source-url').value = '';
    $('notice').textContent = start
      ? 'Gestartet · Der Server übernimmt die Analyse. Du kannst dieses Fenster schließen.'
      : 'Aufgenommen · Die gespeicherte Fassung ist in deiner Übersicht verfügbar.';
  });
});
$('refresh').addEventListener('click', () => perform(signal => overview(signal)));
$('disconnect').addEventListener('click', disconnect);

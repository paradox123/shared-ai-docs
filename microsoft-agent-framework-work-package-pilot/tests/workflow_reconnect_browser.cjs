// Two isolated browser sessions, controlled only through stdin for process faults.
const assert = require('node:assert/strict');
const readline = require('node:readline');
const {chromium} = require(process.env.WPCP_TEST_PLAYWRIGHT ||
  `${process.env.HOME}/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright-core`);
const inputLines = readline.createInterface({input: process.stdin});
const lines = inputLines[Symbol.asyncIterator]();
const receive = async () => JSON.parse((await lines.next()).value);
const send = data => process.stdout.write(JSON.stringify(data) + '\n');
(async () => {
  const input = await receive();
  const browser = await chromium.launch({headless: true, channel: 'chrome'});
  try {
    const page = await browser.newPage(); page.setDefaultTimeout(20000);
    await page.goto(input.baseUrl + '/operator/');
    await page.getByLabel('GitHub-Zugangstoken').fill(input.credential);
    await page.getByRole('button', {name: 'Verbinden', exact: true}).click();
    await page.getByText('Mit GitHub verbunden', {exact: true}).waitFor();
    let reads = 0, refreshFailed = false;
    if (input.catchup) await page.route('**/api/v1/runs/*', async route => {
      const response = await route.fetch();
      const body = await response.json();
      reads++;
      if (reads === 2) {
        send({stage: 'projection-held', runId: body.runId,
          submissionId: await page.locator('[data-field="id"]').textContent()});
        await receive(); // Let the worker commit its final events before releasing the old projection.
        await route.fulfill({response});
      } else if (reads > 2 && !refreshFailed && body.state === 'analysis-completed') {
        refreshFailed = true;
        await route.fulfill({status: 503, contentType: 'application/json', body: JSON.stringify({code: 'run-store-unavailable'})});
      } else await route.fulfill({response});
    });
    await page.getByLabel('GitHub-Issue-URL').fill(input.sourceUrl);
    await page.getByRole('button', {name: 'Starten', exact: true}).click();
      await page.locator('[data-field="source"]').filter({hasText: input.sourceUrl}).waitFor();
    await page.locator('#history-status').filter({hasText: 'Live verbunden'}).waitFor();
    const runId = await page.locator('[data-execution="run-id"]').textContent();
    if (!input.catchup) {
      send({stage: 'watching', runId, submissionId: await page.locator('[data-field="id"]').textContent()});
      await receive();
    }
    await page.locator('#history-list').filter({hasText: 'Requirements analysis complete.'}).waitFor();
    await page.locator('#workflow-state').filter({hasText: 'Analyse abgeschlossen'}).waitFor();
    if (input.catchup) assert.ok(refreshFailed, 'The completed projection refresh was not faulted');
    const headers = {Authorization: 'Bearer ' + input.credential};
    const expected = await (await page.request.get(input.baseUrl + '/api/v1/runs/' + runId + '/events?limit=1000', {headers})).json();
    const ids = await page.locator('#history-list [data-event-id]').evaluateAll(nodes => nodes.map(n => n.dataset.eventId));
    assert.deepEqual(ids, expected.events.map(e => e.eventId));
    // Filter round-trip must preserve canonical order and identity.
    await page.getByLabel('Inhalte', {exact: true}).selectOption('tool');
    await page.getByLabel('Inhalte', {exact: true}).selectOption('all');
    assert.deepEqual(await page.locator('#history-list [data-event-id]').evaluateAll(nodes => nodes.map(n => n.dataset.eventId)), ids);
    send({stage: 'reconnected', events: ids.length, ids});
    await receive();
    await page.getByRole('alert').filter({hasText: 'Zugriff'}).waitFor();
    assert.equal(await page.locator('#workflow').isVisible(), false);
    await page.locator('#history-filter').evaluate(node => { node.value = 'all'; node.dispatchEvent(new Event('change')); });
    assert.equal(await page.locator('#history-list').textContent(), '');
    assert.equal(await page.locator('#artifact-content').textContent(), '');
    assert.equal(await page.locator('#detail').textContent(), '');
    assert.equal(await page.locator('#run-list').textContent(), '');
    send({stage: 'revoked', cleared: true});
  } finally { await browser.close(); inputLines.close(); }
})().catch(error => { console.error(error.stack); process.exitCode = 1; });

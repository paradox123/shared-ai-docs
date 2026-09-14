const fs = require('node:fs');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.WPCP_TEST_PLAYWRIGHT ||
  `${process.env.HOME}/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright-core`);
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
(async () => {
  const browser = await chromium.launch({headless: true, channel: 'chrome'});
  try {
    const failures = [];
    async function connect(token, hash = '') {
      const context = await browser.newContext({viewport: {width: 1500, height: 1100}});
      const page = await context.newPage();
      page.on('pageerror', error => failures.push(error.message));
      page.setDefaultTimeout(20000);
      await page.goto(input.baseUrl + '/operator/' + hash);
      await page.getByLabel('GitHub-Zugangstoken').fill(token);
      await page.getByRole('button', {name: 'Verbinden', exact: true}).click();
      await page.getByText('Mit GitHub verbunden', {exact: true}).waitFor().catch(async error => {
        throw new Error(error.message + ' UI: ' + await page.locator('#error').textContent());
      });
      return page;
    }
    let first = await connect(input.credential, input.submissionId ? '#' + input.submissionId : '');
    if (!input.submissionId) {
      await first.getByLabel('GitHub-Issue-URL').fill(input.sourceUrl);
      await first.getByRole('button', {name: 'Starten', exact: true}).click();
      await first.locator('[data-field="source"]').filter({hasText: input.sourceUrl}).waitFor();
    }
    await first.locator('[data-execution="state"]').filter({hasText: 'Abgeschlossen'}).waitFor({timeout: input.live ? 180000 : 20000});
    await first.getByRole('heading', {name: 'Workflow und Sessionverlauf', exact: true}).waitFor();
    if (input.live) console.error('Real analysis completed; inspecting workflow.');
    const runId = await first.locator('[data-execution="run-id"]').textContent();
    const submissionId = await first.locator('[data-field="id"]').textContent();
    if (input.artifacts) { await first.context().close(); first = await connect(input.credential, '#' + submissionId); }
    const second = await connect(input.observer, '#' + submissionId);
    async function inspect(page, token) {
      const headers = {Authorization: 'Bearer ' + token};
      const run = await (await page.request.get(input.baseUrl + '/api/v1/runs/' + runId, {headers})).json();
      const attempt = run.attempts.find(a => a.session);
      await page.locator('[data-attempt-id="' + attempt.attemptId + '"]').click();
      await page.locator('#session-detail').filter({hasText: attempt.session.sessionId}).waitFor();
      if (input.paged) {
        await page.locator('#history-status').filter({hasText: 'History teilweise geladen'}).waitFor();
        assert.equal(await page.locator('#history-list [data-event-id]').count() < 100, true);
        while (await page.locator('#history-more').isVisible()) {
          await page.locator('#history-more').click();
          await page.waitForFunction(() => document.getElementById('history-more').disabled === false);
        }
      }
      await page.locator('#history-status').filter({hasText: 'Live verbunden'}).waitFor();
      await page.locator('#session-detail > details > summary').click();
      await page.waitForTimeout(1400); // Existing selection must survive idle live heartbeats.
      assert.equal(await page.locator('#session-detail > details').getAttribute('open'), '', 'Live refresh closed the selected session detail');
      if (input.live) console.error('Session selected and live connected.');
      const events = await (await page.request.get(input.baseUrl + '/api/v1/runs/' + runId + '/events?limit=1000', {headers})).json();
      const expected = events.events.filter(e => e.payload.attemptId === attempt.attemptId);
      const actual = await page.locator('#history-list [data-event-id]').evaluateAll(nodes => nodes.map(n => n.dataset.eventId));
      assert.deepEqual(actual, expected.map(e => e.eventId));
      const text = await page.locator('#history-list').textContent();
      assert.match(text, /read-admitted-issue/);
      if (!input.live) {
        assert.match(text, /Preserve the approved requirements/);
        assert.match(text, /REDACTED/);
      }
      for (const event of expected) {
        const payload = await page.locator('[data-event-id="' + event.eventId + '"] > pre').textContent();
        assert.deepEqual(JSON.parse(payload), event.payload.data ?? event.payload);
      }
      assert.ok(!text.includes('wpcp-controlled-secret-canary-v1'));
      if (input.artifacts) {
        const manifest = await (await page.request.get(input.baseUrl + '/api/v1/runs/' + runId + '/artifacts', {headers})).json();
        assert.ok(manifest.artifacts.length > 0);
        for (const artifact of manifest.artifacts) {
          await page.locator('[data-artifact-id="' + artifact.artifactId + '"] button').click();
          if (artifact.availability !== 'available') {
            await page.locator('#artifact-content').filter({hasText: 'Inhalt nicht verfügbar'}).waitFor();
            const response = await page.request.get(input.baseUrl + '/api/v1/runs/' + runId + '/artifacts/' + artifact.artifactId, {headers});
            assert.equal(response.status(), 410);
            continue;
          }
          await page.waitForFunction(() => { const text = document.getElementById('artifact-content').textContent; try { return !!JSON.parse(text); } catch { return false; } });
          const bytes = await (await page.request.get(input.baseUrl + '/api/v1/runs/' + runId + '/artifacts/' + artifact.artifactId, {headers})).text();
          assert.deepEqual(JSON.parse(await page.locator('#artifact-content').textContent()), JSON.parse(bytes));
        }
      }
      return {runId, attemptId: attempt.attemptId, sessionId: attempt.session.sessionId, events: actual.length};
    }
    const a = await inspect(first, input.credential);
    const b = await inspect(second, input.observer);
    await second.locator('#workflow').evaluate(node => node.scrollIntoView({block: 'start'}));
    if (input.screenshot) await second.screenshot({path: input.screenshot, fullPage: false});
    await second.setViewportSize({width: 390, height: 844});
    assert.ok(await second.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Mobile overflow');
    await second.locator('#workflow').evaluate(node => node.scrollIntoView({block: 'start'}));
    if (input.mobileScreenshot) await second.screenshot({path: input.mobileScreenshot, fullPage: false});
    assert.deepEqual(await second.evaluate(() => ({local: Object.keys(localStorage), session: Object.keys(sessionStorage)})), {local: [], session: []});
    assert.deepEqual(failures, []);
    process.stdout.write(JSON.stringify({first: a, second: b}));
  } finally { await browser.close(); }
})().catch(error => { console.error(error.stack); process.exitCode = 1; });

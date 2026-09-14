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
      if (!await first.locator('.intake-disclosure').evaluate(node => node.open)) await first.locator('.intake-disclosure > summary').click();
      await first.getByLabel('GitHub-Issue-URL').fill(input.sourceUrl);
      await first.getByRole('button', {name: 'Starten', exact: true}).click();
      await first.locator('[data-field="source"]').filter({hasText: input.sourceUrl}).waitFor();
    }
    await first.locator('[data-execution="state"]').filter({hasText: 'Analyse abgeschlossen'}).waitFor({timeout: input.live ? 180000 : 20000});
    await first.getByRole('tab', {name: 'Verlauf', exact: true}).click();
    await first.getByRole('heading', {name: 'Workflow und Sessionverlauf', exact: true}).waitFor();
    if (input.live) console.error('Real analysis completed; inspecting workflow.');
    const runId = await first.locator('[data-execution="run-id"]').textContent();
    const submissionId = await first.locator('[data-field="id"]').textContent();
    if (input.artifacts) { await first.context().close(); first = await connect(input.credential, '#' + submissionId); }
    const second = await connect(input.observer, '#' + submissionId);
    async function inspect(page, token) {
      await page.getByRole('tab', {name: 'Verlauf', exact: true}).click();
      const headers = {Authorization: 'Bearer ' + token};
      const run = await (await page.request.get(input.baseUrl + '/api/v1/runs/' + runId, {headers})).json();
      const attempt = run.attempts.find(a => a.session);
      if (input.nativeTools) await page.locator('#session-detail').getByRole('heading', {name: 'Anforderungen analysieren', exact: true}).waitFor();
      await page.locator('[data-attempt-id="' + attempt.attemptId + '"]').click();
      if (input.unknownShapes) await page.locator('#history-list').getByText('Der Verlauf bleibt lesbar.', {exact: true}).waitFor();
      if (input.runtimeFailure) {
        const list = page.locator('#history-list');
        await list.getByText('Upstream model quota exhausted', {exact: true}).waitFor();
        const failure = list.locator('article').filter({has: page.getByRole('heading', {name: 'git status --short', exact: true})});
        await failure.getByText('Fehler · 42 ms', {exact: true}).waitFor();
        await failure.getByText('Ergebnis und Fehler ansehen', {exact: true}).click();
        await failure.getByText('fatal: cannot open repository', {exact: true}).waitFor();
        await page.locator('#session-detail .outcome-summary').getByText('Requirements analysis complete.', {exact: true}).waitFor();
      }
      if (input.nativeTools) {
        const list = page.locator('#history-list');
        assert.equal(await list.getByText('Prüfe den Arbeitsstand.', {exact: true}).count(), 1, 'Protocol duplicate appears as a second authored message');
        await page.getByLabel('Inhalte', {exact: true}).selectOption('tool');
        const failure = list.locator('article').filter({has: page.getByRole('heading', {name: 'git status --short', exact: true})});
        await failure.getByText('Fehler · 42 ms', {exact: true}).waitFor();
        await failure.getByText('Ergebnis und Fehler ansehen', {exact: true}).click();
        await failure.getByText('Berechtigung fehlt', {exact: true}).waitFor();
        await failure.getByText('<img src=x onerror="window.untrustedRan=true">', {exact: true}).waitFor();
        assert.equal(await failure.locator('img').count(), 0);
        assert.equal(await page.evaluate(() => Boolean(window.untrustedRan)), false);
      }
      if (input.readable) {
        await page.locator('#session-detail').getByRole('heading', {name: 'Anforderungen analysieren', exact: true}).waitFor();
        await page.locator('#history-list').getByText('Ich prüfe die freigegebenen Anforderungen.', {exact: true}).waitFor();
        assert.equal(await page.locator('#workflow pre:visible').count(), 0, 'The default view requires decoding JSON');
        assert.ok(!(await page.locator('#workflow').innerText()).includes(attempt.attemptId), 'Raw identities dominate the default view');
        await page.locator('#history-list').getByText('Requirements analysis complete.', {exact: true}).waitFor();
      }
      await page.locator('#session-detail').filter({hasText: attempt.session.sessionId}).waitFor();
      await page.getByLabel('Inhalte', {exact: true}).selectOption('all');
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
        const card = page.locator('[data-event-id="' + event.eventId + '"]');
        if (event.payload.type === 'result' && typeof event.payload.data?.summary === 'string') {
          assert.equal(await card.locator(':scope > .structured-content > .readable-text').innerText(), event.payload.data.summary);
          if (event.payload.data.findings.length) {
            await card.locator('.findings-details > summary').click();
            assert.deepEqual(await card.locator('.findings-details li').allInnerTexts(), event.payload.data.findings);
            await card.locator('.findings-details > summary').click();
          }
        }
        await card.locator('.event-raw > summary').click();
        const payload = await card.locator('.event-raw > pre').textContent();
        assert.deepEqual(JSON.parse(payload), event);
        await card.locator('.event-raw > summary').click();
      }
      assert.ok(!text.includes('wpcp-controlled-secret-canary-v1'));
      if (input.artifacts) {
        const manifest = await (await page.request.get(input.baseUrl + '/api/v1/runs/' + runId + '/artifacts', {headers})).json();
        assert.ok(manifest.artifacts.length > 0);
        await page.getByRole('tab', {name: 'Dateien', exact: true}).click();
        for (const artifact of manifest.artifacts) {
          await page.locator('[data-artifact-id="' + artifact.artifactId + '"] button').click();
          if (artifact.availability !== 'available') {
            await page.locator('#artifact-content').filter({hasText: 'Inhalt nicht verfügbar'}).waitFor();
            const response = await page.request.get(input.baseUrl + '/api/v1/runs/' + runId + '/artifacts/' + artifact.artifactId, {headers});
            assert.equal(response.status(), 410);
            continue;
          }
          await page.locator('#artifact-content .artifact-raw > summary').waitFor();
          if (input.artifacts) {
            assert.equal(await page.locator('#artifact-content pre:visible').count(), 0, 'Artifact opens as a JSON dump');
            const original = JSON.parse(await page.locator('#artifact-content .artifact-raw > pre').textContent());
            if (Array.isArray(original.events)) await page.locator('#artifact-content').getByText('Sessionereignisse · ' + original.events.length, {exact: true}).waitFor();
          }
          await page.locator('#artifact-content .artifact-raw > summary').click();
          const bytes = await (await page.request.get(input.baseUrl + '/api/v1/runs/' + runId + '/artifacts/' + artifact.artifactId, {headers})).text();
          assert.deepEqual(JSON.parse(await page.locator('#artifact-content .artifact-raw > pre').textContent()), JSON.parse(bytes));
          await page.locator('#artifact-content .artifact-raw > summary').click();
        }
      }
      await page.getByRole('tab', {name: 'Verlauf', exact: true}).click();
      await page.locator('#session-detail > details > summary').click();
      await page.getByLabel('Inhalte', {exact: true}).selectOption('conversation');
      assert.equal(await page.locator('#history-list .event-raw[open], #session-detail details[open]').count(), 0);
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

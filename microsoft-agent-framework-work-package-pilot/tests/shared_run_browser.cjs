const fs = require('node:fs');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.WPCP_TEST_PLAYWRIGHT ||
  `${process.env.HOME}/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright-core`);
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
(async () => {
  const browser = await chromium.launch({headless: true, channel: 'chrome'});
  try {
    const page = await browser.newPage({viewport: {width: 1024, height: 1000}});
    page.setDefaultTimeout(7000);
    if (input.blockedOther) await page.route('**/api/v1/submissions/' + input.blockedOther + '/execution', () => {});
    if (input.revokedDuringOpen) {
      let reading;
      const hydration = new Promise(resolve => {reading = resolve;});
      await page.route('**/api/v1/submissions/' + input.submissionId, async route => {
        const response = await route.fetch();
        await new Promise(resolve => setTimeout(resolve, 150));
        await route.fulfill({response});
      });
      await page.route('**/api/v1/runs/' + input.runId, async route => {
        reading();
        await new Promise(resolve => setTimeout(resolve, 500));
        await route.abort().catch(() => {});
      });
      await page.route('**/api/v1/submissions/' + input.revokedDuringOpen + '/execution', async route => {
        await hydration;
        await route.fulfill({status: 403, json: {code: 'repository-access-denied'}});
      });
    }
    await page.goto(input.baseUrl + '/operator/#' + (input.previousSubmissionId || input.submissionId));
    await page.getByLabel('GitHub-Zugangstoken').fill(input.credential);
    await page.getByRole('button', {name: 'Verbinden', exact: true}).click();
    if (input.revokedDuringOpen) {
      await page.locator('#error').filter({hasText: 'keinen Lesezugriff'}).waitFor();
      await page.waitForTimeout(800); // Allow the aborted hydration's continuation to run.
      assert.equal(await page.locator('#sign-in').isVisible(), true, 'Aborted hydration published a connected workspace');
      assert.equal(await page.locator('#workspace').isVisible(), false);
      assert.equal(await page.locator('#connection-label').textContent(), 'Nicht verbunden');
      process.stdout.write(JSON.stringify({revoked: true, cleared: true}));
      return;
    }
    await page.getByText('Mit GitHub verbunden', {exact: true}).waitFor();
    if (input.admitted) {
      if (input.previousSubmissionId) {
        await page.locator(`.submission-row[data-id="${input.submissionId}"]`).click();
        await page.locator('[data-execution="state"]').filter({hasText: /^Aufgenommen$/}).waitFor();
      }
      assert.equal(await page.locator('[data-execution="state"]').textContent(), 'Aufgenommen');
      assert.equal(await page.locator(`.submission-row[data-id="${input.submissionId}"] .badge`).textContent(), 'Aufgenommen');
      await page.getByRole('button', {name: 'Analyse starten', exact: true}).waitFor();
      const tab = page.getByRole('tab', {name: 'Verlauf', exact: true});
      await tab.click();
      await page.locator('#history-status').filter({hasText: 'Noch kein Run gestartet.'}).waitFor();
      assert.equal(await page.locator('#workflow-state').textContent(), '', 'Previous run state leaked into admitted requirements');
      const started = await page.request.post(input.baseUrl + '/api/v1/submissions/' + input.submissionId + '/start',
        {headers: {Authorization: 'Bearer ' + input.credential}, data: {}});
      assert.equal(started.status(), 202);
      await page.locator('[data-execution="state"]').filter({hasText: /^Wartend$/}).waitFor();
      await page.locator('#history-status').filter({hasText: 'Live verbunden'}).waitFor();
      assert.equal(await tab.getAttribute('aria-selected'), 'true');
      assert.equal(await tab.evaluate(node => node === document.activeElement), true);
      process.stdout.write(JSON.stringify({submissionId: input.submissionId, state: 'queued'}));
      return;
    }
    const response = await page.request.get(input.baseUrl + '/api/v1/submissions/' + input.submissionId + '/execution',
      {headers: {Authorization: 'Bearer ' + input.credential}});
    assert.equal((await response.json()).state, 'completed');
    await page.locator('[data-execution="state"]').filter({hasText: /^Analyse abgeschlossen$/}).waitFor();
    assert.equal(await page.locator(`.submission-row[data-id="${input.submissionId}"] .badge`).textContent(),
      'Analyse abgeschlossen', 'List contradicts the confirmed completed analysis');
    await page.locator('[data-execution="state"]').filter({hasText: /^Analyse abgeschlossen$/}).waitFor();
    if (input.otherSubmissionId) {
      const headers = {Authorization: 'Bearer ' + input.credential};
      const read = async suffix => (await page.request.get(input.baseUrl + '/api/v1/' + suffix, {headers})).json();
      const first = await read('submissions/' + input.submissionId);
      const second = await read('submissions/' + input.otherSubmissionId);
      const oldRun = await read('runs/' + first.runId);
      await page.locator(`.submission-row[data-id="${second.submissionId}"]`).click();
      await page.locator('[data-field="title"]').filter({hasText: second.title}).waitFor();
      let release, requested;
      const held = new Promise(resolve => { release = resolve; });
      const started = new Promise(resolve => { requested = resolve; });
      await page.route('**/api/v1/runs/' + first.runId, async route => {
        requested(); await held;
        await route.fulfill({json: oldRun}).catch(() => {});
      });
      await page.locator(`.submission-row[data-id="${first.submissionId}"]`).click();
      await started;
      await page.locator(`.submission-row[data-id="${second.submissionId}"]`).click();
      await page.locator('[data-field="title"]').filter({hasText: second.title}).waitFor();
      release();
      await page.getByRole('tab', {name: 'Verlauf', exact: true}).click();
      await page.locator('#history-status').filter({hasText: 'Live verbunden'}).waitFor();
      assert.equal(await page.locator('[data-execution="run-id"]').textContent(), second.runId);
      assert.equal(await page.locator('[data-field="source"]').getAttribute('href'), second.source.url);
      const currentRun = await read('runs/' + second.runId);
      assert.deepEqual(await page.locator('#workflow-graph [data-attempt-id]').evaluateAll(nodes => nodes.map(n => n.dataset.attemptId)),
        currentRun.activities.flatMap(activity => currentRun.attempts.filter(a => a.activityId === activity.activityId).map(a => a.attemptId)));
    }
    if (input.states) {
      let state = 'queued', offline = false;
      await page.route('**/api/v1/submissions/*/execution', async route => {
        if (offline) return route.abort('connectionfailed');
        const response = await route.fetch();
        await route.fulfill({response, json: {...await response.json(), state,
          code: state === 'failed' ? 'transport-failure' : null}});
      });
      const tab = page.getByRole('tab', {name: 'Verlauf', exact: true});
      await tab.click();
      for (const [value, label] of [['queued', 'Wartend'], ['running', 'Läuft'],
        ['reconciling', 'Ergebnisabgleich'], ['failed', 'Fehlgeschlagen'],
        ['completed', 'Analyse abgeschlossen'], ['future-state', 'Unbekannt']]) {
        state = value;
        await page.locator('[data-execution="state"]').filter({hasText: label}).waitFor();
        assert.equal(await page.locator(`.submission-row[data-id="${input.submissionId}"] .badge`).textContent(), label);
        assert.equal(await tab.getAttribute('aria-selected'), 'true');
        assert.equal(await tab.evaluate(node => node === document.activeElement), true);
      }
      state = 'running';
      await page.locator('[data-execution="state"]').filter({hasText: 'Läuft'}).waitFor();
      offline = true;
      await page.locator('[data-execution="freshness"]').filter({hasText: 'Verbindung unterbrochen'}).waitFor();
      assert.match(await page.locator('[data-execution="state"]').textContent(), /zuletzt bestätigt/);
      offline = false; state = 'completed';
      await page.locator('[data-execution="state"]').filter({hasText: /^Analyse abgeschlossen$/}).waitFor();
      assert.equal(await page.locator('[data-execution="freshness"]').textContent(), '');
      assert.equal(await tab.evaluate(node => node === document.activeElement), true);
    }
    if (input.navigation) {
      const read = async suffix => (await page.request.get(input.baseUrl + '/api/v1/' + suffix,
        {headers: {Authorization: 'Bearer ' + input.credential}})).json();
      const record = await read('submissions/' + input.submissionId);
      for (const width of [1024, 390]) {
        await page.setViewportSize({width, height: 1000});
        const resultTab = page.getByRole('tab', {name: 'Ergebnis', exact: true});
        await resultTab.waitFor();
        assert.equal(await resultTab.getAttribute('aria-selected'), 'true');
        assert.equal(await page.locator('[data-field="body"]').isVisible(), false);
        const title = await page.locator('[data-field="title"]').boundingBox();
        const navigation = await resultTab.boundingBox();
        assert.ok(navigation.y - title.y < 220, 'Long content precedes run navigation');
        await resultTab.focus();
        await page.keyboard.press('ArrowRight');
        assert.equal(await page.getByRole('tab', {name: 'Verlauf', exact: true}).getAttribute('aria-selected'), 'true');
        await page.locator('#history-status').filter({hasText: 'Live verbunden'}).waitFor();
        await page.keyboard.press('ArrowRight');
        assert.equal(await page.getByRole('tab', {name: 'Dateien', exact: true}).getAttribute('aria-selected'), 'true');
        await page.keyboard.press('ArrowRight');
        assert.equal(await page.locator('[data-field="body"]').innerText(), record.body);
        assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Horizontal page overflow');
        await page.keyboard.press('Home');
        assert.equal(await resultTab.getAttribute('aria-selected'), 'true');
      }
    }
    process.stdout.write(JSON.stringify({submissionId: input.submissionId, state: 'completed'}));
  } finally { await browser.close(); }
})().catch(error => {console.error(error.stack); process.exitCode = 1;});

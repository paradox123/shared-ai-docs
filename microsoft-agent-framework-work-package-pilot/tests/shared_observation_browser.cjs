// Interactive driver: the test owns worker/restart timing; the browser uses public surfaces.
const readline = require('node:readline');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.WPCP_TEST_PLAYWRIGHT ||
  `${process.env.HOME}/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright-core`);
const channel = readline.createInterface({input: process.stdin});
const lines = channel[Symbol.asyncIterator]();
const next = async () => JSON.parse((await lines.next()).value);
const send = value => process.stdout.write(JSON.stringify(value) + '\n');
(async () => {
  const input = await next();
  const browser = await chromium.launch({headless: true, channel: 'chrome'});
  const failures = [];
  try {
    let baseUrl = input.baseUrl;
    async function connect(width, id = '') {
      const page = await browser.newPage({viewport: {width, height: width === 390 ? 844 : 1000}});
      page.setDefaultTimeout(15000);
      page.on('pageerror', error => failures.push(error.message));
      await page.goto(baseUrl + '/operator/' + (id ? '#' + id : ''));
      await page.getByLabel('GitHub-Zugangstoken').fill(input.credential);
      await page.getByRole('button', {name: 'Verbinden', exact: true}).click();
      await page.getByText('Mit GitHub verbunden', {exact: true}).waitFor();
      return page;
    }
    const read = async (page, suffix) => (await page.request.get(baseUrl + '/api/v1/' + suffix,
      {headers: {Authorization: 'Bearer ' + input.credential}})).json();
    async function state(page, label) {
      await page.locator('[data-execution="state"]').filter({hasText: new RegExp('^' + label + '$')}).waitFor({timeout: input.live ? 180000 : 20000});
      const row = page.locator('.submission-row[aria-current=true] .badge');
      assert.equal(await row.textContent(), label);
    }
    const page = await connect(1024);
    await page.locator('.intake-disclosure > summary').click();
    await page.getByLabel('GitHub-Issue-URL').fill(input.sourceUrl);
    await page.getByRole('button', {name: 'Starten', exact: true}).click();
    await state(page, 'Wartend');
    const submissionId = await page.locator('[data-field="id"]').textContent();
    const runId = await page.locator('[data-execution="run-id"]').textContent();
    await page.getByRole('tab', {name: 'Verlauf', exact: true}).click();
    const admission = page.locator('#workflow-graph [data-attempt-id]').first();
    await admission.focus();
    const attemptId = await admission.getAttribute('data-attempt-id');
    send({stage: 'queued', submissionId, runId});
    await next();
    await state(page, 'Läuft');
    await page.waitForFunction(() => document.querySelectorAll('#workflow-graph [data-attempt-id]').length > 1);
    assert.equal(await page.evaluate(id => document.activeElement?.dataset.attemptId === id, attemptId), true,
      'A live workflow update lost keyboard focus');
    await page.locator(`[data-attempt-id="${attemptId}"]`).click();
    assert.equal(await page.evaluate(id => document.activeElement?.dataset.attemptId === id, attemptId), true,
      'Selecting a workflow step lost keyboard focus');
    send({stage: 'running'});
    await next();
    await state(page, 'Analyse abgeschlossen');
    await page.locator('#workflow-state').filter({hasText: 'Analyse abgeschlossen'}).waitFor();
    assert.equal(await page.evaluate(id => document.activeElement?.dataset.attemptId === id, attemptId), true);
    assert.equal(await page.getByRole('tab', {name: 'Verlauf', exact: true}).getAttribute('aria-selected'), 'true');
    send({stage: 'completed', submissionId, runId});
    baseUrl = (await next()).baseUrl;
    const observed = [];
    for (const width of [1024, 390]) {
      const reopened = await connect(width, submissionId);
      await state(reopened, 'Analyse abgeschlossen');
      const record = await read(reopened, 'submissions/' + submissionId);
      const run = await read(reopened, 'runs/' + runId);
      const attempt = run.attempts.find(a => a.session);
      let result = attempt.session.originalResult;
      if (result.artifactId) result = await read(reopened, 'runs/' + runId + '/artifacts/' + result.artifactId);
      assert.equal(await reopened.locator('[data-field="title"]').textContent(), record.title);
      assert.equal(await reopened.locator('[data-field="source"]').getAttribute('href'), record.source.url);
      await reopened.waitForFunction(summary => document.querySelector('[data-execution="result"]').textContent === summary, result.summary);
      assert.deepEqual(await reopened.locator('[data-execution="findings"] li').allTextContents(), result.findings);
      assert.equal(await reopened.getByRole('tab', {name: 'Ergebnis', exact: true}).getAttribute('aria-selected'), 'true');
      assert.equal(await reopened.locator('[data-field="body"]').isVisible(), false);
      assert.ok(await reopened.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      if (input.evidence) {
        fs.mkdirSync(input.evidence, {recursive: true});
        await reopened.keyboard.press('Tab');
        await reopened.locator('.submission-row[aria-current=true]').focus();
        await reopened.screenshot({path: path.join(input.evidence, 'result-' + width + '.png'), fullPage: true});
      }
      await reopened.getByRole('tab', {name: 'Anforderungen', exact: true}).click();
      assert.equal(await reopened.locator('[data-field="body"]').textContent(), record.body);
      observed.push({width, submissionId: record.submissionId, runId: run.runId, state: 'completed',
        title: record.title, summary: result.summary, findings: result.findings, bodyMatches: true, horizontalOverflow: false});
      await reopened.close();
    }
    assert.deepEqual(failures, []);
    send({stage: 'verified', observed, browserErrors: failures});
  } finally { await browser.close(); channel.close(); }
})().catch(error => {console.error(error.stack); process.exitCode = 1;});

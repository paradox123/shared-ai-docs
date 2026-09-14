// Runs the production GUI; private credentials arrive over stdin only.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.WPCP_TEST_PLAYWRIGHT ||
  `${process.env.HOME}/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright-core`);
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
(async () => {
  const browser = await chromium.launch({headless: true, channel: 'chrome'});
  const failures = [];
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 1100}});
    page.on('pageerror', error => failures.push(error.message));
    await page.goto(input.baseUrl + '/operator/' + (input.submissionId ? '#' + input.submissionId : ''));
    await page.getByLabel('GitHub-Zugangstoken').fill(input.credential);
    await page.getByRole('button', {name: 'Verbinden', exact: true}).click();
    await page.getByText('Mit GitHub verbunden', {exact: true}).waitFor();
    if (input.mode === 'start') {
      await page.getByLabel('GitHub-Issue-URL').fill(input.sourceUrl);
      await page.getByRole('button', {name: 'Starten', exact: true}).click();
    } else if (input.mode === 'start-saved') {
      await page.getByRole('button', {name: 'Analyse starten', exact: true}).click();
    }
    await page.locator('[data-execution="run-id"]').filter({hasText: /[0-9a-f]{8}-/}).waitFor({state: 'attached'});
    await page.locator('[data-execution="state"]').filter({hasText: /\S/}).waitFor();
    if (input.expectedState) {
      await page.locator('[data-execution="state"]').filter({hasText: input.expectedState}).waitFor({timeout: 180000});
      if (input.summary) assert.match(await page.locator('[data-execution="result"]').textContent(), new RegExp(input.summary));
    }
    const submissionId = await page.locator('#detail [data-field="id"]').textContent();
    const runId = await page.locator('[data-execution="run-id"]').textContent();
    const state = await page.locator('[data-execution="state"]').textContent();
    const result = await page.locator('[data-execution="result"]').textContent();
    if (input.runId) assert.equal(runId, input.runId);
    if (input.screenshot) await page.screenshot({path: input.screenshot, fullPage: true});
    await page.setViewportSize({width: 390, height: 844});
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Mobile overflow');
    if (input.mobileScreenshot) await page.screenshot({path: input.mobileScreenshot, fullPage: true});
    assert.deepEqual(await page.evaluate(() => ({local: Object.keys(localStorage), session: Object.keys(sessionStorage)})), {local: [], session: []});
    assert.deepEqual(failures, []);
    process.stdout.write(JSON.stringify({submissionId, runId, state, result, browserErrors: failures}));
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });

// Browser boundary proof. Credentials arrive only over stdin and are never retained.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.WPCP_TEST_PLAYWRIGHT ||
  `${process.env.HOME}/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright-core`);
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
(async () => {
  const browser = await chromium.launch({headless: true, channel: 'chrome'});
  const failures = [];
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 1000}});
    page.on('pageerror', error => failures.push(error.message));
    await page.goto(input.baseUrl + '/operator/');
    await page.getByLabel('GitHub-Zugangstoken').fill(input.credential);
    await page.getByRole('button', {name: 'Verbinden', exact: true}).click();
    await page.getByText('Mit GitHub verbunden', {exact: true}).waitFor();
    assert.equal(await page.getByLabel('GitHub-Zugangstoken').inputValue(), '');
    if (input.admit) {
      assert.equal(await page.locator('#count').textContent(), '0', 'Acceptance must start with empty overview');
      if (!await page.locator('.intake-disclosure').evaluate(node => node.open)) await page.locator('.intake-disclosure > summary').click();
      await page.getByLabel('GitHub-Issue-URL').fill(input.sourceUrl);
      await page.getByRole('button', {name: 'Aufnehmen', exact: false}).click();
      await page.locator('#notice').filter({hasText: 'Aufgenommen'}).waitFor();
    }
    await page.locator('#detail [data-field="title"]').filter({hasText: input.title}).waitFor();
    assert.equal(await page.locator('#detail [data-field="title"]').textContent(), input.title);
    assert.equal(await page.locator('#detail [data-field="body"]').textContent(), input.body);
    assert.equal(await page.locator('#detail [data-field="repository"]').textContent(), input.repository);
    assert.equal(await page.locator('#detail [data-field="source"]').getAttribute('href'), input.sourceUrl);
    assert.match(await page.locator('.execution-note').textContent(), /noch nicht gestartet/);
    const id = await page.locator('#detail [data-field="id"]').textContent();
    const read = await page.request.get(input.baseUrl + '/api/v1/submissions/' + id,
      {headers: {Authorization: `Bearer ${input.credential}`}});
    assert.equal(read.status(), 200);
    const snapshot = await read.json();
    assert.equal(snapshot.state, 'admitted');
    assert.equal(snapshot.runId, null);
    assert.equal(snapshot.title, input.title);
    assert.equal(snapshot.body, input.body);
    if (input.expectedSnapshot) assert.deepEqual(snapshot, input.expectedSnapshot);
    // A second submission takes the actual UI path and must rediscover the same identity.
    if (!await page.locator('.intake-disclosure').evaluate(node => node.open)) await page.locator('.intake-disclosure > summary').click();
      await page.getByLabel('GitHub-Issue-URL').fill(input.sourceUrl);
    await page.getByRole('button', {name: 'Aufnehmen', exact: false}).click();
    await page.locator('#notice').filter({hasText: 'Aufgenommen'}).waitFor();
    assert.equal(await page.locator('#count').textContent(), '1');
    assert.equal(await page.locator('#detail [data-field="id"]').textContent(), id);
    assert.deepEqual(await page.evaluate(() => ({local: Object.keys(localStorage), session: Object.keys(sessionStorage)})), {local: [], session: []});
    assert.equal(await page.locator('#detail script, #detail img').count(), 0, 'Provider markup must remain inert');
    if (input.screenshot) await page.screenshot({path: input.screenshot, fullPage: true});
    await page.setViewportSize({width: 390, height: 844});
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Mobile page overflows');
    if (input.mobileScreenshot) await page.screenshot({path: input.mobileScreenshot, fullPage: true});
    await page.getByRole('button', {name: 'Abmelden', exact: true}).click();
    await page.getByRole('heading', {name: 'Mit GitHub verbinden'}).waitFor();
    assert.equal(await page.locator('#detail').textContent(), '');
    assert.deepEqual(failures, []);
    process.stdout.write(JSON.stringify({snapshot, browserErrors: failures, mobileOverflow: false}));
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });

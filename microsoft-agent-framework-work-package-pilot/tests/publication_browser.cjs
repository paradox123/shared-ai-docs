// Real browser execution used by the trusted evidence plan fixture.
const { chromium } = require(process.argv[2]);
(async () => {
  const browser = await chromium.launch({headless: true, channel: 'chrome'});
  try {
    const page = await browser.newPage({viewport: {width: 900, height: 560}});
    await page.goto(process.argv[3]);
    if (process.argv[5] === 'interact') {
      await page.getByRole('button', {name: 'Create record'}).click();
      await page.getByText('Records: 1', {exact: true}).waitFor();
    }
    await page.screenshot({path: process.argv[4]});
    console.log(await page.locator('h1').innerText());
  } finally { await browser.close(); }
})().catch(() => { process.exitCode = 1; });

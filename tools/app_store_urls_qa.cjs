const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'data/app-store-website-urls.json'), 'utf8'));
const base = process.env.QA_BASE || 'http://127.0.0.1:4198/';
const out = process.env.QA_OUTPUT || '/tmp/oneglp-app-store-urls-qa';

(async () => {
  fs.mkdirSync(out, {recursive: true});
  const browser = await chromium.launch({headless: true, executablePath: process.env.QA_BROWSER});
  const results = [];
  try {
    for (const width of [1280, 390, 320]) {
      const context = await browser.newContext({viewport: {width, height: 900}, isMobile: width < 600, hasTouch: width < 600});
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push(String(e)));
      for (const incoming of data.paths) {
        const expected = data.aliases[incoming] || incoming;
        await page.goto(new URL(incoming, base).href);
        await page.waitForURL(new URL(expected, base).href);
        await page.waitForLoadState('networkidle');
        await page.evaluate(() => document.fonts.ready);
        const actual = await page.evaluate(() => ({
          title: document.title, lang: document.documentElement.lang.toLowerCase(),
          overflow: document.documentElement.scrollWidth - innerWidth,
          robots: [...document.querySelectorAll('meta[name="robots"]')].map(x => x.content),
          brand: document.querySelector('[data-rebrand-link]')?.textContent,
          contact: [...document.querySelectorAll('a[href^="mailto:"]')].map(a => a.getAttribute('href')),
          policyLinks: [...document.querySelectorAll('body a[href]')].map(a => a.href).filter(href => /\/(support|privacy)\.html$/.test(new URL(href).pathname)),
        }));
        const locale = expected.split('/').length === 3 ? expected.split('/')[1] : 'en';
        assert(locale === 'en-gb' ? ['en', 'en-gb'].includes(actual.lang) : actual.lang === locale,
          `${incoming}: expected ${locale}, got ${actual.lang}`);
        assert(actual.title.includes('OneGLP'), `${incoming}: old title`);
        assert(actual.brand?.includes('OneGLP'), `${incoming}: missing rebrand notice`);
        assert(actual.overflow <= 1, JSON.stringify({incoming, width, actual}));
        assert.deepEqual(actual.robots, ['index,follow']);
        if (expected.endsWith('/support.html')) assert(actual.contact.length, `${incoming}: no support route`);
        for (const href of new Set(actual.policyLinks)) {
          const response = await context.request.get(href);
          assert.equal(response.status(), 200, href);
          assert(/<title>[^<]*OneGLP/.test(await response.text()), href);
        }
        if (data.aliases[incoming] || incoming === '/privacy.html' || incoming === '/support.html') {
          await page.screenshot({path: `${out}/${incoming.replaceAll('/', '_')}-${width}.png`});
        }
        results.push({incoming, expected, width, ...actual});
      }
      assert.deepEqual(errors, []);
      const missing = await context.request.get(new URL('/FR/index.html', base).href);
      assert.equal(missing.status(), 404, 'Preview must not silently accept undeclared case aliases');
      await context.close();
      console.log(`PASS: all 54 App Store website paths at ${width}px`);
    }
    const context = await browser.newContext({javaScriptEnabled: false});
    const page = await context.newPage();
    for (const [alias, target] of Object.entries(data.aliases)) {
      await page.goto(new URL(alias, base).href);
      await page.waitForURL(new URL(target, base).href);
      assert((await page.title()).includes('OneGLP'));
    }
    await context.close();
    fs.writeFileSync(`${out}/results.json`, JSON.stringify(results, null, 2));
    console.log('PASS: 10 deliberate same-language redirects also work without JavaScript; support/privacy links resolve. Local only, not a deployment check.');
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode = 1;});

const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'data/rebrand-page.json'), 'utf8'));
const base = process.env.QA_BASE || 'http://127.0.0.1:4197/';
const out = process.env.QA_OUTPUT || '/tmp/oneglp-name-page-qa';
fs.mkdirSync(out, {recursive: true});

(async () => {
  const browser = await chromium.launch({headless: true, executablePath: process.env.QA_BROWSER});
  const results = [];
  try {
    for (const width of [1280, 390, 320]) {
      const context = await browser.newContext({viewport: {width, height: width === 1280 ? 900 : 844}, isMobile: width < 600, hasTouch: width < 600});
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push(String(e)));
      for (const locale of Object.keys(data.translations)) {
        const prefix = locale === 'en' ? '' : `${locale}/`;
        const rel = `${prefix}${data.slug}/`;
        const response = await page.goto(base + rel, {waitUntil: 'networkidle'});
        assert.equal(response.status(), 200);
        await page.evaluate(() => document.fonts.ready);
        await page.locator('.name-logo img').evaluate(img => img.decode());
        const check = await page.evaluate(() => {
          const visible = [...document.querySelectorAll('h1, h2, p, a, img, summary')].filter(el => el.getClientRects().length);
          return {
            overflow: document.documentElement.scrollWidth - innerWidth,
            clipped: visible.filter(el => {const r = el.getBoundingClientRect(); return r.left < -1 || r.right > innerWidth + 1 || el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).display !== 'inline';}).map(el => el.textContent.trim() || el.tagName),
            brokenImages: [...document.images].filter(img => !img.complete || !img.naturalWidth).length,
            robots: [...document.querySelectorAll('meta[name="robots"]')].map(el => el.content),
            title: document.querySelector('h1').textContent,
          };
        });
        assert(check.overflow <= 1 && !check.clipped.length && !check.brokenImages, JSON.stringify({rel, width, ...check}));
        assert.deepEqual(check.robots, ['index,follow']);
        await page.screenshot({path: `${out}/${locale}-${width}.png`, fullPage: true});
        await page.locator('.name-languages summary').click();
        const menu = await page.locator('.name-languages ul').boundingBox();
        assert(menu.x >= 0 && menu.x + menu.width <= width + 1, `${locale} menu overflow at ${width}`);
        await page.locator('.name-languages a[hreflang="en"]').click();
        await page.waitForURL(`**/${data.slug}/index.html`);
        assert.equal(await page.locator('h1').innerText(), data.translations.en.title);
        await page.goto(base + prefix, {waitUntil: 'networkidle'});
        await page.evaluate(() => document.fonts.ready);
        const hook = page.locator('[data-rebrand-link]');
        assert.equal(await hook.count(), 1);
        assert(await hook.isVisible());
        const home = await page.evaluate(() => ({overflow: document.documentElement.scrollWidth - innerWidth, hero: document.querySelector('.hero')?.getBoundingClientRect().bottom}));
        assert(home.overflow <= 1, JSON.stringify({locale, width, home}));
        await page.screenshot({path: `${out}/home-${locale}-${width}.png`});
        await hook.click();
        await page.waitForURL(`**/${data.slug}/index.html`);
        results.push({locale, width, ...check, home});
        console.log(`PASS ${locale} ${width}px: rebrand page, language menu and homepage hook`);
      }
      assert.deepEqual(errors, []);
      await context.close();
    }
    const context = await browser.newContext({javaScriptEnabled: false, viewport: {width: 390, height: 844}});
    const page = await context.newPage();
    await page.goto(base + data.slug + '/');
    assert.equal(await page.locator('h1').innerText(), data.translations.en.title);
    assert.equal(await page.locator('[data-app-store-link]').count(), 2);
    assert(await page.locator('[data-app-store-link]').first().isVisible());
    const ordinary = await context.request.get(base + data.slug + '/');
    for (const bot of ['OAI-SearchBot', 'GPTBot', 'ChatGPT-User']) {
      const response = await context.request.get(base + data.slug + '/', {headers: {'User-Agent': bot}});
      assert.equal(response.status(), 200);
      assert(!/noindex/i.test(response.headers()['x-robots-tag'] || ''));
      assert.equal(await response.text(), await ordinary.text());
    }
    await context.close();
    fs.writeFileSync(`${out}/results.json`, JSON.stringify(results, null, 2));
    console.log(`PASS: ${results.length * 2} views at desktop/390px/320px; no-JS content and equivalent bot responses. Screenshots: ${out}`);
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode = 1;});

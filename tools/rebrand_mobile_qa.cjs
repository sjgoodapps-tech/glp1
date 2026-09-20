const fs = require('node:fs');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.QA_BASE || 'http://127.0.0.1:4197/';
const out = process.env.QA_OUTPUT || '/tmp/oneglp-mobile-qa';
fs.mkdirSync(out, {recursive:true});
(async () => {
  const browser = await chromium.launch({headless:true, executablePath:process.env.QA_BROWSER});
  const results = [];
  try {
    for (const width of [390,320]) {
      const context = await browser.newContext({viewport:{width,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2});
      const page = await context.newPage();
      for (const rel of ['', 'free-lifetime/', 'ar/', 'zh-hans/', 'zh-hant/', 'ja/', 'hi/', 'pt-pt/', 'support.html']) {
        await page.goto(base+rel, {waitUntil:'networkidle'});
        await page.evaluate(() => document.fonts.ready);
        const result = await page.evaluate(() => {
          const notice = document.querySelector('.rebrand-notice');
          const r = notice.getBoundingClientRect();
          return {overflow:document.documentElement.scrollWidth-innerWidth,notice:notice.textContent,clipped:r.left < -1 || r.right > innerWidth+1,position:getComputedStyle(notice).position,logo:getComputedStyle(document.querySelector('.brand-lockup')).backgroundImage};
        });
        assert(result.overflow <= 1 && !result.clipped && result.position === 'static', JSON.stringify({rel,width,...result}));
        assert(result.logo.includes('oneglp-logo-dark.svg'));
        await page.screenshot({path:`${out}/${(rel||'home').replaceAll('/','-')}-${width}.png`});
        results.push({rel,width,...result});
      }
      await page.goto(base,{waitUntil:'networkidle'});
      await page.locator('[data-language-toggle]').tap();
      assert(await page.locator('[data-language-panel]').isVisible());
      await page.locator('[data-language-option="ar"]').tap();
      await page.waitForURL('**/ar/index.html');
      assert((await page.locator('.rebrand-notice').innerText()).includes('أصبح'));
      await context.close();
    }
    fs.writeFileSync(`${out}/results.json`,JSON.stringify(results,null,2));
    console.log(`PASS: ${results.length} touch-enabled mobile views; notice wrapping, logo, overflow and language selection.`);
  } finally { await browser.close(); }
})().catch(error => {console.error(error);process.exitCode=1;});

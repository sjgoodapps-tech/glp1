const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.QA_BASE || 'http://127.0.0.1:4189/';
const out = process.env.QA_OUTPUT || '/tmp/glpzy-growth-qa-output';
const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/localisation-qa.json')));
const roots = ['', 'free-lifetime/', 'glp1-weight-dose-symptom-tracker.html', 'mounjaro-tracker-iphone.html', 'wegovy-tracker-iphone.html', 'zepbound-tracker-iphone.html', 'tirzepatide-tracker-iphone.html', 'semaglutide-tracker-iphone.html', 'glp1-progress-photo-tracker.html', 'glp1-side-effect-symptom-tracker.html', 'glp1-weight-tracker.html', 'glp1-dose-reminder-app.html', 'apple-health-glp-tracker.html', 'local-first-private-glp-tracker.html'];
const pages = [...roots, ...manifest.priority_locales.flatMap(locale => ['index.html', 'data-rights.html', 'medical-safety.html'].map(page => `${locale}/${page}`)), 'bg/index.html', 'pt-br/index.html', 'th/terms.html'];
fs.mkdirSync(out, {recursive: true});

async function settled(page) {
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].filter(img => {
      const r = img.getBoundingClientRect();
      return r.top < innerHeight && r.bottom > 0 && r.width;
    }).map(img => img.decode().catch(() => {})));
  });
}

async function measure(page) {
  return page.evaluate(() => {
    const visible = el => {
      const r = el.getBoundingClientRect(), s = getComputedStyle(el);
      return !el.hidden && s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
    };
    return {
      overflow: document.documentElement.scrollWidth - innerWidth,
      robots: [...document.querySelectorAll('meta[name="robots"]')].map(x => x.content),
      clipped: [...document.querySelectorAll('.founding-offer-banner a,.founding-offer-banner button,.hero-proof,.hero-proof-item,.hero-actions a,.offer-sticky-cta a')].filter(visible).filter(x => {const r=x.getBoundingClientRect();return r.left < -1 || r.right > innerWidth+1 || x.scrollWidth > x.clientWidth+1;}).map(x=>x.innerText),
      broken: [...document.images].filter(x => visible(x) && x.getBoundingClientRect().top < innerHeight && x.complete && x.naturalWidth === 0).map(x=>x.src),
      sticky: [...document.querySelectorAll('.offer-sticky-cta,.mobile-store-cta')].filter(visible).length,
      heroImage: document.querySelector('.hero-visual img')?.currentSrc,
    };
  });
}

(async () => {
  const browser = await chromium.launch({headless:true, executablePath:process.env.QA_BROWSER});
  const views = [], interactions = [], errors = [];
  try {
    for (const width of [1280,390,320]) {
      const context = await browser.newContext({viewport:{width,height:900}});
      const page = await context.newPage();
      page.on('pageerror', error => errors.push(String(error)));
      for (const rel of pages) {
        const response = await page.goto(base+rel, {waitUntil:'networkidle'});
        await settled(page);
        const result = await measure(page);
        const screenshot = `${rel || 'homepage'}`.replace(/\/$/,'').replaceAll('/','-').replace('.html','')+`-${width}.png`;
        await page.screenshot({path:path.join(out,screenshot)});
        views.push({rel,width,status:response.status(),screenshot,...result});
        if (manifest.priority_locales.some(l=>rel===`${l}/index.html`)) {
          await page.locator('#premium').scrollIntoViewIfNeeded();
          await settled(page);
          await page.screenshot({path:path.join(out,screenshot.replace('.png','-premium.png'))});
        }
      }
      await context.close();
      console.log(`Settled screenshots: ${pages.length} pages at ${width}px`);
    }
    for (const width of [1280,390,320]) {
      const context = await browser.newContext({viewport:{width,height:900}});
      const page = await context.newPage();
      await page.clock.install({time:new Date('2026-12-31T23:59:50Z')});
      await page.goto(base, {waitUntil:'networkidle'});
      await page.clock.fastForward(8100);
      assert.equal((await measure(page)).sticky,0,'active hero must not be covered');
      await page.clock.fastForward(3000);
      assert.equal(await page.locator('.founding-offer-banner').count(),0);
      await page.reload({waitUntil:'networkidle'});
      await settled(page);
      assert.equal((await measure(page)).sticky,0,'expired fresh hero must not be covered');
      await page.screenshot({path:path.join(out,`expired-homepage-${width}.png`)});
      await page.goto(base+'free-lifetime/',{waitUntil:'networkidle'});
      await settled(page);
      assert((await page.locator('h1').innerText()).includes('has ended'));
      assert((await measure(page)).heroImage.includes('/responsive/'));
      await page.screenshot({path:path.join(out,`expired-offer-${width}.png`)});
      await context.close();

      const fresh = await browser.newContext({viewport:{width,height:900}});
      const tab = await fresh.newPage();
      await tab.goto(base+'pt-pt/privacy.html',{waitUntil:'networkidle'});
      await tab.locator('[data-language-toggle]').click();
      await tab.locator('[data-language-option="en"]').click();
      await tab.waitForLoadState('networkidle');
      assert.equal(new URL(tab.url()).pathname,'/privacy.html');
      await tab.goto(base,{waitUntil:'networkidle'});
      await tab.getByRole('button',{name:'Dismiss founding offer',exact:true}).click();
      await tab.reload({waitUntil:'networkidle'});
      assert.equal(await tab.locator('.founding-offer-banner').count(),0);
      interactions.push({width,activeHero:true,expiredHero:true,expiredOffer:true,englishRoute:true,dismissal:true});
      await fresh.close();
    }
    const failed = views.filter(v=>v.status!==200 || v.overflow>1 || v.clipped.length || v.broken.length || v.robots.length!==1);
    fs.writeFileSync(path.join(out,'visual-results.json'),JSON.stringify({views,interactions,errors,failed},null,2));
    assert.equal(errors.length,0,errors.join('\n'));
    assert.equal(failed.length,0,JSON.stringify(failed));
    console.log(`PASS: ${views.length} views; no overflow, clipped CTAs, broken visible images or browser errors; active/expired interaction checks passed.`);
  } finally {
    await browser.close();
  }
})().catch(error=>{console.error(error);process.exitCode=1;});

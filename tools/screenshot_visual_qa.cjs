const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'data/screenshot-manifest.json')));
const locales = Object.keys(JSON.parse(fs.readFileSync(path.join(root, 'data/screenshot-copy.json'))).translations);
const representative = ['ar','de','fr','pt-pt','es-es','it','nl','ja','ko','hi','zh-hans','zh-hant'];
const english = ['', 'free-lifetime/', ...Object.keys(manifest.page_slots), 'methodology.html', 'medical-safety.html', 'privacy.html', 'support.html'];
const pages = [...new Set([...english, ...locales.map(l=>`${l}/index.html`), ...representative.flatMap(l=>[`${l}/wegovy-tracker-iphone.html`,`${l}/medical-safety.html`])])];
const base = process.env.QA_BASE || 'http://127.0.0.1:4201/';
const out = process.env.QA_OUTPUT || '/tmp/oneglp-v5-visual-qa';
fs.mkdirSync(out, {recursive:true});

async function settled(page) {
  await page.evaluate(async()=>{
    await document.fonts.ready;
    await Promise.race([Promise.all([...document.images].filter(i=>{const r=i.getBoundingClientRect();return r.width&&r.height&&r.top<innerHeight&&r.bottom>0;}).map(i=>i.decode().catch(()=>{}))),new Promise(r=>setTimeout(r,10000))]);
  });
}

async function measure(page) {
  return page.evaluate(()=>{
    const shown=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none';};
    const image=document.querySelector('.hero-screens');
    const clipped=[...document.querySelectorAll('.hero-actions a,.website-shot figcaption,.hero-shot figcaption,.shot-enlarge,.offer-sticky-cta,.hero-proof')].filter(shown).filter(e=>{const r=e.getBoundingClientRect();return r.left< -1||r.right>innerWidth+1||e.scrollWidth>e.clientWidth+1;}).map(e=>e.textContent.trim());
    const heroResources=[...document.querySelectorAll('.hero-visual img')].filter(shown).map(i=>performance.getEntriesByName(i.currentSrc).at(-1)).filter(Boolean);
    return {
      overflow:document.documentElement.scrollWidth-innerWidth,
      clipped,
      broken:[...document.images].filter(i=>shown(i)&&i.getBoundingClientRect().top<innerHeight&&i.complete&&!i.naturalWidth).map(i=>i.src),
      robots:[...document.querySelectorAll('meta[name="robots"]')].map(m=>m.content),
      heroTop:image?.getBoundingClientRect().top,
      heroBytes:heroResources.reduce((n,r)=>n+r.encodedBodySize,0),
      hiddenGraphRequested:innerWidth<=720&&!![...document.querySelectorAll('.hero-weight img')].find(i=>i.currentSrc&&!i.currentSrc.startsWith('data:')),
      performance:window.__imagePerf,
    };
  });
}

(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.QA_BROWSER});
 const results=[], interactions=[], errors=[];
 try {
  for(const width of [1280,390,320]) {
   const context=await browser.newContext({viewport:{width,height:width===1280?900:width===390?844:812},deviceScaleFactor:2});
   const page=await context.newPage();
   page.on('pageerror',e=>errors.push(String(e)));
   await page.addInitScript(()=>{
     window.__imagePerf={lcp:0,cls:0};
     new PerformanceObserver(list=>{for(const e of list.getEntries())window.__imagePerf.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});
     new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__imagePerf.cls+=e.value;}).observe({type:'layout-shift',buffered:true});
   });
   for(const rel of pages) {
    const response=await page.goto(base+rel,{waitUntil:'networkidle'});
    await settled(page);
    const name=(rel||'home').replaceAll('/','-').replace('.html','')+`-${width}.png`;
    const result={rel,width,status:response.status(),...await measure(page)};
    const capture=english.includes(rel)||representative.includes(rel.split('/')[0]);
    if(capture){await page.screenshot({path:path.join(out,name)});result.screenshot=name;}
    results.push(result);
    if(rel===''||representative.some(l=>rel===`${l}/index.html`)||rel==='glp1-progress-photo-tracker.html') {
      const figures=page.locator('.website-shot');
      for(let n=0;n<await figures.count();n++) {
        await figures.nth(n).scrollIntoViewIfNeeded();await settled(page);
        const check=await measure(page);
        assert.equal(check.overflow,0,`Scrolled overflow ${rel} ${width}`);
        assert.equal(check.broken.length,0,`Broken gallery image ${rel} ${width}`);
        assert.equal(check.clipped.length,0,`Clipped gallery caption ${rel} ${width}`);
      }
      if(await figures.count()) {
        await figures.first().scrollIntoViewIfNeeded();await settled(page);
        await page.screenshot({path:path.join(out,name.replace('.png','-gallery.png'))});
      }
    }
   }
   await context.close();
   console.log(`${width}px: ${pages.length} pages checked`);
  }
  for(const width of [1280,390,320]) {
    const context=await browser.newContext({viewport:{width,height:900}});
    const page=await context.newPage();
    await page.clock.install({time:new Date('2026-12-31T23:59:50Z')});
    await page.goto(base,{waitUntil:'networkidle'});await settled(page);
    await page.clock.fastForward(8100);
    assert.equal(await page.locator('.offer-sticky-cta:visible,.mobile-store-cta:visible').count(),0,'sticky must stay hidden over hero');
    await page.clock.fastForward(3000);
    assert.equal(await page.locator('.founding-offer-banner').count(),0,'open-page expiry');
    assert(!(await page.locator('.hero-copy').innerText()).includes('is free until'),'no stale active hero copy');
    await page.screenshot({path:path.join(out,`expired-home-${width}.png`)});
    await page.goto(base+'free-lifetime/',{waitUntil:'networkidle'});await settled(page);
    assert((await page.locator('[data-offer-copy$="landingTitle"]').innerText()).includes('has ended'));
    assert.equal((await measure(page)).broken.length,0);
    await page.screenshot({path:path.join(out,`expired-offer-${width}.png`)});
    await context.close();
    const fresh=await browser.newContext({viewport:{width,height:900}});
    const tab=await fresh.newPage();
    await tab.goto(base,{waitUntil:'networkidle'});
    await tab.getByRole('button',{name:'Dismiss founding offer',exact:true}).click();
    await tab.reload({waitUntil:'networkidle'});
    assert.equal(await tab.locator('.founding-offer-banner').count(),0);
    await tab.goto(base+'pt-pt/index.html',{waitUntil:'networkidle'});
    await tab.locator('[data-language-toggle]').click();
    await tab.locator('[data-language-option="en"]').click();
    await tab.waitForLoadState('networkidle');
    assert.equal(new URL(tab.url()).pathname,'/index.html');
    await tab.locator('.shot-enlarge').first().click();
    await tab.waitForURL(/oneglp-v5-log-1320.webp/);
    await tab.locator('img').evaluate(i=>i.decode());
    assert.equal(await tab.locator('img').evaluate(i=>i.naturalWidth),1320);
    await tab.goBack({waitUntil:'networkidle'});
    interactions.push({width,openPageExpiry:true,expiredOffer:true,bannerDismissal:true,languageSwitch:true,enlargeImage:true,heroStickySuppressed:true});
    await fresh.close();
  }
  const failed=results.filter(r=>r.status!==200||r.overflow>1||r.clipped.length||r.broken.length||r.robots.length!==1||r.robots[0].replaceAll(' ','')!=='index,follow'||r.hiddenGraphRequested);
  fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({results,interactions,errors,failed},null,2));
  assert.equal(errors.length,0,errors.join('\n'));
  assert.equal(failed.length,0,JSON.stringify(failed));
  console.log(`PASS: ${results.length} views; ${interactions.length} interaction/expiry sets; no overflow, clipped new captions, broken visible images or hidden mobile hero-graph requests.`);
 } finally {
   fs.writeFileSync(path.join(out,'progress.json'),JSON.stringify({results,interactions,errors},null,2));
   await browser.close();
 }
})().catch(e=>{console.error(e);process.exitCode=1;});

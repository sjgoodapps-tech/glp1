const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const facts = JSON.parse(fs.readFileSync(path.join(root, 'data/product-facts.json'), 'utf8'));
const expiry = Date.parse(facts.founding_offer.expires_at);

for (const file of ['index.html', 'free-lifetime/index.html']) {
  const html = fs.readFileSync(path.join(root, file), 'utf8');
  assert.equal((html.match(/class="hero-proof"/g) || []).length, 1, `${file}: one proof strip`);
  for (const key of ['proofDownloads', 'proofDownloadsLabel', 'proofRating', 'proofRatingLabel', 'proofChecked']) {
    assert(html.includes(`data-claim-copy="${key}">${facts.product_claims[key]}<`), `${file}: proof copy must match the source`);
  }
  assert(!html.includes('"aggregateRating"'), `${file}: do not invent aggregate rating schema`);
}
assert.equal(facts.social_proof_sources.rating.storefront, 'US');
assert.equal(facts.social_proof_sources.downloads.independently_verified, false);

function page(at, locale = 'en') {
  let now = at;
  const timers = [];
  function element(tag = 'div') {
    const classes = new Set();
    return {
      tagName: tag, children: [], attrs: {}, style: { setProperty() {} }, hidden: false,
      classList: {
        add: (...names) => names.forEach(name => classes.add(name)),
        remove: (...names) => names.forEach(name => classes.delete(name)),
        contains: name => classes.has(name),
        toggle: (name, on) => on ? classes.add(name) : classes.delete(name),
      },
      setAttribute(name, value) { this.attrs[name] = value; },
      getAttribute(name) { return this.attrs[name] || null; },
      appendChild(child) { child.parentNode = this; this.children.push(child); return child; },
      insertBefore(child) { child.parentNode = this; this.children.unshift(child); },
      removeChild(child) { this.children = this.children.filter(item => item !== child); child.parentNode = null; },
      remove() { if (this.parentNode) this.parentNode.removeChild(this); },
      addEventListener() {}, querySelector() { return null; },
      getBoundingClientRect() { return { top: 0, bottom: 80, left: 0, right: 320, width: 320, height: 80 }; },
    };
  }
  const body = element('body');
  const html = element('html');
  html.scrollHeight = 4000;
  const copies = ['active.heroLine', 'expired.heroLine'].map(key => {
    const item = element('p'); item.setAttribute('data-offer-copy', key); return item;
  });
  const storage = () => ({ getItem() { return null; }, setItem() {}, removeItem() {} });
  const document = {
    body, documentElement: html, readyState: 'complete',
    currentScript: { src: 'https://www.glpzy.app/site-cta.js' },
    createElement: element,
    querySelector(selector) {
      return body.children.find(item => String(item.className || '').split(' ').includes(selector.slice(1))) || null;
    },
    querySelectorAll(selector) { return selector === '[data-offer-copy]' ? copies : []; },
  };
  class Clock extends Date { static now() { return now; } }
  const window = {
    location: new URL(`https://www.glpzy.app/${locale === 'en' ? '' : locale + '/'}`),
    localStorage: storage(), sessionStorage: storage(), innerHeight: 700, scrollY: 0,
    addEventListener() {}, setTimeout(fn, delay) { timers.push({ fn, delay }); },
  };
  const context = vm.createContext({ document, window, Date: Clock, URL });
  for (const script of ['site-preflight.js', 'site-config.js', 'site-cta.js']) {
    vm.runInContext(fs.readFileSync(path.join(root, script), 'utf8'), context, { filename: script });
  }
  return { body, html, copies, timers, document, window, advance: value => { now = value; } };
}

assert.equal(new Date(expiry).toISOString(), '2027-01-01T00:00:00.000Z');
const active = page(expiry - 1000);
assert(active.document.querySelector('.founding-offer-banner'));
assert(active.html.classList.contains('founding-offer-space'));
assert(active.copies.every(item => item.textContent === facts.founding_offer.active.heroLine));
const transition = active.timers.find(timer => timer.delay === 1001);
assert(transition, 'Open pages must schedule the expiry transition');
active.advance(expiry + 1);
transition.fn();
assert(!active.document.querySelector('.founding-offer-banner'));
assert(!active.document.querySelector('.offer-sticky-cta'));
assert(active.document.querySelector('.mobile-store-cta'));
assert(active.copies.every(item => item.textContent === facts.founding_offer.expired.heroLine));
assert(!active.html.classList.contains('founding-offer-space'));

const expired = page(expiry);
assert(!expired.document.querySelector('.founding-offer-banner'));
assert(expired.copies.every(item => item.textContent === facts.founding_offer.expired.heroLine));
const early = page(Date.parse('2026-09-08T12:00:00Z'));
assert(early.timers.every(timer => timer.delay <= 2147483647), 'Timers must not overflow');

const expectedMonths = { ar: 'ديسمبر', de: 'Dezember', fr: 'décembre', 'es-es': 'diciembre', 'pt-pt': 'dezembro', nl: 'december', it: 'dicembre', hi: 'दिसंबर', ja: '12月31日', ko: '12월', 'zh-hans': '12月31日', 'zh-hant': '12月31日' };
for (const [locale, month] of Object.entries(expectedMonths)) {
  const sample = page(expiry - 1000, locale);
  const banner = sample.document.querySelector('.founding-offer-banner');
  assert(banner.children[0].children[0].textContent.includes(month), `${locale}: expected December`);
  const sticky = sample.document.querySelector('.offer-sticky-cta');
  assert(sticky.children[0].textContent.includes(month), `${locale}: sticky date must not be truncated`);
}
console.log('PASS: central proof copy, December deadline, before/at expiry, open-page transition, stale expired HTML, timer limits and 12 translated banners.');

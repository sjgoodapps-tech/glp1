const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const copy = JSON.parse(fs.readFileSync(path.join(root, 'data/website-press-copy.json'), 'utf8'));
const source = fs.readFileSync(path.join(root, 'site-press.js'), 'utf8');
for (const locale of Object.keys(copy.translations)) {
  const bdi = {textContent: '2026-09-14'};
  const time = {getAttribute: () => '2026-09-14', querySelector: () => bdi};
  const document = {documentElement: {lang: locale}, querySelectorAll: () => [time]};
  vm.runInNewContext(source, {document, Intl, Date});
  assert.equal(bdi.textContent, new Intl.DateTimeFormat(locale, {
    year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC'
  }).format(new Date('2026-09-14T12:00:00Z')));
  // Browsers without a formatter retain the exact visible machine date.
  bdi.textContent = '2026-09-14';
  vm.runInNewContext(source, {document, Intl: {}, Date});
  assert.equal(bdi.textContent, '2026-09-14');
  function MissingLocale() { throw new Error('must not format missing locale'); }
  MissingLocale.supportedLocalesOf = () => [];
  vm.runInNewContext(source, {document, Intl: {DateTimeFormat: MissingLocale}, Date});
  assert.equal(bdi.textContent, '2026-09-14');
  function IncompleteMonth() {
    return {formatToParts: () => [{type: 'month', value: 'M09'}],
      format: () => { throw new Error('must not expose missing month data'); }};
  }
  IncompleteMonth.supportedLocalesOf = () => [locale];
  vm.runInNewContext(source, {document, Intl: {DateTimeFormat: IncompleteMonth}, Date});
  assert.equal(bdi.textContent, '2026-09-14');
}
console.log(`PASS: ${Object.keys(copy.translations).length} locale date formats and no-Intl/missing-locale fallbacks; UTC date preserved`);

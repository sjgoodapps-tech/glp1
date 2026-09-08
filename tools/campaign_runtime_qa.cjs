const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../site-config.js'), 'utf8');
// A fixture token checks URL wiring only. It is never written to website files.
for (const provider of [null, '123456']) {
  for (const pathname of ['/', '/ar/', '/zh-hant/', '/pt-pt/']) {
    const code = source.replace(/(\/\/ generated:app-store-campaign:start)[\s\S]*?(\/\/ generated:app-store-campaign:end)/,
      `$1\nvar appStoreCampaign = ${JSON.stringify({provider_token: provider})};\n$2`);
    const window = {location: {pathname}};
    vm.runInNewContext(code, {window});
    for (const [key, href] of Object.entries(window.GLPZY_SITE_CONFIG.appStoreCampaigns)) {
      const url = new URL(href);
      assert.equal(url.hostname, 'apps.apple.com');
      assert(url.pathname.includes('id6761775005'));
      assert(url.searchParams.get('ct'), key);
      assert.equal(url.searchParams.get('pt'), provider);
      assert.equal(url.searchParams.get('mt'), provider ? '8' : null);
    }
  }
}
console.log('PASS: campaign URLs preserve storefronts and names, support a provider token and never invent one.');

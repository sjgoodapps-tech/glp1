const assert = require('node:assert/strict');
const ensureBuild = require('./ensure_offer_pages_build.cjs');
const expiry = Date.parse(require('../data/product-facts.json').founding_offer.expires_at);

async function scenario({ now = expiry, latest = { status: 'built', commit: 'old' }, config, failure } = {}) {
  const calls = [];
  const github = { request: async route => {
    calls.push(route);
    if (failure) throw Object.assign(new Error('API unavailable'), { status: 403 });
    if (route.endsWith('/pages')) return { data: config || { build_type: 'legacy', source: { branch: 'main', path: '/' } } };
    if (route.endsWith('/latest')) {
      if (!latest) throw Object.assign(new Error('No build yet'), { status: 404 });
      return { data: latest };
    }
    return { data: { status: 'queued' } };
  } };
  await ensureBuild({ github, context: { repo: { owner: 'example', repo: 'site' } }, core: { info() {} }, now, head: 'new' });
  return calls.filter(route => route.startsWith('POST')).length;
}

(async () => {
  assert.equal(await scenario({ now: expiry - 1 }), 0);
  assert.equal(await scenario(), 1);
  assert.equal(await scenario({ latest: null }), 1);
  assert.equal(await scenario({ config: { source: { branch: 'main', path: '/' } } }), 1);
  assert.equal(await scenario({ latest: { status: 'built', commit: 'new' } }), 0);
  assert.equal(await scenario({ latest: { status: 'building', commit: 'old' } }), 0);
  assert.equal(await scenario({ latest: { status: 'queued', commit: 'new' } }), 0);
  assert.equal(await scenario({ latest: { status: 'errored', commit: 'new' } }), 1);
  await assert.rejects(scenario({ failure: true }), /API unavailable/);
  await assert.rejects(scenario({ config: { build_type: 'workflow' } }), /configuration changed/);
  console.log('PASS: Pages request date guard, deployed/pending guards, missing/failed build retry and fail-closed API/configuration checks. No network requests made.');
})().catch(error => { console.error(error); process.exitCode = 1; });

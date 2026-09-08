const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');

module.exports = async function ensureBuild({ github, context, core, now = Date.now(), head }) {
  const facts = JSON.parse(fs.readFileSync(path.join(root, 'data/product-facts.json'), 'utf8'));
  const expiresAt = Date.parse(facts.founding_offer.expires_at);
  if (!Number.isFinite(expiresAt)) throw new Error('Invalid offer expiry date');
  if (now < expiresAt) return core.info('Offer is active; no expiry build requested.');

  const repo = context.repo;
  const { data: site } = await github.request('GET /repos/{owner}/{repo}/pages', repo);
  if ((site.build_type && site.build_type !== 'legacy') || site.source?.branch !== 'main' || site.source?.path !== '/') {
    throw new Error('Pages publishing configuration changed; review the expiry deployment path.');
  }
  const expected = head || execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim();
  let latest;
  try {
    latest = (await github.request('GET /repos/{owner}/{repo}/pages/builds/latest', repo)).data;
  } catch (error) {
    if (error.status !== 404) throw error;
  }
  if (latest?.status === 'built' && latest.commit === expected) return core.info('Expired copy is already deployed.');
  if (latest?.status === 'queued' || latest?.status === 'building') return core.info('Pages build is already pending; the daily fallback will recheck.');

  // A GITHUB_TOKEN push alone does not trigger a branch-based Pages build.
  await github.request('POST /repos/{owner}/{repo}/pages/builds', repo);
  core.info('Requested a Pages build for expired offer copy. Check the deployment result separately.');
};

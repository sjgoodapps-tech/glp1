# OneGLP rebrand draft

Status: local, uncommitted draft. Release requires the owner's approval. The rebrand announcement uses the completed name change as requested; it does not claim that a particular App Store update is available.

## Preserved

- Current www.glpzy.app domain, page paths, App Store ID 6761775005 and existing campaign URLs. Canonical tags are now deduplicated and translation indexing restrictions removed under the owner's updated policy.
- Support address, backup extension and browser preference keys. The owner confirmed on 20 September that Steven Good personally is the publisher; GLPzy is not a legal name. Product facts, schema and publisher credits now use Steven Good, and the three English privacy pages no longer say "trading as GLPzy". Terms continue to identify OneGLP as the app made available by Steven Good.
- Every existing image byte and image/source element. The 17 modified PNGs in the original checkout were not copied or changed; this worktree uses committed screenshots.
- Existing homepage hero structure, offer deadline, medical safety boundaries and Free/Premium limits.
- Existing GitHub Actions workflows. No commit, push, deployment or App Store Connect edit.

## Changes

- Display branding, HTML titles/descriptions/social text, app/site JSON-LD names and source copy use OneGLP. Publisher JSON-LD uses Person, Steven Good, linked through #publisher. The app icon and App Store listing are not represented as the person's logo or sameAs identity.
- New SVG header logo and versioned icon paths under assets/oneglp. No web manifest or service worker added.
- All 1,304 pages have one static translated rebrand notice, sourced from data/rebrand.json across 53 locale directories plus root pages. Names use bdi isolation for RTL.
- Exact English notice: "GLPzy is now OneGLP."
- English homepage/support continuity: "OneGLP is the new name for GLPzy. It is the same app. Your existing records and Premium purchases remain available when you update."
- Banner CTA: "Get OneGLP". The offer and expiry otherwise remain unchanged.
- CSS and runtime cache version: 20260918-oneglp-draft.
- Sitemap lastmod rebuilt for changed pages. Same-day site-wide edits legitimately share dates; validation no longer requires artificial date variation.
- tools/sync_rebrand.py reapplies branding/notices without rewriting protected URLs or screenshot elements. It corrects legacy publisher entities and references to the confirmed individual, removes the incorrect trading-name phrase, and preserves product/publisher separation. Regression fixtures check legacy and already-rebranded inputs, nested entities, publisher/author references and repeat-run stability. Run it after legacy generation tools.
- New preservation and mobile-emulation tests: tools/rebrand_qa.py and tools/rebrand_mobile_qa.cjs.

## Verification on 18 September 2026

Passed:

```sh
python3 tools/sync_rebrand.py --check
python3 tools/rebrand_qa.py
python3 tools/sync_site_content.py --check
python3 tools/sync_website_copy.py --check
python3 tools/validate_offer_expiry.py
python3 tools/localisation_qa.py --all
python3 tools/website_growth_qa.py
node tools/offer_runtime_qa.cjs
node tools/offer_pages_build_qa.cjs
node tools/campaign_runtime_qa.cjs
git diff --check
```

Browser QA requires PLAYWRIGHT_MODULE pointing at installed Playwright, QA_BROWSER pointing at Edge/Chromium, and QA_BASE pointing at the local preview. Run:

```sh
node tools/website_visual_qa.cjs
node tools/rebrand_mobile_qa.cjs
```

53 pages at 1280, 390 and 320 pixels: 159 settled screenshot views, no detected horizontal overflow, clipped checked CTAs, broken visible images or page script errors. Existing active/expired offer, hero sticky suppression and dismissal checks passed.

Nine pages at each mobile width using touch/mobile emulation: 18 further views passed notice wrapping, logo, overflow and language-selection checks. This is Chromium emulation, not physical iPhone/Safari certification.

Screenshots/results: /tmp/oneglp-rebrand-qa and /tmp/oneglp-mobile-qa. Manually inspected desktop homepage, mobile English, Arabic, Traditional Chinese and offer page captures.

SEO validation passes except the existing missing Apple campaign provider token. Campaign construction tests pass; attributable-download reporting is not ready without the real provider token.

## Before release

1. Decide whether to supply new OneGLP screenshots or retain explicitly labelled old-version screenshots. No image edits or new screenshot claims are approved in this draft. Some existing artwork contains the previous branding and "current screenshots" wording; resolve before release.
2. Supply/approve the social-sharing image. Existing screenshot-based social images are deliberately retained pending the asset decision; no placeholder image is published.
3. Native-language review of the new notices remains useful, but is not an indexing gate. All published translations must remain indexable. Longer continuity text is English-only; other locales receive their own translated short notice, not fallback English.
4. Recheck the public OneGLP App Store listing, current rating and purchase/data continuity. Owner has confirmed same-app continuity; no actual upgrade test was done here.
5. Verify the owner-reported OneGLP.app redirect; it was not changed or tested in this pass.
6. Obtain the real App Store campaign provider token if attribution is required. Never invent it.
7. Rerun sync/tests and rebuild sitemap dates on release day. Review against current main for intervening offer or site changes; do not deploy the branch blindly.

## Release and rollback

Keep this draft isolated until approved. No automatic rebrand date is configured. Once approved, review the explicit diff, exclude the original modified PNGs, commit and push only under a separate owner instruction. Use the macOS Keychain Git command. Verify GitHub Pages and live output afterwards.

Before release, rollback means leaving this isolated draft unused; the original checkout is unchanged. After a future release, revert the approved rebrand commit through a new reviewed commit, preserving unrelated updates and existing user assets.

## Name-change page and indexing update: 20 September 2026

The owner now requires every published translation to remain indexable, including translations without native approval. This supersedes the previous locale gates. The rule is recorded in AGENTS.md and data/locale-indexing.json and enforced by the generator and regression checks.

- Added /glpzy-is-now-oneglp/ and translated equivalents in Arabic, Simplified Chinese, Traditional Chinese, Spanish (Spain), German, French, Portuguese (Portugal), Japanese, Korean, Hindi, Italian and Dutch. These are 13 full pages; other locales retain their translated short rebrand notices. No English fallback page was added under other locale paths.
- Exact English headline: "GLPzy is now OneGLP". Supporting line: "Same app. New name."
- Exact introduction: "OneGLP is the new name for GLPzy, the GLP-1 tracking app developed by Steven Good. It uses the same App Store listing. The name change does not change your existing records or Premium purchases."
- Visible questions address the same app, reinstalling and existing Premium purchases. No App Store release date, new legal identity, altered treatment advice or new entitlement is claimed.
- Existing notices link to the matching full page where available; root English, /en/ and /en-gb/ use the canonical root English announcement.
- Page copy and translations live in data/rebrand-page.json. tools/build_rebrand_pages.py renders them without a JavaScript dependency. rebrand-page.css is scoped to the new pages; the homepage hero and screenshots are unchanged.
- App schema retains the same #software identity and App Store ID. alternateName identifies GLPzy; subjectOf links to the rebrand explanation. Static HTML and metadata clearly connect both names. No rating schema, testimonials, analytics or popups were added.
- New CTA campaign: rebrandPage / ct=rebrand_explanation. Example: https://apps.apple.com/us/app/glpzy-glp-1-tracker/id6761775005?ct=rebrand_explanation. Storefronts follow each language. The actual Apple provider token is still missing; this is not yet verified download attribution.
- All 1,317 HTML pages now have exactly one index,follow robots tag. The sitemap contains 1,293 self-canonical URLs. The 24 /en/ duplicates retain their root English canonicals and are not separate sitemap entries. Hreflang clusters contain every existing canonical translation and are reciprocal.
- Removed pre-existing duplicate canonical tags on 1,025 pages, including nonexistent slash-style canonical targets. Social og:url values now agree with canonical URLs.
- The indexation inventory, consolidation map and Search Console cleanup instructions now follow the new policy. Copy warnings are recorded separately and do not change indexability.

### Current verification

Passed:

```sh
python3 tools/build_rebrand_pages.py --check
python3 tools/rebrand_page_qa.py
python3 tools/locale_indexing_qa.py
python3 tools/sync_rebrand.py --check
python3 tools/rebrand_qa.py
python3 tools/sync_site_content.py --check
python3 tools/sync_website_copy.py --check
python3 tools/localisation_qa.py --all
python3 tools/website_growth_qa.py
node tools/offer_runtime_qa.cjs
git diff --check
```

The expiry contract also passed within seo_validate.py. The offer remains valid through 31 December 2026, with open-page browser expiry verified. No deployment workflow was changed.

Browser command (set PLAYWRIGHT_MODULE and QA_BROWSER as described above):

```sh
node tools/rebrand_page_visual_qa.cjs
```

78 settled screenshot views passed: 13 name-change pages and 13 homepages at 1280px, 390px and 320px. Checks cover horizontal overflow, clipped text, image loading, language menus, translated homepage links and browser errors. Mobile checks use touch-enabled Chromium emulation, not a physical iPhone. English desktop/mobile, Arabic desktop/320px, Traditional Chinese 320px and the English homepage at 390px were manually inspected. Evidence: /tmp/oneglp-name-page-qa/results.json and PNG screenshots alongside it.

The new page works with JavaScript disabled. Local HTTP requests using OAI-SearchBot, GPTBot and ChatGPT-User return identical HTML to ordinary requests, HTTP 200 and no X-Robots-Tag restriction. A read-only live check of https://www.glpzy.app/robots.txt with the OAI-SearchBot user agent returned HTTP 200 and User-agent: * / Allow: /. This checks user-agent access, not actual requests from OpenAI IP ranges or proof of indexing.

seo_validate.py: 19 of 21 checks pass. The two remaining failures are pre-existing mixed-English Thai/Vietnamese copy and the absent App Store campaign provider token. The mixed strings were confirmed in committed HEAD, not introduced by the rebrand. localisation_qa.py passes its current key-based rules, but does not cover every string that the broader SEO scanner catches. No locale was noindexed to hide either problem.

### Discovery limits and release actions

OpenAI documents OAI-SearchBot as its search crawler and GPTBot as a separate training crawler: https://developers.openai.com/api/docs/bots. Allowing access does not guarantee a crawl, search citation, ranking, training use or a date when answers change. The rebrand exists only in this local draft until release is approved.

After an approved deployment: verify public HTTP responses and Cloudflare bot/firewall rules, submit the updated sitemap in Google Search Console and Bing Webmaster Tools, inspect the homepage and name-change URL, and monitor old-brand/new-brand queries and referral evidence. Do not claim ChatGPT has adopted the name from a single generated answer. Keep the same App Store listing and align its public name/description through the owner's separate App Store release process. No Search Console, Bing, Cloudflare, App Store Connect, DNS or hosting changes were made here.

Native-language approval is still outstanding. The full name-change article currently covers the 13 languages listed above; the site's other translated notices and pages remain indexable. Existing screenshot/social artwork decisions and real upgrade-continuity testing remain owner release actions.

To rebuild this draft in order:

```sh
python3 tools/build_rebrand_pages.py
python3 tools/sync_rebrand.py
python3 tools/seo_gate_sitemap.py
python3 tools/seo_inventory.py
python3 tools/build_indexation_map.py
```

The original main checkout still contains only its 17 pre-existing modified PNGs. Nothing was staged, committed, pushed or deployed. Rollback before approval remains: leave the isolated draft unused; do not reset or overwrite the original checkout.
# Current Release Status

The owner approved publishing the website on 20 September 2026, ahead of the separate app release. See `docs/ONEGLP-WEBSITE-RELEASE.md` for the current 53-language coverage, App Store URL repairs, verification and remaining owner actions. The dated notes below are the earlier draft history, not the current release checklist.

# Google Search Console Cleanup Plan

Prepared: 2026-07-16

This report covers stale URLs and snippets found during the public search spot-check. Search results vary by location and account, so confirm each item in Google Search Console before taking action.

## Deploy First

1. Deploy the responsive image, duplicate-content, static-copy and sitemap changes together.
2. Confirm `https://www.glpzy.app/sitemap.xml` returns the new sitemap.
3. Submit the sitemap again in the `https://www.glpzy.app/` Search Console property.
4. Confirm the submitted sitemap reports 32 root English canonical URLs.

## Request Indexing for Current Canonical Pages

Use URL Inspection after the deployment. Test the live URL, confirm the selected canonical matches the page, then request indexing.

- `https://www.glpzy.app/`
- `https://www.glpzy.app/free-lifetime/`
- `https://www.glpzy.app/glp1-weight-dose-symptom-tracker.html`
- `https://www.glpzy.app/mounjaro-tracker-iphone.html`
- `https://www.glpzy.app/wegovy-tracker-iphone.html`
- `https://www.glpzy.app/zepbound-tracker-iphone.html`
- `https://www.glpzy.app/tirzepatide-tracker-iphone.html`
- `https://www.glpzy.app/semaglutide-tracker-iphone.html`
- `https://www.glpzy.app/glp1-dose-reminder-app.html`
- `https://www.glpzy.app/glp1-side-effect-symptom-tracker.html`
- `https://www.glpzy.app/glp1-weight-tracker.html`
- `https://www.glpzy.app/glp1-progress-photo-tracker.html`
- `https://www.glpzy.app/apple-health-glp-tracker.html`
- `https://www.glpzy.app/local-first-private-glp-tracker.html`

## Remove Stale English Duplicates Naturally

Public results exposed old `/en/` URLs during the review. These pages already use `noindex,follow` and point to the root English canonical. Keep returning `200`; do not redirect every locale URL to the homepage.

Inspect these representative URLs and request a recrawl:

- `https://www.glpzy.app/en/`
- `https://www.glpzy.app/en/index.html`
- `https://www.glpzy.app/en/mounjaro-tracker-iphone.html`
- `https://www.glpzy.app/en/wegovy-tracker-iphone.html`
- `https://www.glpzy.app/en/glp1-weight-dose-symptom-tracker.html`

Expected result: Google sees one `noindex,follow` robots tag and the matching root English canonical. Use Search Console's temporary removal tool only if an outdated result is causing immediate harm. A temporary removal does not replace `noindex` and recrawling.

## Clear Old Product Copy

The public homepage snippet still showed the previous photo allowance during the review. After deployment:

1. Inspect `https://www.glpzy.app/`.
2. Check that the live test contains “2 new photo uploads per month”.
3. Request indexing.
4. Check the result again after Google recrawls it. Google may choose different snippet text.

## Check Gated Locales

All non-root locales are now held outside search until native review is documented. The pages remain available through the language picker, but they use `noindex,follow`, do not appear in the sitemap and do not participate in hreflang clusters.

Use URL Inspection on representative pages after deployment:

- `https://www.glpzy.app/ko/mounjaro-tracker-iphone.html`
- `https://www.glpzy.app/ko/wegovy-tracker-iphone.html`
- `https://www.glpzy.app/ko/glp1-weight-dose-symptom-tracker.html`

Repeat this check for any locale URL that appears in Performance reports. Do not make a locale indexable until it is added to `data/locale-indexing.json` after native copy, medical wording and mobile checks.

## Consolidation Review

Use `reports/indexation-consolidation-map.csv` as the page-level decision record. Do not merge overlapping root medicine pages immediately.

1. Collect at least 28 days of query and canonical data.
2. Keep a page when it earns distinct relevant queries.
3. Improve a page when it receives impressions but has weak CTR.
4. Consolidate only when a page has no distinct demand and overlaps the mapped target.
5. Record the final decision in the map before changing redirects, canonicals or indexation.

## Validation After Recrawl

Check after 7 days and again after 28 days:

- Indexed pages: root English canonical URLs increase or remain stable.
- Excluded pages: `/en/` duplicates move to “Excluded by noindex” or disappear from results.
- Canonicals: no priority page is listed as “Duplicate, Google chose different canonical”.
- Snippets: no result mentions the previous six-photo allowance.
- Locales: gated pages move to “Excluded by noindex” and stop receiving new impressions.
- Sitemap: submitted and discovered URL totals match the generated indexable set.

## Do Not Do

- Do not request indexing for `noindex` locale pages.
- Do not add stale or redirected URLs back to the sitemap.
- Do not use temporary removals as the permanent fix.
- Do not promise that a recrawl will preserve the supplied meta description as the search snippet.

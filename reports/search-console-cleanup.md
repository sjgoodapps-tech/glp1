# OneGLP Search Console investigation

Audit date: 7 October 2026. Property: `sc-domain:oneglp.app`.

The owner authorised committing and pushing these indexing fixes on 7 October 2026, excluding the 17 existing screenshot asset edits. This report records the pre-release investigation and validation; public deployment and representative translated URL inspections are the release verification steps. The existing public sitemap was resubmitted successfully in Search Console. No URL removal or App Store change was made.

## Evidence and limits

The owner's four CSV exports contain the Page indexing snapshot dated 4 October 2026. The signed-in Safari session supplied the complete 43 canonical-disagreement examples, 160 discovered examples, four crawled examples, and the Performance CSV export. Evidence files remain in the owner's Downloads directory and `/private/tmp`; raw account exports are not added to the website repository.

| Page indexing status | URLs | Interpretation and action |
| --- | ---: | --- |
| Indexed | 1,213 | 78.3% of the 1,550 known URLs in this dated snapshot. This is not a current recount. |
| Discovered, currently not indexed | 160 | Mostly translated overview, privacy, private-tracker, support and terms pages. Check discovery and content; a crawl has not yet been recorded. |
| Google chose a different canonical | 43 | Includes 17 homepages, 13 translated private-tracker pages and regional English pages. Inspect current status before changing canonical signals. |
| Crawled, currently not indexed | 4 | Finnish and Greek homepages, Hebrew overview, and sitemap.xml. An XML sitemap does not need to appear as a search result. |
| Alternate with proper canonical | 114 | Expected duplicate URL handling can account for these entries. Do not apply blanket fixes or removals. |
| Redirect | 16 | Redirect destinations matter; redirecting source URLs do not need independent indexing. |

Fresh URL Inspection results differ from the older summary:

- `https://oneglp.app/`: indexed; declared and selected canonical are the inspected root URL. Latest reported crawl: 7 October 2026.
- `https://oneglp.app/fr/`: indexed.
- `https://oneglp.app/free-lifetime/`: indexed.
- `https://oneglp.app/press/`: indexed.
- `https://oneglp.app/bn/local-first-private-glp-tracker.html`: not indexed; Google selected `https://oneglp.app/bn/privacy.html`. The two pages shared their title and main content before this local fix.

These are representative inspections, not a claim that every excluded URL has been resolved.

## Local fixes

1. Align internal anchors with the declared canonical route. Home, Press and name-change links use directory URLs; /en/ navigation resolves to its root English equivalent. Queries, fragments, external links and asset references are preserved. Shared builders and copy synchronisation use the same normaliser.
2. Link the complete language directory from the English homepage footer. It previously had no incoming HTML anchor. All 1,386 canonical pages are now reachable from the homepage through static links.
3. Separate page intent across 51 non-English locales: translated tracker detail pages have tracker-specific titles; privacy pages have policy-specific titles; overview snippets describe the product/trust hub; private-tracker pages explain a practical workflow. This updates 204 pages. No different-page title or description collision remains within an individual locale.
4. Replace the private-tracker pages' repeated privacy grid with logging, progress, appointment-summary and account/local-backup cards. Existing translated feature copy is reused. The four cards use two desktop columns and one mobile column. New short titles and workflow text received an AI meaning/language review; native-speaker review is still outstanding.
5. Preserve exact external Press titles, review quotes/dates, the existing hero design and all 17 pre-existing screenshot asset modifications. Preserve every translated self-canonical, root English canonicals for /en/ aliases, reciprocal language links and every published translation in the sitemap.

The post-fix crawl audit finds zero navigational links to duplicate aliases and zero unreachable canonical pages. Five fragment-only links on /en/index.html deliberately remain local jumps within that document, rather than cross-page navigation.

## Live sitemap action

Search Console showed a successful sitemap last read on 30 September with 1,333 discovered URLs. The public `https://oneglp.app/sitemap.xml` now returns 1,386 canonical URLs, including 53 Press pages. Resubmitting this existing public sitemap returned **“Sitemap submitted successfully”** on 7 October. The discovered count still showed the prior 1,333 immediately afterwards; Google has not yet reported processing the resubmission.

Sampled HTTPS/www and former GLPzy-host redirects return 301 to OneGLP and preserve the page path. The public canonical homepage returns 200. No hosting change is needed for the tested migration paths.

## Search performance

The UI selected “Last 3 months”, but the available export covers only 22 September–4 October 2026: 13 days. Totals reconcile to **3 clicks, 268 impressions, 1.1% CTR and average position 13.1**. All three clicks were mobile; mobile had 148 impressions and desktop 120.

Clicked pages were the root homepage, Spanish Wegovy page and Turkish semaglutide page, with one click each. The visible query export has 50 rows and zero attributed clicks, so it does not identify the queries behind the three clicks. Do not interpret zero query-row clicks as zero site clicks.

Watch these pages after deployment rather than consolidating them on this small sample:

| Page | Impressions | Clicks | Average position |
| --- | ---: | ---: | ---: |
| /es-es/glp1-weight-dose-symptom-tracker.html | 20 | 0 | 7.1 |
| /pl/wegovy-tracker-iphone.html | 15 | 0 | 8.53 |
| /glpzy-is-now-oneglp/ | 12 | 0 | 6.17 |

Translated pages are earning impressions and clicks. Maintain those URLs and the former-name explanation. The sample is too small to establish a stable CTR trend or justify deleting, merging or de-indexing landing pages.

## Validation and remaining work

Final validation passed the crawl/discovery audit, all-page indexability check, 14 website-growth tests, Press checks, all 55 social-proof pages, and all 53 name-change pages. Copy synchronisation, both page builders and rebrand synchronisation report zero drift. `git diff --check` passed. The broad SEO validator passes its indexing and content checks, with the existing campaign-attribution failure described below.

- Run `python3 tools/seo_gate_sitemap.py`, then `python3 tools/locale_indexing_qa.py`.
- Run `python3 tools/search_discovery_qa.py`: checks canonical navigation, query/fragment preservation, complete reachability, translated metadata separation and source idempotence.
- Existing website-growth, Press, social-proof and name-change page checks cover the surrounding functionality. Static-copy and page builders must report zero drift.
- Twenty local responsive checks cover eight representative pages at 390px and 1440px, plus homepage, Free Lifetime, French private-tracker and Arabic private-tracker at 360px. No horizontal overflow or clipped main text was found. Existing text-only desktop hero spacing is retained under the project's hero-preservation constraint.
- The broad SEO validator has an existing unrelated failure: Apple's App Store campaign provider token is unset. Download links work; complete campaign attribution requires the owner's token. No credential was read or invented.
- The older full rebrand preservation check compares screenshot bytes against an earlier preservation commit and fails on the owner's pre-existing screenshot edits. These asset modifications were excluded from this work; the current rebrand synchronisation and name-change page checks are used for code validation.
- Release is explicitly authorised. Exclude the existing screenshot edits, verify the public HTML and sitemap after pushing, then inspect representative translated private-tracker URLs and request indexing where appropriate. Do not start “Validate fix” for content that is still only local.
- Google decides whether and when to crawl, select a canonical and index a page; sitemap acceptance and technical eligibility do not confirm future indexing.

Google guidance: [canonical URL consolidation and internal links](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls), [Page indexing report statuses](https://support.google.com/webmasters/answer/7440203?hl=en), and [requesting a recrawl](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl).

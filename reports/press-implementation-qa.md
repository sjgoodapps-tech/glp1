# Local Press implementation and QA — 2 October 2026

## Architecture and changes

The existing registry has 53 locales. Root English is canonical; `/en/` duplicates
canonicalise to the matching root page. Other locales retain their own prefix and
canonical. Copy is static HTML synchronised from keyed JSON resources. Footers are
stored in static pages with several template variants; there is no runtime footer
component. `overview.html` is the existing trust/about destination. The public
name-change family already explains the GLPzy to OneGLP continuity.

New source files: `data/press.json`, `data/website-press-copy.json`,
`tools/press_content.py`, `tools/build_press_pages.py`, `press.css`, `site-press.js`,
`tools/press_qa.py`, `tools/press_runtime_qa.cjs`, and `docs/PRESS.md`.
Existing copy and rebrand generators now share Press link synchronisation.

Generated changes: 53 canonical Press pages plus one `/en/press/` alias; 1,411
same-locale footer links across the final site; contextual links in overview and
existing rebrand pages; rebuilt sitemap and indexing report. Four pre-existing
truncated closing tags were repaired in `vi/overview.html`,
`vi/apple-health-glp-tracker.html`, `ur/foundayo-tracker-iphone.html`, and
`hu/wegovy-tracker-iphone.html` so their footers could be synchronised.

All tracked HTML was compared with the shared Press synchronisation applied to
the original HEAD content. No additional HTML changes were found. Existing image
changes were present before this task and were not edited. Primary navigation,
homepage hero design and screenshot assets were preserved. No commit, push or
deployment was performed.

## Translation keys and data separation

Seventeen keys were added in the established key-array resource format:
`site.nav.press`, `press.heading`, `press.description`, `press.continuity`,
`press.published`, `press.readArticle`, `press.type.interview`, `press.type.profile`,
`press.empty`, `press.context`, `press.checked`, `press.type.interviewFeature`,
`press.type.promotionFeature`, `press.article.monj.description`,
`press.article.monj.disclosure`, `press.article.startup.description`, and
`press.article.newmobilelife.description`. Metadata title combines the navigation label
with `| OneGLP`; metadata description uses `press.description`.

Translator context explicitly defines editorial coverage, protected current/former
brand names, unchanged external identity, same-app continuity and the link placeholder.
Article identity, URLs and dates live once in `data/press.json`; no editorial facts
are duplicated into locale translation resources. The dataset now contains the three owner-supplied verified records in the requested
order: Monj, start-up.ro, NewMobileLife / 流動日報. Every locale renders all three.
The exact original titles, URLs, supplied author, dates and publisher names are
preserved. Descriptions and Monj’s no-payment disclosure are owned translated copy.
Monj uses Checked 23 September 2026, separately from the two publication dates.
Rendering tests also use clearly synthetic samples outside the repository.

## Checks and results

- Static/HTTP Press QA: 53/53 locales pass, plus the English alias. Exactly one H1,
  localised title/description, valid canonical, full reciprocal hreflang including
  x-default, same-locale footer/context links, valid internal links and Press-to-Press
  language destinations were checked. Original article titles, authors, publisher
  names, URLs and dates remain unchanged across locales.
- Sitemap: 53 canonical Press URLs; no alias, duplicates or missing language versions.
  Final sitemap has 1,386 URLs, compared with 1,333 before this work.
- Global footer QA: 1,411/1,411 pages have one correct localised Press footer link.
- All-page indexing QA: passes with zero issues; every translation remains indexable.
- Browser QA: 159 populated real-page layouts (53 locales × 320/390/1280 pixels)
  pass without horizontal overflow or clipping of checked content. All 477 rendered
  cards retain their original identity and date. Arabic mobile layout was visually
  inspected; original article titles keep their own direction. Earlier scaffolding
  QA also checked 159 unpublished synthetic layouts.
- Mobile language-menu QA: 53/53 menus fit the viewport; changing to English
  stays on Press. Keyboard focus shows the existing visible 3px outline.
- Date runtime QA: 53 locale formats pass in bundled Node, including ISO preservation
  without Intl/locale support and with missing month data. The browser uses ISO
  date fallback for `or` and `pa`; it displays localised dates for the other locales.
- Press builder, rebrand builder and website-copy synchronisation checks: zero drift.
- Rebrand page QA and all-locale localisation QA: pass.
- Python compilation, JavaScript syntax and `git diff --check`: pass.
- Broader existing SEO validator: all checks pass except the existing App Store CTA
  provider-token readiness check. `data/product-facts.json` remains unchanged; this
  is not a Press routing or localisation failure.

The existing indexing report had 340 copy warnings/canonical notes; it now has 341,
with the added English Press alias canonical note. Existing unrelated copy issues
were not rewritten or used to remove translation URLs from indexing.

## Remaining work

- Obtain native review of the new translations. Structural and layout QA does not
  certify fluency or replace native editorial review.
- Resolve the existing CTA provider-token readiness issue separately if required
  for a later website release.

Implementation and all three supplied records are local and reviewable. No commit,
push, deployment or App Store Connect action was performed. Source verification
and the populated-page follow-up are recorded in `reports/press-records-qa.md`.

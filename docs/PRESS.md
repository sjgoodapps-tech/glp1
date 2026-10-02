# Maintaining the Press page

This is the existing static website, with 53 locales from `tools/seo_gate_sitemap.py`.
English is unprefixed; `/en/` copies canonicalise to root English. Other locales use
their existing lowercase prefix. Press follows the same directory-page convention
as the name-change page: `/press/`, `/de/press/`, and so on. The English alias is
`/en/press/`. Its canonical is `/press/`, and it is excluded from the sitemap.

`data/press.json` stores factual article records once. `data/website-press-copy.json`
uses the site's existing `keys`/`translations` JSON format for OneGLP-owned text,
including translator context and review status. The generator renders every string,
article and link into HTML; no client-side translation framework is introduced.

The first three verified records are Monj, start-up.ro, and NewMobileLife / 流動日報,
in that fixed display order. Their original titles, publisher names, supplied author
and URLs are locale-independent. Only OneGLP-owned descriptions, disclosure and UI
labels are translated. Temporary synthetic QA fixtures stay outside the repository
and never appear in generated Press pages.

## Adding verified coverage

Add one record to `articles`, with these fields:

- `id`: stable record identifier.
- `publisher`: exact publication name.
- `originalTitle`: exact published article title, unchanged in every locale.
- `url`: original HTTPS publisher URL, without a translated proxy.
- `author`: exact author name, if supplied by the publication.
- `publicationDate` or `checkedDate`: exactly one verified date in `YYYY-MM-DD` form.
  Checked dates retain a distinct translated Checked label and never become publication dates.
- `coverageType`: `interview`, `profile`, `interviewFeature` or `promotionFeature`,
  mapped to translated UI labels.
- `legacyBrand`: boolean indicating coverage under the GLPzy name.
- `language`: article's BCP 47 language tag, for accessible title language and isolation.
- `descriptionKey`: optional key for a OneGLP-owned description translated in all locales.
- `noteKey`: optional key for a factual OneGLP-owned explanation translated in all locales.

Check the publisher's original source before adding facts. Do not invent missing
authors, dates, endorsements or translated editorial titles. No article paragraphs,
publisher logos or ratings belong in the data. New coverage types or factual notes
require contextual translations in the existing press resource. The resource currently
has 17 keys. Monj uses the supplied historical Checked 23 September 2026 record;
start-up.ro and NewMobileLife use their publication dates. Preserve the Monj
no-payment disclosure, distinguish historical promotion coverage from a current
OneGLP offer, and do not assign a Taiwanese location to Traditional Chinese coverage.

## Rebuild and verify locally

Run from the repository root:

```sh
python3 tools/build_rebrand_pages.py
python3 tools/build_press_pages.py
python3 tools/sync_website_copy.py
python3 tools/seo_gate_sitemap.py
python3 tools/build_rebrand_pages.py --check
python3 tools/build_press_pages.py --check
python3 tools/sync_website_copy.py --check
python3 tools/press_qa.py
python3 tools/locale_indexing_qa.py
python3 tools/localisation_qa.py --all
node tools/press_runtime_qa.cjs
git diff --check
```

The shared sync helper updates all existing footer variants in place. It also adds
one contextual link to each existing `overview.html` (the trust/about destination)
and name-change page. The rebrand generator applies the same helper, so rebuilding
history pages preserves their Press links. Primary navigation and homepage heroes
are unaffected. Four pre-existing truncated footer endings are repaired by this pass.

`seo_gate_sitemap.py` remains the sole canonical/hreflang/sitemap authority. Press
does not maintain a separate locale array or hand-written language-family mapping.
Its language menu reuses the name-change header and links Press to Press for all
53 locales. All translations remain indexable, including unreviewed copy.

Dates use browser-native `Intl.DateTimeFormat` with UTC, while their exact ISO date
remains in `time[datetime]`. Without JavaScript, Intl, locale data or proper month
names, the ISO date stays visible. The tested browser used this fallback for Odia
and Punjabi; the bundled Node runtime formatted all 53 locales. Publisher names,
author names and original titles use `bdi`, with the article title's own language
and automatic direction rather than reversing editorial identity in RTL layouts.

For HTTP QA, start a local preview and run:

```sh
python3 tools/press_qa.py --base-url http://127.0.0.1:4198/
```

`--fixture-dir /private/tmp/oneglp-press-visual` optionally writes unpublished samples
outside this checkout for responsive and RTL inspection. The fixture HTML points
its assets at the local preview with a `base` element. Inspect real pages and samples
at 320, 390 and 1280 pixels through the Codex browser tools. Current browser results
are recorded in `reports/press-browser-qa.json`.

## Review status

New copy has contextual draft translations for all registered locales. Native
language review remains outstanding. Review the media meaning of press/coverage,
the September 2026 same-app explanation, and the contextual link sentence. Preserve
OneGLP and GLPzy, and do not translate external titles. Copy review never gates
indexability. Regional English/French variants share neutral wording; Spanish and
Portuguese variants have regional copy where relevant.

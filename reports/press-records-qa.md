# Verified Press records — local QA, 2 October 2026

The first three owner-supplied records are rendered in this fixed order across all
53 supported locales and the root-English `/en/press/` alias:

1. [Monj](https://monj.co.uk/oneglp/) — independent profile, Checked 23 September
   2026. The original H1 matches the supplied title. The publisher states it receives
   no commission, referral fee or payment; that disclosure is translated separately.
   The current source displays Checked 24 September 2026. The requested historical
   checked date is retained, with no invented publication date.
2. [start-up.ro](https://start-up.ro/glpzy-aplicatia-pentru-monitorizarea-tratamentelor-folosite-in-diabetul-de-tip-2-si-controlul-greutatii/)
   — interview / feature, 14 September 2026, Alexandra Ciornei. The Romanian original
   title, author and publication date match the source. Former GLPzy naming is
   explained in owned copy without changing the external title.
3. [NewMobileLife / 流動日報](https://www.newmobilelife.com/2026/07/08/glpzyglp-1%E8%A8%98%E9%8C%84-%E9%99%90%E6%99%82%E5%85%8D%E8%B2%BB-2/)
   — editorial / promotion feature, 8 July 2026. The original Traditional Chinese
   title, including its fullwidth space, and publication date match the source.
   Coverage is described as Traditional Chinese, with no Taiwanese attribution.
   The historical Lifetime Premium promotion is attributed to the article.

No publisher endorsement, recommendation, copied article prose, ratings or logos
were added. All three OneGLP-owned English descriptions match the supplied wording.
Shared factual identity lives in `data/press.json`; seven new owned-copy keys extend
the existing keyed translation resource to 17 keys in all 53 locales.

## Validation

- Static and HTTP QA check all 53 locale routes plus the English alias, exact
  editorial identity and order, original URLs, dates and date labels, translated
  descriptions and disclosure, footer/context links, metadata, reciprocal hreflang
  and canonical sitemap entries.
- Browser QA checks 159 populated layouts at 320, 390 and 1280 pixels: no horizontal
  overflow or checked-element clipping; all 477 rendered cards preserve identity.
  Arabic mobile layout was inspected visually with a normal viewport screenshot.
- Original titles use their source language and automatic direction inside `bdi`;
  publisher and author names remain isolated in RTL layouts.
- Browser locale-date data is unavailable for Odia and Punjabi; both retain visible
  ISO dates. All 53 locales format successfully in the bundled Node runtime. UTC
  and the exact `datetime` values are preserved.
- All-page indexing QA reports zero issues. The sitemap contains 53 canonical
  Press URLs among 1,386 site URLs; the English duplicate remains indexable with
  the root-English canonical and is omitted from the sitemap.
- Optional absent author/note fields produce blank lines without trailing whitespace,
  matching the central SEO generator; Press generation remains stable after rebuilding
  sitemap and reciprocal language links.

See `press-browser-qa.json` for individual browser results and
`press-implementation-qa.md` for the full implementation validation.

Native review of contextual draft translations remains pending. Structural and
browser checks do not certify native fluency. No commit, push, deployment or App
Store Connect operation was performed.

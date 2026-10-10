# OneGLP top 10 localisation implementation ledger

Updated: 10 October 2026.
Status: **INCOMPLETE: not a release approval**.
Feature branch: codex/website-top10-localisation-parity.
Baseline main SHA: 12c90f3738213acd383b9d25c3c76f0560a83314.
Never merge, modify main, or deploy without separate user approval.

## Target coverage

14 locale variants, 10 language groups: es-es, es-mx, de, fr, fr-ca, pt-br, pt-pt, ar, zh-hans, zh-hant, ja, ko, hi, it.

| Locale | Six complete P0 policy documents | Entire website / P1-P2 | Independent native/legal review |
| --- | --- | --- | --- |
| es-es | Source-section counts restored and checked | Incomplete | Not performed |
| es-mx | Source-section counts restored and checked | Incomplete | Not performed |
| de | Six abbreviated/out-of-scope pages | Incomplete | Not performed |
| fr | Six abbreviated/out-of-scope pages | Incomplete | Not performed |
| fr-ca | Six abbreviated/out-of-scope pages | Incomplete | Not performed |
| pt-br | Six abbreviated/out-of-scope pages | Incomplete | Not performed |
| pt-pt | Six abbreviated/out-of-scope pages | Incomplete | Not performed |
| ar | Six abbreviated/out-of-scope pages | Incomplete | Not performed |
| zh-hans | Six abbreviated/out-of-scope pages | Incomplete | Not performed |
| zh-hant | Six abbreviated/out-of-scope pages | Incomplete | Not performed |
| ja | Six abbreviated/out-of-scope pages | Incomplete | Not performed |
| ko | Six abbreviated/out-of-scope pages | Incomplete | Not performed |
| hi | Six abbreviated/out-of-scope pages | Incomplete | Not performed |
| it | Six abbreviated/out-of-scope pages | Incomplete | Not performed |

The six restored Spanish policy documents in each locale are privacy.html, data-rights.html, terms.html, medical-safety.html, methodology.html, support.html.

Verified structural baseline counts per variant: privacy 17 sections / 19 list items / 12 table rows; data rights 12 / 3; terms 6 sections; medical safety 11 sections / 20 list items; methodology 14 sections / 48 list items / 10 table rows; support 12 sections / 14 list items. These checks are necessary but not sufficient for semantic or legal acceptance.

## Completed source-first corrections

* Reconciled English terms and support to current non-renewing founding Lifetime Premium entitlement and oneglp.app, SHA 4ee9a01eac884db947012c25a6e1248f552a70c4.
* Corrected weekly Trulicity mistakenly grouped with daily treatment descriptions in English and Spanish, SHA 4bc74f4975600870c6bada12b37701bf5797574b.
* Corrected Spanish offer copy to state 31 December 2026 explicitly, SHA 936b4fc31b8c768978a128c7d77250b71e388e4f.
* Restored Spanish (Spain) full six policies via individual commits, with complete original official-reference links.
* Restored Spanish (Mexico) full six policies in commit bfe884674dd8e67faa15bbacfa0a713ad60eb757. Regional wording, language tag, metadata, App Store routing and references inspected.
* Added nonmutating tools/website_locale_parity.py audit, eight unit tests, and read-only feature-branch workflow .github/workflows/priority-localisation-review.yml.
* Fixed tools/search_content.py to preserve full Spanish privacy-policy metadata during site regeneration.
* Passing CI run: https://github.com/sjgoodapps-tech/glp1/actions/runs/38078899083 (eight tests; Spanish P0 gate, SEO/canonical/hreflang QA, existing localisation QA). The later Spanish-offer update passed https://github.com/sjgoodapps-tech/glp1/actions/runs/38079104213.

## Important outstanding work

1. The Spanish language group is NOT complete. P1/P2 commercial, medication, SEO and other pages need substantive review; navigation still has Subscription wording, and commercial Lifetime Premium pricing needs review.
2. Six English source SEO pages have no corresponding translations in any priority locale: apple-health-weight-loss-injection-tracker.html; glp1-dose-reminder-app.html; glp1-progress-photo-tracker.html; glp1-side-effect-symptom-tracker.html; glp1-weight-tracker.html; weight-loss-injection-tracker.html. There are 84 missing locale-page instances over 14 locales. English free-lifetime/index.html and languages.html are currently explicit exception candidates for separately justified decisions.
3. Twelve locales still have six abbreviated critical policy pages each: 72 outstanding documents. Restore complete sections without legal or medical omissions and validate meaning.
4. The existing site includes other non-English strings and dynamically generated app-store/offer copy requiring full source-key parity review. Preserve indexability and reciprocal hreflang.
5. Native-speaker, local legal, medical, browser visual 320/390 px, RTL, screen-reader and interactive runtime QA are NOT complete.
6. Full Spanish policies currently use explicit static HTML sections. Build a maintainable contextual translation source/provenance pipeline without letting old generators overwrite reviewed copy.

## Resume and acceptance

Resume on the same feature branch after verifying both branch and main remote SHAs. Complete Spanish (es-es and es-mx) across all pages and source resources before starting German. Review and correct Spanish as a language group, run the full site QA and commit its reviewed stages. Then repeat, committing and reviewing each group independently: German; French (FR/CA); Portuguese (BR/PT); Arabic; Chinese (Hans/Hant); Japanese; Korean; Hindi; Italian.

Commands when running in a worktree:
* python3 -m unittest discover -s tools -p test_website_locale_parity.py -v
* python3 tools/website_locale_parity.py --locale es-es --locale es-mx --gate-essential
* python3 tools/website_locale_parity.py --locale es-es --locale es-mx --gate
* python3 tools/locale_indexing_qa.py
* python3 tools/localisation_qa.py --all
* python3 tools/seo_gate_sitemap.py (run only when actively rebuilding branch sitemap and hreflang)

The full --gate should remain red until missing English-only pages are translated or documented as justified exceptions; do not disable requirements to manufacture green results.

Before final release, verify every applicable page and claim, mobile layout, accurate translations, source links, safety and legal notices, then obtain independent native/legal review and explicit owner approval. Green structural CI alone is not acceptance. Live website and main must remain unchanged.

# OneGLP priority website localisation: implementation and test ledger

Updated 11 October 2026. **NOT A PRODUCTION RELEASE APPROVAL.** 
Working branch: `codex/website-top10-localisation-parity`. Verified unchanged main: `12c90f3738213acd383b9d25c3c76f0560a83314`.
GitHub Actions remain owner-disabled; no Actions workflow was started or modified.

## Reconciled scope and baseline

Target: 14 locales (es-es, es-mx, de, fr, fr-ca, pt-br, pt-pt, ar, zh-hans, zh-hant, ja, ko, hi, it). Six critical policy documents and six incremental SEO landing families per locale.

Previous source-status summary: seven locales (Spanish ES/MX, German, French FR/CA, Portuguese BR/PT) had policy reconstructions and all six SEO families added. Their full translation quality has NOT been independently accepted. Earlier rows listing all their policy pages as abbreviated and all 84 SEO pages absent are no longer current. These seven statuses are historical-source reported, not new native-review approvals.

As of the six Arabic commits below, eight locales have source-structure coverage on all six priority policies; seven locales have six additional SEO families. Six locales (Chinese Hans/Hant, Japanese, Korean, Hindi, Italian) still require their six policy restorations. Seven locales (those six plus Arabic) still lack all six additional SEO families.

Remaining based on the verified/reported inventory: **36 priority policy restorations + 42 SEO page expansions**. These counts do not include any additional semantic, marketing, medicine, navigation, metadata or accessibility defects revealed by the full audit.

## 11 October 2026 Arabic P0 commit ledger

| Page | Commit SHA | Source sections | Scope | Native/legal approval |
|---|---|---:|---|---|
| ar/privacy.html | `c1a65e7ae620a6ba3e89303959ce8dc2672ca52e` | 17 | Arabic policy MAIN, metadata | Pending |
| ar/data-rights.html | `629b7fe338d1b73c385825a4f8d760c114da7083` | 12 | Arabic data-rights MAIN, metadata | Pending |
| ar/terms.html | `c9e80ac5d12848a6bb21d8fa7ca70ec2a600aab7` | 6 | Arabic legal/trader MAIN, metadata | Pending |
| ar/medical-safety.html | `2b55596e286656a3ae7c311fb939bf81f5ea4174` | 11 | Arabic safety MAIN, 15 external references | Pending |
| ar/methodology.html | `7999a156d802a7c75e5db5cae1228e31f0ad821f` | 14 | Arabic methodology MAIN, 17 references, formulae | Pending |
| ar/support.html | `9d90ad4cd1be07832dbac70138d9bd0b4c425d97` | 12 | Arabic support MAIN, metadata | Pending |

At each commit: branch HEAD lease, main SHA, source English blob, previous Arabic blob, unique MAIN block, section/paragraph/list/table counts, external references, key safety phrases and Arabic title/description were checked before writing. Each commit fast-forwarded only `codex/website-top10-localisation-parity`. Full native fluency, safety meaning, browser or regulatory correctness was not thereby proved.

## Tests and open quality gates

| Gate | Result as of 11 October 2026 |
|---|---|
| Saved Arabic fragment and installer regression suite | PASS 63/63 (fixture tests, Linux, Python 3.13.5) |
| Six Arabic against pinned English source | PASS structural tag counts, links and required literals; GitHub source blobs matched |
| Feature-only GitHub commit/ref safety | PASS six sequential fast-forward commits |
| Existing repository unit/integration tests against complete checkout | NOT RUN (Git clone blocked by DNS in this environment) |
| Full 14-locale content and semantic parity | NOT PASSED |
| Sitemap rebuild, canonical, reciprocal hreflang site-wide QA | NOT RUN after Arabic policy edits |
| Live browser widths 320 px and 390 px | NOT RUN |
| RTL layout and runtime retranslation | NOT PASSED |
| Accessibility and screen-reader interaction | NOT RUN |
| Independent native-speaker review | 0/14 approved |
| Independent legal/medical review | 0/14 approved |
| Deployment/main merge | NOT AUTHORISED and NOT PERFORMED |

## Source issues requiring resolution

See `docs/TOP10_LOCALISATION_SOURCE_REVIEW_FINDINGS_2026-10-11.md`. In particular, the English medical-safety page embeds editorial indexing text; English Apple Health scope descriptions conflict; Arabic shell and language-picker copy still contains English and subscription terminology. Copy was not silently corrected without verifying shipping app behaviour. Regeneration protection remains incomplete.

## Remaining actions

Complete each of Arabic's six SEO page families, then Chinese Hans/Hant, Japanese, Korean, Hindi and Italian with six policy restorations plus six SEO families each. Add source/provenance data and automated source consistency gates. Finish all 14 locale marketing, medicine, SEO, metadata, links, accessibility and language QA. Run all project tests in an authenticated local complete checkout with GitHub Actions disabled, record failures and correct them. Keep every translation page indexable; preserve `main`, `.github` configuration, current hero and image assets, and do not deploy without explicit release sign-off.

---
## Historical ledger (superseded where contradictory above)

# OneGLP top 10 localisation implementation ledger

Updated: 10 October 2026; resumed after cross-turn branch verification.
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

## Progress on resumption

- Verified main remains at SHA 12c90f3738213acd383b9d25c3c76f0560a83314 and the feature branch advanced independently; no main changes.
- Spanish (Spain) static pages and Spanish (Mexico) pages were synchronised to the corrected Premium navigation and non-renewing entitlement wording in separate commits ffe17e685cbf2108e808e1d5af15bb45edbcd631 and b984c4e5e3f251b35dfdda66a7657e0d3459f180.
- Fixed localisation correction processing in 1c517ef2a10d4029431ebdbc542f1ab8f8a7ea63. Extended the founding-offer year to all 14 target locales in de3c8a7f6f99d2bbe85b56b8b1e587174381c301. The latter is a narrow correction, not full parity for those languages.
- CI was successful at https://github.com/sjgoodapps-tech/glp1/actions/runs/38079984786 .
- Checked both batches of all 26 Spanish (Spain) static HTML pages for unintended visible Subscription wording, obsolete glpzy.app references and the inaccurate daily Trulicity grouping. Expected safety-negation and non-subscription statements are preserved.
- Added targeted Spanish P0 semantic invariants to the regression suite at 194c45258f42d2bedbf0389e588dac99c7983af5: 24/12-month data retention, GDPR articles 6/9, weekly Trulicity, non-renewing Premium, and canonical URLs.
- CI for that last change: https://github.com/sjgoodapps-tech/glp1/actions/runs/38080359825 . **Do not call the latest change validated until this run has concluded successfully.**

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


# OneGLP Screenshot Refresh

Date: 20 September 2026

Status: local draft. Not committed, pushed or deployed. App Store metadata and app behaviour were not changed.

## Result

- Refreshed 1,304 HTML pages, including stylesheet-version updates. Audited all 1,357 HTML files for legacy screenshot references.
- Selected 15 genuine screenshots from `/Users/utm/Desktop/SCREENS_5.0/EN/`. The originals are stored unchanged under `assets/screens/v5/en/`.
- Generated 120 responsive assets: AVIF and WebP at 360, 720, 1080 and 1320 pixels. Published image fallbacks use WebP rather than the large PNGs.
- The homepage and offer hero use one shared frame. Desktop shows Today, before/after photos and a smaller weight chart. At 390px and 320px, only Today and photos appear. The two main image windows have equal heights. The desktop-only chart has an empty mobile picture source so it does not download as a hidden hero image.
- Captions are real HTML, not text painted into screenshots. Captions, alt text, language notes and enlargement links are maintained centrally for all 53 locale entries.
- All translations remain indexable. The sitemap still contains 1,333 canonical URLs; `/en/` duplicates retain root English canonicals.
- All 17 pre-existing modified PNGs are byte-for-byte unchanged from the pre-task snapshot and remain unstaged. Their committed versions were used in the separate live-equivalent preview.

## Image Selection

| Page purpose | Screens used |
| --- | --- |
| Homepage and offer hero | Today, before/after photos, weight chart; two on mobile |
| Homepage screenshot section | Today, before/after photos, weight chart, Log today, calendar, clinician PDF summary |
| General GLP-1 tracker | Today, Log today, before/after photos, clinician PDF summary |
| Mounjaro | Today, dose history, before/after photos |
| Wegovy, Zepbound, semaglutide | Log today, weight chart, before/after photos |
| Tirzepatide | Medicine list, dual chart, Estimated Exposure |
| Dose reminders | Today hero; Log today, dose history, calendar, medicine supplies |
| Symptoms | Log today, clinician PDF summary; neither is labelled as a symptom-entry form |
| Weight | Weight chart, dual chart, body measurements |
| Progress photos | Photo selection, before/after editor, comparison slider |
| Medical safety and methodology | Calculation methods and references |
| Privacy, terms, support, data rights, overview and Apple Health | Text-only hero; unrelated legacy screenshots removed |

The supplied set does not show Apple Health permissions, backup/restore, reminder setup or widgets. Those features are not illustrated with unrelated screens. Two calculator screens, the second medicine-list screen and two video-reel stills were not used. A static video image is not presented as a working video.

No displayed legacy screenshot URLs remain. Old files are retained in the repository, not deleted or overwritten. Current social metadata still uses the OneGLP brand icon, not a legacy app screenshot.

## Exact English Image Copy

Hero captions:

- "Next dose, weight and daily records."
- "Compare photos and choose what to share."
- "Weight records over time."
- "App screens shown in English."

Screenshot captions:

- "See your next dose, weight and daily records."
- "Make a before-and-after image. Cover faces and choose what to share."
- "Review weight records and recorded dose stages on one chart."
- "Choose what to record: a dose, weight, symptoms, nutrition, a photo or measurements."
- "Review dose days, weight entries and photos by date."
- "Review recorded doses and injection sites."
- "Choose two photos to compare, save or share."
- "Compare two photos with a slider."
- "View weight records with an Estimated Exposure overlay."
- "Review historical Estimated Exposure and a run-off projection."
- "Review recorded body measurements and changes over time."
- "Review a PDF summary of doses, weight, symptoms and body measurements."
- "Record medicine supplies and manage reorder reminders."
- "Browse medicine names during setup."
- "Read the app's calculation methods and medical references."

English image alt text uses `OneGLP: ` followed by its screenshot caption. Translated pages use the corresponding translated description, not an English fallback. The translated descriptions are deliberately short; they do not add unverified feature claims.

Other changed image-adjacent copy:

- Section heading: "OneGLP screenshots".
- Core tracking heading: "Record doses, weight, symptoms and photos".
- Image link: "Enlarge image". It opens the full-size WebP; browser Back returns to the page.
- Figure safety wording where needed: "Estimated Exposure is a personal tracking estimate, not measured blood concentration. Do not use it to guide dosing."

Existing product facts, medical warnings, legal text, purchase claims, campaign destinations, offer deadline and dismissal keys are preserved. Translated safety warnings remain in their page text.

## Files

- `data/screenshot-manifest.json`: approved source files, dimensions, page mappings, captions and schema descriptions.
- `data/screenshot-copy.json`: keyed screenshot copy for every published locale.
- `tools/refresh_screenshots.py`: targeted static HTML updates, responsive pictures, translated captions and hero composition.
- `tools/build_responsive_images.py`: one screenshot map for homepage and SEO assets.
- `tools/seo_priority_pass.py`: page-specific figures and image schema from the same map.
- `tools/screenshot_qa.py` and `tools/screenshot_visual_qa.cjs`: static and browser regression checks.
- `tools/seo_validate.py`, `tools/rebrand_qa.py`, `tools/sync_rebrand.py`: updated expectations and independent CSS versioning.
- `styles.css`: framed responsive hero and screenshot figures.
- Root and locale HTML: image references, captions, alt text, image loading, relevant schema and stylesheet references.
- `assets/screens/v5/en/`: 15 new source PNGs. `assets/responsive/seo-oneglp-v5-*`: 120 derived files.
- `reports/image-pipeline-report.md`, `reports/localisation-noindex-report.md` and this report.

## Verification

The clean preview at `/tmp/oneglp-v5-live-equivalent` contains the current draft with only the 17 protected PNGs replaced by their committed HEAD versions. The working checkout was not altered by that substitution. A case-sensitive server also preserves the declared App Store compatibility routes.

Passed:

- Static screenshot QA: 1,357 HTML files, 53 locale entries, 15 originals and 120 responsive variants; no legacy references, missing files, copy drift or changed protected PNG hashes.
- Browser QA: 95 routes at 1280x900, 390x844 and 320x812, DPR 2; 285 checks. No horizontal overflow, clipped new captions, broken visible images, unexpected robots directives or desktop hero-chart loads on mobile.
- Routes include English homepage, offer, all 12 priority SEO pages, safety, methodology, privacy, support, all 53 locale homepages, plus Wegovy and medical-safety pages in 12 representative locales.
- Active/expired offer states, a page left open across midnight, banner dismissal and reload, Portuguese-to-English page switching and full-size image links passed at all three widths.
- Additional framed-hero checks: 18 locale/width combinations; three desktop/two mobile screenshots; equal Today/photo frame heights; no sticky CTA overlap at seven scroll positions.
- Manually inspected settled English, Arabic, Portuguese, Simplified Chinese and Traditional Chinese screenshots, including the framed hero, offer page and selected screenshot sections. Browser automation is not native-language approval.
- Content synchronisation, localisation QA, indexability/hreflang/canonicals, 14 growth regression tests, rebrand identity/preserved-assets QA, rebrand-page QA, offer-runtime QA, offer-expiry contract and whitespace checks passed.

The full SEO validator is **not completely green**: its only failing check is the existing missing Apple campaign provider token (`pt`). App Store links still work, but reliable App Store campaign attribution is not ready. No token was invented and this pass does not change that configuration.

The localisation report still has the same 340 copy warnings or canonical notes as HEAD. These include earlier translation wording and missing upgraded answer modules. The dedicated localisation regression suite passes; neither result is a claim that every translated sentence is native quality.

### Reproduce

```sh
python3 tools/refresh_screenshots.py --check
python3 tools/screenshot_qa.py --protected-snapshot /tmp/oneglp-image-refresh-protected.json
python3 tools/sync_site_content.py --check
python3 tools/sync_website_copy.py --check
python3 tools/sync_rebrand.py --check
python3 tools/localisation_qa.py
python3 tools/locale_indexing_qa.py
python3 tools/rebrand_page_qa.py
python3 tools/website_growth_qa.py
python3 tools/validate_offer_expiry.py
/Users/utm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/offer_runtime_qa.cjs
python3 tools/seo_validate.py
git diff --check
```

`seo_validate.py` intentionally exits nonzero until a valid Apple provider token is supplied. For the protected-PNG check, the snapshot is local QA evidence, not a file to publish.

Start the clean preview from `/tmp/oneglp-v5-live-equivalent`:

```sh
python3 tools/preview_rebrand.py --port 4202
```

Run the browser suite from the website repository:

```sh
PLAYWRIGHT_MODULE=/Users/utm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright \
QA_BROWSER='/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge' \
QA_BASE=http://127.0.0.1:4202/ \
/Users/utm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/screenshot_visual_qa.cjs
```

Run preserved-assets rebrand QA in the clean preview, not the intentionally dirty original PNG checkout:

```sh
cd /tmp/oneglp-v5-live-equivalent
GIT_DIR='/Volumes/My Shared Files/999_Projects/GLPzy_Website/.git' \
GIT_WORK_TREE=/tmp/oneglp-v5-live-equivalent python3 tools/rebrand_qa.py
```

## Local Load Comparison

Three cold runs per width/version, Edge, DPR 2, 100ms latency, 200,000 bytes/second download and 4x CPU throttling. These are local lab results, not Lighthouse scores or field Core Web Vitals. Small timing differences should not be treated as a forecast.

| Width | Old hero bytes | New hero bytes | Old median LCP | New median LCP | New image top |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1280 | 53,921 | 76,021 | 1.468s | 1.428s | 199px |
| 390 | 36,963 | 60,554 | 1.168s | 1.472s | 537px |
| 320 | 22,576 | 34,535 | 1.168s | 1.356s | 561px |

The new mobile images start about 210px earlier at 390px and 226px earlier at 320px. The trade-off is more image data than the old single collage. Maximum observed CLS in these comparison runs was 0.023. No download-conversion improvement is claimed without measurement.

## Evidence

- Draft: `http://127.0.0.1:4201/index.html`.
- Final hero screenshots: `/tmp/oneglp-v5-hero/home-1280.png`, `home-390.png`, `home-320.png`.
- Settled page screenshots and results: `/tmp/oneglp-v5-visual-qa/` and `results.json`.
- Framed-hero geometry/sticky results: `/tmp/oneglp-framed-hero-qa.json`.
- Controlled comparison: `/tmp/oneglp-image-load-comparison.json`.
- Protected PNG hashes: `/tmp/oneglp-image-refresh-protected.json`.
- SEO output: `/tmp/oneglp-v5-final-seo-qa.txt`.

## Remaining Owner Decisions

- Review the framed hero and supplied face-cover style. Emoji face covers are part of the original screenshot; no source pixels were changed.
- The supplied Today/PDF and weight screenshots show different total weight changes. Captions do not claim a specific result, but consistent example records would make a future capture set clearer.
- Provide native-language approval when available. The screenshots themselves remain English, explicitly labelled in each language.
- Supply missing Apple Health, privacy/backup and reminder/widget screenshots before illustrating those specific controls.
- Supply Apple's campaign provider token for attribution. Recheck the existing US rating before release; this image-only pass did not reverify the rating or download total.
- No physical iPhone/Safari test, field-performance study, App Store update or live deployment was performed.

## Rollback And Release

No live rollback is needed: nothing was deployed. To discard the draft, first preserve a patch and the new untracked assets, then selectively undo this pass's HTML/CSS/data/tool changes. Leave the 17 pre-existing modified PNGs alone. Do not use a whole-worktree reset or clean.

Suggested next prompt:

> Review the final OneGLP screenshot-refresh diff and reports/screenshot-refresh.md. Confirm the framed three-image desktop and two-image mobile hero, page-specific screenshots and translated captions. Recheck the US App Store rating and report the missing campaign provider-token limitation. Preserve the 17 existing modified PNG assets. Do not commit, push or deploy until I approve the release.

# OneGLP Website Release

Prepared on 20 September 2026. The owner has approved publishing the website before the app's name-change release. App Store Connect, DNS and the canonical domain are not being changed.

## Website Changes

- OneGLP display branding, titles, descriptions, sharing metadata and app schema across the site. The previous name is retained in the rename explanation and app `alternateName`.
- 53 translated, static name-change pages with reciprocal language links, self-canonicals and homepage links. All translations remain indexable. English `/en/` duplicates retain root English canonicals.
- Shorter English homepage heading: "Private GLP-1 tracker for iPhone". One linked "GLPzy is now OneGLP." notice replaces the repeated homepage continuity paragraph. Hero layout and screenshots are unchanged.
- "Get OneGLP" buttons before and after the announcement FAQs, translated in every locale. Separate campaign names: `rebrand_explanation` and `rebrand_explanation_bottom`.
- Approved OneGLP icon used for social sharing. Existing PNGs are unchanged; `assets/oneglp/social-icon.png` is a new copy of the supplied 512px icon.
- Thai and Vietnamese corrections for download labels, history, export and backup copy. Both localisation and SEO QA now reject the known mixed-English fragments.
- Support and privacy navigation on those pages no longer sends visitors to the homepage.
- The offer remains free through 31 December 2026. No second expiry system was added. App Store pricing and existing entitlements are outside the website's control.

## Existing App Store URLs

`data/app-store-website-urls.json` records the 54 exact website paths in the owner's App Store Connect evidence. Ten mixed-case paths currently fail on the public site. Lowercase counterparts exist. This Mac's case-insensitive filesystem can hide this failure.

The ten compatibility sources under `compatibility/` use Jekyll front-matter permalinks to generate the exact mixed-case paths during the existing branch-based GitHub Pages build. They use an immediate HTML redirect, a same-language fallback link and the lowercase canonical URL. These are not HTTP 301 redirects. They require the existing Jekyll build; do not add `.nojekyll` without replacing this routing mechanism.

The destinations keep their content indexable. The aliases are not additional sitemap entries. Domain redirects remain unchanged. `.glpzybackup`, app ID 6761775005, existing purchase identifiers and working GLPzy URLs are preserved.

## Verification

Completed before release preparation:

- 318 homepage/announcement browser views: 53 languages at 1280px, 390px and 320px. Language menus, overflow, image loading, static indexability and no-JavaScript access passed.
- 162 App Store-linked page views: all 54 paths at the same widths. The ten intentional redirects also passed without JavaScript. Support contact routes and linked support/privacy pages passed.
- Final 159-view priority-page regression passed, including active/expired offers, open-page expiry, saved banner dismissal, language selection and mobile CTA overlap.
- Manual settled-screenshot review includes English desktop and mobile, Traditional Chinese at 320px and Urdu at 390px.
- Fourteen focused source-copy and campaign regression fixtures passed.
- `sync_site_content.py --check`, `sync_website_copy.py --check`, `rebrand_page_qa.py`, `rebrand_qa.py`, `localisation_qa.py --all`, `validate_offer_expiry.py`, `offer_runtime_qa.cjs` and `offer_pages_build_qa.cjs` passed.
- Jekyll 3.9.5 safe-mode build of the compatibility sources passed. `build_app_store_aliases.py --check --built-dir /tmp/oneglp-jekyll-alias-output` confirms all ten case-sensitive output paths and matching HTML.
- SEO validation: 20/21 checks pass. The only failure is the missing Apple campaign provider token. CTA wiring passes for 142 labelled priority links with `--allow-unconfigured`; no download attribution is claimed.
- 1,333 canonical sitemap URLs; 1,357 content HTML pages with all translations indexable. The ten generated compatibility destinations are separate redirect pages.
- Original checkout still has exactly its 17 pre-existing modified PNGs, unstaged. Draft preservation QA compares all committed image bytes and hero image markup with the original commit.

Live verification results are reported in the release conversation. Local evidence is under `/tmp/oneglp-conversion-qa`, `/tmp/oneglp-app-store-urls-qa` and `/tmp/oneglp-final-growth-qa`.

## Owner Actions and Limits

- Supply an Apple-generated campaign URL/provider token. Store its real `pt` value in `data/product-facts.json`, rebuild the name-change pages and run `sync_site_content.py`. Both `ct` and `pt` are needed before claiming Apple campaign attribution works.
- Decide when to replace the screenshots. Existing screenshots still show GLPzy and are intentionally preserved.
- Complete native-language review. Automated checks catch known errors and layout problems; they do not certify all 53 translations. Copy warnings remain reported, never converted into noindex restrictions.
- App Store name, screenshots and public release remain the owner's separate app release. No App Store metadata is edited by this website release.
- Search engines decide indexing and ranking. Allowing crawlers and explaining the rename does not guarantee ChatGPT inclusion or model training. Search Console/Bing submission and recrawl monitoring are still owner actions.
- Browser offer expiry is automatic, including open pages. Scheduled builds and crawler refreshes can lag. Website expiry does not change App Store pricing or entitlements.

## Repeatable Release Checks

```sh
python3 tools/build_rebrand_pages.py --check
python3 tools/build_app_store_aliases.py --check
python3 tools/sync_site_content.py --check
python3 tools/sync_website_copy.py --check
python3 tools/rebrand_page_qa.py
python3 tools/rebrand_qa.py
python3 tools/website_growth_qa.py
python3 tools/localisation_qa.py --all
python3 tools/locale_indexing_qa.py
python3 tools/validate_offer_expiry.py
node tools/offer_runtime_qa.cjs
node tools/offer_pages_build_qa.cjs
node tools/campaign_runtime_qa.cjs
python3 tools/seo_validate.py
python3 tools/cta_campaign_audit.py --check --allow-unconfigured
git diff --check
```

For browser checks set `PLAYWRIGHT_MODULE`, `QA_BROWSER`, `QA_BASE` and `QA_OUTPUT` to local paths, then run `tools/rebrand_page_visual_qa.cjs`, `tools/app_store_urls_qa.cjs` and `tools/website_visual_qa.cjs` with Node. The case-sensitive local preview is `python3 tools/preview_rebrand.py --port 4198`.

After deployment, run the exact URL check, which follows HTTP and immediate HTML redirects and checks the final path, title and language:

```sh
python3 tools/check_app_store_website.py --output /tmp/oneglp-live-app-store-urls.json
```

Recheck the homepage, announcement, both Chinese support links, sitemap and assets using ordinary live URLs, not only cache-busting URLs. Verify the GitHub Pages build commit as well as HTTP content.

## Rollback

Before committing, keep the original checkout unchanged and leave the isolated draft unused. After publishing, revert the release commit in a clean worktree, review the revert, then push an approved rollback. Do not use a hard reset or include the 17 unrelated PNG modifications. Do not delete or change the existing OneGLP-to-GLPzy domain redirect as part of a website-content rollback.

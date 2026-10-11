# Localisation audit integrity checkpoint

Date: 11 October 2026. Status: tooling checkpoint, not translation acceptance.
Branch: `codex/website-top10-localisation-parity` only.
Verified starting HEAD: `0f8a8bdb2256ff090498c2c1e84eab354b69e4ac`.
Verified starting main: `12c90f3738213acd383b9d25c3c76f0560a83314`.

## Verified defects and corrections

- `pages_present` counted absent exception pages as present. It now counts actual files and separately reports `exception_pages_not_present`. Present + required missing + absent exceptions reconciles to the English inventory.
- A set comparison accepted duplicate or reordered policy section numbers. The comparison now preserves order and multiplicity, including Arabic-Indic numerals.
- Missing English essential source pages could permit a false pass. Source errors now make both command-line gates fail.
- Missing or changed outbound reference links were not checked. Essential documents now preserve the English source's outbound reference URLs. Translated labels are allowed; internal navigation and mail links are excluded.

## Local evidence

Environment: Linux, Python 3.13.5; standard library only.
The retrieved original `tools/website_locale_parity.py` was reconstructed locally and verified against Git blob `10f82339b966b8808a04c29e04f642451238c9b9` before editing.

Command: `python -m unittest discover -s tools -p test_website_locale_parity_integrity.py -v`.
Before correction: 18 tests run, 7 failures, 4 errors.
After correction: all 18 tests pass.
`python -m py_compile tools/website_locale_parity.py tools/test_website_locale_parity_integrity.py` passes.

Tested file blobs:
- `tools/website_locale_parity.py`: `7f885e98d3ddb23beb2a0f77158f34a74af51a82`.
- `tools/test_website_locale_parity_integrity.py`: `2a9eccf7e8d3b7bc2f9a139ad8684470cedaefaf`.

## Limits

These are deterministic fixture tests, not a run against a complete website checkout. Direct cloning and public archive retrieval were unavailable in this session. The existing integration suite, all-locale structural audit, sitemap/hreflang regression, actual mobile layouts, screen-reader checks, native-language approval and legal approval have NOT been completed by this checkpoint. No page translation is certified here. GitHub Actions settings and workflow files were not changed, no workflow was started, and main was not updated.

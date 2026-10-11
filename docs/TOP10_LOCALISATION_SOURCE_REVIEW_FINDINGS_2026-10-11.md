# Source review findings and unresolved acceptance items

11 October 2026. These are source-review findings, not a full legal, clinical or app-code audit.

## S01: Internal editorial and indexing instructions appear in public medical copy

Source: English `medical-safety.html`, section 10, at `91c8ffc`.
The source contains conditional Foundayo editorial instructions, references to noindex supplementary pages, and language about core sitemap targets. The repository AGENTS.md separately requires published translations to remain indexable.

Verified fact: the source contains this wording. Inference: it reads like internal publishing instructions rather than finished user-facing safety information. The exact status of each medicine page's robots/canonical/sitemap treatment has NOT been re-audited here; do not infer a specific live indexing failure from this textual inconsistency alone.

The Arabic draft preserves the source meaning and references; it does not silently resolve this issue. Before accepting translations, replace inappropriate source editorial instructions with verified, user-facing product information and then propagate the approved source change to all affected locales. Do not remove URLs from the sitemap or hide translations to make tests green.

## S02: English Apple Health descriptions differ

Sources: `privacy.html` sections 3/8; `data-rights.html` section 7; `support.html` section 9; `methodology.html` product facts.

The privacy/methodology pages describe a broader read-only context including glucose and additional nutrition information. The support page uses limiting language with a narrower list. The data-rights page has another earlier list. This is a source consistency issue, not proof that any specific capability exists or does not exist in the shipping app.

The Arabic drafts retain the source statements. Verify actual shipping permissions and capabilities against the authoritative app release before changing English and all translations together. No iOS-source/binary verification was performed by this checkpoint.

## S03: Arabic page-shell work remains

The retrieved Arabic privacy shell contains `settings.tile.subscription.title` rendered as الاشتراك, plus English accessibility labels for home, navigation and language search. The new policy MAIN fragments do not cover the shell or site-i18n runtime resources.

Complete static and dynamic Premium wording together, localise accessibility labels, and test rehydration/regeneration. Do not remove localisation hooks without understanding runtime dependencies. Retain the hero design and screenshot assets.

## S04: Regeneration protection is partial

The retrieved `tools/search_content.py` explicitly preserves full privacy metadata when `data-english-section="1"` is present. The drafts include numbered section attributes. This does not prove protection against every other generator or runtime script.

Before completion, add durable source/provenance records and regression tests for generation without translation loss. Re-running an existing generator must not restore abbreviated policies or overwrite reviewed terminology.

## S05: Source-reference fidelity is not current-reference validation

The drafts preserve outbound reference URLs from the source exactly. This is important for provenance, but does not establish that all linked labels are current, correctly targeted, available, or sufficient for every claim. No linked medical PDF was analysed in this checkpoint.

Limited external checks performed:
- The manufacturer's current UK Trulicity SmPC and Lilly medical information support once-weekly administration, consistent with the corrected source statement. This is not patient-specific dosing advice.
- Apple's standard EULA page exists and describes the standard/custom-EULA relationship. This does not independently prove this app's current App Store Connect EULA configuration.
- ICO guidance states that special-category health data requires an Article 6 lawful basis and an applicable Article 9 condition. This does not prove OneGLP's implementation meets every relevant obligation or that its listed bases are appropriate for each processing purpose.

## S06: Acceptance cannot be inferred from markup tests

The bundle includes six policy MAIN blocks, not complete Arabic locale parity. Shell/footer/SEO page translation, campaign runtime, App Store routing, accessibility, actual browser layout and all other locale reviews remain outstanding. Native, legal and clinical reviewers have not approved these translations.

## Bibliography

[1] https://github.com/sjgoodapps-tech/glp1/blob/91c8ffc7479f7d36d64f03ccdfdb4bf08a426f53/AGENTS.md (primary; high for repository constraints).
[2] https://github.com/sjgoodapps-tech/glp1/blob/91c8ffc7479f7d36d64f03ccdfdb4bf08a426f53/medical-safety.html (primary; high for what the source says, not independent clinical validation).
[3] https://github.com/sjgoodapps-tech/glp1/blob/91c8ffc7479f7d36d64f03ccdfdb4bf08a426f53/privacy.html (primary source text).
[4] https://github.com/sjgoodapps-tech/glp1/blob/91c8ffc7479f7d36d64f03ccdfdb4bf08a426f53/support.html (primary source text).
[5] https://github.com/sjgoodapps-tech/glp1/blob/91c8ffc7479f7d36d64f03ccdfdb4bf08a426f53/data-rights.html (primary source text).
[6] https://github.com/sjgoodapps-tech/glp1/blob/91c8ffc7479f7d36d64f03ccdfdb4bf08a426f53/methodology.html (primary source text).
[7] https://github.com/sjgoodapps-tech/glp1/blob/91c8ffc7479f7d36d64f03ccdfdb4bf08a426f53/ar/privacy.html (primary source text).
[8] https://github.com/sjgoodapps-tech/glp1/blob/91c8ffc7479f7d36d64f03ccdfdb4bf08a426f53/tools/search_content.py (primary source code).
[9] https://www.medicines.org.uk/emc/product/3634/smpc (manufacturer SmPC; primary, high).
[10] https://medical.lilly.com/uk/products/answers/trulicity-dulaglutide-how-to-use-the-pen-116202 (manufacturer medical information; primary, high).
[11] https://www.apple.com/legal/internet-services/itunes/dev/stdeula/ (Apple legal source; primary, high).
[12] https://cy.ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/information-about-workers-health/data-protection-and-workers-health-information/ (regulator guidance, employment context; primary, high for general Article 6/9 relationship only).

## Document created in

ChatGPT working environment, Linux; UTF-8 Markdown. Evidence checked on 11 October 2026. Not an independent professional approval.
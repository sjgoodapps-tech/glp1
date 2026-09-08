# Privacy-First App Store CTA Measurement

Generated: 2026-09-08T00:42:55+00:00

## What Is Implemented

- Campaign names are configured. Attribution is NOT ready until an Apple-generated provider token is supplied and the strict audit passes.
- Every priority SEO page uses its own Apple campaign token.
- Hero, answer and bottom CTAs are labelled in HTML so placement can be audited.
- JavaScript resolves each named campaign key to the same token used in crawler-visible HTML.
- No third-party analytics, tracking pixel, cookie, fingerprint or click beacon is added.

## Data Flow

1. The website displays ordinary App Store links. Apple requires both `ct` and its generated `pt` provider token for campaign attribution.
2. No measurement request is sent when the page loads.
3. Apple receives the campaign token only when the visitor chooses the App Store link.
4. Results are reviewed in App Store Connect when Apple provides enough campaign data.

## Campaign Scope

Homepage placements have separate campaign names. Priority SEO pages use page-level names. These labels do not prove that any downloads have been measured.

## Limits

- App Store campaign data can compare attributed App Store activity, but it cannot provide website click-through rate on its own.
- Website CTR requires aggregate first-party click counts. No such endpoint is added in this pass.
- Do not infer performance from campaigns that do not meet Apple reporting thresholds.

## Decision Rule

Keep each campaign unchanged for at least 28 days. Compare matched time periods. Change one major page element at a time, and do not claim a conversion improvement without enough attributed activity.

Audited priority CTA links: 36
Configured campaign keys: 17

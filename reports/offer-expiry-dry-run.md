# Lifetime Premium Offer Expiry Dry Run

Expiry configured: `2026-09-01T00:00:00+01:00`
Expiry in UTC: `2026-08-31T23:00:00+00:00`
Before test: `2026-08-31T23:59:59+01:00` -> active
At-expiry test: `2026-09-01T00:00:00+01:00` -> expired

## Assertions

- The offer is active one second before expiry.
- The offer is expired at the configured expiry instant.
- Every crawler-visible offer page changes from active keys to expired keys.
- No page exposes active and expired static variants together.
- The test does not write website files.

Crawler-visible pages switched: 14

- `apple-health-weight-loss-injection-tracker.html`
- `free-lifetime/index.html`
- `glp1-dose-reminder-app.html`
- `glp1-progress-photo-tracker.html`
- `glp1-side-effect-symptom-tracker.html`
- `glp1-weight-dose-symptom-tracker.html`
- `glp1-weight-tracker.html`
- `index.html`
- `mounjaro-tracker-iphone.html`
- `semaglutide-tracker-iphone.html`
- `tirzepatide-tracker-iphone.html`
- `wegovy-tracker-iphone.html`
- `weight-loss-injection-tracker.html`
- `zepbound-tracker-iphone.html`

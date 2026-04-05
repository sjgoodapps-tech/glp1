# Search Console setup

1. Replace placeholders:
   - `__SITE_URL__` with the full live site URL, for example `https://www.glpzy.app`
   - `__APP_STORE_URL__` with the live App Store URL when available
   - `__TESTFLIGHT_URL__` with the live TestFlight invite URL when available
2. Check `site-config.js`, all HTML canonical and Open Graph tags, `robots.txt`, and `sitemap.xml` after replacement.
3. Deploy the full contents of `output/site_bundle_updated` to the site root.
4. In Google Search Console:
   - choose a **Domain property** if you control the custom domain DNS
   - otherwise choose a **URL-prefix property** for the exact deployed base URL
5. Verify ownership using your preferred method.
6. If you use HTML tag verification, paste the provided `google-site-verification` meta tag in the `<head>` where this comment appears:
   - `<!-- Google Search Console verification meta tag goes here -->`
7. Submit `__SITE_URL__/sitemap.xml` in Search Console.
8. Request indexing for:
   - the homepage
   - `mounjaro-tracker-iphone.html`
   - `wegovy-tracker-iphone.html`
   - `zepbound-tracker-iphone.html`
   - `tirzepatide-tracker-iphone.html`
   - `semaglutide-tracker-iphone.html`
   - `glp1-weight-dose-symptom-tracker.html`
9. Recheck that App Store and TestFlight buttons hide correctly when their placeholders are blank or still contain placeholder values.

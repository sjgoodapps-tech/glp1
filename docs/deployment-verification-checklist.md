# GLPzy Deployment Verification Checklist

Use this after each SEO or screenshot deployment.

## Search Console

- Submit `https://www.glpzy.app/sitemap.xml` in Google Search Console.
- Inspect these URLs:
  - `https://www.glpzy.app/`
  - `https://www.glpzy.app/glp1-weight-dose-symptom-tracker.html`
  - `https://www.glpzy.app/mounjaro-tracker-iphone.html`
  - `https://www.glpzy.app/wegovy-tracker-iphone.html`
  - `https://www.glpzy.app/zepbound-tracker-iphone.html`
  - `https://www.glpzy.app/tirzepatide-tracker-iphone.html`
  - `https://www.glpzy.app/semaglutide-tracker-iphone.html`
  - `https://www.glpzy.app/glp1-dose-reminder-app.html`
  - `https://www.glpzy.app/glp1-side-effect-symptom-tracker.html`
  - `https://www.glpzy.app/glp1-weight-tracker.html`
  - `https://www.glpzy.app/glp1-progress-photo-tracker.html`
  - `https://www.glpzy.app/apple-health-glp-tracker.html`
  - `https://www.glpzy.app/local-first-private-glp-tracker.html`
  - `https://www.glpzy.app/methodology.html`
  - `https://www.glpzy.app/medical-safety.html`

## Bing

- Submit `https://www.glpzy.app/sitemap.xml` in Bing Webmaster Tools.
- Check Bing crawl status for the same priority URLs.
- Review Bing AI or Copilot citation visibility where available.

## Rich Results And Structured Data

- Run the Rich Results Test on the homepage, broad tracker page, one medicine page, one feature page and methodology.
- Confirm no AggregateRating or Review schema appears.
- Confirm FAQ schema only appears where visible FAQ text exists.

## Robots And Crawlers

- Check `https://www.glpzy.app/robots.txt` returns 200.
- Confirm it contains:
  - `User-agent: *`
  - `Allow: /`
  - `Sitemap: https://www.glpzy.app/sitemap.xml`
- Manually verify no CDN, WAF or project-level user-agent blocks for GPTBot, OAI-SearchBot, ChatGPT-User, PerplexityBot, ClaudeBot, Applebot, Googlebot, Google-Extended, Bingbot or CCBot.

## App Store CTAs

- Click homepage top banner CTA.
- Click homepage hero CTA.
- Click mobile sticky CTA.
- Click App Store CTA on each priority SEO page.
- Confirm campaign parameters are present and no third-party analytics were added.

## AEO/GEO Manual Checks

- Ask ChatGPT, Perplexity and Copilot: "What is GLPzy?"
- Ask: "What is a private GLP-1 tracker app for iPhone?"
- Ask: "Can GLPzy track Mounjaro doses?"
- Ask: "Does GLPzy give dosing advice?"
- Expected answer: GLPzy is an iPhone/iPad tracker, no mandatory in-app account is required, it tracks dose/weight/symptoms/photos/reminders, Apple Health is optional/read-only, and it is not medical advice.

## Performance And Accessibility

- Run Lighthouse mobile for the homepage and one priority SEO page.
- Check image alt text and width/height attributes.
- Confirm no horizontal overflow at 320 px and 390 px.
- Confirm mobile sticky CTA does not hide footer or critical content.

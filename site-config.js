(function(){
  var storefronts = {
    "en": { country: "us", currency: "USD" },
    "en-gb": { country: "gb", currency: "GBP" },
    "ar": { country: "sa", currency: "SAR" },
    "bg": { country: "bg", currency: "BGN" },
    "bn": { country: "bd", currency: "BDT" },
    "cs": { country: "cz", currency: "CZK" },
    "da": { country: "dk", currency: "DKK" },
    "de": { country: "de", currency: "EUR" },
    "el": { country: "gr", currency: "EUR" },
    "es-es": { country: "es", currency: "EUR" },
    "es-mx": { country: "mx", currency: "MXN" },
    "et": { country: "ee", currency: "EUR" },
    "fi": { country: "fi", currency: "EUR" },
    "fil": { country: "ph", currency: "PHP" },
    "fr": { country: "fr", currency: "EUR" },
    "fr-ca": { country: "ca", currency: "CAD" },
    "gu": { country: "in", currency: "INR" },
    "he": { country: "il", currency: "ILS" },
    "hi": { country: "in", currency: "INR" },
    "hr": { country: "hr", currency: "EUR" },
    "hu": { country: "hu", currency: "HUF" },
    "id": { country: "id", currency: "IDR" },
    "it": { country: "it", currency: "EUR" },
    "ja": { country: "jp", currency: "JPY" },
    "kn": { country: "in", currency: "INR" },
    "ko": { country: "kr", currency: "KRW" },
    "lt": { country: "lt", currency: "EUR" },
    "lv": { country: "lv", currency: "EUR" },
    "ml": { country: "in", currency: "INR" },
    "mr": { country: "in", currency: "INR" },
    "ms": { country: "my", currency: "MYR" },
    "nb": { country: "no", currency: "NOK" },
    "nl": { country: "nl", currency: "EUR" },
    "or": { country: "in", currency: "INR" },
    "pa": { country: "in", currency: "INR" },
    "pl": { country: "pl", currency: "PLN" },
    "pt-br": { country: "br", currency: "BRL" },
    "pt-pt": { country: "pt", currency: "EUR" },
    "ro": { country: "ro", currency: "RON" },
    "ru": { country: "ru", currency: "RUB" },
    "sk": { country: "sk", currency: "EUR" },
    "sl": { country: "si", currency: "EUR" },
    "sr": { country: "rs", currency: "RSD" },
    "sv": { country: "se", currency: "SEK" },
    "ta": { country: "in", currency: "INR" },
    "te": { country: "in", currency: "INR" },
    "th": { country: "th", currency: "THB" },
    "tr": { country: "tr", currency: "TRY" },
    "uk": { country: "ua", currency: "UAH" },
    "ur": { country: "pk", currency: "PKR" },
    "vi": { country: "vn", currency: "VND" },
    "zh-hans": { country: "cn", currency: "CNY" },
    "zh-hant": { country: "tw", currency: "TWD" }
  };

  function localeFromPath(pathname){
    var firstSegment = String(pathname || "")
      .replace(/^\/+/, "")
      .split("/")[0]
      .toLowerCase();

    return storefronts[firstSegment] ? firstSegment : "en";
  }

  var locale = localeFromPath(window.location.pathname);
  var storefront = storefronts[locale];
  var appStoreBaseUrl = "https://apps.apple.com/" + storefront.country + "/app/glpzy-glp-1-tracker/id6761775005";

  function campaignUrl(token){
    if(!token) return appStoreBaseUrl;

    return appStoreBaseUrl + "?ct=" + encodeURIComponent(token);
  }

  // generated:product-claims:start
  var productClaims = {
    "heroH1": "Track GLP-1 doses, weight, symptoms, photos and Apple Health context privately.",
    "heroSupport": "Log doses, weight, symptoms, appetite, nutrition, photos and reminders in one private iPhone app. Optional Apple Health support can add read-only weight, glucose, body, movement and nutrition context.",
    "appleHealthScope": "Optional read-only Apple Health support can include weight history, height, glucose readings, body composition, movement, workouts, calories, protein, water, carbs, fat, fiber and sugar. GLPzy does not write data back to Apple Health.",
    "freeSummary": "Free includes setup, daily dose entry, reminders, optional read-only Apple Health context, CSV and JSON export for core records, CSV import, charts, current and previous month calendar review, months needed for an active reorder reminder where applicable, historical Estimated Exposure context, 2 new photo uploads per month, photo comparison and the small Next Dose widget.",
    "freeEdits": "Basic same-treatment edits stay free: dose, start date, and reminder time.",
    "advancedEdits": "Advanced treatment changes, including switching country, medicine, administration route, medicine form, dosing frequency, custom treatment, or compounded treatment setup, may require Premium.",
    "premiumSummary": "Premium adds unlimited photo uploads, extra before-and-after montage styles, broader older and future calendar browsing, projected Estimated Exposure scenarios, advanced summaries, clinician-ready PDF summaries, deeper export and reporting tools, injection-site rotation review, maintenance tools, larger widgets, Apple Watch support and longer-range planning controls.",
    "exportSummary": "CSV and JSON history export stay available for core records. Clinician-ready PDF summaries and deeper export/reporting tools are Premium.",
    "supplySafety": "Supply tracking and reorder reminders are for personal planning only and do not change dose instructions.",
    "safetyPrimary": "Estimated Exposure is a personal tracking estimate, not measured blood concentration and not medical advice.",
    "safetyClinician": "Do not use Estimated Exposure to guide dosing. Always check with your clinician before making medical decisions.",
    "lifetimeUnlock": "Lifetime Premium is a one-time unlock tied to your Apple ID. It does not renew."
  };
  // generated:product-claims:end

  // generated:founding-offer-copy:start
  var foundingOfferCopy = {
    "active": {
      "banner": "Founding offer: Lifetime Premium free until 31 August. No subscription or renewal.",
      "bannerCta": "Get GLPzy",
      "heroLine": "Lifetime Premium is free until 31 August 2026.",
      "support": "Claim once and keep Premium. No subscription, no renewal, no account required.",
      "heroCta": "Get Lifetime Premium free",
      "sticky": "Lifetime Premium free until 31 Aug",
      "stickyCta": "Get the app",
      "landingTitle": "Lifetime Premium is free until 31 August 2026",
      "landingSupport": "Claim once and keep Premium. No subscription, no renewal, no account required.",
      "landingProof": "Track doses, weight, symptoms, photos, imports, exports and Apple Health context in one private GLP-1 app.",
      "landingCtaTitle": "Claim Lifetime Premium free before 31 August 2026",
      "keepExplanation": "This is a founding offer. Claim Lifetime Premium once before 31 August 2026 and keep Premium. There is no subscription and no renewal.",
      "faqTitle": "Founding offer questions",
      "faqKeepQuestion": "Do I keep Premium after 31 August?",
      "faqKeepAnswer": "Yes. If you claim Lifetime Premium before 31 August 2026, you keep Premium. There is no subscription or renewal."
    },
    "expired": {
      "heroLine": "The Lifetime Premium founding offer has ended.",
      "support": "You can still download GLPzy from the App Store for private GLP-1 tracking.",
      "heroCta": "View on the App Store",
      "landingTitle": "The Lifetime Premium founding offer has ended",
      "landingSupport": "You can still download GLPzy from the App Store for private GLP-1 tracking.",
      "landingProof": "GLPzy remains available for private dose, weight, symptom, photo, import, export and Apple Health context tracking.",
      "landingCtaTitle": "Download GLPzy from the App Store",
      "keepExplanation": "The founding offer has ended. GLPzy remains available on the App Store.",
      "faqTitle": "Premium offer status",
      "faqKeepQuestion": "Has the founding offer ended?",
      "faqKeepAnswer": "Yes. The Lifetime Premium founding offer ended after 31 August 2026. You can still download GLPzy from the App Store."
    }
  };
  // generated:founding-offer-copy:end

  window.GLPZY_SITE_CONFIG = {
    siteUrl: "https://www.glpzy.app",
    appStoreUrl: appStoreBaseUrl,
    appStoreCampaigns: {
      siteDefault: campaignUrl("founding_site_default"),
      homepageTopBanner: campaignUrl("founding_home_top_banner"),
      homepageHero: campaignUrl("founding_home_hero"),
      mobileSticky: campaignUrl("founding_mobile_sticky"),
      freeLifetime: campaignUrl("founding_free_lifetime"),
      seoMounjaro: campaignUrl("seo_mounjaro_tracker"),
      seoWegovy: campaignUrl("seo_wegovy_tracker"),
      seoZepbound: campaignUrl("seo_zepbound_tracker"),
      seoTirzepatide: campaignUrl("seo_tirzepatide_tracker"),
      seoSemaglutide: campaignUrl("seo_semaglutide_tracker"),
      seoGlp1Tracker: campaignUrl("seo_glp1_tracker"),
      seoSideEffectTracker: campaignUrl("seo_side_effect_tracker"),
      seoInjectionTracker: campaignUrl("seo_injection_tracker"),
      seoPhotoTracker: campaignUrl("seo_photo_tracker"),
      seoWeightTracker: campaignUrl("seo_weight_tracker"),
      seoDoseReminder: campaignUrl("seo_dose_reminder"),
      seoAppleHealthInjection: campaignUrl("seo_apple_health_injection")
    },
    appStoreCountry: storefront.country,
    appStoreCurrency: storefront.currency,
    locale: locale,
    foundingOffer: {
      expiresAt: "2026-09-01T00:00:00+01:00",
      copy: foundingOfferCopy,
      bannerDismissStorageKey: "glpzy-founding-offer-dismissed-until-v2",
      bannerDismissSessionKey: "glpzy-founding-offer-dismissed-session-v2",
      stickyDismissSessionKey: "glpzy-founding-offer-sticky-dismissed-session"
    },
    productClaims: productClaims,
    testFlightUrl: ""
  };
})();

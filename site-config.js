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

  window.GLPZY_SITE_CONFIG = {
    siteUrl: "https://www.glpzy.app",
    appStoreUrl: "https://apps.apple.com/" + storefront.country + "/app/glpzy-glp-1-tracker/id6761775005",
    appStoreCountry: storefront.country,
    appStoreCurrency: storefront.currency,
    locale: locale,
    testFlightUrl: ""
  };
})();

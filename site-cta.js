(function () {
  var config = window.GLPZY_SITE_CONFIG || {};

  function isLiveUrl(value) {
    return typeof value === 'string' && value.trim() !== '' && value.indexOf('__') === -1;
  }

  function bind(container) {
    var appStore = container.querySelector('[data-app-store-link]');
    var testFlight = container.querySelector('[data-testflight-link]');
    var note = container.querySelector('[data-cta-note]');
    var liveCount = 0;

    if (appStore) {
      if (isLiveUrl(config.appStoreUrl)) {
        appStore.href = config.appStoreUrl;
        liveCount += 1;
      } else {
        appStore.hidden = true;
      }
    }

    if (testFlight) {
      if (isLiveUrl(config.testFlightUrl)) {
        testFlight.href = config.testFlightUrl;
        liveCount += 1;
      } else {
        testFlight.hidden = true;
      }
    }

    if (note) {
      if (liveCount === 0) {
        note.textContent = 'Coming Soon.';
      } else if (liveCount === 1) {
        note.textContent = 'Coming Soon.';
      } else {
        note.textContent = 'Choose the current route that suits you.';
      }
    }
  }

  document.querySelectorAll('[data-site-cta]').forEach(bind);
}());

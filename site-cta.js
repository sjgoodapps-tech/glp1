(function () {
  var config = window.GLPZY_SITE_CONFIG || {};
  var headerBadgeSrc = 'assets/app-store-badge-white.svg';
  var footerBadgeSrc = 'assets/app-store-badge-black.svg';

  function isLiveUrl(value) {
    return typeof value === 'string' && value.trim() !== '' && value.indexOf('__') === -1;
  }

  function buildBadge(url, extraClass, badgeSrc) {
    var anchor = document.createElement('a');
    anchor.href = url;
    anchor.setAttribute('aria-label', 'Download GLPzy on the App Store');
    anchor.className = extraClass ? 'app-store-badge ' + extraClass : 'app-store-badge';

    var image = document.createElement('img');
    image.src = badgeSrc;
    image.alt = 'Download on the App Store';
    image.width = 180;
    image.height = 60;
    image.loading = 'lazy';

    anchor.appendChild(image);
    return anchor;
  }

  function hydrateAppStoreLink(anchor, extraClass, badgeSrc) {
    if (!anchor || !isLiveUrl(config.appStoreUrl)) {
      if (anchor) {
        anchor.hidden = true;
      }
      return;
    }
    anchor.href = config.appStoreUrl;
    anchor.setAttribute('aria-label', 'Download GLPzy on the App Store');
    anchor.classList.remove('button', 'button-primary', 'button-secondary');
    anchor.classList.add('app-store-badge');
    if (extraClass) {
      anchor.classList.add(extraClass);
    }
    anchor.innerHTML = '';

    var image = document.createElement('img');
    image.src = badgeSrc;
    image.alt = 'Download on the App Store';
    image.width = 180;
    image.height = 60;
    image.loading = 'lazy';
    anchor.appendChild(image);
    anchor.hidden = false;
  }

  function ensureHeaderBadge() {
    if (!isLiveUrl(config.appStoreUrl)) {
      return;
    }
    document.querySelectorAll('.topbar').forEach(function (topbar) {
      if (topbar.querySelector('.header-store-cta')) {
        return;
      }
      var badge = buildBadge(config.appStoreUrl, 'header-store-cta', headerBadgeSrc);
      topbar.appendChild(badge);
    });
  }

  function ensureFooterBadge() {
    if (!isLiveUrl(config.appStoreUrl)) {
      return;
    }
    document.querySelectorAll('.footer-card').forEach(function (card) {
      if (card.querySelector('.footer-store-cta')) {
        return;
      }
      var target = card.querySelector('.footer-grid > div:last-child') || card;
      var wrapper = document.createElement('div');
      wrapper.className = 'footer-store-row';
      wrapper.appendChild(buildBadge(config.appStoreUrl, 'footer-store-cta', footerBadgeSrc));
      target.appendChild(wrapper);
    });
  }

  function ensureBottomBand() {
    if (!isLiveUrl(config.appStoreUrl)) {
      return;
    }
    var hasManualDownloadBand = Array.prototype.some.call(
      document.querySelectorAll('.cta-band h2'),
      function (heading) {
        return heading.textContent && heading.textContent.indexOf('Download GLPzy for iPhone and iPad.') !== -1;
      }
    );
    document.querySelectorAll('footer.footer').forEach(function (footer) {
      if (hasManualDownloadBand || document.querySelector('.auto-download-band')) {
        return;
      }

      var section = document.createElement('section');
      section.className = 'page-wrap compact-top compact-bottom auto-download-band';

      var shell = document.createElement('div');
      shell.className = 'shell';

      var band = document.createElement('div');
      band.className = 'cta-band cta-band-compact';
      band.setAttribute('data-site-cta', '');

      var copy = document.createElement('div');
      copy.innerHTML = '<div class="kicker">Get GLPzy</div><h2>Download GLPzy for iPhone and iPad.</h2><p></p>';

      var actions = document.createElement('div');
      var actionRow = document.createElement('div');
      actionRow.className = 'site-cta-actions';
      var link = document.createElement('a');
      link.className = 'button button-primary';
      link.setAttribute('data-app-store-link', '');
      link.href = config.appStoreUrl;
      link.textContent = 'View on the App Store';
      actionRow.appendChild(link);
      var note = document.createElement('div');
      note.className = 'site-cta-note';
      note.setAttribute('data-cta-note', '');
      actions.appendChild(actionRow);
      actions.appendChild(note);

      band.appendChild(copy);
      band.appendChild(actions);
      shell.appendChild(band);
      section.appendChild(shell);
      footer.parentNode.insertBefore(section, footer);
    });
  }

  function bind(container) {
    var appStore = container.querySelector('[data-app-store-link]');
    var testFlight = container.querySelector('[data-testflight-link]');
    var note = container.querySelector('[data-cta-note]');
    var liveCount = 0;

    if (appStore) {
      if (isLiveUrl(config.appStoreUrl)) {
        hydrateAppStoreLink(appStore, '', footerBadgeSrc);
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
      note.textContent = liveCount > 1 ? 'Choose the current route that suits you.' : '';
    }
  }

  ensureHeaderBadge();
  ensureBottomBand();
  ensureFooterBadge();
  document.querySelectorAll('[data-site-cta]').forEach(bind);
}());

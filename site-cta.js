(function(){
  var config = window.GLPZY_SITE_CONFIG || {};
  var script = document.currentScript || document.querySelector('script[src$="site-cta.js"]');
  var root = script ? new URL('.', script.src) : new URL('./', window.location.href);

  function asset(path){ return new URL(path, root).href; }

  var headerBadgeSrc = asset('assets/app-store-badge-white.svg');
  var footerBadgeSrc = asset('assets/app-store-badge-black.svg');

  function isLiveUrl(value){
    return typeof value === 'string' && value.trim() !== '' && value.indexOf('__') === -1;
  }

  function badgeSrcFor(anchor){
    var theme = (anchor && anchor.getAttribute('data-badge-theme') || '').toLowerCase();
    return theme === 'light' ? headerBadgeSrc : footerBadgeSrc;
  }

  function badgeAriaLabel(){
    return 'Download GLPzy on the App Store';
  }

  function badgeImgAlt(){
    return 'Download on the App Store';
  }

  function buildBadge(url, extraClass, badgeSrc){
    var anchor = document.createElement('a');
    anchor.href = url;
    anchor.setAttribute('aria-label', badgeAriaLabel());
    anchor.className = extraClass ? 'app-store-badge ' + extraClass : 'app-store-badge';

    var image = document.createElement('img');
    image.src = badgeSrc;
    image.alt = badgeImgAlt();
    image.width = 180;
    image.height = 60;
    image.loading = 'lazy';
    anchor.appendChild(image);
    return anchor;
  }

  function hydrate(anchor, extraClass, badgeSrc){
    if(!anchor || !isLiveUrl(config.appStoreUrl)){
      if(anchor) anchor.hidden = true;
      return;
    }

    anchor.href = config.appStoreUrl;
    anchor.setAttribute('aria-label', badgeAriaLabel());
    anchor.classList.remove('button', 'button-primary', 'button-secondary');
    anchor.classList.add('app-store-badge');
    if(extraClass) anchor.classList.add(extraClass);
    anchor.innerHTML = '';

    var image = document.createElement('img');
    image.src = badgeSrc;
    image.alt = badgeImgAlt();
    image.width = 180;
    image.height = 60;
    image.loading = 'lazy';
    anchor.appendChild(image);
    anchor.hidden = false;
  }

  function hydrateAllBadges(){
    if(!isLiveUrl(config.appStoreUrl)) return;
    document.querySelectorAll('a[data-app-store-link]').forEach(function(anchor){
      hydrate(anchor, '', badgeSrcFor(anchor));
    });
  }

  function ensureHeaderBadge(){
    if(!isLiveUrl(config.appStoreUrl)) return;
    document.querySelectorAll('.topbar').forEach(function(topbar){
      if(topbar.querySelector('.header-store-cta')) return;
      topbar.appendChild(buildBadge(config.appStoreUrl, 'header-store-cta', headerBadgeSrc));
    });
  }

  function ensureFooterBadge(){
    if(!isLiveUrl(config.appStoreUrl)) return;
    document.querySelectorAll('.footer-card').forEach(function(card){
      if(card.querySelector('.footer-store-cta')) return;
      var target = card.querySelector('.footer-grid > div:last-child') || card;
      var wrapper = document.createElement('div');
      wrapper.className = 'footer-store-row';
      wrapper.appendChild(buildBadge(config.appStoreUrl, 'footer-store-cta', footerBadgeSrc));
      target.appendChild(wrapper);
    });
  }

  function bind(container){
    var appStoreAnchor = container.querySelector('[data-app-store-link]');
    var testFlightAnchor = container.querySelector('[data-testflight-link]');
    var note = container.querySelector('[data-cta-note]');
    var liveCount = 0;

    if(appStoreAnchor){
      if(isLiveUrl(config.appStoreUrl)){
        hydrate(appStoreAnchor, '', badgeSrcFor(appStoreAnchor));
        liveCount++;
      } else {
        appStoreAnchor.hidden = true;
      }
    }

    if(testFlightAnchor){
      if(isLiveUrl(config.testFlightUrl)){
        testFlightAnchor.href = config.testFlightUrl;
        liveCount++;
      } else {
        testFlightAnchor.hidden = true;
      }
    }

    if(note) note.textContent = liveCount > 1 ? 'Choose the current route that suits you.' : '';
  }

  function init(){
    hydrateAllBadges();
    ensureHeaderBadge();
    ensureFooterBadge();
    document.querySelectorAll('[data-site-cta]').forEach(bind);
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

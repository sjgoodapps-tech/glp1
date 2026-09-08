(function(){
  var config = window.GLPZY_SITE_CONFIG || {};
  var script = document.currentScript || document.querySelector('script[src*="site-cta.js"]');
  var root = script ? new URL('.', script.src) : new URL('./', window.location.href);
  var offerConfig = config.foundingOffer || {};
  var dayMs = 24 * 60 * 60 * 1000;

  function asset(path){ return new URL(path, root).href; }

  var headerBadgeSrc = asset('assets/app-store-badge-white.svg');
  var footerBadgeSrc = asset('assets/app-store-badge-black.svg');

  var offerMessages = {
    "ar": "عرض للمستخدمين الأوائل: احصل على Lifetime Premium مجانًا حتى 31 ديسمبر. فعّل مرة واحدة واحتفظ بـ Premium للأبد. بلا اشتراك أو تجديد.",
    "bg": "Оферта за първи потребители: Вземете Lifetime Premium безплатно до 31 декември. Отключете веднъж и запазете Premium завинаги. Без абонамент или подновяване.",
    "bn": "প্রাথমিক ব্যবহারকারীদের অফার: ৩১ ডিসেম্বরের মধ্যে Lifetime Premium বিনামূল্যে নিন। একবার আনলক করুন, Premium চিরকাল রাখুন। সাবস্ক্রিপশন বা নবায়ন নেই।",
    "cs": "Nabídka pro první uživatele: Získejte Lifetime Premium zdarma do 31. prosince. Odemkněte jednou a Premium vám zůstane navždy. Bez předplatného a prodlužování.",
    "da": "Tilbud til tidlige brugere: Få Lifetime Premium gratis senest 31. december. Lås op én gang, og behold Premium for altid. Intet abonnement, ingen fornyelse.",
    "de": "Angebot für frühe Nutzer: Lifetime Premium bis 31. Dezember kostenlos sichern. Einmal freischalten und Premium dauerhaft behalten. Kein Abo, keine Verlängerung.",
    "el": "Προσφορά για πρώτους χρήστες: Αποκτήστε δωρεάν Lifetime Premium έως 31 Δεκεμβρίου. Ξεκλειδώστε μία φορά και κρατήστε το Premium για πάντα. Χωρίς συνδρομή ή ανανέωση.",
    "en": "Founding offer: Lifetime Premium free until 31 December 2026. No subscription or renewal.",
    "en-gb": "Founding User Offer: Claim Lifetime Premium free by 31 December 2026. Unlock once and keep Premium forever. No subscription or renewal.",
    "es-es": "Oferta para primeros usuarios: consigue Lifetime Premium gratis hasta el 31 de diciembre. Desbloquea una vez y mantén Premium para siempre. Sin suscripción ni renovación.",
    "es-mx": "Oferta para primeros usuarios: obtén Lifetime Premium gratis hasta el 31 de diciembre. Desbloquea una vez y mantén Premium para siempre. Sin suscripción ni renovación.",
    "et": "Varajase kasutaja pakkumine: hankige Lifetime Premium tasuta 31. detsembrini. Avage üks kord ja säilitage Premium alatiseks. Tellimust ega uuendamist ei ole.",
    "fi": "Tarjous varhaisille käyttäjille: lunasta Lifetime Premium maksutta 31.12. mennessä. Avaa kerran ja pidä Premium ikuisesti. Ei tilausta eikä uusimista.",
    "fil": "Alokasyon para sa mga unang user: Kunin ang Lifetime Premium nang libre hanggang 31 Disyembre. I-unlock nang isang beses at panatilihin ang Premium. Walang subscription o renewal.",
    "fr": "Offre aux premiers utilisateurs : obtenez Lifetime Premium gratuit jusqu’au 31 décembre inclus. Déverrouillez une fois et gardez Premium à vie. Sans abonnement ni renouvellement.",
    "fr-ca": "Offre aux premiers utilisateurs : obtenez Lifetime Premium gratuit d’ici le 31 décembre. Déverrouillez une fois et gardez Premium à vie. Aucun abonnement ni renouvellement.",
    "gu": "પ્રારંભિક વપરાશકર્તા ઓફર: 31 ડિસેમ્બર સુધી Lifetime Premium મફત મેળવો. એક વાર અનલૉક કરો અને Premium હંમેશા રાખો. કોઈ સબ્સ્ક્રિપ્શન કે રિન્યુઅલ નહીં.",
    "he": "הצעה למשתמשים ראשונים: קבלו Lifetime Premium בחינם עד 31 בדצמבר. פתחו פעם אחת ושמרו על Premium לתמיד. ללא מנוי או חידוש.",
    "hi": "शुरुआती उपयोगकर्ता ऑफ़र: 31 दिसंबर तक Lifetime Premium मुफ़्त पाएं। एक बार अनलॉक करें और Premium हमेशा रखें। कोई सदस्यता या नवीनीकरण नहीं।",
    "hr": "Ponuda za prve korisnike: preuzmite Lifetime Premium besplatno do 31. prosinca. Otključajte jednom i zadržite Premium zauvijek. Bez pretplate i obnove.",
    "hu": "Ajánlat korai felhasználóknak: igényeld ingyen a Lifetime Premiumot december 31-ig. Oldd fel egyszer, és tartsd meg a Premiumot örökre. Nincs előfizetés vagy megújítás.",
    "id": "Penawaran pengguna awal: klaim Lifetime Premium gratis hingga 31 Desember. Buka sekali dan simpan Premium selamanya. Tanpa langganan atau perpanjangan.",
    "it": "Offerta per i primi utenti: richiedi Lifetime Premium gratis entro il 31 dicembre. Sblocca una volta e tieni Premium per sempre. Nessun abbonamento o rinnovo.",
    "ja": "初期ユーザー限定オファー：12月31日までにLifetime Premiumを無料で入手。一度アンロックすればPremiumをずっと利用できます。サブスクリプションも自動更新もありません。",
    "kn": "ಆರಂಭಿಕ ಬಳಕೆದಾರರ ಆಫರ್: ಡಿಸೆಂಬರ್ 31ರೊಳಗೆ Lifetime Premium ಅನ್ನು ಉಚಿತವಾಗಿ ಪಡೆಯಿರಿ. ಒಮ್ಮೆ ಅನ್ಲಾಕ್ ಮಾಡಿ, Premium ಅನ್ನು ಸದಾಕಾಲ ಇಟ್ಟುಕೊಳ್ಳಿ. ಚಂದಾದಾರಿಕೆ ಅಥವಾ ನವೀಕರಣ ಇಲ್ಲ.",
    "ko": "초기 사용자 혜택: 12월 31일까지 Lifetime Premium을 무료로 받으세요. 한 번 잠금 해제하면 Premium을 영구적으로 이용할 수 있습니다. 구독이나 자동 갱신 없음.",
    "lt": "Pasiūlymas pirmiesiems naudotojams: gaukite Lifetime Premium nemokamai iki gruodžio 31 d. Atrakinkite vieną kartą ir išsaugokite Premium visam laikui. Be prenumeratos ir atnaujinimo.",
    "lv": "Piedāvājums pirmajiem lietotājiem: iegūstiet Lifetime Premium bez maksas līdz 31. decembrim. Atbloķējiet vienu reizi un saglabājiet Premium uz visiem laikiem. Bez abonementa un atjaunošanas.",
    "ml": "ആദ്യകാല ഉപയോക്തൃ ഓഫർ: ഡിസംബർ 31-നകം Lifetime Premium സൗജന്യമായി നേടൂ. ഒരിക്കൽ അൺലോക്ക് ചെയ്ത് Premium എന്നേക്കും നിലനിർത്തൂ. സബ്സ്ക്രിപ്ഷൻ അല്ലെങ്കിൽ പുതുക്കൽ ഇല്ല.",
    "mr": "सुरुवातीच्या वापरकर्त्यांसाठी ऑफर: 31 डिसेंबरपर्यंत Lifetime Premium मोफत मिळवा. एकदाच अनलॉक करा आणि Premium कायम ठेवा. सदस्यता किंवा नूतनीकरण नाही.",
    "ms": "Tawaran pengguna awal: tuntut Lifetime Premium percuma sehingga 31 Disember. Buka kunci sekali dan simpan Premium selama-lamanya. Tiada langganan atau pembaharuan.",
    "nb": "Tilbud til tidlige brukere: få Lifetime Premium gratis innen 31. desember. Lås opp én gang og behold Premium for alltid. Uten abonnement eller fornyelse.",
    "nl": "Aanbieding voor vroege gebruikers: ontvang Lifetime Premium gratis tot en met 31 december. Ontgrendel één keer en houd Premium voor altijd. Geen abonnement of verlenging.",
    "or": "ଆରମ୍ଭିକ ବ୍ୟବହାରକାରୀ ଅଫର: 31 ଡିସେମ୍ବର ମଧ୍ୟରେ Lifetime Premium ମାଗଣାରେ ପାଆନ୍ତୁ। ଥରେ ଅନଲକ୍ କରନ୍ତୁ ଏବଂ Premium ସଦାକାଳ ପାଇଁ ରଖନ୍ତୁ। କୌଣସି ସବ୍ସକ୍ରିପ୍ସନ୍ କିମ୍ବା ନବୀକରଣ ନାହିଁ।",
    "pa": "ਸ਼ੁਰੂਆਤੀ ਯੂਜ਼ਰ ਆਫ਼ਰ: 31 ਦਸੰਬਰ ਤੱਕ Lifetime Premium ਮੁਫ਼ਤ ਪ੍ਰਾਪਤ ਕਰੋ। ਇੱਕ ਵਾਰ ਅਨਲੌਕ ਕਰੋ ਅਤੇ Premium ਹਮੇਸ਼ਾਂ ਲਈ ਰੱਖੋ। ਕੋਈ ਸਬਸਕ੍ਰਿਪਸ਼ਨ ਜਾਂ ਨਵੀਨੀਕਰਨ ਨਹੀਂ।",
    "pl": "Oferta dla pierwszych użytkowników: odbierz Lifetime Premium za darmo do 31 grudnia. Odblokuj raz i zachowaj Premium na zawsze. Bez subskrypcji i odnowienia.",
    "pt-br": "Oferta para primeiros usuários: resgate o Lifetime Premium grátis até 31 de dezembro. Desbloqueie uma vez e mantenha o Premium para sempre. Sem assinatura ou renovação.",
    "pt-pt": "Oferta primeiros utilizadores: obtenha Lifetime Premium grátis até 31 de dezembro. Desbloqueie uma vez e mantenha Premium para sempre. Sem subscrição nem renovação.",
    "ro": "Ofertă pentru primii utilizatori: obține Lifetime Premium gratuit până pe 31 decembrie. Deblochează o dată și păstrează Premium pe viață. Fără abonament sau reînnoire.",
    "ru": "Предложение для первых пользователей: получите Lifetime Premium бесплатно до 31 декабря. Разблокируйте один раз и сохраните Premium навсегда. Без подписки и продления.",
    "sr": "Ponuda za prve korisnike: preuzmite Lifetime Premium besplatno do 31. decembra. Otključajte jednom i zadržite Premium zauvek. Bez pretplate ili obnavljanja.",
    "sk": "Ponuka pre prvých používateľov: získajte Lifetime Premium zadarmo do 31. decembra. Odomknite raz a ponechajte si Premium navždy. Bez predplatného a obnovy.",
    "sl": "Ponudba za prve uporabnike: do 31. decembra brezplačno pridobite Lifetime Premium. Odklenite enkrat in obdržite Premium za vedno. Brez naročnine ali podaljšanja.",
    "sv": "Erbjudande för tidiga användare: hämta Lifetime Premium gratis senast 31 december. Lås upp en gång och behåll Premium för alltid. Ingen prenumeration eller förnyelse.",
    "ta": "ஆரம்ப பயனர் சலுகை: டிசம்பர் 31க்குள் Lifetime Premiumஐ இலவசமாகப் பெறுங்கள். ஒருமுறை திறந்து Premiumஐ என்றும் வைத்திருங்கள். சந்தா அல்லது புதுப்பிப்பு இல்லை.",
    "te": "ప్రారంభ వినియోగదారుల ఆఫర్: డిసెంబర్ 31లోపు Lifetime Premiumను ఉచితంగా పొందండి. ఒక్కసారి అన్‌లాక్ చేసి Premiumను శాశ్వతంగా ఉంచుకోండి. సబ్‌స్క్రిప్షన్ లేదా రీన్యువల్ లేదు.",
    "th": "ข้อเสนอสำหรับผู้ใช้รุ่นแรก: รับ Lifetime Premium ฟรีภายใน 31 ธันวาคม ปลดล็อกครั้งเดียวและเก็บ Premium ไว้ตลอดไป ไม่มีการสมัครสมาชิกหรือการต่ออายุ",
    "tr": "Erken kullanıcı teklifi: 31 Aralık’a kadar Lifetime Premium’u ücretsiz alın. Bir kez açın ve Premium’u sonsuza kadar kullanın. Abonelik veya yenileme yok.",
    "uk": "Пропозиція для перших користувачів: отримайте Lifetime Premium безкоштовно до 31 грудня. Розблокуйте один раз і збережіть Premium назавжди. Без підписки чи поновлення.",
    "ur": "ابتدائی صارفین کی پیشکش: 31 دسمبر تک Lifetime Premium مفت حاصل کریں۔ ایک بار اَن لاک کریں اور Premium ہمیشہ کے لیے رکھیں۔ کوئی سبسکرپشن یا تجدید نہیں۔",
    "vi": "Ưu đãi cho người dùng đầu tiên: nhận Lifetime Premium miễn phí đến hết ngày 31 tháng 12. Mở khóa một lần và giữ Premium mãi mãi. Không đăng ký hay gia hạn.",
    "zh-hans": "早期用户优惠：截至12月31日免费领取 Lifetime Premium。解锁一次，永久保留 Premium。无需订阅或续费。",
    "zh-hant": "早期用戶優惠：截至12月31日免費領取 Lifetime Premium。解鎖一次，永久保留 Premium。無需訂閱或續費。"
  };

  function isLiveUrl(value){
    return typeof value === 'string' && value.trim() !== '' && value.indexOf('__') === -1;
  }

  function isOfferActive(){
    var expiresAt = offerConfig.expiresAt ? new Date(offerConfig.expiresAt).getTime() : NaN;
    return Number.isFinite(expiresAt) && Date.now() < expiresAt;
  }

  function storageGet(storage, key){
    try { return storage.getItem(key); }
    catch(error){ return null; }
  }

  function storageSet(storage, key, value){
    try { storage.setItem(key, value); }
    catch(error){}
  }

  function storageRemove(storage, key){
    try { storage.removeItem(key); }
    catch(error){}
  }

  function isBannerDismissed(){
    var key = offerConfig.bannerDismissStorageKey || 'glpzy-founding-offer-dismissed-until';
    var dismissedUntil = Number(storageGet(window.localStorage, key) || 0);
    if(dismissedUntil > Date.now()) return true;
    if(dismissedUntil) storageRemove(window.localStorage, key);
    return false;
  }

  function wasBannerDismissedThisSession(){
    var key = offerConfig.bannerDismissSessionKey || 'glpzy-founding-offer-dismissed-session';
    return storageGet(window.sessionStorage, key) === '1';
  }

  function markBannerDismissed(){
    var localKey = offerConfig.bannerDismissStorageKey || 'glpzy-founding-offer-dismissed-until';
    var sessionKey = offerConfig.bannerDismissSessionKey || 'glpzy-founding-offer-dismissed-session';
    storageSet(window.localStorage, localKey, String(Date.now() + (7 * dayMs)));
    storageSet(window.sessionStorage, sessionKey, '1');
  }

  function campaignUrl(key){
    var campaigns = config.appStoreCampaigns || {};
    return campaigns[key] || campaigns.siteDefault || config.appStoreUrl || '';
  }

  function defaultCampaignKey(){
    return isOfferActive() && window.location.pathname.indexOf('/free-lifetime/') !== -1 ? 'freeLifetime' : 'siteDefault';
  }

  function appStoreUrlFor(anchorOrKey){
    var key = typeof anchorOrKey === 'string'
      ? anchorOrKey
      : anchorOrKey && anchorOrKey.getAttribute('data-app-store-campaign');

    return campaignUrl(key || defaultCampaignKey());
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

  function valueAt(rootObject, path){
    return String(path || '').split('.').reduce(function(value, part){
      if(value == null || part === '') return value;
      return value[part];
    }, rootObject);
  }

  function offerCopyPath(path){
    if(typeof path !== 'string') return path;
    return path.replace(/^(active|expired)\./, isOfferActive() ? 'active.' : 'expired.');
  }

  function applyConfiguredCopy(){
    document.querySelectorAll('[data-offer-copy]').forEach(function(element){
      var path = element.getAttribute('data-offer-copy');
      var value = valueAt(offerConfig.copy || {}, offerCopyPath(path));
      if(typeof value !== 'string') value = valueAt(offerConfig.copy || {}, path);
      if(typeof value === 'string') element.textContent = value;
    });

    document.querySelectorAll('[data-claim-copy]').forEach(function(element){
      var value = valueAt(config.productClaims || {}, element.getAttribute('data-claim-copy'));
      if(typeof value === 'string') element.textContent = value;
    });
  }

  function offerMessage(){
    return offerMessages[config.locale] || valueAt(offerConfig.copy || {}, 'active.banner') || offerMessages.en;
  }

  function localizedStoreLabel(fallback){
    if(config.locale === 'en' || config.locale === 'en-gb') return fallback;
    var label = document.querySelector('[data-i18n="settings.copy.see.app.store.pricing"]');
    return label && String(label.textContent || '').trim() || 'App Store';
  }

  function localizedDismissLabel(){
    return config.locale === 'en' || config.locale === 'en-gb' ? 'Dismiss' : '×';
  }

  function localizedStickyMessage(){
    if(config.locale === 'en' || config.locale === 'en-gb'){
      return valueAt(offerConfig.copy || {}, 'active.sticky') || 'Lifetime Premium free until 31 Dec';
    }
    var message = offerMessage().replace(/^[^:：]*[:：]\s*/, '');
    // A full stop after a day number is part of the date, not a sentence end.
    var sentenceEnd = message.search(/[^0-9][.!؟。।]/);
    return sentenceEnd < 0 ? message : message.slice(0, sentenceEnd + 1);
  }

  function localizedStickyButtonLabel(){
    var fallback = valueAt(offerConfig.copy || {}, 'active.stickyCta') || 'Get the app';
    if(config.locale === 'en' || config.locale === 'en-gb') return fallback;
    var label = localizedStoreLabel('App Store');
    return label.length > 14 ? 'App Store' : label;
  }

  function buildBadge(campaignKey, extraClass, badgeSrc){
    var anchor = document.createElement('a');
    anchor.href = appStoreUrlFor(campaignKey);
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

    anchor.href = appStoreUrlFor(anchor);
    anchor.setAttribute('aria-label', anchor.getAttribute('aria-label') || badgeAriaLabel());

    if(anchor.getAttribute('data-app-store-style') === 'text'){
      anchor.hidden = false;
      return;
    }

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
      topbar.appendChild(buildBadge(defaultCampaignKey(), 'header-store-cta', headerBadgeSrc));
    });
  }

  function ensureFooterBadge(){
    if(!isLiveUrl(config.appStoreUrl)) return;
    document.querySelectorAll('.footer-card').forEach(function(card){
      if(card.querySelector('.footer-store-cta')) return;
      var target = card.querySelector('.footer-grid > div:last-child') || card;
      var wrapper = document.createElement('div');
      wrapper.className = 'footer-store-row';
      wrapper.appendChild(buildBadge(defaultCampaignKey(), 'footer-store-cta', footerBadgeSrc));
      target.appendChild(wrapper);
    });
  }

  function updateOfferBannerHeight(banner){
    var height = banner ? Math.ceil(banner.getBoundingClientRect().height) : 0;
    document.documentElement.style.setProperty('--offer-banner-height', height + 'px');
  }

  function removeOfferBanner(banner){
    if(banner && banner.parentNode) banner.parentNode.removeChild(banner);
    document.body.classList.remove('founding-offer-banner-visible');
    document.documentElement.classList.remove('founding-offer-space');
    updateOfferBannerHeight(null);
  }

  function ensureOfferBanner(){
    if(!isOfferActive() || isBannerDismissed()){
      document.documentElement.classList.remove('founding-offer-space');
      document.body.classList.remove('founding-offer-banner-visible');
      updateOfferBannerHeight(null);
      return;
    }
    if(document.querySelector('.founding-offer-banner')) return;

    var banner = document.createElement('div');
    banner.className = 'founding-offer-banner';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', offerMessage());

    var inner = document.createElement('div');
    inner.className = 'founding-offer-banner-inner';

    var text = document.createElement('p');
    text.className = 'founding-offer-banner-text';
    text.textContent = offerMessage();

    var cta = document.createElement('a');
    cta.className = 'founding-offer-banner-cta';
    cta.href = appStoreUrlFor('homepageTopBanner');
    cta.textContent = localizedStoreLabel(valueAt(offerConfig.copy || {}, 'active.bannerCta') || 'Get GLPzy');

    var dismiss = document.createElement('button');
    dismiss.className = 'founding-offer-dismiss';
    dismiss.type = 'button';
    dismiss.textContent = localizedDismissLabel();
    dismiss.setAttribute('aria-label', config.locale === 'en' || config.locale === 'en-gb' ? 'Dismiss founding offer' : localizedDismissLabel());
    dismiss.addEventListener('click', function(){
      markBannerDismissed();
      removeOfferBanner(banner);
      var sticky = document.querySelector('.offer-sticky-cta');
      if(sticky) sticky.hidden = true;
    });

    inner.appendChild(text);
    inner.appendChild(cta);
    inner.appendChild(dismiss);
    banner.appendChild(inner);
    document.documentElement.classList.add('founding-offer-space');
    document.body.insertBefore(banner, document.body.firstChild);
    document.body.classList.add('founding-offer-banner-visible');
    updateOfferBannerHeight(banner);
    window.addEventListener('resize', function(){ updateOfferBannerHeight(banner); });
  }

  function bindMobileBadgeVisibility(anchor){
    var footer = document.querySelector('.footer-card');
    if(!anchor || !footer) return;

    function setSuppressed(value){
      document.body.classList.toggle('mobile-cta-suppressed', value);
    }

    function update(){
      var rect = footer.getBoundingClientRect();
      setSuppressed(rect.top < window.innerHeight && rect.bottom > 0);
    }

    if('IntersectionObserver' in window){
      var observer = new IntersectionObserver(function(entries){
        setSuppressed(entries.some(function(entry){
          return entry.isIntersecting;
        }));
      }, { threshold: 0.08 });

      observer.observe(footer);
    }

    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  }

  function ensureFallbackMobileBadge(){
    if(!isLiveUrl(config.appStoreUrl) || document.querySelector('.mobile-store-cta')) return;
    var badge = document.body.appendChild(buildBadge(defaultCampaignKey(), 'mobile-store-cta', headerBadgeSrc));
    bindMobileBadgeVisibility(badge);
    function update(){
      var hero = document.querySelector('.hero');
      var rect = hero && hero.getBoundingClientRect();
      var heroVisible = rect && rect.bottom > 0 && rect.top < window.innerHeight;
      document.body.classList.toggle('mobile-cta-hero-visible', Boolean(heroVisible));
      badge.hidden = Boolean(heroVisible) || wasBannerDismissedThisSession();
      if(!badge.hidden) badge.hidden = overlapsContent(badge);
    }
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  }

  function overlapsContent(cta){
    var rect = cta.getBoundingClientRect();
    return Array.from(document.querySelectorAll('h1, h2, h3, h4, p, li, td, th, img, a, button, input, select, textarea'))
      .some(function(element){
        if(cta.contains(element) || element.hidden) return false;
        var style = window.getComputedStyle(element);
        if(style.display === 'none' || style.visibility === 'hidden') return false;
        var other = element.getBoundingClientRect();
        return other.width > 0 && other.height > 0 && other.bottom > rect.top && other.top < rect.bottom && other.right > rect.left && other.left < rect.right;
      });
  }

  function ensureOfferSticky(){
    if(!isLiveUrl(config.appStoreUrl) || document.querySelector('.offer-sticky-cta')) return;

    var dismissedKey = offerConfig.stickyDismissSessionKey || 'glpzy-founding-offer-sticky-dismissed-session';
    var sticky = document.createElement('aside');
    sticky.className = 'offer-sticky-cta';
    sticky.hidden = true;
    sticky.setAttribute('aria-label', localizedStickyMessage());

    var copy = document.createElement('p');
    copy.textContent = localizedStickyMessage();

    var cta = document.createElement('a');
    cta.className = 'offer-sticky-button';
    cta.href = appStoreUrlFor('mobileSticky');
    cta.textContent = localizedStickyButtonLabel();

    var dismiss = document.createElement('button');
    dismiss.type = 'button';
    dismiss.className = 'offer-sticky-dismiss';
    dismiss.textContent = localizedDismissLabel();
    dismiss.setAttribute('aria-label', config.locale === 'en' || config.locale === 'en-gb' ? 'Dismiss Lifetime Premium offer' : localizedDismissLabel());

    sticky.appendChild(copy);
    sticky.appendChild(cta);
    sticky.appendChild(dismiss);
    document.body.appendChild(sticky);
    bindMobileBadgeVisibility(sticky);

    var timeEligible = false;
    var scrollEligible = false;

    function isDismissed(){
      return storageGet(window.sessionStorage, dismissedKey) === '1' || wasBannerDismissedThisSession();
    }

    function update(){
      var maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      scrollEligible = (window.scrollY / maxScroll) >= 0.25;
      var hero = document.querySelector('.hero');
      var heroVisible = false;
      if(hero){
        var heroRect = hero.getBoundingClientRect();
        heroVisible = heroRect.bottom > 0 && heroRect.top < window.innerHeight;
      }
      document.body.classList.toggle('mobile-cta-hero-visible', heroVisible);
      var shouldHide = isDismissed() || heroVisible || !(timeEligible || scrollEligible);
      if(shouldHide){
        sticky.hidden = true;
        return;
      }

      // Hide over reading content as well as controls and headings.
      sticky.hidden = false;
      sticky.hidden = overlapsContent(sticky);
    }

    dismiss.addEventListener('click', function(){
      storageSet(window.sessionStorage, dismissedKey, '1');
      sticky.hidden = true;
    });

    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    window.setTimeout(function(){
      timeEligible = true;
      update();
    }, 8000);
    update();
  }

  function ensureMobileBadge(){
    if(isOfferActive()) ensureOfferSticky();
    else ensureFallbackMobileBadge();
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

  function setOfferBodyState(){
    var active = isOfferActive();
    document.body.classList.toggle('founding-offer-current', active);
    document.body.classList.toggle('founding-offer-expired', !active);
    document.querySelectorAll('.offer-active-only').forEach(function(element){
      element.hidden = !active;
    });
    document.querySelectorAll('.offer-expired-only').forEach(function(element){
      element.hidden = active;
    });
  }

  function init(){
    applyConfiguredCopy();
    setOfferBodyState();
    hydrateAllBadges();
    ensureHeaderBadge();
    ensureFooterBadge();
    ensureOfferBanner();
    ensureMobileBadge();
    document.querySelectorAll('[data-site-cta]').forEach(bind);
    setOfferBodyState();
  }

  function checkOfferExpiry(){
    if(isOfferActive()){
      var remaining = new Date(offerConfig.expiresAt).getTime() - Date.now();
      window.setTimeout(checkOfferExpiry, Math.min(remaining + 1, 2147483647));
      return;
    }
    applyConfiguredCopy();
    setOfferBodyState();
    removeOfferBanner(document.querySelector('.founding-offer-banner'));
    var sticky = document.querySelector('.offer-sticky-cta');
    if(sticky) sticky.remove();
    ensureFallbackMobileBadge();
  }

  function start(){
    init();
    checkOfferExpiry();
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();

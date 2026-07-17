(function(){
  var expiresAt = "2026-09-01T00:00:00+01:00";
  var dismissalKey = "glpzy-founding-offer-dismissed-until-v2";
  var dismissedUntil = 0;
  try { dismissedUntil = Number(window.localStorage.getItem(dismissalKey) || 0); }
  catch(error){}
  if(Date.now() < new Date(expiresAt).getTime() && dismissedUntil <= Date.now()){
    document.documentElement.classList.add('founding-offer-space');
  }
})();

/* Progressive date formatting only: all editorial facts and links are static HTML. */
(function () {
  'use strict';
  var formatter;
  try {
    var locale = document.documentElement.lang;
    if (!Intl.DateTimeFormat.supportedLocalesOf([locale]).length) return;
    formatter = new Intl.DateTimeFormat(locale, {
      year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC'
    });
  } catch (error) { return; } // Keep the accessible machine date on older browsers.
  document.querySelectorAll('time[data-press-date]').forEach(function (element) {
    var value = element.getAttribute('datetime');
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return;
    var date = new Date(value + 'T12:00:00Z');
    if (isNaN(date.getTime())) return;
    // Some browser ICU builds recognise a locale but lack its month names.
    // Retain the ISO date instead of exposing technical placeholders like M09.
    if (formatter.formatToParts(date).some(function (part) {
      return part.type === 'month' && /^M\d{2}$/.test(part.value);
    })) return;
    element.querySelector('bdi').textContent = formatter.format(date);
  });
})();

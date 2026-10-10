"""Separate translated landing-page intents using static, locale-specific copy."""
import json
import re
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCE = json.loads((ROOT / 'data/website-search-copy.json').read_text())
COPY = {locale: dict(zip(RESOURCE['keys'], values))
        for locale, values in RESOURCE['translations'].items()}
assert all(len(values) == len(RESOURCE['keys']) and all(values)
           for values in RESOURCE['translations'].values())
FAMILIES = {'glp1-weight-dose-symptom-tracker.html',
            'local-first-private-glp-tracker.html', 'privacy.html', 'overview.html'}


def plain(text):
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]*>', '', text))).strip()


def keyed_text(html, *keys):
    for key in keys:
        match = re.search(r'<(?P<tag>[a-z][a-z0-9]*)\b[^>]*data-i18n="' + re.escape(key)
                          + r'"[^>]*>(.*?)</(?P=tag)>', html, re.S | re.I)
        if match:
            return plain(match[2])
    raise ValueError('Missing localized search-copy source: ' + ', '.join(keys))


def replace_key(html, old, new, value, rtl=False):
    pattern = r'(<(?P<tag>h2|p)\b[^>]*data-i18n=")(?:' + re.escape(old) + '|' + re.escape(new) + r')("[^>]*>).*?</(?P=tag)>'
    markup = escape(value)
    if rtl:
        markup = re.sub(r'OneGLP|GLP-1|iPhone', lambda m: '<bdi>' + m[0] + '</bdi>', markup)
    return re.sub(pattern, lambda m: m[1] + new + m[3] + markup + '</' + m['tag'] + '>', html, count=1, flags=re.S)


def private_cards(locale, html):
    """Explain using the tracker, rather than repeating the privacy-page grid."""
    home = (ROOT / locale / 'index.html').read_text()
    tracker = (ROOT / locale / 'glp1-weight-dose-symptom-tracker.html').read_text()
    cards = [(home, 'site.card.log.title', 'site.card.log.body'),
             (tracker, 'site.card.trends.title', 'site.card.trends.body'),
             (tracker, 'site.card.provider.title', 'site.card.provider.body'),
             (html, 'site.nav.privacy', 'site.card.account.body')]
    markup = '<div class="feature-grid" data-private-workflow-cards>'
    for source, title_key, body_key in cards:
        markup += ('<article class="feature-card"><h3 data-i18n="' + title_key + '">'
                   + escape(keyed_text(source, title_key)) + '</h3><p data-i18n="' + body_key + '">'
                   + escape(keyed_text(source, body_key)) + '</p></article>')
    markup += '</div>'
    pattern = r'<div\b[^>]*class="feature-grid"[^>]*>.*?</div>'
    if not re.search(pattern, html, re.S):
        raise ValueError(locale + ': missing private tracker card grid')
    return re.sub(pattern, lambda _: markup, html, count=1, flags=re.S)


def metadata(html, title, description):
    html = re.sub(r'(<title\b[^>]*>).*?(</title>)',
                  lambda m: m[1] + escape(title) + m[2], html, count=1, flags=re.S | re.I)
    values = {'description': description, 'og:title': title, 'twitter:title': title,
              'og:description': description, 'twitter:description': description}
    def meta(match):
        identity = re.search(r'\b(?:name|property)="([^"]+)"', match[0])
        if not identity or identity[1] not in values:
            return match[0]
        return re.sub(r'\bcontent="[^"]*"', lambda _: 'content="' + escape(values[identity[1]], quote=True) + '"', match[0])
    html = re.sub(r'<meta\b[^>]*>', meta, html, flags=re.I)
    def schema(match):
        document = json.loads(match[2])
        def visit(value):
            if isinstance(value, list):
                for child in value: visit(child)
            elif isinstance(value, dict):
                types = value.get('@type', [])
                if types == 'WebPage' or isinstance(types, list) and 'WebPage' in types:
                    value['name'] = title
                    value['description'] = description
                for child in value.values():
                    if isinstance(child, (list, dict)): visit(child)
        visit(document)
        return match[1] + json.dumps(document, ensure_ascii=False, indent=2) + match[3]
    return re.sub(r'(<script\b[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)', schema, html, flags=re.S)


def sync_search_content(relative, html):
    parts = Path(relative).parts
    if '<head' not in html.lower() or len(parts) != 2 or parts[0] in {'en', 'en-gb'} or parts[0] not in COPY or parts[1] not in FAMILIES:
        return html
    locale, family = parts
    copy = COPY[locale]
    if family == 'local-first-private-glp-tracker.html':
        title = copy['privateTitle']
        description = copy['privateWorkflow']
        html = replace_key(html, 'site.privacy.detail.title', 'search.privateTitle', title, locale in {'ar', 'he', 'ur'})
        html = replace_key(html, 'site.privacy.detail.body', 'search.privateWorkflow', description, locale in {'ar', 'he', 'ur'})
        html = private_cards(locale, html)
        html = re.sub(r'styles\.css(?:\?v=[^"\s<>]+)?', 'styles.css?v=20261007-search-discovery', html)
    elif family == 'glp1-weight-dose-symptom-tracker.html':
        title = copy['trackerTitle']
        description = keyed_text(html, 'site.privacy.body') + ' ' + keyed_text(html, 'site.product.card.summary.body', 'site.card.provider.body')
    elif family == 'privacy.html':
        # Full policy localisations use the English policy's numbered sections and
        # have their own reviewed privacy metadata. Do not replace that text with
        # short marketing-card metadata or require cards removed by full parity.
        if 'data-english-section="1"' in html:
            return html
        title = keyed_text(html, 'settings.detail.privacy.policy')
        description = keyed_text(html, 'site.card.local.body')
    else:
        # Overview describes the product and trust hub, rather than reusing support's snippet.
        old = re.search(r'<title\b[^>]*>(.*?)</title>', html, re.S)
        title = plain(old[1])
        description = keyed_text(html, 'site.card.local.body') + ' ' + keyed_text(html, 'site.product.card.summary.body', 'site.card.provider.body')
    if family != 'overview.html':
        title += ' | OneGLP'
    return metadata(html, title, description)

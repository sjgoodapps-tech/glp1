#!/usr/bin/env python3
"""Render the name-change pages from maintained, locale-specific copy."""
import argparse
import json
import os
from html import escape
from pathlib import Path
from urllib.parse import urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/rebrand-page.json').read_text())
FACTS = json.loads((ROOT / 'data/product-facts.json').read_text())
BRAND = json.loads((ROOT / 'data/rebrand.json').read_text())
SITE = FACTS['site_url'].rstrip('/')


def page_path(locale):
    return Path('' if locale == 'en' else locale) / DATA['slug'] / 'index.html'


def page_url(locale):
    return SITE + '/' + page_path(locale).as_posix()[:-10]


def campaign_url(locale, bottom=False):
    parsed = urlsplit(FACTS['app_store_url'])
    parts = parsed.path.split('/')
    parts[1] = DATA['translations'][locale]['storefront']
    query = {'ct': DATA['campaign'] + ('_bottom' if bottom else '')}
    provider = FACTS['app_store_campaign']['provider_token']
    if provider:
        query.update(pt=str(provider), mt='8')
    return urlunsplit(parsed._replace(path='/'.join(parts), query=urlencode(query)))


def render(locale):
    copy = DATA['translations'][locale]
    path = page_path(locale)
    home = Path('' if locale == 'en' else locale)

    def link(target):
        return escape(os.path.relpath(target, path.parent), quote=True)

    def text(value):
        result = escape(value)
        if locale in {'ar', 'he', 'ur'}:
            for name in ('OneGLP', 'GLPzy', 'GLP-1', 'Steven Good', 'Apple Health', 'App Store', 'Premium', '6761775005'):
                result = result.replace(name, f'<bdi>{name}</bdi>')
        return result

    alternates = {key: page_url(key) for key in DATA['translations']}
    alternates['x-default'] = page_url('en')
    hreflang = '\n'.join(f'  <link rel="alternate" hreflang="{key}" href="{value}">' for key, value in sorted(alternates.items()))
    languages = '\n'.join(
        f'          <li><a lang="{key}" hreflang="{key}" href="{link(page_path(key))}"'
        + (' aria-current="page"' if key == locale else '') + f'>{escape(value["language"])}</a></li>'
        for key, value in DATA['translations'].items()
    )
    items = '\n'.join(f'          <li>{text(value)}</li>' for value in copy['items'])
    questions = '\n'.join(
        f'      <section class="name-question"><h2>{text(q)}</h2><p>{text(a)}</p></section>'
        for q, a in copy['questions']
    )
    graph = {'@context': 'https://schema.org', '@graph': [
        {'@type': FACTS['publisher_type'], '@id': SITE + '/#publisher', 'name': FACTS['publisher']},
        {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': FACTS['app_name'], 'publisher': {'@id': SITE + '/#publisher'}},
        {'@type': 'SoftwareApplication', '@id': SITE + '/#software', 'name': FACTS['app_name'], 'alternateName': BRAND['previous_name'],
         'subjectOf': {'@id': page_url(locale) + '#webpage'},
         'url': SITE + '/', 'downloadUrl': FACTS['app_store_url'], 'operatingSystem': 'iOS', 'applicationCategory': 'HealthApplication',
         'publisher': {'@id': SITE + '/#publisher'}},
        {'@type': 'WebPage', '@id': page_url(locale) + '#webpage', 'url': page_url(locale), 'name': copy['title'],
         'description': copy['description'], 'inLanguage': locale, 'about': {'@id': SITE + '/#software'},
         'isPartOf': {'@id': SITE + '/#website'}, 'publisher': {'@id': SITE + '/#publisher'}},
    ]}
    schema = json.dumps(graph, ensure_ascii=False, indent=2).replace('<', '\\u003c')
    return f'''<!doctype html>
<html lang="{locale}" dir="{'rtl' if locale in {'ar', 'he', 'ur'} else 'ltr'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(copy['title'])}</title>
  <meta name="description" content="{escape(copy['description'], quote=True)}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{page_url(locale)}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="OneGLP">
  <meta property="og:title" content="{escape(copy['title'], quote=True)}">
  <meta property="og:description" content="{escape(copy['description'], quote=True)}">
  <meta property="og:url" content="{page_url(locale)}">
  <meta property="og:image" content="{SITE}/{BRAND['share_image']}">
  <meta property="og:image:width" content="512">
  <meta property="og:image:height" content="512">
  <meta name="twitter:image" content="{SITE}/{BRAND['share_image']}">
  <meta name="twitter:card" content="summary">
  <link rel="icon" href="{link(Path('assets/oneglp/favicon.svg'))}" type="image/svg+xml">
  <link rel="stylesheet" href="{link(Path('rebrand-page.css'))}?v=20260920">
  <script type="application/ld+json">
{schema}
  </script>
{hreflang}
</head>
<body>
  <header class="name-header">
    <div class="name-shell name-header-inner">
      <a class="name-logo" href="{link(home / 'index.html')}"><img src="{link(Path('assets/oneglp/oneglp-logo-dark.svg'))}" width="1330" height="366" alt="OneGLP"></a>
      <details class="name-languages">
        <summary>{escape(copy['language'])}</summary>
        <ul>
{languages}
        </ul>
      </details>
    </div>
  </header>
  <main>
    <section class="name-intro">
      <div class="name-shell">
        <p class="name-tagline">{text(copy['tagline'])}</p>
        <h1>{text(copy['title'])}</h1>
        <p class="name-summary">{text(copy['intro'])}</p>
        <div class="name-actions">
          <a class="name-cta" href="{escape(campaign_url(locale), quote=True)}" data-app-store-link data-app-store-style="text" data-app-store-campaign="rebrandPage" data-cta-placement="hero">{text(copy['cta'])}</a>
          <a href="{link(home / 'index.html')}">{text(copy['explore'])}</a>
        </div>
      </div>
    </section>
    <div class="name-shell name-content">
      <section class="name-unchanged">
        <h2>{text(copy['stays'])}</h2>
        <ul>
{items}
        </ul>
      </section>
{questions}
      <div class="name-actions name-download">
        <a class="name-cta" href="{escape(campaign_url(locale, bottom=True), quote=True)}" data-app-store-link data-app-store-style="text" data-app-store-campaign="rebrandPageBottom" data-cta-placement="bottom">{text(copy['cta'])}</a>
      </div>
      <p class="name-safety">{text(copy['safety'])}</p>
    </div>
  </main>
  <footer class="name-footer name-shell">
    <p>{text(copy['publisher'])}</p>
    <nav><a href="{link(home / 'support.html')}">{text(copy['support'])}</a><a href="{link(home / 'privacy.html')}">{text(copy['privacy'])}</a></nav>
  </footer>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    changed = []
    for locale in DATA['translations']:
        path = ROOT / page_path(locale)
        expected = render(locale)
        if not path.exists() or path.read_text() != expected:
            changed.append(str(page_path(locale)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(expected)
    print(f'Rebrand pages {"drift" if args.check else "updated"}: {len(changed)} of {len(DATA["translations"])}')
    return int(args.check and bool(changed))


if __name__ == '__main__':
    raise SystemExit(main())

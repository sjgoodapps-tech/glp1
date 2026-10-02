#!/usr/bin/env python3
"""Build all Press pages using existing static copy, rebrand UI and SEO generators."""
import argparse
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from build_rebrand_pages import render as render_history
from press_content import (COPY, DATA, ROOT, SITE, RTL, article_markup, locale_of,
                           page_path, page_url, relative_link, sync_links, ui_text, validate_data)
from seo_gate_sitemap import hreflang_clusters, set_hreflang


def render(locale, duplicate=False, articles=None):
    copy = COPY[locale]
    path = page_path(locale, duplicate)
    records = DATA['articles'] if articles is None else articles
    # Reuse the established compact information-page header, including native
    # details language switching; the only new route is the Press family.
    header = re.search(r'<header\b.*?</header>', render_history(locale), re.S)[0]
    header = re.sub(r'(<a lang="([^"]+)" hreflang="[^\"]+" href=")[^"]+',
                    lambda m: m[1] + relative_link(path, page_path(m[2])), header)
    if duplicate:
        header = header.replace('src="../assets/', 'src="../../assets/')
    overview = ('en/' if duplicate else (locale + '/' if locale != 'en' else '')) + 'overview.html'
    footer = re.search(r'<footer\b.*?</footer>', (ROOT / overview).read_text(), re.S)[0]
    def relocate(match):
        url = urlsplit(match[2])
        if url.scheme or url.netloc or match[2].startswith(('#', '/')):
            return match[0]
        target = (ROOT / overview).parent / url.path
        relative = relative_link(path, target.resolve().relative_to(ROOT))
        return match[1] + urlunsplit(url._replace(path=relative)) + match[3]
    footer = re.sub(r'(href=")([^"]+)(")', relocate, footer)
    footer = sync_links(path.as_posix(), footer)
    content = '\n'.join(article_markup(locale, article) for article in records)
    if not records:
        content = '<p data-i18n="press.empty">' + ui_text(copy['press.empty'], locale) + '</p>'
    title = copy['site.nav.press'] + ' | OneGLP'
    def link(target):
        return escape(relative_link(path, target), quote=True)
    schema = {'@context': 'https://schema.org', '@type': 'WebPage', 'url': page_url(locale),
              'name': title, 'description': copy['press.description'], 'inLanguage': locale,
              'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': SITE + '/#software'}}
    schema_json = json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c')
    html = f'''<!doctype html>
<html lang="{locale}" dir="{'rtl' if locale in RTL else 'ltr'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(copy['press.description'], quote=True)}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{page_url(locale)}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="OneGLP">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(copy['press.description'], quote=True)}">
  <meta property="og:url" content="{page_url(locale)}">
  <meta property="og:image" content="{SITE}/assets/oneglp/social-icon.png">
  <link rel="icon" href="{link('assets/oneglp/favicon.svg')}" type="image/svg+xml">
  <link rel="stylesheet" href="{link('styles.css')}?v=20260920-screens-v5">
  <link rel="stylesheet" href="{link('rebrand-page.css')}?v=20260920">
  <link rel="stylesheet" href="{link('press.css')}">
  <script defer src="{link('site-press.js')}"></script>
  <script type="application/ld+json">{schema_json}</script>
</head>
<body class="press-page">
{header}
  <main class="name-shell press-main">
    <h1 data-i18n="press.heading">{ui_text(copy['press.heading'], locale)}</h1>
    <p class="press-intro" data-i18n="press.description">{ui_text(copy['press.description'], locale)}</p>
    <p class="press-continuity" data-i18n="press.continuity">{ui_text(copy['press.continuity'], locale)}</p>
    <div class="press-articles">
{content}
    </div>
  </main>
{footer}
</body>
</html>
'''
    paths = [ROOT / page_path(key) for key in COPY]
    # Match the central SEO pass's whitespace normalisation for optional fields.
    html = '\n'.join(line.rstrip() for line in html.splitlines()) + '\n'
    return set_hreflang(html, hreflang_clusters(paths)[DATA['slug'] + '/index.html'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    validate_data()
    changed = []
    for locale, duplicate in [(key, False) for key in COPY] + [('en', True)]:
        path = ROOT / page_path(locale, duplicate)
        expected = render(locale, duplicate)
        if not path.exists() or path.read_text() != expected:
            changed.append(path.relative_to(ROOT).as_posix())
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(expected)
    print(f'Press pages {"drift" if args.check else "updated"}: {len(changed)}; {len(COPY)} locales and one English alias')
    return int(args.check and bool(changed))


if __name__ == '__main__':
    raise SystemExit(main())

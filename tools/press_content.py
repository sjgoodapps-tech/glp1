"""Shared static press copy, routes and secondary-link synchronisation."""
import json
import os
import re
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
from canonical_links import canonicalize_links

from seo_gate_sitemap import LOCALE_DIRS, ROOT, SITE, locale_for, url_for_path

RESOURCE = json.loads((ROOT / 'data/website-press-copy.json').read_text())
COPY = {locale: dict(zip(RESOURCE['keys'], values))
        for locale, values in RESOURCE['translations'].items()}
DATA = json.loads((ROOT / 'data/press.json').read_text())
RTL = {'ar', 'he', 'ur'}


def validate_data(articles=None):
    assert set(COPY) == LOCALE_DIRS, 'Press translations must cover the existing locale registry'
    for locale, values in RESOURCE['translations'].items():
        assert len(values) == len(RESOURCE['keys']) and all(values), locale
        assert COPY[locale]['press.context'].count('{press}') == 1, locale
    seen = set()
    for article in DATA['articles'] if articles is None else articles:
        for key in ('publisher', 'originalTitle', 'url', 'coverageType', 'legacyBrand', 'language'):
            assert key in article, f'Missing press field: {key}'
        assert all(article[key].strip() for key in ('publisher', 'originalTitle', 'url', 'language'))
        assert urlsplit(article['url']).scheme == 'https' and urlsplit(article['url']).netloc
        assert article['url'] not in seen, 'Duplicate press URL'
        seen.add(article['url'])
        dates = [key for key in ('publicationDate', 'checkedDate') if article.get(key)]
        assert len(dates) == 1, 'Specify one publication date or checked date, never relabel a checked date as published'
        value = article[dates[0]]
        assert date.fromisoformat(value).isoformat() == value
        assert isinstance(article['legacyBrand'], bool)
        assert all('press.type.' + article['coverageType'] in copy for copy in COPY.values())
        for key in ('descriptionKey', 'noteKey'):
            if article.get(key):
                assert all(article[key] in copy for copy in COPY.values())


def page_path(locale, duplicate=False):
    return Path(locale if locale != 'en' or duplicate else '') / DATA['slug'] / 'index.html'


def page_url(locale):
    return url_for_path(page_path(locale).as_posix())


def locale_of(relative):
    locale = locale_for(relative)
    return 'en' if locale == 'root' else locale


def relative_link(source, target):
    return os.path.relpath(target, Path(source).parent).replace(os.sep, '/')


def ui_text(value, locale):
    value = escape(value)
    if locale in RTL:
        value = re.sub(r'OneGLP|GLPzy|App Store|Steven Good|GLP-1|Lifetime Premium|Premium|Monj',
                       lambda m: '<bdi>' + m[0] + '</bdi>', value)
    return value


def press_link(relative):
    locale = locale_of(relative)
    return (f'<a data-i18n="site.nav.press" href="{escape(relative_link(relative, page_path(locale)), quote=True)}">'
            + ui_text(COPY[locale]['site.nav.press'], locale) + '</a>')


def context_markup(relative):
    locale = locale_of(relative)
    before, after = COPY[locale]['press.context'].split('{press}')
    return ('<p class="press-context" data-press-context data-i18n="press.context">'
            + ui_text(before, locale) + press_link(relative) + ui_text(after, locale) + '</p>')


def sync_links(relative, html):
    """Update existing footers in place; never add or duplicate navigation components."""
    # Four older templates end in a truncated closing tag. Repair that boundary
    # so their existing footer can participate in the same synchronisation pass.
    if html.rstrip().endswith('</foot'):
        html = html.rstrip()[:-6] + '</footer></body></html>\n'
    link = press_link(relative)
    def footer(match):
        fragment = match[0]
        if 'data-i18n="site.nav.press"' in fragment:
            return re.sub(r'<a\b[^>]*data-i18n="site.nav.press"[^>]*>.*?</a>', link, fragment, flags=re.S)
        pattern = r'(<p\b[^>]*class="[^"]*\bfooter-links\b[^"]*"[^>]*>)(.*?)(</p>)'
        if re.search(pattern, fragment, re.S):
            return re.sub(pattern, lambda m: m[1] + m[2] + ' · ' + link + m[3], fragment, count=1, flags=re.S)
        if '</nav>' in fragment:
            return fragment.replace('</nav>', link + '</nav>', 1)
        # The original English policy pages have the same information links
        # in a plain small paragraph, without the marketing footer-links class.
        paragraphs = list(re.finditer(r'<p\b[^>]*>.*?</p>', fragment, re.S))
        candidates = [m for m in paragraphs if re.search(r'href="(?!https?:|mailto:)[^"]+"', m[0])]
        if candidates:
            last = candidates[-1]
            return fragment[:last.end() - 4] + ' · ' + link + fragment[last.end() - 4:]
        raise ValueError(f'{relative}: no existing footer information links')
    html = re.sub(r'<footer\b.*?</footer>', footer, html, flags=re.S)
    is_overview = Path(relative).name in {'overview.html', 'about.html'}
    is_history = 'glpzy-is-now-oneglp/' in relative
    if is_overview or is_history:
        markup = context_markup(relative)
        if 'data-press-context' in html:
            html = re.sub(r'<p\b[^>]*data-press-context[^>]*>.*?</p>', markup, html, flags=re.S)
        elif is_history:
            html = html.replace('<p class="name-safety">', markup + '\n      <p class="name-safety">', 1)
        else:
            html = html.replace('</main>', '<div class="shell">' + markup + '</div></main>', 1)
    return canonicalize_links(relative, html)


def article_markup(locale, article):
    """Editorial identity comes exclusively from shared records, never translations."""
    copy = COPY[locale]
    external_language = escape(article['language'], quote=True)
    publisher = escape(article['publisher'])
    author = ('<p class="press-author"><bdi>' + escape(article['author']) + '</bdi></p>') if article.get('author') else ''
    description = (f'<p class="press-description" data-i18n="{article["descriptionKey"]}">'
                   + ui_text(copy[article['descriptionKey']], locale) + '</p>') if article.get('descriptionKey') else ''
    note = (f'<p class="press-note" data-i18n="{article["noteKey"]}">'
            + ui_text(copy[article['noteKey']], locale) + '</p>') if article.get('noteKey') else ''
    date_key = 'press.published' if article.get('publicationDate') else 'press.checked'
    article_date = article.get('publicationDate') or article['checkedDate']
    record_id = escape(article.get('id', ''), quote=True)
    return f'''<article class="press-article" data-press-record="{record_id}" data-legacy-brand="{str(article['legacyBrand']).lower()}">
      <p class="press-publisher"><bdi>{publisher}</bdi></p>
      <h2 class="press-original-title"><bdi lang="{external_language}" dir="auto">{escape(article['originalTitle'])}</bdi></h2>
      {author}
      <p class="press-meta"><span data-i18n="press.type.{article['coverageType']}">{ui_text(copy['press.type.' + article['coverageType']], locale)}</span> · <span data-i18n="{date_key}">{ui_text(copy[date_key], locale)}</span> <time datetime="{article_date}" data-press-date><bdi>{article_date}</bdi></time></p>
      {description}
      {note}
      <a class="press-read" href="{escape(article['url'], quote=True)}"><span data-i18n="press.readArticle">{ui_text(copy['press.readArticle'], locale)}</span> <bdi>— {publisher}</bdi></a>
    </article>'''

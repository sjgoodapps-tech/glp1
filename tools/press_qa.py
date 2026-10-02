#!/usr/bin/env python3
"""Validate generated Press routes and secondary links across the actual locale registry."""
import argparse
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen
from xml.etree import ElementTree as ET

from build_press_pages import render
from locale_indexing_qa import Head
from press_content import (COPY, DATA, ROOT, RTL, article_markup, locale_of,
                           page_path, page_url, sync_links, validate_data)
from seo_gate_sitemap import SITE


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links, self.h1, self.keys, self.times = [], [], [], []
        self.in_footer = False
        self.current_link = self.current_h1 = None
        self.lang = self.direction = self.title = ''
        self.in_title = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang, self.direction = a.get('lang'), a.get('dir')
        if tag == 'footer':
            self.in_footer = True
        if tag == 'h1':
            self.current_h1 = []
        if tag == 'title':
            self.in_title = True
        if tag == 'a':
            self.current_link = {**a, 'footer': self.in_footer, 'text': ''}
            self.links.append(self.current_link)
        if tag == 'time':
            self.times.append(a.get('datetime'))
        if a.get('data-i18n'):
            self.keys.append(a['data-i18n'])

    def handle_endtag(self, tag):
        if tag == 'footer':
            self.in_footer = False
        if tag == 'a':
            self.current_link = None
        if tag == 'h1' and self.current_h1 is not None:
            self.h1.append(''.join(self.current_h1).strip())
            self.current_h1 = None
        if tag == 'title':
            self.in_title = False

    def handle_data(self, text):
        if self.current_link is not None:
            self.current_link['text'] += text
        if self.current_h1 is not None:
            self.current_h1.append(text)
        if self.in_title:
            self.title += text


def local_target(relative, href):
    url = urlsplit(urljoin(SITE + '/' + relative, href))
    if url.netloc != urlsplit(SITE).netloc or url.scheme not in {'https', 'http'}:
        return None
    target = ROOT / url.path.lstrip('/')
    return target / 'index.html' if url.path.endswith('/') else target


def check_links(relative, page):
    for a in page.links:
        target = local_target(relative, a.get('href', ''))
        assert target is None or target.is_file(), f'{relative}: broken {a.get("href")}'


def check_press(locale, html, duplicate=False):
    relative = page_path(locale, duplicate).as_posix()
    page, head = Page(html), Head(html)
    assert page.lang.lower() == locale
    assert page.direction == ('rtl' if locale in RTL else 'ltr')
    assert page.h1 == [COPY[locale]['press.heading']], f'{locale}: heading'
    assert page.title == COPY[locale]['site.nav.press'] + ' | OneGLP'
    assert 'GLPzy' not in page.title + page.h1[0]
    assert head.canonicals == [page_url(locale)]
    expected = {key: page_url(key) for key in COPY}
    expected['x-default'] = page_url('en')
    assert len(head.alternates) == len(expected) and dict(head.alternates) == expected
    assert head.robots == ['index,follow']
    assert re.search(r'<meta name="description" content="[^"]+">', html)
    assert not re.search(r'>\s*(?:press\.[\w.]+|site\.nav\.press|\{press\})\s*<', html)
    links = [a for a in page.links if a.get('hreflang')]
    assert len(links) == len(COPY)
    assert {a['hreflang']: local_target(relative, a['href']) for a in links} == {
        key: ROOT / page_path(key) for key in COPY}
    footers = [a for a in page.links if a['footer'] and a.get('data-i18n') == 'site.nav.press']
    assert len(footers) == 1 and footers[0]['text'] == COPY[locale]['site.nav.press']
    assert local_target(relative, footers[0]['href']) == ROOT / page_path(locale)
    check_links(relative, page)
    # Every emitted new UI string is looked up from the same static resource.
    assert all(key in COPY[locale] for key in page.keys if key.startswith('press.') or key == 'site.nav.press')
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', help='Also verify routes through a running local HTTP preview')
    parser.add_argument('--fixture-dir', type=Path, help='Write visual QA samples outside the repository, never published')
    args = parser.parse_args()
    validate_data()
    # These first three supplied records must never have their external identity
    # translated, their order changed, or Monj's checked date called publication.
    supplied = [
        ('monj', 'Monj', 'OneGLP: a private GLP-1 tracker for iPhone',
         'https://monj.co.uk/oneglp/'),
        ('startup', 'start-up.ro', 'GLPzy, aplicația pentru monitorizarea tratamentelor folosite în diabetul de tip 2 și controlul greutății',
         'https://start-up.ro/glpzy-aplicatia-pentru-monitorizarea-tratamentelor-folosite-in-diabetul-de-tip-2-si-controlul-greutatii/'),
        ('newmobilelife', 'NewMobileLife / 流動日報', 'GLP-1用藥記錄工具　原價 US $79.99《GLPzy》終生版限時免費',
         'https://www.newmobilelife.com/2026/07/08/glpzyglp-1%E8%A8%98%E9%8C%84-%E9%99%90%E6%99%82%E5%85%8D%E8%B2%BB-2/'),
    ]
    assert [(a['id'], a['publisher'], a['originalTitle'], a['url']) for a in DATA['articles'][:3]] == supplied
    assert DATA['articles'][0]['checkedDate'] == '2026-09-23' and 'publicationDate' not in DATA['articles'][0]
    assert DATA['articles'][1]['author'] == 'Alexandra Ciornei'
    assert [a['publicationDate'] for a in DATA['articles'][1:3]] == ['2026-09-14', '2026-07-08']
    fixture = {'publisher': 'Publicație independentă', 'originalTitle': 'GLPzy: sănătate și tehnologie — 原文',
               'url': 'https://example.com/editorial?original=1&language=ro', 'author': 'Autor Original',
               'publicationDate': '2026-09-14', 'coverageType': 'interview', 'legacyBrand': True, 'language': 'ro'}
    validate_data([fixture])
    sitemap = [n.text for n in ET.parse(ROOT / 'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    press_urls = [url for url in sitemap if urlsplit(url).path.endswith('/press/')]
    assert len(press_urls) == len(COPY) and set(press_urls) == {page_url(key) for key in COPY}
    assert page_url('en').replace('/press/', '/en/press/') not in sitemap
    for locale in COPY:
        html = (ROOT / page_path(locale)).read_text()
        page = check_press(locale, html)
        assert page.times == [a.get('publicationDate') or a['checkedDate'] for a in DATA['articles']]
        cards = re.findall(r'<article class="press-article".*?</article>', html, re.S)
        assert len(cards) == len(DATA['articles'])
        assert 'data-i18n="press.empty"' not in html
        for a, card in zip(DATA['articles'], cards):
            assert f'data-press-record="{a["id"]}"' in card
            assert unescape(re.search(r'<h2[^>]*><bdi[^>]*>(.*?)</bdi></h2>', card, re.S)[1]) == a['originalTitle']
            assert any(link['href'] == a['url'] for link in page.links)
            visible = unescape(re.sub(r'<[^>]*>', '', card))
            assert a['publisher'] in visible
            assert not a.get('author') or a['author'] in visible
            assert COPY[locale][a['descriptionKey']] in visible
            date_key = 'press.published' if a.get('publicationDate') else 'press.checked'
            assert f'data-i18n="{date_key}"' in card
            if a.get('noteKey'):
                assert COPY[locale][a['noteKey']] in visible
            assert 'Taiwan' not in card and 'Taiwanese' not in card
        assert 'press.published' not in cards[0]
        # Exercise mixed-script editorial identity independently of the real records.
        # This fixture never becomes a factual press record.
        sample = render(locale, articles=[fixture])
        if args.fixture_dir:
            directory = args.fixture_dir.resolve()
            assert ROOT not in directory.parents and directory != ROOT, 'Fixtures must stay outside the repository'
            directory.mkdir(parents=True, exist_ok=True)
            base = urljoin(args.base_url or 'http://127.0.0.1:4198/', page_path(locale).as_posix())
            preview = sample.replace('<head>', '<head>\n<base href="' + base + '">', 1)
            (directory / (locale + '.html')).write_text(preview)
        assert fixture['originalTitle'] in unescape(sample)
        assert fixture['author'] in unescape(sample) and fixture['publisher'] in unescape(sample)
        assert any(a['href'] == fixture['url'] for a in Page(sample).links)
        assert 'nofollow' not in sample
        assert '<bdi lang="ro" dir="auto">' in sample
        assert Page(sample).times == ['2026-09-14']
        for contextual in [('' if locale == 'en' else locale + '/') + 'overview.html',
                           ('' if locale == 'en' else locale + '/') + 'glpzy-is-now-oneglp/index.html']:
            context_html = (ROOT / contextual).read_text()
            assert context_html.count('data-press-context') == 1, contextual
            anchor = [a for a in Page(context_html).links if not a['footer'] and a.get('data-i18n') == 'site.nav.press']
            assert len(anchor) == 1 and local_target(contextual, anchor[0]['href']) == ROOT / page_path(locale)
        if args.base_url:
            route = page_path(locale).as_posix().removesuffix('index.html')
            with urlopen(urljoin(args.base_url, route), timeout=10) as response:
                assert response.status == 200
                check_press(locale, response.read().decode())
    check_press('en', (ROOT / page_path('en', True)).read_text(), True)
    footer_count = 0
    for path in ROOT.rglob('*.html'):
        if '.git' in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        html = path.read_text()
        page = Page(html)
        footer = [a for a in page.links if a['footer'] and a.get('data-i18n') == 'site.nav.press']
        assert len(footer) == 1, f'{relative}: missing/duplicate footer Press link'
        locale = locale_of(relative)
        assert footer[0]['text'] == COPY[locale]['site.nav.press'], relative
        assert local_target(relative, footer[0]['href']) == ROOT / page_path(locale), relative
        assert sync_links(relative, html) == html, f'{relative}: link sync is not idempotent'
        footer_count += 1
    print(f'PASS: {len(COPY)} locales + English alias; {footer_count} footer links; overview/history links; '
          'all Press internal links, metadata, reciprocal hreflang, sitemap, exact editorial identity and RTL isolation')
    print(f'Actual press records: {len(DATA["articles"])}; fixture tested separately, never published')


if __name__ == '__main__':
    main()

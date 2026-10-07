#!/usr/bin/env python3
"""Audit static crawl paths and distinguish same-locale page intents."""
import json
from collections import defaultdict, deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from canonical_links import canonical_href, canonicalize_links
from search_content import COPY, sync_search_content
from seo_gate_sitemap import ROOT, SITE, LOCALE_DIRS, html_files, rel, url_for_path


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links, self.title, self.description, self.canonical = [], '', '', ''
        self.in_title = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and attrs.get('href'): self.links.append(attrs['href'])
        if tag == 'title': self.in_title = True
        if tag == 'meta' and attrs.get('name') == 'description': self.description = attrs.get('content', '')
        if tag == 'link' and attrs.get('rel') == 'canonical': self.canonical = attrs.get('href', '')

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False

    def handle_data(self, value):
        if self.in_title: self.title += value


def regressions():
    assert canonical_href('fr/support.html', '../en/index.html?ref=help#features') == '../?ref=help#features'
    assert canonical_href('press/index.html', '../fr/index.html#premium') == '../fr/#premium'
    assert canonical_href('en/index.html', 'index.html') == '../'
    assert canonical_href('ar/index.html', '#features') == '#features'
    assert canonical_href('index.html', '?ref=home') == '?ref=home'
    for href in ('mailto:hello@example.com', 'https://example.com/index.html', 'assets/screen-history.png', 'missing.html'):
        assert canonical_href('index.html', href) == href
    sample = '<a data-href="index.html" href="en/index.html?x=1&amp;y=2#faq">English</a>'
    fixed = canonicalize_links('index.html', sample)
    assert fixed == '<a data-href="index.html" href="./?x=1&amp;y=2#faq">English</a>'
    assert canonicalize_links('index.html', fixed) == fixed


def audit():
    assert set(COPY) == LOCALE_DIRS, 'Incomplete search-copy locale registry'
    pages, sources = {}, {}
    for path in html_files():
        relative = rel(path)
        sources[relative] = path.read_text()
        pages[relative] = Page(sources[relative])
    routes = {urlsplit(url_for_path(path)).path: path for path in pages}
    routes.update({'/' + path: path for path in pages})
    graph = {path: set() for path in pages}
    failures, alias_count = [], 0
    for relative, page in pages.items():
        for href in page.links:
            if href.startswith(('#', '?')): continue
            url = urlsplit(urljoin(SITE + '/' + relative, href))
            if url.hostname != 'oneglp.app': continue
            target = routes.get(url.path)
            if target:
                graph[relative].add(target)
                if url.path != urlsplit(pages[target].canonical).path:
                    alias_count += 1
                    failures.append(relative + ': alias link ' + href)
    reachable, queue = {'index.html'}, deque(['index.html'])
    while queue:
        for target in graph[queue.popleft()]:
            if target not in reachable:
                reachable.add(target)
                queue.append(target)
    canonical = {relative for relative, page in pages.items() if page.canonical == url_for_path(relative)}
    orphans = sorted(canonical - reachable)
    failures.extend('Unreachable canonical: ' + path for path in orphans)
    metadata_groups = defaultdict(list)
    for relative in canonical:
        first = relative.split('/', 1)[0]
        locale = first if first in LOCALE_DIRS else 'en'
        for field in ('title', 'description'):
            value = getattr(pages[relative], field)
            if value:
                metadata_groups[locale, field, value].append(relative)
    collisions = [paths for paths in metadata_groups.values() if len(paths) > 1]
    failures.extend('Within-locale metadata collision: ' + ', '.join(paths) for paths in collisions)
    updated = 0
    for locale in sorted(LOCALE_DIRS - {'en', 'en-gb'}):
        pairs = [('index.html', 'glp1-weight-dose-symptom-tracker.html'),
                 ('privacy.html', 'local-first-private-glp-tracker.html'),
                 ('support.html', 'overview.html')]
        for left, right in pairs:
            a, b = pages[locale + '/' + left], pages[locale + '/' + right]
            if a.title == b.title or a.description == b.description:
                failures.append(locale + ': colliding page metadata ' + left + ' / ' + right)
        for family in ('privacy.html', 'local-first-private-glp-tracker.html', 'glp1-weight-dose-symptom-tracker.html', 'overview.html'):
            relative = locale + '/' + family
            if sync_search_content(relative, sources[relative]) != sources[relative]:
                failures.append(relative + ': search-copy drift')
            updated += 1
        source = sources[locale + '/local-first-private-glp-tracker.html']
        if 'data-i18n="search.privateWorkflow"' not in source or 'data-private-workflow-cards' not in source:
            failures.append(locale + ': missing crawler-visible private workflow')
    return failures, {'canonical_pages': len(canonical), 'unreachable_canonical_pages': orphans,
                      'alias_navigation_links': alias_count, 'localized_metadata_pages': updated,
                      'within_locale_metadata_collisions': len(collisions)}


if __name__ == '__main__':
    regressions()
    failures, stats = audit()
    for failure in failures[:30]: print(failure)
    print(('FAIL' if failures else 'PASS') + ': ' + json.dumps(stats))
    raise SystemExit(bool(failures))

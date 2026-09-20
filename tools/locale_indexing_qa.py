#!/usr/bin/env python3
"""Check every published page, including locales with unreviewed copy."""
import json
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET
from seo_gate_sitemap import LOCALE_DIRS, SITE, set_canonical, set_hreflang, set_robots

ROOT = Path(__file__).resolve().parents[1]


class Head(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.robots, self.canonicals, self.alternates = [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and a.get('name', '').lower() == 'robots':
            self.robots.append(a.get('content', '').lower().replace(' ', ''))
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonicals.append(a.get('href'))
        if tag == 'link' and a.get('rel') == 'alternate' and 'hreflang' in a:
            self.alternates.append((a['hreflang'].lower(), a.get('href')))


def url(relative):
    relative = relative[:-10] if relative.endswith('index.html') else relative
    return SITE + '/' + relative


def audit(root=ROOT):
    failures, pages, families = [], {}, {}
    policy = json.loads((root / 'data/locale-indexing.json').read_text())
    if policy.get('index_translations') is not True:
        failures.append('Policy must keep every published translation indexable')
    for path in sorted(root.rglob('*.html')):
        if '.git' in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        first, _, rest = rel.partition('/')
        locale = first if first in LOCALE_DIRS and rest else 'en'
        family = rest if first in LOCALE_DIRS and rest else rel
        duplicate = first == 'en' and (root / rest).is_file()
        canonical = url(rest if duplicate else rel)
        head = Head(path.read_text())
        pages[rel] = (head, canonical, duplicate, family)
        if not duplicate:
            families.setdefault(family, {})[locale] = canonical
    sitemap = ET.parse(root / 'sitemap.xml')
    entries = [n.text for n in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    expected_urls = {canonical for _, canonical, duplicate, _ in pages.values() if not duplicate}
    if len(entries) != len(set(entries)):
        failures.append('Duplicate sitemap URLs')
    if set(entries) != expected_urls:
        failures.append(f'Sitemap mismatch: {len(expected_urls - set(entries))} missing, {len(set(entries) - expected_urls)} unexpected')
    for rel, (head, canonical, _, family) in pages.items():
        if head.robots != ['index,follow']:
            failures.append(f'{rel}: expected exactly one index,follow robots tag, got {head.robots}')
        if head.canonicals != [canonical]:
            failures.append(f'{rel}: incorrect canonical {head.canonicals}')
        expected = dict(families[family])
        if 'en' in expected:
            expected['x-default'] = expected['en']
        if len(head.alternates) != len(expected) or dict(head.alternates) != expected:
            failures.append(f'{rel}: incomplete, duplicate or nonreciprocal language links')
    return failures


def regression_checks():
    sample = '<head>\n<meta name="robots" content="noindex,follow">\n<meta content="noindex" name="robots">\n</head><p>known copy error</p>'
    updated = set_robots(sample, 'index,follow')
    assert Head(updated).robots == ['index,follow']
    assert set_robots(updated, 'index,follow') == updated
    links = {'en': SITE + '/', 'ar': SITE + '/ar/', 'x-default': SITE + '/'}
    updated = set_hreflang(updated, links)
    assert dict(Head(updated).alternates) == links
    assert set_hreflang(updated, links) == updated
    duplicate = '<head><link href="https://www.glpzy.app/fr/privacy/" rel="canonical"/><link rel="canonical" href="wrong"><meta content="wrong" property="og:url"/></head>'
    fixed = set_canonical(duplicate, SITE + '/fr/privacy.html')
    assert Head(fixed).canonicals == [SITE + '/fr/privacy.html']
    assert set_canonical(fixed, SITE + '/fr/privacy.html') == fixed


if __name__ == '__main__':
    regression_checks()
    problems = audit()
    for problem in problems[:50]:
        print(problem)
    print(f'{"FAIL" if problems else "PASS"}: all-page indexability, complete sitemap, canonicals and reciprocal hreflang; {len(problems)} issue(s)')
    raise SystemExit(bool(problems))

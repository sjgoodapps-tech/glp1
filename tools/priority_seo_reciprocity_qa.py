#!/usr/bin/env python3
"""Read-only QA: priority page sitemap and hreflang reciprocity.
No writes. Run at repository root with python3 tools/priority_seo_reciprocity_qa.py.
"""
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ('es-es', 'es-mx', 'de', 'fr', 'fr-ca', 'pt-br', 'pt-pt',
           'ar', 'zh-hans', 'zh-hant', 'ja', 'ko', 'hi', 'it')
SEO = ('apple-health-weight-loss-injection-tracker.html',
       'glp1-dose-reminder-app.html', 'glp1-progress-photo-tracker.html',
       'glp1-side-effect-symptom-tracker.html', 'glp1-weight-tracker.html',
       'weight-loss-injection-tracker.html')
BASE = 'https://oneglp.app/'

class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.alts = {}
        self.canon = []
    def handle_starttag(self, tag, attrs):
        if tag != 'link': return
        a = dict(attrs)
        if a.get('rel') == 'alternate' and a.get('hreflang'):
            key = a['hreflang'].lower()
            self.alts.setdefault(key, []).append(a.get('href'))
        if a.get('rel') == 'canonical': self.canon.append(a.get('href'))

def audit(root=ROOT):
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = {node.text for node in ET.parse(root / 'sitemap.xml').findall('.//s:loc', ns)}
    errors = []
    expected_locales = ('en',) + LOCALES
    for page in SEO:
        expected = {'en': BASE + page, **{l:BASE+l+'/'+page for l in LOCALES}}
        for loc, url in expected.items():
            path = root / page if loc == 'en' else root / loc / page
            if not path.is_file():
                errors.append(f'{loc}/{page}: missing file');continue
            if url not in urls:
                errors.append(f'{loc}/{page}: absent from sitemap')
            reader = Head()
            reader.feed(path.read_text(encoding='utf-8'))
            if reader.canon != [url]:
                errors.append(f'{loc}/{page}: canonical mismatch: {reader.canon}')
            for other in expected_locales:
                if reader.alts.get(other) != [expected[other]]:
                    errors.append(f'{loc}/{page}: missing or wrong reciprocal {other}: {reader.alts.get(other)}')
            if reader.alts.get('x-default') != [expected['en']]:
                errors.append(f'{loc}/{page}: x-default mismatch')
    return errors

def main():
    issues = audit()
    print(f'Priority SEO sitemap and hreflang: {len(SEO)* (len(LOCALES)+1)} pages checked, {len(issues)} defects')
    for issue in issues: print('FAIL',issue)
    return 1 if issues else 0
if __name__ == '__main__':
    raise SystemExit(main())
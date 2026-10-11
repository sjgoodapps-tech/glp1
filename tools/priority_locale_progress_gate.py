#!/usr/bin/env python3
"""Read-only inventory/gate for the 14 priority OneGLP website locales.

Structural checks do not confer semantic, medical, legal, native, or visual approval.
"""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

PRIORITY = ('es-es', 'es-mx', 'de', 'fr', 'fr-ca', 'pt-br', 'pt-pt',
            'ar', 'zh-hans', 'zh-hant', 'ja', 'ko', 'hi', 'it')
ESSENTIAL = ('privacy.html', 'data-rights.html', 'terms.html',
             'medical-safety.html', 'methodology.html', 'support.html')
SEO = ('apple-health-weight-loss-injection-tracker.html',
       'glp1-dose-reminder-app.html', 'glp1-progress-photo-tracker.html',
       'glp1-side-effect-symptom-tracker.html', 'glp1-weight-tracker.html',
       'weight-loss-injection-tracker.html')

class Tags(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.main_count = 0
        self.inside_main = 0
        self.counts = {x: 0 for x in ('section', 'p', 'li', 'table', 'tr', 'th', 'td')}
        self.reference_urls = set()
        self.links = []
        self.lang = None
        self.direction = None
        self.canonicals = []
        self.hreflangs = {}
        self.titles = 0
        self.descriptions = 0
        self.robottags = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'html':
            self.lang = d.get('lang')
            self.direction = d.get('dir')
        if tag == 'main':
            self.main_count += 1
            self.inside_main += 1
        if self.inside_main and tag in self.counts:
            self.counts[tag] += 1
        if tag == 'title':
            self.titles += 1
        if tag == 'meta':
            if d.get('name') == 'description':
                self.descriptions += 1
            if d.get('name') == 'robots':
                self.robottags.append(d.get('content','').lower())
        if tag == 'link':
            if d.get('rel') == 'canonical':
                self.canonicals.append(d.get('href'))
            if d.get('rel') == 'alternate' and d.get('hreflang'):
                self.hreflangs[d['hreflang'].lower()] = d.get('href')
        if tag == 'a':
            href = d.get('href') or ''
            self.links.append(href)
            if self.inside_main:
                u=urlparse(href)
                if u.scheme in ('http','https') and u.netloc not in ('oneglp.app','www.oneglp.app'):
                    self.reference_urls.add(href)
    def handle_endtag(self, tag):
        if tag == 'main' and self.inside_main:
            self.inside_main -= 1

def parse(path):
    p=Tags()
    p.feed(path.read_text(encoding='utf-8'))
    p.close()
    return p

def audit(root):
    baseline={name:parse(root/name) if (root/name).is_file() else None for name in ESSENTIAL+SEO}
    source_errors=[p for p,obj in baseline.items() if obj is None or obj.main_count != 1]
    result={'source_errors':source_errors, 'locales':{},
            'accepted':False, 'meaning_and_legal_review':'not certified',
            'browser_accessibility_rtl_review':'not certified'}
    for locale in PRIORITY:
        items={}
        for page in ESSENTIAL+SEO:
            f=root/locale/page
            if not f.is_file():
                items[page]={'status':'missing'}
                continue
            p=parse(f)
            issues=[]
            if p.main_count!=1: issues.append('main_count')
            if not p.lang or p.lang.lower()!=locale: issues.append('lang')
            if locale=='ar' and p.direction!='rtl': issues.append('rtl')
            canonical='https://oneglp.app/'+locale+'/'+page
            if p.canonicals != [canonical]: issues.append('canonical')
            if p.titles != 1 or p.descriptions != 1: issues.append('metadata')
            if any('noindex' in x for x in p.robottags): issues.append('noindex')
            source=baseline[page]
            if source is not None:
                if page in ESSENTIAL:
                    for tag,n in source.counts.items():
                        if p.counts[tag]<n: issues.append('missing_'+tag)
                    if not source.reference_urls.issubset(p.reference_urls):
                        issues.append('missing_references')
                else:
                    for tag in ('section','p','li'):
                        if p.counts[tag] < source.counts[tag]: issues.append('missing_'+tag)
            items[page]={'status':'present' if not issues else 'defective',
                         'issues':sorted(set(issues))}
        result['locales'][locale]={
            'essential_ok':sum(items[p]['status']=='present' for p in ESSENTIAL),
            'seo_ok':sum(items[p]['status']=='present' for p in SEO),
            'pages':items}
    result['structural_pass']=not source_errors and all(
        d['essential_ok']==6 and d['seo_ok']==6 for d in result['locales'].values())
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--output',type=Path)
    p.add_argument('--gate',action='store_true')
    args=p.parse_args()
    result=audit(args.root)
    payload=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output: args.output.write_text(payload+'\n',encoding='utf-8')
    else: print(payload)
    if args.gate and not result['structural_pass']: return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
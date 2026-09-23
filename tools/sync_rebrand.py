#!/usr/bin/env python3
"""Apply the draft display brand while preserving URLs, legal identity and keys."""
import argparse
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/rebrand.json').read_text())
FACTS = json.loads((ROOT / 'data/product-facts.json').read_text())
REBRAND_PAGE = json.loads((ROOT / 'data/rebrand-page.json').read_text())
PUBLISHER_ID = FACTS['site_url'].rstrip('/') + '/#publisher'
LEGACY_PUBLISHER_ID = FACTS['site_url'].rstrip('/') + '/#organization'
SCHEMA_BLOCK = re.compile(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', re.S | re.I)


class MetaTag(HTMLParser):
    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)


def social_metadata(match):
    parser = MetaTag()
    parser.feed(match[0])
    attrs = parser.attrs
    key = attrs.get('property', attrs.get('name'))
    values = {
        'og:image': FACTS['site_url'].rstrip('/') + '/' + DATA['share_image'],
        'twitter:image': FACTS['site_url'].rstrip('/') + '/' + DATA['share_image'],
        'og:image:width': '512', 'og:image:height': '512',
        'og:image:alt': DATA['name'], 'twitter:image:alt': DATA['name'],
        'twitter:card': 'summary',
    }
    if key not in values:
        return match[0]
    attribute = 'property' if 'property' in attrs else 'name'
    return f'<meta {attribute}="{key}" content="{html.escape(values[key], quote=True)}">'


def correct_schema_identity(value):
    if isinstance(value, list):
        for item in value:
            correct_schema_identity(item)
    elif isinstance(value, dict):
        kinds = value.get('@type', [])
        kinds = [kinds] if isinstance(kinds, str) else kinds
        own_names = {DATA['previous_name'], DATA['name'], FACTS['app_name']}
        own_publisher = (value.get('@id') in {LEGACY_PUBLISHER_ID, PUBLISHER_ID}
                         or value.get('name') in own_names | {FACTS['publisher']})
        if value.get('@id') == LEGACY_PUBLISHER_ID:
            value['@id'] = PUBLISHER_ID
        if set(kinds) & {'Organization', 'Person'} and own_publisher:
            value['@type'] = FACTS['publisher_type']
            value['@id'] = PUBLISHER_ID
            value['name'] = FACTS['publisher']
            # App artwork and an App Store listing identify the app, not a person.
            value.pop('logo', None)
            value.pop('sameAs', None)
        elif set(kinds) & {'WebSite', 'SoftwareApplication', 'MobileApplication'}:
            if value.get('name') in own_names:
                value['name'] = FACTS['app_name']
                if set(kinds) & {'SoftwareApplication', 'MobileApplication'}:
                    value['alternateName'] = DATA['previous_name']
                    value['subjectOf'] = {'@id': FACTS['site_url'].rstrip('/') + '/' + REBRAND_PAGE['slug'] + '/#webpage'}
        for child in value.values():
            correct_schema_identity(child)


def correct_schema_block(match):
    value = json.loads(match[2])
    before = json.dumps(value, ensure_ascii=False)
    correct_schema_identity(value)
    if json.dumps(value, ensure_ascii=False) == before:
        return match.group()
    body = json.dumps(value, ensure_ascii=False, indent=2 if '\n' in match[2] else None)
    body = body.replace('<', '\\u003c')
    if '\n' in match[2]:
        body = '\n' + body + '\n'
    return match[1] + body + match[3]


class HeaderEnd(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.lines = source.splitlines(keepends=True)
        self.depth = 0
        self.inside = False
        self.end = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if 'topbar' in dict(attrs).get('class', '').split() and self.end is None:
                self.inside = True
            if self.inside:
                self.depth += 1

    def handle_endtag(self, tag):
        if tag == 'div' and self.inside:
            self.depth -= 1
            if self.depth == 0:
                line, col = self.getpos()
                self.end = sum(map(len, self.lines[:line - 1])) + col + len('</div>')
                self.inside = False


def transform(path, text):
    rel = path.relative_to(ROOT)
    if rel.name == 'index.html' and rel.parent.name == REBRAND_PAGE['slug']:
        # Historical names on these pages are maintained by build_rebrand_pages.py.
        return text
    locale = rel.parts[0] if rel.parts[0] in DATA['notices'] else 'en'
    # The owner confirmed an individual publisher, not a GLPzy trading entity.
    protected = []
    def protect(match):
        protected.append(match.group())
        return f'__PRESERVED_BRAND_{len(protected)-1}__'
    text = text.replace('Steven Good, trading as GLPzy,', 'Steven Good')
    text = text.replace('Steven Good, trading as OneGLP,', 'Steven Good')
    text = re.sub(r'<img\b[^>]*>', protect, text)
    text = re.sub(r'<p\b[^>]*class="rebrand-notice"[^>]*>.*?</p>', '', text, flags=re.S)
    text = re.sub(r'<p\b[^>]*data-i18n="site.rebrand.continuity"[^>]*>.*?</p>', '', text, flags=re.S)
    text = text.replace('GLPzy', DATA['name'])
    for i, value in enumerate(protected):
        text = text.replace(f'__PRESERVED_BRAND_{i}__', value)
    text = SCHEMA_BLOCK.sub(correct_schema_block, text)
    text = re.sub(r'<meta\b[^>]*>', social_metadata, text, flags=re.I)
    text = text.replace('Published by ' + DATA['name'] + '.',
                        'Published by ' + html.escape(FACTS['publisher']) + '.')
    prefix = '../' * (len(rel.parts) - 1)
    text = re.sub(r'(?:\.\./)*assets/(favicon-(?:16x16|32x32)\.png|apple-touch-icon\.png)', lambda m: prefix + 'assets/oneglp/' + m[1], text)
    # Schema uses absolute logo URLs, unlike link elements.
    site = FACTS['site_url'].rstrip('/')
    text = text.replace(site + '/' + prefix + 'assets/oneglp/', site + '/assets/oneglp/')
    text = re.sub(r'(site-(?:config|cta|preflight)\.js)(?:\?v=[^"\s<>]+)?', r'\1?v=20260920-oneglp-conversion', text)
    text = re.sub(r'styles\.css(?:\?v=[^"\s<>]+)?', 'styles.css?v=20260920-screens-v5', text)
    end = HeaderEnd(text).end
    if end is None:
        raise ValueError(f'No topbar in {rel}')
    message = html.escape(DATA['notices'][locale])
    for name in (DATA['previous_name'], DATA['name']):
        message = message.replace(name, f'<bdi>{name}</bdi>')
    notice_locale = locale
    if notice_locale in REBRAND_PAGE['translations']:
        target = ROOT / ('' if notice_locale == 'en' else notice_locale) / REBRAND_PAGE['slug'] / 'index.html'
        href = html.escape(os.path.relpath(target, path.parent), quote=True)
        message = f'<a href="{href}" data-rebrand-link>{message}</a>'
    notice = f'<p class="rebrand-notice" data-i18n="site.rebrand.notice">{message}</p>'
    if rel.as_posix() in ('support.html', 'en/support.html', 'en-gb/support.html'):
        notice += '<p class="rebrand-continuity" data-i18n="site.rebrand.continuity">' + html.escape(DATA['continuity']) + '</p>'
    return text[:end] + notice + text[end:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    changed = []
    for path in sorted(ROOT.rglob('*.html')):
        before = path.read_text()
        after = transform(path, before)
        if before != after:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(after)
    print(f'Rebrand {"drift" if args.check else "updated"}: {len(changed)} pages')
    return int(args.check and bool(changed))


if __name__ == '__main__':
    raise SystemExit(main())

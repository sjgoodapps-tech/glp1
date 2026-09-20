#!/usr/bin/env python3
"""Check screenshot identity, page purpose, translated captions and asset coverage."""
import argparse
import hashlib
import json
import re
import struct
from html import unescape
from pathlib import Path

from localisation_qa import LOCALE_DIRS
from refresh_screenshots import (ROOT, MANIFEST, COPY, TRANSLATIONS, SLOTS, LEGACY,
                                Document, caption, locale_for, page_hero, refreshed_html, MOBILE_CHART_PLACEHOLDER)


def visible(node, text):
    return unescape(re.sub('<[^>]+>', '', text[node.opening_end:node.end].rsplit('</', 1)[0])).strip()


def audit():
    errors = []
    if set(TRANSLATIONS) != LOCALE_DIRS:
        errors.append('Screenshot copy does not cover every published locale')
    for locale, values in COPY['translations'].items():
        if len(values) != len(COPY['keys']) or not all(values):
            errors.append(f'{locale}: missing screenshot translation')
        if locale not in {'en', 'en-gb'} and any(a == b for a, b in zip(values, COPY['translations']['en'])):
            errors.append(f'{locale}: English screenshot-copy fallback')
    for slot, source in MANIFEST['source_assets'].items():
        path = ROOT / source
        if not path.is_file():
            errors.append(f'{slot}: missing original')
            continue
        dims = struct.unpack('>II', path.read_bytes()[16:24])
        if dims != (SLOTS[slot]['width'], SLOTS[slot]['height']):
            errors.append(f'{slot}: incorrect source dimensions')
        for width in MANIFEST['widths']:
            for fmt in ('avif', 'webp'):
                variant = ROOT / 'assets/responsive' / f'seo-{path.stem}-{width}.{fmt}'
                if not variant.is_file() or not variant.stat().st_size:
                    errors.append(f'{slot}: missing {width}px {fmt}')
    count = 0
    for path in sorted(ROOT.rglob('*.html')):
        if '.git' in path.parts:
            continue
        rel, text = path.relative_to(ROOT).as_posix(), path.read_text()
        locale = locale_for(rel)
        doc = Document(text)
        count += 1
        if any('assets/' + old in text or 'assets/responsive/seo-' + Path(old).stem in text for old in LEGACY) or 'assets/responsive/homepage-' in text:
            errors.append(f'{rel}: legacy screenshot reference')
        for node in doc.nodes:
            slot = node.attrs.get('data-image-slot')
            if slot:
                image = next((n for n in node.children if n.tag == 'img'), None)
                expected = 'OneGLP: ' + caption(slot, locale)
                if not image or image.attrs.get('alt') != expected:
                    errors.append(f'{rel}: incorrect translated alt for {slot}')
                if not image or image.attrs.get('width') != '1320' or image.attrs.get('height') != '2868':
                    errors.append(f'{rel}: missing image dimensions for {slot}')
                if image and image.attrs.get('loading') not in {'eager', 'lazy'}:
                    errors.append(f'{rel}: missing image loading priority')
                for source in [n for n in node.children if n.tag in {'source', 'img'}]:
                    if source.attrs.get('srcset', '').startswith('data:image/gif;'):
                        if source.attrs.get('srcset') != MOBILE_CHART_PLACEHOLDER or slot != 'weight' or source.attrs.get('media') != '(max-width: 720px)' or not node.ancestor(lambda n: n.has_class('hero-screens')):
                            errors.append(f'{rel}: unexpected empty screenshot source')
                        continue
                    urls = [source.attrs['src']] if source.tag == 'img' else [item.strip().split()[0] for item in source.attrs.get('srcset', '').split(',')]
                    for url in urls:
                        if not (path.parent / url).is_file():
                            errors.append(f'{rel}: missing served image {url}')
            key = node.attrs.get('data-i18n', '')
            if key.startswith('screens.'):
                if key.endswith('.caption'):
                    expected = caption(key.split('.')[1], locale)
                elif key.startswith('screens.hero.'):
                    expected = TRANSLATIONS[locale][SLOTS[key.split('.')[2]]['copy_key']]
                else:
                    expected = TRANSLATIONS[locale][key.split('.')[1]]
                if visible(node, text) != expected:
                    errors.append(f'{rel}: caption drift: {key}')
        hero = doc.first(lambda n: n.has_class('marketing-hero'))
        if hero:
            home = path.name == 'index.html' and (path.parent == ROOT or path.parent.name in TRANSLATIONS)
            composite = home or rel == 'free-lifetime/index.html'
            expected = ['today', 'before-after', 'weight'] if composite else [page_hero(path.name)] if page_hero(path.name) else []
            actual = [n.attrs['data-image-slot'] for n in doc.nodes if n.inside(hero) and 'data-image-slot' in n.attrs]
            if actual != expected:
                errors.append(f'{rel}: image does not match page purpose: {actual} != {expected}')
        if rel in MANIFEST['page_slots']:
            slots = [n.attrs['data-screenshot-slot'] for n in doc.nodes if 'data-screenshot-slot' in n.attrs]
            if slots != MANIFEST['page_slots'][rel]:
                errors.append(f'{rel}: screenshot section differs from the approved map')
        if any('data-image-slot' in n.attrs for n in doc.nodes) and 'data-i18n="screens.note"' not in text:
            errors.append(f'{rel}: missing screenshot-language note')
        if refreshed_html(rel, text) != text:
            errors.append(f'{rel}: screenshot rewrite is not idempotent')
    print(f'Checked {count} HTML pages, {len(TRANSLATIONS)} locales and {len(SLOTS)} screenshot originals.')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protected-snapshot', type=Path)
    args = parser.parse_args()
    errors = audit()
    if args.protected_snapshot:
        hashes = json.loads(args.protected_snapshot.read_text())
        for rel, expected in hashes.items():
            if hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != expected:
                errors.append(f'Protected original modified: {rel}')
        print(f'Checked {len(hashes)} pre-existing PNG changes against the pre-task hashes.')
    if errors:
        print('\n'.join(errors))
        return 1
    print('PASS: correct page/image mapping, static translated captions and alt text, responsive assets, no legacy references and repeatable generation.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

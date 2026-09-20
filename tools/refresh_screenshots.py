#!/usr/bin/env python3
"""Render approved screenshots and keyed captions without reformatting static pages."""
import argparse
import json
import re
from html import escape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'data/screenshot-manifest.json').read_text())
COPY = json.loads((ROOT / 'data/screenshot-copy.json').read_text())
TRANSLATIONS = {locale: dict(zip(COPY['keys'], values)) for locale, values in COPY['translations'].items()}
SLOTS = {slot['slot']: slot for slot in MANIFEST['slots']}
VERSION = '20260920-screens-v5'
MOBILE_CHART_PLACEHOLDER = 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs='
LEGACY = {'en-hero-sales-wow.png', 'en-screen-advanced-graphs.png', 'en-screen-dashboard.png',
          'en-screen-global-coverage.png', 'en-screen-medication-coverage.png', 'en-screen-photos-export.png',
          'en-screen-projections.png', 'en-screen-quick-logging.png', 'hero-collage.png', 'screen-graphs.png',
          'screen-history.png', 'screen-import.png', 'screen-insights.png', 'screen-recap.png',
          'screen-settings.png', 'screen-welcome.png', 'setup-pair.png'}
TEXT_ONLY = {'privacy.html', 'terms.html', 'support.html', 'data-rights.html', 'overview.html',
             'languages.html', 'local-first-private-glp-tracker.html', 'apple-health-glp-tracker.html',
             'apple-health-weight-loss-injection-tracker.html'}


class Node:
    def __init__(self, tag, attrs, start, opening_end, parent=None):
        self.tag, self.attrs, self.start, self.opening_end = tag, dict(attrs), start, opening_end
        self.end = opening_end
        self.parent, self.children = parent, []

    def has_class(self, name):
        return name in self.attrs.get('class', '').split()

    def inside(self, node):
        return node.start <= self.start and self.end <= node.end

    def ancestor(self, predicate):
        node = self.parent
        while node:
            if predicate(node):
                return node
            node = node.parent
        return None


class Document(HTMLParser):
    """Use parsed element spans so only intended elements change, not whole files."""
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text, self.nodes, self.stack = text, [], []
        self.offsets = [0]
        for line in text.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.feed(text)

    def position(self):
        row, col = self.getpos()
        return self.offsets[row - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.position()
        node = Node(tag, attrs, start, start + len(self.get_starttag_text()), self.stack[-1] if self.stack else None)
        if node.parent:
            node.parent.children.append(node)
        self.nodes.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                end = self.text.index('>', self.position()) + 1
                for node in self.stack[index:]:
                    node.end = end
                del self.stack[index:]
                break

    def first(self, predicate):
        return next((n for n in self.nodes if predicate(n)), None)


def apply_edits(text, edits):
    edits = sorted(edits, key=lambda edit: (edit[0], -edit[1]))
    selected = []
    for edit in edits:
        if selected and edit[0] < selected[-1][1]:
            if edit[1] <= selected[-1][1]:
                continue
            raise ValueError('Overlapping screenshot edits')
        selected.append(edit)
    for start, end, replacement in reversed(selected):
        text = text[:start] + replacement + text[end:]
    return text


def locale_for(path):
    first = Path(path).parts[0]
    return first if first in TRANSLATIONS else 'en'


def caption(slot, locale):
    item = SLOTS[slot]
    if locale in {'en', 'en-gb'}:
        return item['caption']
    return TRANSLATIONS[locale][item['copy_key']]


def responsive_picture(slot, prefix='', locale='en', loading='lazy', priority=False, sizes=None, class_name='responsive-picture', desktop_only=False):
    item = SLOTS[slot]
    stem = Path(MANIFEST['source_assets'][slot]).stem
    base = f'{prefix}assets/responsive/seo-{stem}'
    sizes = sizes or '(max-width: 720px) min(78vw, 280px), 270px'
    alt = 'OneGLP: ' + caption(slot, locale)
    sources = '\n'.join(f'<source type="image/{fmt}" srcset="' + ', '.join(f'{base}-{w}.{fmt} {w}w' for w in MANIFEST['widths']) + f'" sizes="{escape(sizes)}">' for fmt in ('avif', 'webp'))
    if desktop_only:
        # A local empty source avoids downloading the hidden desktop chart on mobile.
        sources = f'<source media="(max-width: 720px)" srcset="{MOBILE_CHART_PLACEHOLDER}">' + sources
    fetch = ' fetchpriority="high"' if priority else ''
    return (f'<picture class="{class_name}" data-image-slot="{slot}">{sources}'
            f'<img src="{base}-720.webp" width="{item["width"]}" height="{item["height"]}" '
            f'loading="{loading}" decoding="async"{fetch} data-i18n-alt="screens.{slot}.alt" alt="{escape(alt, quote=True)}"></picture>')


def figure(slot, prefix='', locale='en', context='detail'):
    item = SLOTS[slot]
    safety = ''
    if item['safety_caption_required'] and locale in {'en', 'en-gb'}:
        safety = '<p class="shot-safety">Estimated Exposure is a personal tracking estimate, not measured blood concentration. Do not use it to guide dosing.</p>'
    stem = Path(MANIFEST['source_assets'][slot]).stem
    label = TRANSLATIONS[locale]['enlarge']
    return (f'<figure class="website-shot" data-screenshot-slot="{slot}" data-image-refresh="v5">'
            + responsive_picture(slot, prefix, locale)
            + f'<figcaption data-i18n="screens.{slot}.caption">{escape(caption(slot, locale))}</figcaption>' + safety
            + f'<a class="shot-enlarge" href="{prefix}assets/responsive/seo-{stem}-1320.webp" '
            f'aria-label="{escape(label + ": " + caption(slot, locale), quote=True)}" data-i18n="screens.enlarge">{escape(label)}</a></figure>')


def language_note(locale):
    return f'<p class="shot-language-note" data-i18n="screens.note">{escape(TRANSLATIONS[locale]["note"])}</p>'


def hero_visual(slot, prefix, locale, composite=False):
    if not slot:
        return ''
    if not composite:
        return ('<div class="hero-visual" data-image-refresh="v5"><figure class="hero-single-shot">'
                + responsive_picture(slot, prefix, locale, 'eager', True, '(max-width: 720px) min(78vw, 280px), 280px', 'responsive-picture seo-hero-picture')
                + f'<figcaption data-i18n="screens.{slot}.caption">{escape(caption(slot, locale))}</figcaption></figure>' + language_note(locale) + '</div>')
    cards = []
    for name, css, sizes in [('today', 'hero-today', '(max-width: 720px) 33vw, 165px'),
                             ('before-after', 'hero-photos', '(max-width: 720px) 52vw, 285px'),
                             ('weight', 'hero-weight', '145px')]:
        picture = responsive_picture(name, prefix, locale, 'lazy' if name == 'weight' else 'eager', name == 'before-after', sizes, desktop_only=name == 'weight')
        crop = ' shot-photo-crop' if name == 'before-after' else ''
        key = SLOTS[name]['copy_key']
        cards.append(f'<figure class="hero-shot {css}"><div class="shot-frame{crop}">{picture}</div><figcaption data-i18n="screens.hero.{name}">{escape(TRANSLATIONS[locale][key])}</figcaption></figure>')
    return '<div class="hero-visual hero-screens" data-image-refresh="v5">' + ''.join(cards) + language_note(locale) + '</div>'


def page_hero(page):
    if page in MANIFEST['page_hero_slots']:
        return MANIFEST['page_hero_slots'][page]
    if page in TEXT_ONLY:
        return None
    if page in {'medical-safety.html', 'methodology.html'}:
        return 'references'
    if page in {'weight-loss-injection-tracker.html'}:
        return 'calendar'
    if page.endswith('-tracker-iphone.html'):
        return 'log'
    return None


def refreshed_html(rel, text):
    path = Path(rel)
    locale = locale_for(rel)
    prefix = '../' * (len(path.parts) - 1)
    home = path.name == 'index.html' and (len(path.parts) == 1 or path.parts[-2] in TRANSLATIONS)
    offer = rel == 'free-lifetime/index.html'
    doc = Document(text)
    hero = doc.first(lambda n: n.has_class('marketing-hero'))
    edits = []
    if hero:
        visual = doc.first(lambda n: n.has_class('hero-visual') and n.inside(hero))
        chosen = 'today' if home or offer else page_hero(path.name)
        markup = hero_visual(chosen, prefix, locale, home or offer)
        if visual:
            start = visual.start
            if not markup and not text[text.rfind('\n', 0, start) + 1:start].strip():
                start = text.rfind('\n', 0, start) + 1
            edits.append((start, visual.end, markup))
        proof = doc.first(lambda n: n.has_class('hero-proof') and n.inside(hero))
        if (home or offer) and visual and proof and proof.parent.has_class('hero-copy'):
            edits.append((proof.start, proof.end, ''))
            edits.append((visual.end, visual.end, text[proof.start:proof.end]))
        if 'image-refresh-hero' not in hero.attrs.get('class', ''):
            opening = text[hero.start:hero.opening_end].replace('marketing-hero', 'marketing-hero image-refresh-hero' + (' hero-text-only' if not chosen else ''))
            edits.append((hero.start, hero.opening_end, opening))
        if (home or offer) and 'data-image-copy-layout' not in hero.attrs:
            copy = doc.first(lambda n: n.has_class('hero-copy') and n.inside(hero))
            support = doc.first(lambda n: n.has_class('hero-support') and n.inside(hero))
            if copy and support:
                moved = [n for n in copy.children if n.has_class('hero-detail-copy') or (locale in {'en', 'en-gb'} and n.attrs.get('data-i18n') == 'site.hero.body') or n.has_class('hero-note')]
                if moved:
                    edits.append((support.opening_end, support.opening_end, ''.join(text[n.start:n.end] for n in moved)))
                    edits.extend((n.start, n.end, '') for n in moved)
            # Layout is a one-time move; content sync still owns the copied text.
            opening = next((e[2] for e in edits if e[0] == hero.start), text[hero.start:hero.opening_end])
            edits = [e for e in edits if e[0] != hero.start]
            edits.append((hero.start, hero.opening_end, opening[:-1] + ' data-image-copy-layout="v5">'))

        if home and locale not in {'en', 'en-gb'}:
            copy = doc.first(lambda n: n.has_class('hero-copy') and n.inside(hero))
            body = doc.first(lambda n: n.attrs.get('data-i18n') == 'site.hero.body' and n.inside(hero))
            actions = doc.first(lambda n: (n.has_class('hero-actions') or n.has_class('site-cta-actions')) and copy and n.inside(copy))
            if body and actions and not body.inside(copy):
                edits.append((body.start, body.end, ''))
                edits.append((actions.start, actions.start, text[body.start:body.end]))

    if home:
        mini = doc.first(lambda n: n.has_class('mini-proof'))
        if mini:
            edits.append((mini.start, mini.end, '<div class="mini-proof">' + figure('log', prefix, locale) + '</div>'))
            article = mini.ancestor(lambda n: n.tag == 'article')
            title = next((n for n in doc.nodes if article and n.inside(article) and n.tag == 'h3'), None)
            if title and locale in {'en', 'en-gb'}:
                edits.append((title.start, title.end, '<h3>Record doses, weight, symptoms and photos</h3>'))
        gallery = doc.first(lambda n: n.attrs.get('id') == 'screens' or n.attrs.get('data-screenshot-gallery') == 'v5')
        heading = 'OneGLP screenshots' if locale in {'en', 'en-gb'} else 'OneGLP'
        gallery_html = ('<section id="screens" class="section-strip" data-screenshot-gallery="v5"><div class="shell">'
                        f'<div class="section-head"><h2>{heading}</h2>{language_note(locale)}</div><div class="website-shot-grid">'
                        + ''.join(figure(s, prefix, locale) for s in MANIFEST['homepage_slots']) + '</div></div></section>')
        if gallery:
            edits.append((gallery.start, gallery.end, gallery_html))
        else:
            main = doc.first(lambda n: n.tag == 'main')
            if main:
                first_section = next((n for n in main.children if n.tag == 'section'), None)
                at = first_section.end if first_section else main.opening_end
                edits.append((at, at, gallery_html))

    # Non-hero legacy illustrations are not evidence for unsupported screenshot slots.
    for img in (n for n in doc.nodes if n.tag == 'img' and Path(n.attrs.get('src', '')).name in LEGACY):
        if any(a <= img.start and img.end <= b for a, b, _ in edits):
            continue
        container = img.ancestor(lambda n: 'data-screenshot-slot' in n.attrs)
        if container:
            edits.append((container.start, container.end, ''))
            continue
        container = img.ancestor(lambda n: n.has_class('screen-panel') or n.has_class('screen-shot-shell'))
        if not container:
            container = img.ancestor(lambda n: n.tag in {'picture', 'figure'}) or img
        edits.append((container.start, container.end, ''))
    text = apply_edits(text, edits)
    # The new stylesheet version is scoped separately from the offer scripts.
    text = re.sub(r'styles\.css(?:\?v=[^"\s<>]+)?', 'styles.css?v=' + VERSION, text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    changed = []
    for path in sorted(ROOT.rglob('*.html')):
        if '.git' in path.parts:
            continue
        before = path.read_text()
        after = refreshed_html(path.relative_to(ROOT).as_posix(), before)
        if before != after:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(after)
    print(f'Screenshot {"drift" if args.check else "updated"}: {len(changed)} pages')
    return int(args.check and bool(changed))


if __name__ == '__main__':
    raise SystemExit(main())

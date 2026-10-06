"""Static social proof for every locale homepage and the English offer page."""
import json
import re
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path

from press_content import COPY as PRESS_COPY, RTL, ui_text
from seo_gate_sitemap import LOCALE_DIRS, ROOT

RESOURCE = json.loads((ROOT / 'data/website-social-proof-copy.json').read_text())
COPY = {locale: dict(zip(RESOURCE['keys'], values))
        for locale, values in RESOURCE['translations'].items()}
STYLE_VERSION = '20261006-international-proof'
CONFIG_VERSION = '20261006-social-proof-r2'


def validate_copy():
    assert set(COPY) == LOCALE_DIRS, 'Social proof must cover every locale'
    for locale, values in RESOURCE['translations'].items():
        assert len(values) == len(RESOURCE['keys']) and all(values), locale
        assert COPY[locale]['checked'].count('{date}') == 1, locale
    for locale, months in RESOURCE.get('date_months', {}).items():
        assert locale in LOCALE_DIRS and len(months) == 12 and all(months), locale


def homepage_locale(relative):
    path = Path(relative)
    if path.as_posix() in {'index.html', 'free-lifetime/index.html'}:
        return 'en'
    if len(path.parts) == 2 and path.name == 'index.html' and path.parts[0] in LOCALE_DIRS:
        return path.parts[0]
    return None


def localized_date(value, locale, attribute):
    # The ISO date is crawler-visible without JavaScript. Existing progressive
    # date formatting supplies local month names when the browser supports them.
    parsed = date.fromisoformat(value)
    visible = f'{parsed.day} {parsed.strftime("%B")} {parsed.year}' if locale in {'en', 'en-gb'} else value
    months = RESOURCE.get('date_months', {}).get(locale)
    if months:
        visible = f'{parsed.day} {months[parsed.month - 1]} {parsed.year}'
    progressive = '' if locale in {'en', 'en-gb'} else f' {attribute}'
    return f'<time datetime="{value}"{progressive}><bdi>{visible}</bdi></time>'


def press_href(relative, locale):
    if locale == 'en':
        return '../' * (len(Path(relative).parts) - 1) + 'press/'
    return 'press/'


def proof_section(facts, locale, href):
    copy = COPY[locale]
    claims = facts['product_claims']

    def label(key, claim_key):
        english = locale in {'en', 'en-gb'}
        attribute = 'data-claim-copy' if english else 'data-social-proof-copy'
        value = claims[claim_key] if english else copy[key]
        return f'{attribute}="{claim_key}"', ui_text(value, locale)

    items = []
    for key, claim_key, label_key, label_claim in (
        ('downloads', 'proofDownloads', 'downloads', 'proofDownloadsLabel'),
        ('us', 'proofRating', 'usRating', 'proofRatingLabel'),
        ('uk', 'proofUkRating', 'ukRating', 'proofUkRatingLabel'),
    ):
        number = f'<span data-claim-copy="{claim_key}">{escape(claims[claim_key])}</span>'
        if key == 'downloads':
            number = f'<strong dir="ltr" data-claim-copy="{claim_key}">{escape(claims[claim_key])}</strong>'
        else:
            number = f'<strong dir="ltr">{number}<span class="rating-scale" aria-hidden="true">/5</span><span class="sr-only"> {escape(copy["outOfFive"])}</span></strong>'
        attribute, text = label(label_key, label_claim)
        items.extend([
            '              <div class="hero-proof-item">',
            f'                {number}',
            f'                <span {attribute}>{text}</span>',
            '              </div>',
        ])
    attribute, worldwide = label('worldwide', 'proofWorldwideRatings')
    items.append(f'              <small {attribute}>{worldwide}</small>')
    if locale in {'en', 'en-gb'}:
        items.append(f'              <small data-claim-copy="proofChecked">{escape(claims["proofChecked"])}</small>')
    else:
        checked = facts['social_proof_sources']['rating']['checked_on']
        before, after = copy['checked'].split('{date}')
        items.append('              <small data-social-proof-copy="proofChecked">'
                     + ui_text(before, locale) + localized_date(checked, locale, 'data-rating-date')
                     + ui_text(after, locale) + '</small>')
    items.append(f'              <a class="hero-press-link" href="{href}"><span>{ui_text(PRESS_COPY[locale]["press.heading"], locale)}</span><span aria-hidden="true">→</span></a>')
    return '\n'.join([
        '<!-- generated:social-proof:start -->',
        f'            <div class="hero-proof" aria-label="{escape(copy["proofLabel"], quote=True)}">',
        *items,
        '            </div>',
        '<!-- generated:social-proof:end -->',
    ])


def review_card(review, locale):
    language = escape(review['language'], quote=True)
    return [
        '            <article class="feature-card app-review">',
        f'              <h3 lang="{language}" dir="ltr">{escape(review["title"])}</h3>',
        f'              <p class="app-review-date">{localized_date(review["date"], locale, "data-review-date")}</p>',
        f'              <blockquote lang="{language}" dir="ltr"><p>{escape(review["body"])}</p></blockquote>',
        '            </article>',
    ]


def review_section(data, locale, href):
    if len(data['reviews']) != 4:
        raise ValueError('The balanced review layout requires four selected reviews')
    copy = COPY[locale]
    publishers = ' · '.join(article['publisher'] for article in
                            json.loads((ROOT / 'data/press.json').read_text())['articles'])
    lines = [
        '    <!-- generated:app-store-reviews:start -->',
        '    <section class="section-strip app-reviews" aria-labelledby="app-reviews-heading" data-app-store-reviews>',
        '      <div class="shell">',
        '        <div class="app-reviews-intro">',
        '          <div class="section-head">',
        f'            <h2 id="app-reviews-heading">{ui_text(copy["heading"], locale)}</h2>',
        f'            <p>{ui_text(copy["description"], locale)}</p>',
        '          </div>',
        f'          <a class="press-feature" href="{href}" aria-labelledby="press-feature-title">',
        f'            <span class="press-feature-eyebrow">{ui_text(copy["pressEyebrow"], locale)}</span>',
        f'            <span class="press-feature-title" id="press-feature-title"><span class="press-feature-name">{ui_text(PRESS_COPY[locale]["press.heading"], locale)}</span><span aria-hidden="true">→</span></span>',
        f'            <span class="press-feature-copy">{ui_text(copy["pressDescription"], locale)}</span>',
        f'            <span class="press-feature-publishers"><bdi dir="ltr">{escape(publishers)}</bdi></span>',
        '          </a>',
        '        </div>',
        f'        <h3 class="app-reviews-label">{ui_text(copy["reviewsLabel"], locale)}</h3>',
        '        <div class="app-review-grid">',
    ]
    # Current pairs balance independent columns and preserve newest-first order
    # when they stack on mobile. Keep the owner-supplied quotations unchanged.
    ordered = sorted(data['reviews'], key=lambda review: len(review['body']), reverse=True)
    for column in ((ordered[0], ordered[-1]), (ordered[1], ordered[-2])):
        lines.append('          <div class="app-review-column">')
        for review in column:
            lines.extend(review_card(review, locale))
        lines.append('          </div>')
    return '\n'.join(lines + [
        '        </div>', '      </div>', '    </section>',
        '    <!-- generated:app-store-reviews:end -->',
    ])


def div_span(text, class_name):
    class Finder(HTMLParser):
        def __init__(self):
            super().__init__()
            self.offsets = [0]
            for line in text.splitlines(keepends=True):
                self.offsets.append(self.offsets[-1] + len(line))
            self.start = self.end = None
            self.depth = 0

        def source_position(self):
            line, column = self.getpos()
            return self.offsets[line - 1] + column

        def handle_starttag(self, tag, attrs):
            if tag != 'div' or self.end is not None:
                return
            if self.depth:
                self.depth += 1
            elif class_name in dict(attrs).get('class', '').split():
                self.start = self.source_position()
                self.depth = 1

        def handle_endtag(self, tag):
            if tag == 'div' and self.depth:
                self.depth -= 1
                if not self.depth:
                    self.end = self.source_position() + len('</div>')
    parser = Finder()
    parser.feed(text)
    if parser.start is None or parser.end is None:
        return None
    return parser.start, parser.end


def sync_homepage(text, relative, facts, reviews):
    locale = homepage_locale(relative)
    if locale is None:
        return text
    validate_copy()
    href = press_href(relative, locale)
    proof = proof_section(facts, locale, href)
    marker = r'<!-- generated:social-proof:start -->.*?<!-- generated:social-proof:end -->'
    if re.search(marker, text, re.S):
        text = re.sub(marker, lambda match: proof, text, flags=re.S)
    else:
        span = div_span(text, 'hero-proof')
        if span:
            text = text[:span[0]] + proof + text[span[1]:]
        else:
            support = div_span(text, 'hero-support')
            if not support:
                raise ValueError(f'{relative}: missing hero support insertion point')
            text = text[:support[0]] + proof + '\n          ' + text[support[0]:]
    section = review_section(reviews, locale, href)
    marker = r'    <!-- generated:app-store-reviews:start -->.*?    <!-- generated:app-store-reviews:end -->'
    if re.search(marker, text, re.S):
        text = re.sub(marker, lambda match: section, text, flags=re.S)
    else:
        text, count = re.subn(r'<main\b[^>]*>', lambda match: match[0] + '\n' + section + '\n', text, count=1)
        if count != 1:
            raise ValueError(f'{relative}: missing main element')
    prefix = '../' * (len(Path(relative).parts) - 1)
    stylesheet = f'  <link rel="stylesheet" href="{prefix}reviews.css?v={STYLE_VERSION}">'
    if re.search(r'<link\b[^>]*href="[^"]*reviews\.css[^>]*>', text):
        text = re.sub(r'  <link\b[^>]*href="[^"]*reviews\.css[^>]*>', stylesheet, text)
    else:
        text = text.replace('</head>', stylesheet + '\n</head>', 1)
    date_script = f'  <script defer src="{prefix}site-press.js?v={STYLE_VERSION}" data-social-proof-dates></script>'
    if 'data-social-proof-dates' in text:
        text = re.sub(r'  <script\b[^>]*data-social-proof-dates[^>]*></script>', date_script, text)
    else:
        text = text.replace('</head>', date_script + '\n</head>', 1)
    return re.sub(r'(site-config\.js)\?v=[^"\s<>]+', rf'\1?v={CONFIG_VERSION}', text)

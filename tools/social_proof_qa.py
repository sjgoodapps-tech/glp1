#!/usr/bin/env python3
"""Check locale coverage and source fidelity independently of the renderer."""
import json
from html.parser import HTMLParser
from pathlib import Path

from seo_gate_sitemap import LOCALE_DIRS, ROOT


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.proof_count = self.section_count = 0
        self.reviews = []
        self.press_links = []
        self.claims = {}
        self.current_review = self.field = self.claim = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        if 'hero-proof' in classes:
            self.proof_count += 1
        if 'data-app-store-reviews' in attrs:
            self.section_count += 1
        if tag == 'a' and any(value in classes for value in ('press-feature', 'hero-press-link')):
            self.press_links.append(attrs['href'])
        if attrs.get('data-claim-copy') in {'proofDownloads', 'proofRating', 'proofUkRating'}:
            self.claim = (tag, attrs['data-claim-copy'])
            self.claims[self.claim[1]] = ''
        if tag == 'article' and 'app-review' in classes:
            self.current_review = {'title': '', 'body': ''}
            self.reviews.append(self.current_review)
        if self.current_review is not None:
            if tag in {'h3', 'blockquote'}:
                self.field = 'title' if tag == 'h3' else 'body'
                self.current_review[self.field + '_lang'] = attrs.get('lang')
                self.current_review[self.field + '_dir'] = attrs.get('dir')
            if tag == 'time':
                self.current_review['date'] = attrs.get('datetime')

    def handle_data(self, text):
        if self.claim:
            self.claims[self.claim[1]] += text
        if self.current_review is not None and self.field:
            self.current_review[self.field] += text

    def handle_endtag(self, tag):
        if self.claim and self.claim[0] == tag:
            self.claim = None
        if tag in {'h3', 'blockquote'}:
            self.field = None
        if tag == 'article':
            self.current_review = None


def main():
    facts = json.loads((ROOT / 'data/product-facts.json').read_text())['product_claims']
    source = json.loads((ROOT / 'data/app-store-reviews.json').read_text())['reviews']
    copy = json.loads((ROOT / 'data/website-social-proof-copy.json').read_text())
    assert set(copy['translations']) == LOCALE_DIRS
    paths = [Path('index.html'), Path('free-lifetime/index.html')]
    paths += [Path(locale) / 'index.html' for locale in sorted(LOCALE_DIRS)]
    for relative in paths:
        text = (ROOT / relative).read_text()
        page = Page(text)
        assert page.proof_count == 1 and page.section_count == 1, relative
        assert page.claims == {key: facts[key] for key in ('proofDownloads', 'proofRating', 'proofUkRating')}, relative
        assert len(page.reviews) == 4, relative
        assert len(page.press_links) == 2, relative
        assert [review['date'] for review in page.reviews] == sorted((review['date'] for review in source), reverse=True), relative
        for review, original in zip(page.reviews, source):
            for key in ('title', 'body', 'date'):
                assert review[key] == original[key], (relative, key)
            assert review['title_lang'] == review['body_lang'] == original['language'], relative
            assert review['title_dir'] == review['body_dir'] == 'ltr', relative
        locale = relative.parts[0] if relative.parts[0] in LOCALE_DIRS else 'en'
        destination = ROOT / ('' if locale == 'en' else locale) / 'press'
        for href in page.press_links:
            assert (ROOT / relative.parent / href).resolve() == destination.resolve(), relative
        if locale not in {'en', 'en-gb'}:
            assert 'data-claim-copy="proofRatingLabel"' not in text, relative
            assert 'data-claim-copy="proofChecked"' not in text, relative
            assert 'data-rating-date' in text and text.count('data-review-date') == 4, relative
        assert 'noindex' not in text.lower(), relative
    print(f'PASS: {len(paths)} pages; all 53 locales, exact original reviews/dates, shared figures, local Press links and no English runtime label override.')


if __name__ == '__main__':
    main()

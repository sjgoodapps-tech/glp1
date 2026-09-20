#!/usr/bin/env python3
"""Static discovery, identity and navigation checks for the name-change pages."""
import json
import re
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit
from urllib.robotparser import RobotFileParser
from build_rebrand_pages import BRAND, DATA, FACTS, ROOT, SITE, campaign_url, page_path, page_url, render


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags, self.visible = [], []
        self.hidden = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag in {'head', 'script', 'style'}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {'head', 'script', 'style'}:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.visible.append(data)


def main():
    assert set(DATA['translations']) == set(BRAND['notices']), 'Every supported language needs an announcement'
    robots = RobotFileParser()
    robots.parse((ROOT / 'robots.txt').read_text().splitlines())
    for locale, copy in DATA['translations'].items():
        path = ROOT / page_path(locale)
        source = path.read_text()
        assert source == render(locale), f'Render drift: {path}'
        page = Page(source)
        visible = re.sub(r'\s+', ' ', ''.join(page.visible))
        for value in [copy['title'], copy['tagline'], copy['intro'], copy['safety'], *copy['items']]:
            assert value in visible, (locale, value)
        for q, a in copy['questions']:
            assert q in visible and a in visible, locale
        assert 'Person:' not in visible and 'trading as' not in visible
        assert 'GLPzy' in visible and 'OneGLP' in visible and '6761775005' in visible
        scripts = [a for t, a in page.tags if t == 'script']
        assert all(a.get('type') == 'application/ld+json' for a in scripts), 'Name-change content must not depend on scripts'
        graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)[1])['@graph']
        app = next(item for item in graph if item['@type'] == 'SoftwareApplication')
        assert app['name'] == FACTS['app_name'] and app['alternateName'] == 'GLPzy'
        assert app['@id'] == SITE + '/#software'
        assert app['downloadUrl'] == FACTS['app_store_url']
        assert not any('aggregateRating' in item for item in graph)
        ctas = [a for t, a in page.tags if t == 'a' and 'data-app-store-link' in a]
        assert len(ctas) == 2 and ctas[0]['href'] == campaign_url(locale)
        assert parse_qs(urlsplit(ctas[0]['href']).query)['ct'] == [DATA['campaign']]
        assert ctas[1]['href'] == campaign_url(locale, bottom=True)
        assert ctas[1]['data-app-store-campaign'] == 'rebrandPageBottom'
        assert len(DATA['campaign'] + '_bottom') <= 40
        for tag, attrs in page.tags:
            if tag not in {'a', 'img', 'link'}:
                continue
            target = attrs.get('href', attrs.get('src', ''))
            if target.startswith(('https:', '#')):
                continue
            assert (path.parent / target.split('?', 1)[0]).exists(), (locale, target)
        for bot in ('OAI-SearchBot', 'GPTBot', 'ChatGPT-User', 'Googlebot', 'Bingbot', 'Applebot', 'ClaudeBot', 'PerplexityBot'):
            assert robots.can_fetch(bot, page_url(locale)), (bot, locale)
        home = ROOT / ('' if locale == 'en' else locale) / 'index.html'
        links = [a for t, a in Page(home.read_text()).tags if t == 'a' and 'data-rebrand-link' in a]
        assert len(links) == 1 and (home.parent / links[0]['href']).resolve() == path.resolve(), locale
    print(f'PASS: {len(DATA["translations"])} static translated rebrand pages; matching copy/schema, same app ID, crawl permission, campaign CTAs, homepage links and no runtime dependency.')


if __name__ == '__main__':
    main()

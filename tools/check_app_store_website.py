#!/usr/bin/env python3
"""Read-only HTTP and HTML-redirect check for the exact App Store website URLs."""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from build_app_store_aliases import URLS


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.title, self.lang, self.refresh, self.title_open = '', '', None, False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'title':
            self.title_open = True
        if tag == 'html':
            self.lang = attrs.get('lang', '').lower()
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
            match = re.fullmatch(r'0;\s*url=(.+)', attrs.get('content', ''), re.I)
            if match:
                self.refresh = match[1]

    def handle_endtag(self, tag):
        if tag == 'title':
            self.title_open = False

    def handle_data(self, text):
        if self.title_open:
            self.title += text


class Redirects(HTTPRedirectHandler):
    def __init__(self, chain):
        self.chain = chain

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({'url': req.full_url, 'status': code, 'location': newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def check(base, path):
    start = urljoin(base, path)
    chain, seen = [], set()
    opener = build_opener(Redirects(chain))
    url = start
    try:
        for _ in range(4):
            if url in seen:
                raise ValueError('HTML redirect loop')
            seen.add(url)
            try:
                response = opener.open(Request(url, headers={'User-Agent': 'OneGLP-Website-QA/1.0'}), timeout=20)
            except HTTPError as error:
                response = error
            with response:
                source = response.read().decode('utf-8', errors='replace')
                final, status = response.geturl(), response.status
            parsed = Page(source)
            chain.append({'url': final, 'status': status})
            if status == 200 and parsed.refresh:
                url = urljoin(final, parsed.refresh)
                if urlsplit(url).netloc != urlsplit(final).netloc:
                    raise ValueError('Unexpected cross-host HTML redirect')
                chain[-1]['html_redirect'] = url
                continue
            expected = URLS['aliases'].get(path, path)
            locale = expected.split('/')[1] if expected.count('/') == 2 else 'en'
            language_ok = parsed.lang in ({'en', 'en-gb'} if locale == 'en-gb' else {locale})
            passed = status == 200 and urlsplit(final).path == expected and language_ok and 'OneGLP' in parsed.title
            return {'url': start, 'final_url': final, 'status': status, 'title': parsed.title,
                    'html_lang': parsed.lang, 'passed': passed, 'chain': chain}
        raise ValueError('Too many HTML redirects')
    except (URLError, ValueError, TimeoutError) as error:
        return {'url': start, 'passed': False, 'error': str(error), 'chain': chain}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default=URLS['origin'])
    parser.add_argument('--aliases-only', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    paths = list(URLS['aliases']) if args.aliases_only else URLS['paths']
    results = [check(args.base_url, path) for path in paths]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    failures = [r for r in results if not r['passed']]
    for result in results:
        print(f'{"PASS" if result["passed"] else "FAIL"} {result["url"]}: {result.get("status", result.get("error"))}')
    print(f'{len(results) - len(failures)}/{len(results)} passed. Evidence: {args.output}')
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())

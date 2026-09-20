#!/usr/bin/env python3
"""Preserve App Store URLs using Jekyll permalinks, even on case-insensitive Macs."""
import argparse
import json
from html import escape
from pathlib import Path

from build_rebrand_pages import DATA, ROOT, SITE

URLS = json.loads((ROOT / 'data/app-store-website-urls.json').read_text())


def source_path(alias):
    return ROOT / 'compatibility' / (alias.strip('/').replace('/', '-') + '.md')


def body(alias, target):
    locale = target.split('/')[1]
    copy = DATA['translations'][locale]
    label = copy['support'] if target.endswith('/support.html') else copy['explore']
    return f'''<!DOCTYPE html>
<html lang="{locale}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index,follow">
  <meta http-equiv="refresh" content="0;url={escape(target, quote=True)}">
  <link rel="canonical" href="{SITE}{target}">
  <title>{escape(copy['title'])}</title>
  <link rel="stylesheet" href="/rebrand-page.css?v=20260920">
</head>
<body><main class="name-shell name-content">
  <h1>{escape(copy['title'])}</h1>
  <p><a href="{escape(target, quote=True)}">{escape(label)}</a></p>
</main></body>
</html>
'''


def source(alias, target):
    # Pages' existing branch build processes front matter. Source filenames never
    # collide with real lowercase locale directories on a case-insensitive Mac.
    return (f'---\nlayout: null\npermalink: {alias}\n---\n'
            + '{::nomarkdown}\n' + body(alias, target) + '{:/nomarkdown}\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--built-dir', type=Path, help='Verify actual Jekyll output against preview HTML')
    args = parser.parse_args()
    assert len(URLS['paths']) == len(set(URLS['paths'])) == 54
    assert not (ROOT / '.nojekyll').exists(), 'Compatibility routes require the existing Jekyll build'
    changed = []
    for alias, target in URLS['aliases'].items():
        assert alias != target and target not in URLS['aliases'], 'Redirect loop'
        assert target in {'/' + p.relative_to(ROOT).as_posix() for p in ROOT.glob('*/*.html')}, target
        path = source_path(alias)
        expected = source(alias, target)
        if args.built_dir:
            outputs = {p.relative_to(args.built_dir).as_posix() for p in args.built_dir.rglob('*.html')}
            assert alias.lstrip('/') in outputs, f'Missing case-sensitive output: {alias}'
            built = (args.built_dir / alias.lstrip('/')).read_text()
            assert built.strip() == body(alias, target).strip(), f'Jekyll/preview HTML differs: {alias}'
        if not path.exists() or path.read_text() != expected:
            changed.append(alias)
            if not args.check:
                path.parent.mkdir(exist_ok=True)
                path.write_text(expected)
    print(f'App Store compatibility routes {"drift" if args.check else "updated"}: {len(changed)} of {len(URLS["aliases"])}')
    return int(args.check and bool(changed))


if __name__ == '__main__':
    raise SystemExit(main())

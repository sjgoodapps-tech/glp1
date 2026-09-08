#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "20260908-growth"
CSS_VERSION = "20260908-offer-proof"
CTA_VERSION = VERSION


def apply(path):
    html = path.read_text(encoding="utf-8")
    html = re.sub(r'\n?\s*<script src="[^"]*site-preflight\.js[^"]*"></script>', "", html, flags=re.I)
    html = re.sub(
        r'\n?\s*<link\b[^>]*data-glpzy-font-preload[^>]*>',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'\n?\s*<link\b[^>]*href="https://fonts\.(?:googleapis|gstatic)\.com[^"]*"[^>]*>',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(r'(styles\.css)\?v=[^"\']+', rf'\1?v={CSS_VERSION}', html)
    html = re.sub(r'(site-cta\.js)\?v=[^"\']+', rf'\1?v={CTA_VERSION}', html)
    html = re.sub(r'(site-config\.js)(?:\?v=[^"\']+)?', rf'\1?v={VERSION}', html)
    stylesheet = re.search(r'<link\b[^>]*href="(?P<prefix>[^"]*?)styles\.css[^>]*>', html, re.I)
    if not stylesheet:
        return False
    prefix = stylesheet.group("prefix")
    tag = f'<script src="{prefix}site-preflight.js?v={VERSION}"></script>\n  '
    html = html[:stylesheet.start()] + tag + html[stylesheet.start():]

    head = re.search(r'<head>(.*?)</head>', html, re.S | re.I)
    if head:
        cleaned = re.sub(r'\n(?:[ \t]*\n){2,}', "\n\n", head.group(1))
        html = html[:head.start(1)] + cleaned + html[head.end(1):]
    if html == path.read_text(encoding="utf-8"):
        return False
    path.write_text(html, encoding="utf-8")
    return True


def main():
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" not in path.parts and apply(path):
            changed += 1
    print(f"added offer preflight to {changed} HTML files")


if __name__ == "__main__":
    main()

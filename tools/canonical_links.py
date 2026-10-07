"""Keep crawlable internal anchors aligned with the site's canonical routes."""
import posixpath
import re
from html import escape, unescape
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://oneglp.app'
INTERNAL_HOSTS = {'oneglp.app', 'www.oneglp.app', 'glpzy.app', 'www.glpzy.app'}
ANCHOR = re.compile(r'<a\b[^>]*>', re.I)
HREF = re.compile(r'(?<![\w-])href\s*=\s*(["\'])(.*?)\1', re.I | re.S)


def canonical_route(relative):
    """Resolve existing HTML only; /en/ aliases use their root equivalent."""
    candidate = relative.lstrip('/')
    if not candidate or candidate.endswith('/'):
        candidate += 'index.html'
    if not candidate.endswith('.html') or not (ROOT / candidate).is_file():
        return None
    if candidate.startswith('en/') and (ROOT / candidate[3:]).is_file():
        candidate = candidate[3:]
    if candidate == 'index.html':
        return '/'
    return '/' + (candidate[:-10] if candidate.endswith('/index.html') else candidate)


def canonical_href(source, href):
    if not href or href.startswith(('#', '?')):
        return href
    original = urlsplit(href)
    resolved = urlsplit(urljoin(SITE + '/' + source, href))
    if resolved.scheme not in {'http', 'https'} or resolved.hostname not in INTERNAL_HOSTS:
        return href
    route = canonical_route(unquote(resolved.path))
    if route is None:
        return href
    # Preserve relative navigation in local HTTP previews and query/fragment state.
    if original.netloc or original.scheme:
        return urlunsplit(('https', 'oneglp.app', route, original.query, original.fragment))
    if original.path.startswith('/'):
        path = route
    else:
        path = posixpath.relpath(route, '/' + posixpath.dirname(source))
        if route.endswith('/'):
            path = './' if path == '.' else path.rstrip('/') + '/'
    return urlunsplit(('', '', path, original.query, original.fragment))


def canonicalize_links(source, html):
    def anchor(match):
        def href(attribute):
            value = canonical_href(source, unescape(attribute[2]))
            if value == unescape(attribute[2]):
                return attribute[0]
            return 'href=' + attribute[1] + escape(value, quote=True) + attribute[1]
        return HREF.sub(href, match[0])
    return ANCHOR.sub(anchor, html)

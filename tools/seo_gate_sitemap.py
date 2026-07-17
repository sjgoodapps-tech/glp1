#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.glpzy.app"
REPORT = ROOT / "reports" / "localisation-noindex-report.md"
LOCALE_INDEXING_PATH = ROOT / "data" / "locale-indexing.json"
LOCALE_INDEXING = json.loads(LOCALE_INDEXING_PATH.read_text(encoding="utf-8"))
NATIVE_REVIEWED_LOCALES = {item.lower() for item in LOCALE_INDEXING["native_reviewed_locales"]}

LOCALE_DIRS = {
    "ar", "bg", "bn", "cs", "da", "de", "el", "en", "en-gb", "es-es", "es-mx",
    "et", "fi", "fil", "fr", "fr-ca", "gu", "he", "hi", "hr", "hu", "id", "it",
    "ja", "kn", "ko", "lt", "lv", "ml", "mr", "ms", "nb", "nl", "or", "pa",
    "pl", "pt-br", "pt-pt", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te",
    "th", "tr", "uk", "ur", "vi", "zh-hans", "zh-hant",
}

APPROVED_ENGLISH_TOKENS = {
    "GLPzy", "Apple Health", "App Store", "CSV", "JSON", "PDF", "iPhone", "iPad",
    "Apple Watch", "Mounjaro", "Wegovy", "Ozempic", "Zepbound", "Victoza",
    "Rybelsus", "Saxenda", "Trulicity", "Foundayo", "tirzepatide", "semaglutide",
}

FAIL_PATTERNS = {
    "mixed or untranslated English": [
        "Bring a clearer lich su",
        "Bring a clearer l\u1ecbch s\u1eed",
        "Summary for your clinician",
        "No in-app account is required",
        "Apple Health access is optional",
        "Clearer ตรวจสอบ surfaces",
        "Calendar ตรวจสอบ",
        "See แอป Store pricing",
        "Fast dose entry without clutter",
        "Administration route and dosing frequency",
        "Medicine form",
        "Choose the medicine form you use",
        "Create a clear PDF summary for appointments",
    ],
    "known broken localisation": [
        "first create a local safety sao l\u01b0u",
        "\u0e40\u0e02\u0e49\u0e32\u0e2a\u0e39\u0e48\u0e23\u0e30\u0e1a\u0e1a\u0e2d\u0e22\u0e48\u0e32\u0e07\u0e23\u0e27\u0e14\u0e40\u0e23\u0e47\u0e27",
        "\u0110\u0103ng nh\u1eadp nhanh ch\u00f3ng",
        "ส่งออก-ready records",
        "A a a",
        "O O O",
        "o o o",
        "hero-via",
        "a a sual",
    ],
    "bad PDF wording": [
        "PDF, PDF",
        "PDF-, PDF-",
        "R\u00e9sum\u00e9s PDF, PDF et PDF",
    ],
    "wrong order wording": [
        "orders",
        "pedidos",
        "\u0111\u01a1n h\u00e0ng",
        "\u0e04\u0e33\u0e2a\u0e31\u0e48\u0e07\u0e0b\u0e37\u0e49\u0e2d",
    ],
    "wrong custom or compounded wording": [
        "Custom / Compounded",
        "custom/compounded setup",
        "route, presentation, cadence",
        "Costume",
        "Coutume",
    ],
    "wrong route/form wording": [
        "Route and cadence",
        "Route and Cadence",
        "Presentation fit",
        ">Presentation<",
        ">Presentations<",
        "packaging that matches",
    ],
    "unsupported sleep claim": [
        "sleep tracking",
        "sleep, movement",
        "sleep, ",
    ],
}

SCOPED_FAIL_PATTERNS = {
    "pt-pt/": {
        "Brazilian Portuguese wording on PT-PT page": [
            "voc\u00ea",
            "Voc\u00ea",
            "Seus registos",
            "Contate",
            "Gerencie",
            "Gerenciar",
            "rastreamento",
            "compartilhar",
            "somente leitura",
        ],
    },
    "nl/": {"Dutch support label risk": [">Steun<"]},
}


def html_files():
    return sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)


def rel(path):
    return path.relative_to(ROOT).as_posix()


def locale_for(rel_path):
    first = rel_path.split("/", 1)[0]
    return first if "/" in rel_path and first in LOCALE_DIRS else "root"


def url_for_path(rel_path):
    if rel_path == "index.html":
        return f"{SITE}/"
    if rel_path.endswith("/index.html"):
        return f"{SITE}/{rel_path[:-10]}"
    return f"{SITE}/{rel_path}"


def root_equivalent(rel_path):
    if not rel_path.startswith("en/"):
        return None
    candidate = rel_path[3:]
    return candidate if (ROOT / candidate).exists() else None


ROBOTS_META_RE = re.compile(
    r'(?P<indent>^[ \t]*)?<meta\b(?=[^>]*\bname\s*=\s*["\']robots["\'])'
    r'(?=[^>]*\bcontent\s*=\s*["\'][^"\']*["\'])[^>]*>(?:[ \t]*\n|(?=<)|$)',
    re.I | re.M,
)


def set_robots(text, content):
    matches = list(ROBOTS_META_RE.finditer(text))
    if matches:
        # Keep the first tag's position, but remove every duplicate regardless
        # of attribute order or self-closing syntax.
        first = matches[0]
        first_start = matches[0].start()
        cleaned = ROBOTS_META_RE.sub("", text)
        indent = first.group("indent") or ""
        replacement = f'{indent}<meta name="robots" content="{content}">\n'
        return cleaned[:first_start] + replacement + cleaned[first_start:]
    return text.replace("</head>", f'  <meta name="robots" content="{content}">\n</head>', 1)


def set_canonical(text, url):
    if re.search(r'<link rel="canonical" href="[^"]*">', text, re.I):
        return re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', text, count=1, flags=re.I)
    return text.replace("</head>", f'  <link rel="canonical" href="{url}">\n</head>', 1)


def text_without_code(html):
    html = re.sub(r"<script\b.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style\b.*?</style>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html)


def detect_failures(rel_path, html):
    loc = locale_for(rel_path)
    if loc in {"root", "en"}:
        return []
    failures = []
    haystack = text_without_code(html)
    for label, patterns in FAIL_PATTERNS.items():
        for pattern in patterns:
            if pattern and pattern in haystack:
                failures.append(f"{label}: {pattern}")
    for prefix, groups in SCOPED_FAIL_PATTERNS.items():
        if rel_path.startswith(prefix):
            for label, patterns in groups.items():
                for pattern in patterns:
                    if pattern in haystack:
                        failures.append(f"{label}: {pattern}")
    commercial_names = {
        "mounjaro-tracker-iphone.html",
        "wegovy-tracker-iphone.html",
        "zepbound-tracker-iphone.html",
        "tirzepatide-tracker-iphone.html",
        "semaglutide-tracker-iphone.html",
        "glp1-dose-reminder-app.html",
        "glp1-side-effect-symptom-tracker.html",
        "glp1-weight-tracker.html",
        "glp1-progress-photo-tracker.html",
        "apple-health-glp-tracker.html",
    }
    if Path(rel_path).name in commercial_names and ("data-seo-answer" not in html or "data-seo-facts" not in html):
        failures.append("locale commercial page lacks upgraded answer/facts module")
    return failures


def fix_hreflang_en(text, current_rel):
    def repl(match):
        href = match.group(1)
        parsed = urlparse(href)
        path = parsed.path.lstrip("/")
        if not path.startswith("en/"):
            return match.group(0)
        target = path[3:]
        if target == "index.html":
            new_href = f"{SITE}/"
        elif (ROOT / target).exists():
            new_href = f"{SITE}/{target}"
        else:
            new_href = href
        return f'hreflang="en" href="{new_href}"'
    return re.sub(r'hreflang="en" href="([^"]+)"', repl, text)


HREFLANG_LINK_RE = re.compile(
    r'<link\b(?=[^>]*\brel=["\']alternate["\'])(?=[^>]*\bhreflang=["\'][^"\']+["\'])[^>]*>[ \t]*\n?',
    re.I,
)


def filter_hreflang(text, page_locale):
    if page_locale != "root" and page_locale not in NATIVE_REVIEWED_LOCALES:
        return HREFLANG_LINK_RE.sub("", text)

    allowed = {"en", "x-default", *NATIVE_REVIEWED_LOCALES}

    def repl(match):
        tag = match.group(0)
        value = re.search(r'\bhreflang=["\']([^"\']+)["\']', tag, re.I)
        if not value or value.group(1).lower() not in allowed:
            return ""
        return tag

    return HREFLANG_LINK_RE.sub(repl, text)


def noindex_and_canonicalise():
    records = []
    for path in html_files():
        rp = rel(path)
        html = path.read_text(encoding="utf-8")
        html = fix_hreflang_en(html, rp)
        locale = locale_for(rp)
        html = filter_hreflang(html, locale)
        reasons = []
        canonical = url_for_path(rp)
        if rp.startswith("en/"):
            target = root_equivalent(rp)
            if target:
                canonical = url_for_path(target)
                reasons.append("English duplicate canonicalised to root English URL")
            else:
                reasons.append("English duplicate without root equivalent")
        failures = detect_failures(rp, html)
        reasons.extend(failures)
        if locale != "root" and locale not in NATIVE_REVIEWED_LOCALES:
            reasons.append("locale held noindex pending documented native-language review")
        if reasons:
            html = set_robots(html, "noindex,follow")
        else:
            html = set_robots(html, "index,follow")
        html = set_canonical(html, canonical)
        if path.read_text(encoding="utf-8") != html:
            path.write_text(html, encoding="utf-8")
        if reasons:
            records.append((rp, reasons, canonical))
    return records


def is_noindex(html):
    return bool(re.search(r'<meta name="robots" content="[^"]*noindex', html, re.I))


def canonical_href(html):
    match = re.search(r'<link rel="canonical" href="([^"]+)"', html, re.I)
    return match.group(1) if match else ""


def git_dirty_paths():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return set()
    return {line[3:] for line in result.stdout.splitlines() if len(line) > 3}


MECHANICAL_HTML_DIFF_MARKERS = {
    "site-preflight.js",
    "styles.css?v=",
    "site-cta.js?v=",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
}


def has_significant_dirty_diff(relative):
    try:
        result = subprocess.run(
            ["git", "diff", "--no-ext-diff", "--unified=0", "--", relative],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return True
    changed_lines = []
    for line in result.stdout.splitlines():
        if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
            continue
        content = line[1:].strip()
        if not content or any(marker in content for marker in MECHANICAL_HTML_DIFF_MARKERS):
            continue
        changed_lines.append(content)
    return bool(changed_lines)


def existing_sitemap_lastmods():
    path = ROOT / "sitemap.xml"
    if not path.exists():
        return {}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return {}
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    values = {}
    for entry in root.findall("sm:url", namespace):
        location = entry.findtext("sm:loc", default="", namespaces=namespace)
        lastmod = entry.findtext("sm:lastmod", default="", namespaces=namespace)
        if location and re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmod):
            values[location] = lastmod
    return values


def significant_lastmod(path, dirty_paths, canonical, existing_lastmods):
    relative = rel(path)
    if relative in dirty_paths and has_significant_dirty_diff(relative):
        return datetime.now(timezone.utc).date().isoformat()
    if canonical in existing_lastmods:
        return existing_lastmods[canonical]
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", relative],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        value = result.stdout.strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return value
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).date().isoformat()


def build_sitemap():
    urls = []
    seen = set()
    dirty_paths = git_dirty_paths()
    existing_lastmods = existing_sitemap_lastmods()
    for path in html_files():
        rp = rel(path)
        html = path.read_text(encoding="utf-8")
        if is_noindex(html):
            continue
        canonical = canonical_href(html) or url_for_path(rp)
        own = url_for_path(rp)
        if canonical != own:
            continue
        if canonical in seen:
            continue
        seen.add(canonical)
        urls.append((canonical, significant_lastmod(path, dirty_paths, canonical, existing_lastmods)))
    urls.sort()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, lastmod in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(url)}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return urls


def write_report(records, urls):
    REPORT.parent.mkdir(exist_ok=True)
    lines = [
        "# Localisation Index Gate Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        f"Indexable sitemap URLs: {len(urls)}",
        f"Noindexed pages: {len(records)}",
        f"Native-reviewed indexable locales: {', '.join(sorted(NATIVE_REVIEWED_LOCALES)) or 'none'}",
        "",
        "## Canonical Decision",
        "",
        "Root English URLs are the canonical English marketing pages. `/en/` duplicates are `noindex,follow` and canonicalised to their root English equivalent when one exists.",
        "Locale pages remain accessible through the language picker. They are excluded from indexing and hreflang clusters until native review is recorded in `data/locale-indexing.json`.",
        "",
        "## Noindexed Pages",
        "",
    ]
    if not records:
        lines.append("None.")
    for rp, reasons, canonical in records:
        lines.append(f"- `{rp}` -> canonical `{canonical}`")
        for reason in reasons[:8]:
            lines.append(f"  - {reason}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Apply locale gates and build the sitemap.")
    parser.add_argument(
        "--sitemap-only",
        action="store_true",
        help="Rebuild sitemap.xml without changing HTML or the localisation report.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.sitemap_only:
        urls = build_sitemap()
        print(f"wrote sitemap.xml with {len(urls)} URLs")
        return

    records = noindex_and_canonicalise()
    urls = build_sitemap()
    write_report(records, urls)
    print(f"noindexed {len(records)} pages")
    print(f"wrote sitemap.xml with {len(urls)} URLs")
    print(f"wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

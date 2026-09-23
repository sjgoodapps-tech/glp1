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
SITE = json.loads((ROOT / "data" / "product-facts.json").read_text(encoding="utf-8"))["site_url"].rstrip("/")
LEGACY_SITE = "https://www.glpzy.app"
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
    "OneGLP", "Apple Health", "App Store", "CSV", "JSON", "PDF", "iPhone", "iPad",
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
    pattern = re.compile(r'<link\b(?=[^>]*\brel\s*=\s*["\']canonical["\'])[^>]*>', re.I)
    matches = list(pattern.finditer(text))
    first = matches[0].start() if matches else None
    replacement = f'<link rel="canonical" href="{escape(url, quote=True)}">'
    if matches:
        text = pattern.sub(lambda match: replacement if match.start() == first else '', text)
    else:
        text = text.replace('</head>', '  ' + replacement + '\n</head>', 1)
    # Old locale templates also exposed nonexistent slash URLs in social metadata.
    og = re.compile(r'<meta\b(?=[^>]*\bproperty\s*=\s*["\']og:url["\'])[^>]*>', re.I)
    text = og.sub(f'<meta property="og:url" content="{escape(url, quote=True)}">', text)
    return re.sub(r'[ \t]+$', '', text, flags=re.M)


SCHEMA_BLOCK_RE = re.compile(
    r'(?P<open><script\b(?=[^>]*\btype\s*=\s*["\']application/ld\+json["\'])[^>]*>)'
    r'(?P<body>.*?)(?P<close></script>)',
    re.S | re.I,
)
META_TAG_RE = re.compile(r'<meta\b[^>]*>', re.I)
SOCIAL_IMAGE_KEY_RE = re.compile(r'\b(?:property|name)\s*=\s*["\'](?:og:image|twitter:image)["\']', re.I)


def migrate_schema_hosts(text):
    def count_legacy_urls(value):
        if isinstance(value, dict):
            if any(LEGACY_SITE in key for key in value):
                raise ValueError("Legacy site URL used as a JSON-LD key")
            return sum(count_legacy_urls(child) for child in value.values())
        if isinstance(value, list):
            return sum(count_legacy_urls(child) for child in value)
        if isinstance(value, str) and LEGACY_SITE in value:
            if not (value.startswith(LEGACY_SITE) and value.count(LEGACY_SITE) == 1
                    and (len(value) == len(LEGACY_SITE) or value[len(LEGACY_SITE)] in "/?#")):
                raise ValueError("Legacy site URL occurs outside a JSON-LD URL value")
            return 1
        return 0

    def replace_block(match):
        body = match.group("body")
        if LEGACY_SITE not in body:
            return match.group(0)
        document = json.loads(body)
        if count_legacy_urls(document) != body.count(LEGACY_SITE):
            raise ValueError("Unrecognised legacy site URL in JSON-LD")
        return match.group("open") + body.replace(LEGACY_SITE, SITE) + match.group("close")

    return SCHEMA_BLOCK_RE.sub(replace_block, text)


def migrate_social_image_hosts(text):
    def replace_tag(match):
        tag = match.group(0)
        return tag.replace(LEGACY_SITE, SITE) if SOCIAL_IMAGE_KEY_RE.search(tag) else tag

    return META_TAG_RE.sub(replace_tag, text)


def text_without_code(html):
    html = re.sub(r"<script\b.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style\b.*?</style>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html)


def detect_failures(rel_path, html):
    loc = locale_for(rel_path)
    if loc in {"root", "en", "en-gb"}:
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


def page_family(rel_path):
    return rel_path.split("/", 1)[1] if locale_for(rel_path) != "root" else rel_path


def hreflang_clusters(paths):
    families = {}
    for path in paths:
        rp = rel(path)
        locale = locale_for(rp)
        family = families.setdefault(page_family(rp), {})
        if locale == "en" and root_equivalent(rp):
            continue
        family["en" if locale == "root" else locale] = url_for_path(rp)
    for family in families.values():
        if "en" in family:
            family["x-default"] = family["en"]
    return families


def set_hreflang(text, alternates):
    # Replace the whole cluster so removed gates cannot leave stale or one-way links.
    text = re.sub(r'^[ \t]*' + HREFLANG_LINK_RE.pattern, "", text, flags=re.I | re.M)
    links = "\n".join(
        f'  <link rel="alternate" hreflang="{escape(locale)}" href="{escape(url)}">'
        for locale, url in sorted(alternates.items())
    )
    return text.replace("</head>", links + "\n</head>", 1)


def index_and_canonicalise():
    records = []
    paths = html_files()
    clusters = hreflang_clusters(paths)
    for path in paths:
        rp = rel(path)
        html = path.read_text(encoding="utf-8")
        html = set_hreflang(html, clusters[page_family(rp)])
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
        # Copy issues remain QA findings, never an automatic indexing restriction.
        html = set_robots(html, "index,follow")
        html = set_canonical(html, canonical)
        html = migrate_schema_hosts(html)
        html = migrate_social_image_hosts(html)
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
    "site-config.js",
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
    added_lines, removed_lines = [], []
    for line in result.stdout.splitlines():
        if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
            continue
        content = line[1:].strip()
        if not content or any(marker in content for marker in MECHANICAL_HTML_DIFF_MARKERS):
            continue
        normalized = content.replace(LEGACY_SITE, SITE)
        (added_lines if line.startswith("+") else removed_lines).append(normalized)
    return added_lines != removed_lines


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
    if canonical.startswith(SITE + "/"):
        legacy_canonical = LEGACY_SITE + canonical[len(SITE):]
        if legacy_canonical in existing_lastmods:
            return existing_lastmods[legacy_canonical]
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


def sync_robots_sitemap():
    path = ROOT / "robots.txt"
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'^Sitemap:[ \t]*https?://[^\s]+/sitemap\.xml[ \t]*$',
        f"Sitemap: {SITE}/sitemap.xml",
        text,
        flags=re.M,
    )
    if count != 1:
        raise ValueError("Expected one sitemap declaration in robots.txt")
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def write_report(records, urls):
    REPORT.parent.mkdir(exist_ok=True)
    lines = [
        "# Localisation Indexability and Copy Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        f"Indexable sitemap URLs: {len(urls)}",
        "Translation-based noindex restrictions: none",
        f"Pages with copy warnings or canonical notes: {len(records)}",
        f"Documented native reviews (not an indexing gate): {', '.join(sorted(NATIVE_REVIEWED_LOCALES)) or 'none'}",
        "",
        "## Canonical Decision",
        "",
        "All published pages use `index,follow`. `/en/` duplicates retain root English canonicals; only those canonical root URLs are in the sitemap and English hreflang entries.",
        "All other published translations have self-canonicals, sitemap entries and reciprocal language links. Copy quality and native review do not gate indexability. Search engines decide actual indexing.",
        "",
        "## Copy Warnings and Canonical Notes",
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
    parser = argparse.ArgumentParser(description="Make published translations indexable and build the sitemap.")
    parser.add_argument(
        "--sitemap-only",
        action="store_true",
        help="Rebuild sitemap.xml without changing HTML or the localisation report.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    sync_robots_sitemap()
    if args.sitemap_only:
        urls = build_sitemap()
        print(f"wrote sitemap.xml with {len(urls)} URLs")
        return

    records = index_and_canonicalise()
    urls = build_sitemap()
    write_report(records, urls)
    print(f"all published pages indexable; {len(records)} copy warnings or canonical notes")
    print(f"wrote sitemap.xml with {len(urls)} URLs")
    print(f"wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

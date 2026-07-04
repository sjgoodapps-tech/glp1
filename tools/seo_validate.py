#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.glpzy.app"

PRIORITY_PAGES = [
    "glp1-weight-dose-symptom-tracker.html",
    "mounjaro-tracker-iphone.html",
    "wegovy-tracker-iphone.html",
    "zepbound-tracker-iphone.html",
    "tirzepatide-tracker-iphone.html",
    "semaglutide-tracker-iphone.html",
    "local-first-private-glp-tracker.html",
    "glp1-dose-reminder-app.html",
    "glp1-side-effect-symptom-tracker.html",
    "glp1-weight-tracker.html",
    "glp1-progress-photo-tracker.html",
    "apple-health-glp-tracker.html",
]

AI_BOTS = [
    "GPTBot",
    "OAI-SearchBot",
    "ChatGPT-User",
    "PerplexityBot",
    "ClaudeBot",
    "Claude-SearchBot",
    "Claude-User",
    "Applebot",
    "Applebot-Extended",
    "Googlebot",
    "Google-Extended",
    "Bingbot",
    "CCBot",
]

BAD_STRINGS = [
    "PDF, PDF",
    "PDF-, PDF-",
    "Unlock exports",
    "Current mes",
    "Current maand",
    "Current mês",
    "Đăng nhập nhanh chóng",
    "Tóm tắt nhà cung cấp",
    "orders where it means reminders",
    "sleep tracking",
]


def text_without_tags(html):
    html = re.sub(r"<script\b.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style\b.*?</style>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def page_path_from_url(url):
    path = urlparse(url).path.lstrip("/")
    if not path:
        return "index.html"
    if path.endswith("/"):
        return path + "index.html"
    return path


def sitemap_urls():
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    xml = ET.parse(ROOT / "sitemap.xml")
    return [loc.text for loc in xml.findall(".//sm:loc", ns) if loc.text]


def report(results, name, ok, detail=""):
    results.append((name, ok, detail))


def check_robots(results):
    path = ROOT / "robots.txt"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    report(results, "robots.txt exists", path.exists())
    report(results, "robots allows all crawlers", "User-agent: *" in text and "Allow: /" in text)
    report(results, "robots declares sitemap", "Sitemap: https://www.glpzy.app/sitemap.xml" in text)
    blocked = [bot for bot in AI_BOTS if re.search(rf"User-agent:\s*{re.escape(bot)}.*?Disallow:\s*/", text, re.I | re.S)]
    report(results, "no explicit AI/search bot blocks", not blocked, ", ".join(blocked))


def check_sitemap(results):
    urls = sitemap_urls()
    report(results, "sitemap exists", bool(urls), f"{len(urls)} URLs")
    noindex_urls = []
    missing = []
    missing_meta = []
    for url in urls:
        path = ROOT / page_path_from_url(url)
        if not path.exists():
            missing.append(url)
            continue
        html = path.read_text(encoding="utf-8")
        if re.search(r'<meta name="robots" content="[^"]*noindex', html, re.I):
            noindex_urls.append(url)
        required = [
            ("title", r"<title>[^<]+</title>"),
            ("description", r'<meta\b(?=[^>]*name="description")(?=[^>]*content="[^"]+")[^>]*>'),
            ("canonical", r'<link\b(?=[^>]*rel="canonical")(?=[^>]*href="[^"]+")[^>]*>'),
            ("h1", r"<h1[^>]*>.*?</h1>"),
        ]
        for label, pattern in required:
            if not re.search(pattern, html, re.I | re.S):
                missing_meta.append(f"{url} missing {label}")
    report(results, "every sitemap URL resolves locally", not missing, "; ".join(missing[:10]))
    report(results, "no noindex URL in sitemap", not noindex_urls, "; ".join(noindex_urls[:10]))
    report(results, "sitemap URLs have title, meta description, canonical and H1", not missing_meta, "; ".join(missing_meta[:10]))


def json_ld_ok(html):
    scripts = re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
    if not scripts:
        return False, "missing JSON-LD"
    for script in scripts:
        try:
            json.loads(script)
        except json.JSONDecodeError as exc:
            return False, str(exc)
    return True, ""


def check_priority_pages(results):
    missing = []
    for rel in PRIORITY_PAGES:
        html = (ROOT / rel).read_text(encoding="utf-8")
        checks = {
            "answer block": "data-seo-answer" in html,
            "facts table": "data-seo-facts" in html,
            "App Store CTA": "data-app-store-link" in html and "data-app-store-campaign" in html,
            "safety block": "data-seo-safety" in html and "not measured blood concentration" in html,
            "medical safety link": 'href="medical-safety.html"' in html,
            "methodology link": 'href="methodology.html"' in html,
            "at least 2 screenshots": len(re.findall(r"<img\b", html, re.I)) >= 2,
        }
        ok_schema, schema_detail = json_ld_ok(html)
        checks["valid JSON-LD"] = ok_schema
        checks["FAQ schema backed by visible FAQ"] = ("FAQPage" not in html) or ("data-seo-faq" in html)
        for label, ok in checks.items():
            if not ok:
                detail = schema_detail if label == "valid JSON-LD" else ""
                missing.append(f"{rel}: {label} {detail}".strip())
        if "Estimated Exposure" in text_without_tags(html) and 'href="methodology.html">Estimated Exposure</a>' not in html:
            missing.append(f"{rel}: Estimated Exposure mention lacks visible methodology link")
    report(results, "priority pages have answer/facts/CTA/safety/schema/screenshots", not missing, "; ".join(missing[:20]))


def check_bad_strings(results):
    failures = []
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for bad in BAD_STRINGS:
            if bad in html:
                failures.append(f"{rel}: {bad}")
    report(results, "known bad localisation/source strings absent", not failures, "; ".join(failures[:20]))


def check_internal_links(results):
    broken = []
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("http", "mailto:", "#", "tel:")):
                continue
            target = href.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if target.endswith("/"):
                resolved = resolved / "index.html"
            if not resolved.exists():
                try:
                    broken.append(f"{rel}: {href}")
                except ValueError:
                    broken.append(f"{rel}: {href}")
    report(results, "no broken internal links", not broken, "; ".join(broken[:20]))


def main():
    results = []
    check_robots(results)
    check_sitemap(results)
    check_priority_pages(results)
    check_bad_strings(results)
    check_internal_links(results)
    width = max(len(name) for name, _, _ in results)
    failed = False
    print("SEO validation")
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        print(f"{status}  {name.ljust(width)}  {detail}")
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

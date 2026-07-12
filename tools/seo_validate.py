#!/usr/bin/env python3
import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.glpzy.app"

PRIORITY_PAGES = [
    "index.html",
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
    "methodology.html",
]

SEO_REQUIRED_PAGES = [p for p in PRIORITY_PAGES if p not in {"index.html", "methodology.html"}]

AI_BOTS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "ClaudeBot",
    "Claude-SearchBot", "Claude-User", "Applebot", "Applebot-Extended",
    "Googlebot", "Google-Extended", "Bingbot", "CCBot",
]

BAD_STRINGS = [
    "Bring a clearer lịch sử",
    "Summary for your clinician",
    "No in-app account is required</",
    "Apple Health access is optional",
    "first create a local safety sao lưu",
    "Clearer ตรวจสอบ surfaces",
    "Calendar ตรวจสอบ",
    "ส่งออก-ready records",
    "See แอป Store pricing",
    "เข้าสู่ระบบอย่างรวดเร็ว",
    "PDF, PDF",
    "PDF-, PDF-",
    "Résumés PDF, PDF et PDF",
    "sleep tracking",
]

UNSAFE_CLAIMS = [
    "measured blood concentration",
    "blood level",
    "dosing recommendation",
    "dose recommendation",
    "tells you how much",
]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def html_files():
    return sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)


def page_path_from_url(url):
    path = urlparse(url).path.lstrip("/")
    if not path:
        return "index.html"
    if path.endswith("/"):
        return path + "index.html"
    return path


def sitemap_urls():
    path = ROOT / "sitemap.xml"
    if not path.exists():
        return []
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    xml = ET.parse(path)
    return [loc.text for loc in xml.findall(".//sm:loc", ns) if loc.text]


def canonical(html):
    match = re.search(r'<link rel="canonical" href="([^"]+)"', html, re.I)
    return match.group(1) if match else ""


def noindex(html):
    return bool(re.search(r'<meta name="robots" content="[^"]*noindex', html, re.I))


def json_ld_scripts(html):
    return re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S | re.I)


def json_ld_types(html):
    types = []
    for script in json_ld_scripts(html):
        try:
            data = json.loads(script)
        except json.JSONDecodeError as exc:
            return ["invalid:" + str(exc)]
        items = data.get("@graph") if isinstance(data, dict) else None
        items = items if isinstance(items, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            t = item.get("@type")
            if isinstance(t, list):
                types.extend(t)
            elif t:
                types.append(t)
    return types


def visible_faq_pairs(html):
    match = re.search(r'<div class="faq-mini" data-seo-faq>(.*?)</div>', html, re.S | re.I)
    scope = match.group(1) if match else html
    return re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", scope, re.S | re.I)


def schema_faq_pairs(html):
    pairs = []
    for script in json_ld_scripts(html):
        try:
            data = json.loads(script)
        except json.JSONDecodeError:
            continue
        items = data.get("@graph") if isinstance(data, dict) else []
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "FAQPage":
                for entity in item.get("mainEntity", []):
                    answer = entity.get("acceptedAnswer", {}) if isinstance(entity, dict) else {}
                    pairs.append((entity.get("name", ""), answer.get("text", "")))
    return pairs


def strip_tags(text):
    return unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip())


def report(results, name, ok, detail=""):
    results.append((name, ok, detail))


def check_robots(results):
    path = ROOT / "robots.txt"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    report(results, "robots.txt exists", path.exists())
    report(results, "robots allow-all policy", "User-agent: *" in text and "Allow: /" in text and "Disallow:" not in text)
    report(results, "robots declares sitemap", "Sitemap: https://www.glpzy.app/sitemap.xml" in text)
    blocked = [bot for bot in AI_BOTS if re.search(rf"User-agent:\s*{re.escape(bot)}.*?Disallow:\s*/", text, re.I | re.S)]
    report(results, "known AI/search bots not blocked in robots", not blocked, ", ".join(blocked))


def check_sitemap(results):
    urls = sitemap_urls()
    report(results, "sitemap exists", bool(urls), f"{len(urls)} URLs")
    failures = []
    duplicates = sorted({u for u in urls if urls.count(u) > 1})
    for url in urls:
        if not url.startswith(SITE + "/"):
            failures.append(f"{url}: not absolute site URL")
            continue
        rel = page_path_from_url(url)
        path = ROOT / rel
        if not path.exists():
            failures.append(f"{url}: missing local file")
            continue
        html = path.read_text(encoding="utf-8")
        if noindex(html):
            failures.append(f"{url}: noindex URL in sitemap")
        if canonical(html) and canonical(html) != url:
            failures.append(f"{url}: canonical is {canonical(html)}")
    report(results, "sitemap has no duplicate URLs", not duplicates, "; ".join(duplicates[:10]))
    report(results, "sitemap includes canonical indexable 200 URLs only", not failures, "; ".join(failures[:20]))


def check_priority_pages(results):
    failures = []
    for rel in PRIORITY_PAGES:
        html = read(rel)
        if noindex(html):
            failures.append(f"{rel}: priority page is noindex")
        if 'styles.css?v=20260712-seo' not in html:
            failures.append(f"{rel}: missing current CSS cache key")
        if not re.search(r"<title>[^<]+</title>", html, re.I):
            failures.append(f"{rel}: missing title")
        if not re.search(r'<meta name="description" content="[^"]{40,}', html, re.I):
            failures.append(f"{rel}: missing useful meta description")
        if not canonical(html):
            failures.append(f"{rel}: missing canonical")
        types = json_ld_types(html)
        if any(t.startswith("invalid:") for t in types) or not types:
            failures.append(f"{rel}: missing or invalid JSON-LD")
        if rel == "index.html":
            for expected in ["WebSite", "SoftwareApplication", "WebPage"]:
                if expected not in types:
                    failures.append(f"{rel}: missing {expected} schema")
        elif rel == "methodology.html":
            if "TechArticle" not in types:
                failures.append(f"{rel}: missing TechArticle schema")
            if "not measured blood concentration" not in html or "not for dosing decisions" not in html:
                failures.append(f"{rel}: missing Estimated Exposure boundary")
        else:
            required = {
                "answer block": "data-seo-answer" in html,
                "facts table": "data-seo-facts" in html,
                "safety block": "data-seo-safety" in html and "not measured blood concentration" in html,
                "App Store CTA": "data-app-store-link" in html and "data-app-store-campaign" in html,
                "FAQ block": "data-seo-faq" in html,
                "FAQPage schema": "FAQPage" in types,
                "SoftwareApplication schema": "SoftwareApplication" in types,
                "related links": "data-seo-related" in html and len(re.findall(r'data-seo-related>.*?<a ', html, re.S)) >= 0,
                "medical safety link": 'href="medical-safety.html"' in html,
                "methodology link": 'href="methodology.html"' in html,
                "at least 2 screenshot slots": len(re.findall(r'data-screenshot-slot="', html)) >= 2,
            }
            for label, ok in required.items():
                if not ok:
                    failures.append(f"{rel}: missing {label}")
            visible = [(strip_tags(q), strip_tags(a)) for q, a in visible_faq_pairs(html)]
            schema = schema_faq_pairs(html)
            if visible and schema and visible != schema:
                failures.append(f"{rel}: FAQ schema differs from visible FAQ")
            for tag in re.findall(r"<img\b[^>]*>", html, re.I):
                for attr in ["alt", "width", "height"]:
                    if f" {attr}=" not in tag:
                        failures.append(f"{rel}: image missing {attr}: {tag[:120]}")
                if "loading=" not in tag and "fetchpriority=" not in tag:
                    failures.append(f"{rel}: image missing loading/fetchpriority: {tag[:120]}")
    report(results, "priority pages have metadata, modules, schema, CTAs, images and safety", not failures, "; ".join(failures[:30]))


def check_bad_strings(results):
    failures = []
    for path in html_files():
        html = path.read_text(encoding="utf-8")
        if noindex(html):
            continue
        rel = path.relative_to(ROOT).as_posix()
        is_locale_page = "/" in rel and not rel.startswith("free-lifetime/")
        for bad in BAD_STRINGS:
            if bad in {"Summary for your clinician", "No in-app account is required</", "Apple Health access is optional"} and not is_locale_page:
                continue
            if bad in html:
                failures.append(f"{rel}: {bad}")
        if re.search(r"\bsleep\b", html, re.I):
            failures.append(f"{rel}: sleep")
    report(results, "known bad localisation/source strings absent", not failures, "; ".join(failures[:30]))


def check_medical_claims(results):
    failures = []
    for path in [ROOT / p for p in PRIORITY_PAGES if (ROOT / p).exists()]:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for claim in UNSAFE_CLAIMS:
            if claim in html and claim not in {
                "measured blood concentration",
                "blood level",
            }:
                failures.append(f"{rel}: {claim}")
        if "Estimated Exposure" in html and 'href="methodology.html">Estimated Exposure</a>' not in html and rel != "methodology.html":
            failures.append(f"{rel}: Estimated Exposure lacks methodology link")
    report(results, "priority medical boundary wording is safe", not failures, "; ".join(failures[:20]))


def check_internal_links(results):
    broken = []
    for path in html_files():
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("http", "mailto:", "tel:", "#")):
                continue
            target = href.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if target.endswith("/"):
                resolved = resolved / "index.html"
            if not resolved.exists():
                broken.append(f"{rel}: {href}")
    report(results, "no broken internal links", not broken, "; ".join(broken[:30]))


def check_en_duplicates(results):
    leaks = []
    urls = set(sitemap_urls())
    for path in (ROOT / "en").glob("*.html"):
        html = path.read_text(encoding="utf-8")
        own = f"{SITE}/en/{path.name}"
        if not noindex(html):
            leaks.append(f"{path.relative_to(ROOT)} is indexable")
        if own in urls:
            leaks.append(f"{own} in sitemap")
    report(results, "/en/ duplicates are gated", not leaks, "; ".join(leaks[:20]))


def main():
    results = []
    check_robots(results)
    check_sitemap(results)
    check_priority_pages(results)
    check_bad_strings(results)
    check_medical_claims(results)
    check_internal_links(results)
    check_en_duplicates(results)
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

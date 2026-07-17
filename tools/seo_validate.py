#!/usr/bin/env python3
import json
import re
import subprocess
import sys
from datetime import date
from html import unescape
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.glpzy.app"
FACTS = json.loads((ROOT / "data" / "product-facts.json").read_text(encoding="utf-8"))
SCREENSHOTS = json.loads((ROOT / "data" / "screenshot-manifest.json").read_text(encoding="utf-8"))
LOCALE_POLICY = json.loads((ROOT / "data" / "locale-indexing.json").read_text(encoding="utf-8"))
NATIVE_REVIEWED_LOCALES = {item.lower() for item in LOCALE_POLICY["native_reviewed_locales"]}
REVIEWED_DATE = date.fromisoformat(FACTS["content_reviewed"])
REVIEWED_DISPLAY = f"{REVIEWED_DATE.day} {REVIEWED_DATE.strftime('%B %Y')}"
RESPONSIVE_WIDTHS = [360, 720, 1080, 1320]

LOCALE_DIRS = {
    "ar", "bg", "bn", "cs", "da", "de", "el", "en", "en-gb", "es-es", "es-mx",
    "et", "fi", "fil", "fr", "fr-ca", "gu", "he", "hi", "hr", "hu", "id", "it",
    "ja", "kn", "ko", "lt", "lv", "ml", "mr", "ms", "nb", "nl", "or", "pa",
    "pl", "pt-br", "pt-pt", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te",
    "th", "tr", "uk", "ur", "vi", "zh-hans", "zh-hant",
}

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

PHOTO_ALLOWANCE = "2 new photo uploads per month"
PHOTO_ALLOWANCE_SOURCES = {
    "index.html": PHOTO_ALLOWANCE,
    "en/index.html": PHOTO_ALLOWANCE,
    "en-gb/index.html": PHOTO_ALLOWANCE,
    "free-lifetime/index.html": PHOTO_ALLOWANCE,
    "glp1-progress-photo-tracker.html": PHOTO_ALLOWANCE,
    "site-config.js": PHOTO_ALLOWANCE,
    "data/product-facts.json": PHOTO_ALLOWANCE,
    "tools/seo_priority_pass.py": "FACTS['free_photo_allowance']",
}


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


def sitemap_entries():
    path = ROOT / "sitemap.xml"
    if not path.exists():
        return []
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    xml = ET.parse(path)
    entries = []
    for item in xml.findall(".//sm:url", ns):
        loc = item.find("sm:loc", ns)
        lastmod = item.find("sm:lastmod", ns)
        entries.append((loc.text if loc is not None else "", lastmod.text if lastmod is not None else ""))
    return entries


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

    date_failures = []
    dates = []
    for url, value in sitemap_entries():
        try:
            parsed = date.fromisoformat(value)
            dates.append(value)
            if parsed > date.today():
                date_failures.append(f"{url}: future lastmod {value}")
        except ValueError:
            date_failures.append(f"{url}: invalid lastmod {value or '(missing)'}")
    if len(urls) > 1 and len(set(dates)) < 2:
        date_failures.append("all sitemap URLs use the same lastmod date")
    report(results, "sitemap lastmod values are page-specific ISO dates", not date_failures, "; ".join(date_failures[:20]))


def check_priority_pages(results):
    failures = []
    for rel in PRIORITY_PAGES:
        html = read(rel)
        if noindex(html):
            failures.append(f"{rel}: priority page is noindex")
        if 'styles.css?v=20260716-fonts' not in html:
            failures.append(f"{rel}: missing current CSS cache key")
        if 'site-preflight.js?v=20260716-offer-space' not in html:
            failures.append(f"{rel}: missing offer layout preflight")
        if 'site-cta.js?v=20260716-layout' not in html:
            failures.append(f"{rel}: missing current CTA cache key")
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
                "reviewed source block": "data-seo-evidence" in html and f"Reviewed {REVIEWED_DISPLAY}" in html,
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
            if f'"dateModified": "{FACTS["content_reviewed"]}"' not in html:
                failures.append(f"{rel}: schema is missing the reviewed date")
            visible = [(strip_tags(q), strip_tags(a)) for q, a in visible_faq_pairs(html)]
            schema = schema_faq_pairs(html)
            if visible and schema and visible != schema:
                failures.append(f"{rel}: FAQ schema differs from visible FAQ")
            if len(re.findall(r'<div class="faq-mini(?:\s|\")', html, re.I)) != 1:
                failures.append(f"{rel}: expected one visible FAQ block")
            if len(re.findall(r'<div class="meta-links(?:\s|\")', html, re.I)) != 1:
                failures.append(f"{rel}: expected one related-links block")
            if 'class="responsive-picture seo-hero-picture"' not in html:
                failures.append(f"{rel}: hero is missing responsive picture markup")
            hero_picture = re.search(
                r'<picture class="responsive-picture seo-hero-picture">.*?<img\b[^>]*>',
                html,
                re.S | re.I,
            )
            if not hero_picture or 'loading="eager"' not in hero_picture.group(0) or 'fetchpriority="high"' not in hero_picture.group(0):
                failures.append(f"{rel}: hero image is not eager/high priority")
            for figure in re.findall(r'<figure class="feature-card seo-screenshot".*?</figure>', html, re.S | re.I):
                if '<source type="image/avif"' not in figure or '<source type="image/webp"' not in figure:
                    failures.append(f"{rel}: SEO screenshot is missing AVIF/WebP sources")
                image = re.search(r'<img\b[^>]*>', figure, re.I)
                if not image or 'loading="lazy"' not in image.group(0) or 'fetchpriority="high"' in image.group(0):
                    failures.append(f"{rel}: below-fold SEO screenshot has the wrong loading priority")
            for tag in re.findall(r"<img\b[^>]*>", html, re.I):
                for attr in ["alt", "width", "height"]:
                    if f" {attr}=" not in tag:
                        failures.append(f"{rel}: image missing {attr}: {tag[:120]}")
                if "loading=" not in tag and "fetchpriority=" not in tag:
                    failures.append(f"{rel}: image missing loading/fetchpriority: {tag[:120]}")
    report(results, "priority pages have metadata, modules, schema, CTAs, images and safety", not failures, "; ".join(failures[:30]))


def check_responsive_assets(results):
    failures = []
    hero_assets = SCREENSHOTS.get("priority_page_hero_assets", {})
    for rel in SEO_REQUIRED_PAGES:
        if rel not in hero_assets:
            failures.append(f"missing hero source mapping: {rel}")
    source_names = (
        set(SCREENSHOTS.get("source_assets", {}).values())
        | set(hero_assets.values())
    )
    for source_name in sorted(source_names):
        stem = Path(source_name).stem
        for width in RESPONSIVE_WIDTHS:
            for extension in ["avif", "webp"]:
                relative = Path("assets") / "responsive" / f"seo-{stem}-{width}.{extension}"
                path = ROOT / relative
                if not path.exists() or path.stat().st_size == 0:
                    failures.append(str(relative))
    report(results, "priority SEO responsive image assets exist", not failures, "; ".join(failures[:20]))


def check_content_sync(results):
    command = [sys.executable, str(ROOT / "tools" / "sync_site_content.py"), "--check"]
    process = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    detail = process.stdout.strip().replace("\n", "; ")
    report(results, "crawler-visible product and offer copy matches source data", process.returncode == 0, detail)
    offer_classes = []
    for path in html_files():
        html = path.read_text(encoding="utf-8")
        if "offer-active-only" in html or "offer-expired-only" in html:
            offer_classes.append(path.relative_to(ROOT).as_posix())
    report(results, "HTML contains one offer state rather than active and expired variants", not offer_classes, "; ".join(offer_classes[:20]))


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


def check_photo_allowance(results):
    failures = []
    for rel, expected in PHOTO_ALLOWANCE_SOURCES.items():
        path = ROOT / rel
        if not path.exists() or expected not in path.read_text(encoding="utf-8"):
            failures.append(f"{rel}: missing {expected}")

    stale_pattern = re.compile(r"\b6 new (?:photo )?uploads every 30 days\b", re.I)
    paths = html_files() + [
        ROOT / "site-config.js",
        ROOT / "data/product-facts.json",
        ROOT / "tools/seo_priority_pass.py",
    ]
    for path in paths:
        if path.exists() and stale_pattern.search(path.read_text(encoding="utf-8")):
            failures.append(f"{path.relative_to(ROOT).as_posix()}: stale photo allowance")

    report(results, "Free photo allowance is consistent", not failures, "; ".join(failures[:20]))


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


def locale_for_path(path):
    relative = path.relative_to(ROOT)
    return relative.parts[0].lower() if len(relative.parts) > 1 and relative.parts[0].lower() in LOCALE_DIRS else "root"


def check_locale_indexing(results):
    failures = []
    urls = set(sitemap_urls())
    for path in html_files():
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        locale = locale_for_path(path)
        if locale != "root" and locale not in NATIVE_REVIEWED_LOCALES:
            if not noindex(html):
                failures.append(f"{rel}: locale lacks native approval but is indexable")
            own_url = f"{SITE}/{rel}" if not rel.endswith("/index.html") else f"{SITE}/{rel[:-10]}"
            if own_url in urls:
                failures.append(f"{rel}: unreviewed locale is in sitemap")
            if re.search(r'<link\b[^>]*\bhreflang=', html, re.I):
                failures.append(f"{rel}: gated locale still exposes hreflang alternates")
        if noindex(html):
            continue
        for href in re.findall(r'<link\b[^>]*\bhreflang=["\'][^"\']+["\'][^>]*\bhref=["\']([^"\']+)', html, re.I):
            target_rel = page_path_from_url(href)
            target = ROOT / target_rel
            if target.exists() and noindex(target.read_text(encoding="utf-8")):
                failures.append(f"{rel}: hreflang points to noindex {target_rel}")
    report(
        results,
        "locale indexation requires documented native review",
        not failures,
        "; ".join(failures[:30]),
    )


def check_offer_preflight(results):
    config = (ROOT / "site-config.js").read_text(encoding="utf-8")
    preflight = (ROOT / "site-preflight.js").read_text(encoding="utf-8")
    config_expiry = re.search(r'\bexpiresAt:\s*"([^"]+)"', config)
    preflight_expiry = re.search(r'\bvar expiresAt = "([^"]+)"', preflight)
    config_key = re.search(r'\bbannerDismissStorageKey:\s*"([^"]+)"', config)
    preflight_key = re.search(r'\bvar dismissalKey = "([^"]+)"', preflight)
    failures = []
    if not config_expiry or not preflight_expiry or config_expiry.group(1) != preflight_expiry.group(1):
        failures.append("expiry timestamp differs between preflight and runtime")
    if not config_key or not preflight_key or config_key.group(1) != preflight_key.group(1):
        failures.append("dismissal key differs between preflight and runtime")
    report(results, "offer preflight matches runtime state", not failures, "; ".join(failures))


def check_release_contracts(results):
    checks = [
        ("offer expiry contract passes before and after the deadline", [sys.executable, str(ROOT / "tools" / "validate_offer_expiry.py")]),
        ("App Store CTA campaigns resolve without third-party analytics", [sys.executable, str(ROOT / "tools" / "cta_campaign_audit.py"), "--check"]),
    ]
    for label, command in checks:
        process = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        detail = process.stdout.strip().replace("\n", "; ")
        report(results, label, process.returncode == 0, detail)


def main():
    results = []
    check_robots(results)
    check_sitemap(results)
    check_priority_pages(results)
    check_responsive_assets(results)
    check_content_sync(results)
    check_bad_strings(results)
    check_medical_claims(results)
    check_photo_allowance(results)
    check_internal_links(results)
    check_en_duplicates(results)
    check_locale_indexing(results)
    check_offer_preflight(results)
    check_release_contracts(results)
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

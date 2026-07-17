#!/usr/bin/env python3
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.glpzy.app"
CSV_OUT = ROOT / "reports" / "seo-url-inventory.csv"
MD_OUT = ROOT / "reports" / "seo-url-inventory-summary.md"

LOCALE_DIRS = {
    "ar", "bg", "bn", "cs", "da", "de", "el", "en", "en-gb", "es-es", "es-mx",
    "et", "fi", "fil", "fr", "fr-ca", "gu", "he", "hi", "hr", "hu", "id", "it",
    "ja", "kn", "ko", "lt", "lv", "ml", "mr", "ms", "nb", "nl", "or", "pa",
    "pl", "pt-br", "pt-pt", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te",
    "th", "tr", "uk", "ur", "vi", "zh-hans", "zh-hant",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.robots = "index,follow"
        self.canonical = ""
        self.h1 = ""
        self.links = []
        self.images = []
        self.json_ld = []
        self.hreflangs = []
        self._tag = None
        self._ld = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._tag = "title"
        elif tag == "h1" and not self.h1:
            self._tag = "h1"
        elif tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content", "")
        elif tag == "meta" and attrs.get("name") == "robots":
            self.robots = attrs.get("content", "")
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "")
        elif tag == "link" and attrs.get("rel") == "alternate" and attrs.get("hreflang"):
            self.hreflangs.append((attrs.get("hreflang", ""), attrs.get("href", "")))
        elif tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        elif tag == "img":
            self.images.append(attrs)
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self._ld = ""

    def handle_endtag(self, tag):
        if tag in ("title", "h1"):
            self._tag = None
        if tag == "script" and self._ld is not None:
            self.json_ld.append(self._ld)
            self._ld = None

    def handle_data(self, data):
        if self._tag == "title":
            self.title += data.strip()
        elif self._tag == "h1":
            self.h1 += data.strip()
        elif self._ld is not None:
            self._ld += data


def html_files():
    return sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)


def rel(path):
    return path.relative_to(ROOT).as_posix()


def url_for_path(rel_path):
    if rel_path == "index.html":
        return f"{SITE}/"
    if rel_path.endswith("/index.html"):
        return f"{SITE}/{rel_path[:-10]}"
    return f"{SITE}/{rel_path}"


def path_from_url(url):
    path = urlparse(url).path.lstrip("/")
    if not path:
        return "index.html"
    if path.endswith("/"):
        return path + "index.html"
    return path


def strip_text(html):
    text = re.sub(r"<script\b.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sitemap_urls():
    path = ROOT / "sitemap.xml"
    if not path.exists():
        return set()
    xml = ET.parse(path)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {loc.text for loc in xml.findall(".//sm:loc", ns) if loc.text}


def locale(rel_path):
    first = rel_path.split("/", 1)[0]
    return first if "/" in rel_path and first in LOCALE_DIRS else "root"


def family(rel_path):
    name = Path(rel_path).name
    if name == "index.html":
        return "home"
    if name in {"mounjaro-tracker-iphone.html", "wegovy-tracker-iphone.html", "zepbound-tracker-iphone.html"}:
        return "medicine"
    if name in {"tirzepatide-tracker-iphone.html", "semaglutide-tracker-iphone.html"}:
        return "ingredient"
    if name in {"glp1-dose-reminder-app.html", "glp1-side-effect-symptom-tracker.html", "glp1-weight-tracker.html", "glp1-progress-photo-tracker.html", "apple-health-glp-tracker.html"}:
        return "feature"
    if "privacy" in name or "local-first" in name or "data-rights" in name:
        return "privacy"
    if "medical-safety" in name or "methodology" in name or "support" in name or "terms" in name:
        return "trust"
    if "tracker" in name or "reminder" in name:
        return "commercial"
    return "other"


def schema_types(scripts):
    types = []
    for script in scripts:
        try:
            data = json.loads(script)
        except json.JSONDecodeError:
            types.append("invalid")
            continue
        graph = data.get("@graph") if isinstance(data, dict) else None
        items = graph if isinstance(graph, list) else [data]
        for item in items:
            t = item.get("@type") if isinstance(item, dict) else None
            if isinstance(t, list):
                types.extend(t)
            elif t:
                types.append(t)
    return sorted(set(types))


def build_inlinks(files):
    counts = defaultdict(int)
    for file in files:
        html = file.read_text(encoding="utf-8")
        base = file.parent
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("http", "mailto:", "tel:", "#")):
                continue
            target = href.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            resolved = (base / target).resolve()
            if target.endswith("/"):
                resolved = resolved / "index.html"
            try:
                counts[resolved.relative_to(ROOT).as_posix()] += 1
            except ValueError:
                pass
    return counts


def recommendation(status, noindex, canonical, own_url, html, word_count, parser):
    if status != 200:
        return "delete"
    if noindex:
        return "noindex"
    if canonical and canonical != own_url:
        return "redirect"
    missing_priority = []
    if not parser.title:
        missing_priority.append("title")
    if not parser.description:
        missing_priority.append("description")
    if not parser.h1:
        missing_priority.append("h1")
    if family(path_from_url(own_url)) in {"medicine", "ingredient", "feature", "broad tracker"}:
        for marker, label in [
            ("data-seo-answer", "answer"),
            ("data-seo-facts", "facts"),
            ("data-seo-safety", "safety"),
            ("data-app-store-link", "CTA"),
        ]:
            if marker not in html:
                missing_priority.append(label)
    if missing_priority:
        return "fix-before-index"
    if word_count < 250 and family(path_from_url(own_url)) in {"medicine", "ingredient", "feature", "commercial"}:
        return "fix-before-index"
    return "index"


def main():
    files = html_files()
    inlinks = build_inlinks(files)
    sitemap = sitemap_urls()
    rows = []
    p0 = []

    for file in files:
        rp = rel(file)
        own_url = url_for_path(rp)
        html = file.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(html)
        text = strip_text(html)
        noindex = "noindex" in parser.robots.lower()
        types = schema_types(parser.json_ld)
        row = {
            "url": own_url,
            "path": rp,
            "locale": locale(rp),
            "page_family": family(rp),
            "http_status": 200,
            "canonical_url": parser.canonical,
            "index_noindex": "noindex" if noindex else "index",
            "sitemap_included": "yes" if own_url in sitemap else "no",
            "title": parser.title,
            "meta_description": parser.description,
            "h1": parser.h1,
            "word_count": len(re.findall(r"\b[\w'-]+\b", text)),
            "answer_block_present": "yes" if "data-seo-answer" in html else "no",
            "facts_table_present": "yes" if "data-seo-facts" in html else "no",
            "safety_block_present": "yes" if "data-seo-safety" in html or "Estimated Exposure is a personal tracking estimate" in html else "no",
            "app_store_cta_present": "yes" if "data-app-store-link" in html or "apps.apple.com" in html else "no",
            "screenshot_slots_images_count": len(parser.images),
            "json_ld_present": "yes" if parser.json_ld else "no",
            "faq_present": "yes" if "data-seo-faq" in html or "<details" in html else "no",
            "faqpage_schema_present": "yes" if "FAQPage" in " ".join(types) else "no",
            "hreflang_cluster_status": f"{len(parser.hreflangs)} alternates" if parser.hreflangs else "none",
            "internal_inlinks_count": inlinks.get(rp, 0),
        }
        row["recommendation"] = recommendation(200, noindex, parser.canonical, own_url, html, row["word_count"], parser)
        if row["recommendation"] == "fix-before-index" or (noindex and own_url in sitemap):
            p0.append(row)
        rows.append(row)

    CSV_OUT.parent.mkdir(exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    counts = defaultdict(int)
    for row in rows:
        counts[row["recommendation"]] += 1
    lines = [
        "# GLPzy URL Inventory Summary",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        f"Total generated HTML URLs: {len(rows)}",
        f"Sitemap URLs: {len(sitemap)}",
        "",
        "## Recommendations",
        "",
    ]
    for key in sorted(counts):
        lines.append(f"- {key}: {counts[key]}")
    lines.extend(["", "## P0 Pages Not Ready For Indexing", ""])
    blockers = [r for r in rows if r["recommendation"] in {"noindex", "fix-before-index"}]
    if not blockers:
        lines.append("None.")
    else:
        for row in blockers[:300]:
            lines.append(f"- `{row['path']}`: {row['recommendation']} ({row['index_noindex']}, sitemap {row['sitemap_included']})")
        if len(blockers) > 300:
            lines.append(f"- ...and {len(blockers) - 300} more rows in the CSV.")
    lines.extend(["", "## Files", "", f"- Machine inventory: `{CSV_OUT.relative_to(ROOT)}`", f"- Summary: `{MD_OUT.relative_to(ROOT)}`"])
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {CSV_OUT.relative_to(ROOT)} with {len(rows)} URLs")
    print(f"wrote {MD_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

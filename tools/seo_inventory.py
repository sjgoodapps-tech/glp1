#!/usr/bin/env python3
import csv
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.glpzy.app"
OUT = ROOT / "seo-url-inventory.csv"


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
        self.json_ld = 0
        self.hreflangs = []
        self._tag = None
        self._in_ld = False

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
            self.hreflangs.append(attrs.get("hreflang", ""))
        elif tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        elif tag == "img":
            self.images.append(attrs.get("src", ""))
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self._in_ld = True
            self.json_ld += 1

    def handle_endtag(self, tag):
        if tag in ("title", "h1"):
            self._tag = None
        elif tag == "script":
            self._in_ld = False

    def handle_data(self, data):
        if self._tag == "title":
            self.title += data.strip()
        elif self._tag == "h1":
            self.h1 += data.strip()


def strip_text(html):
    text = re.sub(r"<script\b.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sitemap_urls():
    xml = ET.parse(ROOT / "sitemap.xml")
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in xml.findall(".//sm:loc", ns) if loc.text]


def path_from_url(url):
    path = urlparse(url).path.lstrip("/")
    if not path:
        path = "index.html"
    elif path.endswith("/"):
        path += "index.html"
    return path


def family(path):
    name = Path(path).name
    if name == "index.html":
        return "home"
    if "mounjaro" in name or "wegovy" in name or "zepbound" in name or "tirzepatide" in name or "semaglutide" in name:
        return "medicine"
    if "privacy" in name or "local-first" in name or "data-rights" in name:
        return "privacy"
    if "medical-safety" in name or "methodology" in name:
        return "trust"
    if "tracker" in name or "reminder" in name:
        return "commercial"
    return "support"


def locale(path):
    first = path.split("/", 1)[0]
    return first if "/" in path and first not in {"free-lifetime"} else "root"


def main():
    urls = sitemap_urls()
    html_files = sorted(ROOT.rglob("*.html"))
    inlink_counts = {}
    for file in html_files:
        rel = file.relative_to(ROOT).as_posix()
        html = file.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("http", "mailto:", "#")):
                continue
            target = (file.parent / href.split("#", 1)[0]).resolve()
            try:
                key = target.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            if key.endswith("/"):
                key += "index.html"
            inlink_counts[key] = inlink_counts.get(key, 0) + 1

    rows = []
    sitemap_set = set(urls)
    for url in urls:
        path = path_from_url(url)
        file = ROOT / path
        status = 200 if file.exists() else 404
        parser = PageParser()
        html = file.read_text(encoding="utf-8") if file.exists() else ""
        if html:
            parser.feed(html)
        text = strip_text(html)
        noindex = "noindex" in parser.robots.lower()
        recommendation = "index"
        if status != 200 or noindex or not parser.canonical or not parser.title or not parser.description or not parser.h1:
            recommendation = "fix-before-index" if status == 200 else "delete"
        if noindex:
            recommendation = "noindex"
        rows.append({
            "path": "/" + path.replace("index.html", "") if path.endswith("/index.html") else "/" + path,
            "locale": locale(path),
            "page_family": family(path),
            "status_code": status,
            "index_noindex": "noindex" if noindex else "index",
            "canonical": parser.canonical,
            "title": parser.title,
            "meta_description": parser.description,
            "h1": parser.h1,
            "word_count": len(re.findall(r"\b[\w'-]+\b", text)),
            "internal_inlinks": inlink_counts.get(path, 0),
            "app_store_cta_present": "yes" if "apps.apple.com" in html or "data-app-store-link" in html else "no",
            "answer_block_present": "yes" if "data-seo-answer" in html else "no",
            "safety_block_present": "yes" if "data-seo-safety" in html or "Estimated Exposure is a personal tracking estimate" in html else "no",
            "screenshots_present": len(parser.images),
            "json_ld_present": "yes" if parser.json_ld else "no",
            "hreflang_cluster_status": f"{len(parser.hreflangs)} alternates" if parser.hreflangs else "none",
            "sitemap_included": "yes" if url in sitemap_set else "no",
            "recommendation": recommendation,
        })

    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)} with {len(rows)} URLs")


if __name__ == "__main__":
    sys.exit(main())

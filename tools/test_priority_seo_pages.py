#!/usr/bin/env python3
"""Local-only regression coverage for completed priority SEO page families.

This does not certify native-language quality, medical advice, legal adequacy, or
mobile rendering. Run from a checked-out feature-branch worktree on a local Mac.
GitHub Actions must remain disabled.
"""
import json
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("es-es", "es-mx", "de", "fr", "fr-ca")
SLUGS = (
    "apple-health-weight-loss-injection-tracker.html",
    "weight-loss-injection-tracker.html",
    "glp1-dose-reminder-app.html",
    "glp1-progress-photo-tracker.html",
    "glp1-side-effect-symptom-tracker.html",
    "glp1-weight-tracker.html",
)
FAQ_COUNTS = (3, 3, 6, 7, 6, 6)
IMAGE_COUNTS = (0, 0, 4, 3, 2, 3)
ALT_LOCALES = frozenset(("en",) + LOCALES + ("x-default",))
ROOT_SITE = "https://oneglp.app/"


def head(html):
    match = re.search(r"<head\b[\s\S]*?</head>", html, re.I)
    return match.group() if match else ""


def attr_tags(text, tag):
    return re.findall(r"<" + tag + r"\b[^>]*>", text, re.I)


def attr(tag, name):
    match = re.search(r'\\b' + re.escape(name) + r'=\"([^\"]+)\"', tag, re.I)
    return match.group(1) if match else None


def url(path):
    return ROOT_SITE + path


class PrioritySEORegression(unittest.TestCase):
    def test_english_and_priority_locales(self):
        for index, slug in enumerate(SLUGS):
            expected = {"en": url(slug), "x-default": url(slug)}
            expected.update({locale: url(locale + "/" + slug) for locale in LOCALES})
            for locale in ("en",) + LOCALES:
                rel = slug if locale == "en" else locale + "/" + slug
                with self.subTest(path=rel):
                    html = (ROOT / rel).read_text(encoding="utf-8")
                    markup = head(html)
                    doc_lang = attr(attr_tags(html, "html")[0], "lang")
                    self.assertEqual(locale, doc_lang.lower().replace("_", "-"))
                    self.assertEqual("index,follow", next(
                        (attr(x, "content") for x in attr_tags(markup, "meta")
                         if attr(x, "name") == "robots"), None))
                    canonical = [
                        attr(x, "href") for x in attr_tags(markup, "link")
                        if attr(x, "rel") == "canonical"
                    ]
                    self.assertEqual([expected[locale]], canonical)
                    alts = {}
                    for tag in attr_tags(markup, "link"):
                        language = attr(tag, "hreflang")
                        if language:
                            self.assertNotIn(language, alts)
                            alts[language] = attr(tag, "href")
                    self.assertEqual(expected, alts)
                    self.assertIn("<main", html)
                    self.assertIn("OneGLP", markup)
                    self.assertEqual(FAQ_COUNTS[index], len(re.findall(r"<details\b", html)))
                    self.assertEqual(IMAGE_COUNTS[index], len(re.findall(r"<figure\b", html)))
                    for script in re.findall(
                        r'<script\b[^>]*type="application/ld\+json"[^>]*>([\s\S]*?)</script>',
                        html, re.I):
                        json.loads(script)
                    if locale != "en":
                        self.assertNotIn("glpzy.app", markup)
                        for asset in re.findall(
                            r'(?:src|href)="../(assets/[^"]+)"', html):
                            self.assertTrue((ROOT / asset).is_file(),
                                            rel + ": asset missing " + asset)

    def test_sitemap_matches_every_canonical_page(self):
        sm = ET.parse(ROOT / "sitemap.xml")
        urls = [x.text for x in sm.findall(
            ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertEqual(len(urls), len(set(urls)))
        expected = set()
        for page in ROOT.rglob("*.html"):
            relative = page.relative_to(ROOT).as_posix()
            if relative.startswith("en/") or ".git" in page.parts:
                continue
            if relative.endswith("/index.html"):
                relative = relative[:-10]
            elif relative == "index.html":
                relative = ""
            expected.add(url(relative))
        self.assertEqual(expected, set(urls))

    def test_translated_text_ctas_are_preserved(self):
        js = (ROOT / "site-cta.js").read_text(encoding="utf-8")
        self.assertIn("anchor.classList.contains('button')", js)
        for locale in LOCALES:
            for slug in SLUGS:
                html = (ROOT / locale / slug).read_text(encoding="utf-8")
                self.assertRegex(html, r'<a[^>]*class="[^"]*button')
                self.assertIn("data-app-store-link", html)


if __name__ == "__main__":
    unittest.main()

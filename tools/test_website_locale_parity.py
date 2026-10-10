#!/usr/bin/env python3
"""Regression tests for the read-only structural localisation audit."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from website_locale_parity import ESSENTIAL, audits, facts


def fixture(locale: str = "es-es"):
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    (root / "data").mkdir()
    (root / "data/locale-indexing.json").write_text(json.dumps({
        "native_reviewed_locales": [],
        "index_translations": True,
    }))
    (root / locale).mkdir()
    attrs = f'lang="{locale}"' + (' dir="rtl"' if locale == "ar" else '')
    en = '<html lang="en"><main><section><h2>1. Something</h2><p>Source meaning.</p><ul><li>Detail</li></ul></section></main></html>'
    tr = f'<html {attrs}><main><section data-english-section="1"><h2>1. Traducción</h2><p>Significado correcto.</p><ul><li>Detalle</li></ul></section></main></html>'
    for path in ESSENTIAL:
        (root / path).write_text(en, encoding="utf-8")
        (root / locale / path).write_text(tr, encoding="utf-8")
    return temp, root


class LocaleParityTests(unittest.TestCase):
    def test_completed_structural_pages_are_not_native_approved(self):
        h, root = fixture()
        try:
            status = audits(root, ("es-es",))["locales"]["es-es"]
            self.assertEqual([], status["essential_errors"])
            self.assertEqual("pending", status["native_review"])
            self.assertEqual(6, len(status["essential"]))
        finally:
            h.cleanup()

    def test_shortened_privacy_translation_is_detected(self):
        h, root = fixture()
        try:
            (root / "es-es/privacy.html").write_text('<html lang="es-ES"><main><p>Resumen.</p></main></html>')
            status = audits(root, ("es-es",))["locales"]["es-es"]
            self.assertTrue(any(x["page"] == "privacy.html" for x in status["essential_errors"]))
        finally:
            h.cleanup()

    def test_missing_essential_is_detected(self):
        h, root = fixture()
        try:
            (root / "es-es/medical-safety.html").unlink()
            status = audits(root, ("es-es",))["locales"]["es-es"]
            self.assertIn("medical-safety.html", status["missing_pages"])
            self.assertTrue(any(x["page"] == "medical-safety.html" for x in status["essential_errors"]))
        finally:
            h.cleanup()

    def test_english_only_landing_page_remains_reportable(self):
        h, root = fixture()
        try:
            (root / "new-feature.html").write_text('<html lang="en"><main><p>English only.</p></main></html>')
            status = audits(root, ("es-es",))["locales"]["es-es"]
            self.assertIn("new-feature.html", status["missing_pages"])
            self.assertFalse(status["essential_errors"])
        finally:
            h.cleanup()

    def test_arabic_requires_rtl(self):
        h, root = fixture("ar")
        try:
            privacy = root / "ar/privacy.html"
            privacy.write_text(privacy.read_text().replace(' dir="rtl"', ''))
            status = audits(root, ("ar",))["locales"]["ar"]
            self.assertTrue(any("right-to-left" in str(x["issues"]) for x in status["essential_errors"]))
        finally:
            h.cleanup()

    def test_noindex_is_a_defect(self):
        h, root = fixture()
        try:
            privacy = root / "es-es/privacy.html"
            privacy.write_text(privacy.read_text().replace("<main>", '<meta name="robots" content="noindex"><main>'))
            status = audits(root, ("es-es",))["locales"]["es-es"]
            self.assertTrue(any("noindex" in str(x["issues"]) for x in status["essential_errors"]))
        finally:
            h.cleanup()

    def test_fact_counts_not_declared_semantic_approval(self):
        v = facts('<main><section><h2>1. Example</h2><p>text</p></section></main>')
        self.assertEqual([1], v["numbered_headings"])
        self.assertEqual(1, v["paragraphs"])


if __name__ == "__main__":
    unittest.main()

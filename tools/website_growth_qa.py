#!/usr/bin/env python3
"""Focused regression fixtures for website copy, locale coverage and attribution."""
import unittest
import json
import re
from html import escape, unescape
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

import localisation_qa as qa
import sync_site_content as sync
from sync_website_copy import corrected_html, TRANSLATIONS, ESSENTIAL_TRANSLATIONS


class WebsiteGrowthQA(unittest.TestCase):
    def test_export_and_purchase_copy_all_locales(self):
        for locale in qa.LOCALE_DIRS:
            copy = TRANSLATIONS.get('en' if locale == 'en-gb' else locale) or ESSENTIAL_TRANSLATIONS[locale]
            for key in ('site.card.control.body', 'paywall.legal'):
                original = f'<p data-i18n="{key}">Wrong restore or billing text</p>'
                with self.subTest(locale=locale, key=key):
                    result = corrected_html(f'{locale}/data-rights.html', original)
                    self.assertEqual(result, f'<p data-i18n="{key}">{escape(copy[key])}</p>')

    def test_noindex_is_not_a_copy_check_exemption(self):
        html = '<meta name="robots" content="noindex,follow"><p data-i18n="site.card.control.body">Replace device records</p>'
        self.assertTrue(qa.check_website_copy('pt-pt/privacy.html', html))

    def test_missing_priority_anchor_is_a_failure(self):
        self.assertTrue(qa.check_website_copy('ar/index.html', '<p>GLPzy</p>'))

    def test_english_is_allowed_in_british_english(self):
        self.assertEqual(qa.scan_one('en-gb/index.html', '<p>Administration route and dosing frequency</p>', True), [])

    def test_wrong_domain_korean_is_replaced(self):
        result = corrected_html('ko/data-rights.html', '<h2 data-i18n="history.export.title">수출 내역</h2>')
        self.assertIn('기록 내보내기', result)
        self.assertNotIn('수출', result)

    def test_safety_warning_does_not_require_english_in_japanese(self):
        text = '<p>Estimated Exposure: 血中濃度 投与判断 医療上の助言</p>'
        self.assertEqual(qa.scan_one('ja/medical-safety.html', text, True), [])
        self.assertTrue(qa.scan_one('ja/medical-safety.html', '<p>血中濃度 投与判断</p>', True))

    def test_live_manifest_includes_all_gated_locales(self):
        paths = qa.live_paths()
        self.assertEqual({qa.locale_for(p) for p in paths} - {'root'}, qa.LOCALE_DIRS)
        for locale in ('ar', 'zh-hans', 'zh-hant', 'pt-pt', 'ja', 'hi', 'it', 'ko'):
            self.assertIn(f'{locale}/data-rights.html', paths)
            self.assertIn(f'{locale}/medical-safety.html', paths)

    def test_english_link_preserves_page(self):
        for rel, target in [('ar/privacy.html', '../privacy.html'), ('index.html', 'index.html'), ('free-lifetime/index.html', '../free-lifetime/index.html')]:
            result = corrected_html(rel, '<a href="../en/index.html" data-language-option="en">English</a>')
            self.assertIn(f'href="{target}"', result)

    def test_provider_reaches_static_home_offer_and_locale_links(self):
        facts = json.loads(sync.FACTS_PATH.read_text())
        facts['app_store_campaign']['provider_token'] = '123456'
        with patch.object(sync, 'FACTS_PATH') as source:
            source.read_text.return_value = json.dumps(facts)
            _, desired = sync.desired_files(sync.parsed_time('2026-09-08T12:00:00Z'))
        for rel in ('index.html', 'free-lifetime/index.html', 'ar/index.html', 'mounjaro-tracker-iphone.html'):
            text = desired[sync.ROOT / rel]
            tags = re.findall(r'<a\b(?=[^>]*\bdata-app-store-link\b)[^>]*>', text)
            self.assertTrue(tags, rel)
            for tag in tags:
                query = parse_qs(urlsplit(unescape(re.search(r'href="([^"]+)"', tag).group(1))).query)
                self.assertEqual(query['pt'], ['123456'])
                self.assertEqual(query['mt'], ['8'])
                self.assertTrue(query['ct'])

    def test_reject_provider_placeholders(self):
        facts = json.loads(sync.FACTS_PATH.read_text())
        facts['app_store_campaign']['provider_token'] = 'REPLACE_ME'
        with patch.object(sync, 'FACTS_PATH') as source:
            source.read_text.return_value = json.dumps(facts)
            with self.assertRaises(ValueError):
                sync.desired_files(sync.parsed_time('2026-09-08T12:00:00Z'))


if __name__ == '__main__':
    unittest.main(verbosity=2)

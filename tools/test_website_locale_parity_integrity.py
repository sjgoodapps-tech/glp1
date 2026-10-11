#!/usr/bin/env python3
"""Offline regressions for honest coverage counts and policy source integrity."""
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import website_locale_parity as parity


class AuditIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'data').mkdir()
        (self.root / 'data/locale-indexing.json').write_text(
            json.dumps({'native_reviewed_locales': []}), encoding='utf-8')
        (self.root / 'ar').mkdir()
        for page in parity.ESSENTIAL:
            self.write(page, self.html('en'))
            self.write('ar/' + page, self.html('ar'))

    @staticmethod
    def html(locale, numbers=(1, 2), reference=''):
        direction = ' dir="rtl"' if locale == 'ar' else ''
        text = 'Source explanation.' if locale == 'en' else 'شرح مترجم.'
        sections = ''.join(f'<section><h2>{n}. Heading</h2><p>{text}</p></section>'
                           for n in numbers)
        return f'<html lang="{locale}"{direction}><main>{sections}{reference}</main></html>'

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding='utf-8')

    def report(self):
        return parity.audits(self.root, ('ar',))

    def status(self):
        return self.report()['locales']['ar']

    def test_missing_exceptions_are_not_counted_as_present(self):
        for name in parity.EXPECTED_EXCEPTIONS:
            self.write(name, self.html('en'))
        status = self.status()
        self.assertEqual(6, status['pages_present'])
        self.assertEqual(8, status['english_pages'])
        self.assertEqual(sorted(parity.EXPECTED_EXCEPTIONS),
                         status['exception_pages_not_present'])
        self.assertEqual('PASS', status['structural_gate'])

    def test_present_exception_is_counted(self):
        self.write('languages.html', self.html('en'))
        self.write('ar/languages.html', self.html('ar'))
        status = self.status()
        self.assertEqual(7, status['pages_present'])
        self.assertEqual([], status['exception_pages_not_present'])

    def test_inventory_reconciles_with_missing_pages_and_exceptions(self):
        self.write('languages.html', self.html('en'))
        self.write('new-feature.html', self.html('en'))
        (self.root / 'ar/support.html').unlink()
        status = self.status()
        self.assertEqual(status['english_pages'], status['pages_present'] +
                         len(status['missing_pages']) +
                         len(status['exception_pages_not_present']))
        self.assertEqual('FAIL', status['structural_gate'])

    def test_duplicate_numbered_sections_fail(self):
        self.write('ar/privacy.html', self.html('ar', (1, 1, 2)))
        self.assertTrue(any('numbered policy sections' in str(x['issues'])
                            for x in self.status()['essential_errors']))

    def test_reordered_numbered_sections_fail(self):
        self.write('ar/privacy.html', self.html('ar', (2, 1)))
        self.assertTrue(any('numbered policy sections' in str(x['issues'])
                            for x in self.status()['essential_errors']))

    def test_arabic_indic_numbered_sections_pass(self):
        self.write('ar/privacy.html', self.html('ar', ('١', '٢')))
        self.assertEqual([], self.status()['essential_errors'])

    def test_missing_english_policy_is_source_error(self):
        (self.root / 'privacy.html').unlink()
        report = self.report()
        self.assertTrue(any(x['page'] == 'privacy.html' for x in report['source_errors']))
        self.assertEqual('FAIL', report['locales']['ar']['structural_gate'])

    def test_missing_english_main_is_source_error(self):
        self.write('privacy.html', '<html lang="en"><p>Broken source.</p></html>')
        self.assertTrue(any(x['page'] == 'privacy.html' for x in self.report()['source_errors']))

    def test_missing_reference_fails_policy_gate(self):
        ref = '<a href="https://www.accessdata.fda.gov/example.pdf">Official reference</a>'
        self.write('medical-safety.html', self.html('en', reference=ref))
        self.assertTrue(any('reference links missing' in str(x['issues'])
                            for x in self.status()['essential_errors']))

    def test_changed_reference_fails_policy_gate(self):
        self.write('medical-safety.html', self.html('en', reference=
                   '<a href="https://www.accessdata.fda.gov/example.pdf">Reference</a>'))
        self.write('ar/medical-safety.html', self.html('ar', reference=
                   '<a href="https://www.accessdata.fda.gov/other.pdf">مرجع</a>'))
        self.assertTrue(self.status()['essential_errors'])

    def test_same_reference_with_translated_label_passes(self):
        url = 'https://example.org/label?a=1&amp;b=2'
        self.write('medical-safety.html', self.html('en', reference=f'<a href="{url}">Reference</a>'))
        self.write('ar/medical-safety.html', self.html('ar', reference=f"<a href='{url}'>مرجع</a>"))
        self.assertEqual([], self.status()['essential_errors'])

    def test_same_site_and_mail_links_are_not_official_reference_requirements(self):
        ref = '<a href="https://oneglp.app/privacy.html">Privacy</a><a href="mailto:sjgoodapps@gmail.com">Support</a>'
        self.write('terms.html', self.html('en', reference=ref))
        self.assertEqual([], self.status()['essential_errors'])

    def test_source_failure_makes_both_cli_gates_nonzero(self):
        (self.root / 'privacy.html').unlink()
        for gate in ('--gate', '--gate-essential'):
            with self.subTest(gate=gate), patch.object(parity, 'ROOT', self.root), \
                    patch.object(sys, 'argv', ['audit', '--locale', 'ar', gate]), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, parity.main())

    def test_complete_fixture_passes_both_cli_gates(self):
        for gate in ('--gate', '--gate-essential'):
            with self.subTest(gate=gate), patch.object(parity, 'ROOT', self.root), \
                    patch.object(sys, 'argv', ['audit', '--locale', 'ar', gate]), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, parity.main())

    def test_audit_does_not_mutate_input_files(self):
        def snapshot():
            return {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob('*') if p.is_file()}
        before = snapshot()
        self.report()
        self.assertEqual(before, snapshot())

    def test_structure_does_not_certify_translation_or_native_review(self):
        status = self.status()
        self.assertEqual('pending', status['native_review'])
        self.assertIn('not certified', status['semantic_translation_review'])
        self.assertIn('not certified', status['mobile_visual_review'])

    def test_missing_essential_translation_still_fails(self):
        (self.root / 'ar/support.html').unlink()
        self.assertIn('support.html', self.status()['missing_pages'])
        self.assertTrue(self.status()['essential_errors'])

    def test_rejects_locale_traversal(self):
        with self.assertRaises(ValueError):
            parity.audits(self.root, ('../ar',))


if __name__ == '__main__':
    unittest.main()

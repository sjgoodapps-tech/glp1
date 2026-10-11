import tempfile
import unittest
from pathlib import Path
from priority_locale_progress_gate import audit, ESSENTIAL, SEO, PRIORITY

class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.page='<html lang="{lang}" {direction}><head><title>Example</title><meta name="description" content="Something"><link rel="canonical" href="https://oneglp.app/{url}"></head><body><main><section><p>Text</p></section></main></body></html>'
        for page in ESSENTIAL+SEO:
            self.write(page, self.page.format(lang='en',direction='',url=page))
        for locale in PRIORITY:
            for page in ESSENTIAL+SEO:
                self.write(locale+'/'+page,self.page.format(lang=locale,direction='dir="rtl"' if locale=='ar' else '',url=locale+'/'+page))
    def write(self,name,html):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(html,encoding='utf8')
    def test_complete_fixture(self):
        self.assertTrue(audit(self.root)['structural_pass'])
    def test_missing_seo_red(self):
        (self.root/'ja'/SEO[0]).unlink();self.assertFalse(audit(self.root)['structural_pass'])
    def test_missing_reference_red(self):
        p=self.root/ESSENTIAL[3]
        p.write_text(p.read_text().replace('<p>Text</p>','<p><a href="https://www.cdc.gov/bmi/about/index.html">Reference</a></p>'))
        self.assertEqual('defective',audit(self.root)['locales']['ja']['pages'][ESSENTIAL[3]]['status'])
    def test_arabic_rtl_red(self):
        p=self.root/'ar'/ESSENTIAL[0]
        p.write_text(p.read_text().replace('dir="rtl"',''))
        self.assertIn('rtl',audit(self.root)['locales']['ar']['pages'][ESSENTIAL[0]]['issues'])
    def test_nonindex_red(self):
        p=self.root/'it'/SEO[0]
        p.write_text(p.read_text().replace('</head>','<meta name="robots" content="noindex"></head>'))
        self.assertFalse(audit(self.root)['structural_pass'])
    def test_missing_english_source_red(self):
        (self.root/SEO[0]).unlink();self.assertIn(SEO[0],audit(self.root)['source_errors'])

    def test_regional_app_store_identity_passes(self):
        en=self.root/ESSENTIAL[4]
        local=self.root/'it'/ESSENTIAL[4]
        en.write_text(en.read_text().replace('<p>Text</p>',
            '<p><a href="https://apps.apple.com/us/app/id6761775005?ct=a">App Store</a></p>'))
        local.write_text(local.read_text().replace('<p>Text</p>',
            '<p><a href="https://apps.apple.com/it/app/id6761775005?ct=b">App Store</a></p>'))
        self.assertEqual('present', audit(self.root)['locales']['it']['pages'][ESSENTIAL[4]]['status'])

    def test_changed_app_store_identity_fails(self):
        en=self.root/ESSENTIAL[4]
        local=self.root/'it'/ESSENTIAL[4]
        en.write_text(en.read_text().replace('<p>Text</p>',
            '<p><a href="https://apps.apple.com/us/app/id6761775005">App Store</a></p>'))
        local.write_text(local.read_text().replace('<p>Text</p>',
            '<p><a href="https://apps.apple.com/it/app/id99999999">App Store</a></p>'))
        self.assertIn('missing_references',
                      audit(self.root)['locales']['it']['pages'][ESSENTIAL[4]]['issues'])

    def test_not_native_certified(self):
        r=audit(self.root);self.assertFalse(r['accepted']);self.assertEqual('not certified',r['meaning_and_legal_review'])
if __name__=='__main__':unittest.main()
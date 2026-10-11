import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('qa', str(Path(__file__).resolve().parent / 'priority_seo_reciprocity_qa.py'))
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)
class Checks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.orig_loc, self.orig_seo = qa.LOCALES, qa.SEO
        qa.LOCALES = ('ar',)
        qa.SEO = ('example.html',)
        self.addCleanup(lambda: setattr(qa, 'LOCALES', self.orig_loc))
        self.addCleanup(lambda: setattr(qa, 'SEO', self.orig_seo))
        (self.root/'ar').mkdir()
        def doc(loc):
            path = 'example.html' if loc == 'en' else 'ar/example.html'
            self.root.joinpath(path).write_text('<html><head><link rel="canonical" href="https://oneglp.app/'+path+'">'+'<link rel="alternate" hreflang="en" href="https://oneglp.app/example.html"><link rel="alternate" hreflang="ar" href="https://oneglp.app/ar/example.html"><link rel="alternate" hreflang="x-default" href="https://oneglp.app/example.html"></head></html>')
        doc('en');doc('ar')
        self.root.joinpath('sitemap.xml').write_text('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://oneglp.app/example.html</loc></url><url><loc>https://oneglp.app/ar/example.html</loc></url></urlset>')
    def test_complete_passes(self): self.assertEqual([], qa.audit(self.root))
    def test_sitemap_missing_fails(self):
        p=self.root/'sitemap.xml';p.write_text(p.read_text().replace('<url><loc>https://oneglp.app/ar/example.html</loc></url>',''))
        self.assertTrue(any('sitemap' in x for x in qa.audit(self.root)))
    def test_reciprocal_missing_fails(self):
        p=self.root/'example.html';p.write_text(p.read_text().replace('<link rel="alternate" hreflang="ar" href="https://oneglp.app/ar/example.html">',''))
        self.assertTrue(any('reciprocal ar' in x for x in qa.audit(self.root)))
    def test_canonical_wrong_fails(self):
        p=self.root/'ar/example.html';p.write_text(p.read_text().replace('rel="canonical" href="https://oneglp.app/ar/example.html"','rel="canonical" href="https://oneglp.app/example.html"'))
        self.assertTrue(any('canonical mismatch' in x for x in qa.audit(self.root)))
    def test_missing_file_fails(self):
        (self.root/'ar/example.html').unlink();self.assertTrue(any('missing file' in x for x in qa.audit(self.root)))
if __name__ == '__main__': unittest.main()
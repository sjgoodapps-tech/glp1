#!/usr/bin/env python3
"""Check draft branding and preservation against the committed website."""
import io
import json
import re
import subprocess
import tarfile
from html.parser import HTMLParser
from pathlib import Path
from sync_rebrand import DATA, ROOT, SCHEMA_BLOCK, transform
from localisation_qa import LOCALE_DIRS


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def selected(self, predicate):
        return [attrs for tag, attrs in self.tags if predicate(tag, attrs)]


def main():
    facts = json.loads((ROOT / 'data/product-facts.json').read_text())
    assert facts['publisher'] == 'Steven Good'
    assert facts['publisher_type'] == 'Person'
    organization_id = facts['site_url'].rstrip('/') + '/#organization'
    publisher_id = facts['site_url'].rstrip('/') + '/#publisher'
    schema_counts = {'Person': 0, 'WebSite': 0, 'SoftwareApplication': 0, 'MobileApplication': 0}

    def check_identity(value):
        if isinstance(value, list):
            for item in value:
                check_identity(item)
        elif isinstance(value, dict):
            kinds = value.get('@type', [])
            kinds = [kinds] if isinstance(kinds, str) else kinds
            assert value.get('@id') != organization_id
            assert not ('Organization' in kinds and value.get('name') in {'GLPzy', 'OneGLP', 'Steven Good'})
            for kind in schema_counts:
                if kind in kinds and 'name' in value:
                    expected = facts['publisher'] if kind == 'Person' else facts['app_name']
                    assert value['name'] == expected, (kind, value['name'], expected)
                    if kind == 'Person':
                        assert value['@id'] == publisher_id
                        assert 'logo' not in value and 'sameAs' not in value
                    if kind in {'SoftwareApplication', 'MobileApplication'}:
                        assert value['alternateName'] == DATA['previous_name']
                        assert value['subjectOf']['@id'].endswith('/glpzy-is-now-oneglp/#webpage')
                    schema_counts[kind] += 1
            for relation in ('publisher', 'author'):
                if isinstance(value.get(relation), dict) and '@id' in value[relation]:
                    assert value[relation]['@id'] == publisher_id
            for child in value.values():
                check_identity(child)

    for name in ('GLPzy', 'OneGLP'):
        graph = {'@context': 'https://schema.org', '@graph': [
            {'@type': ['Organization'], '@id': organization_id, 'name': name, 'logo': 'app-icon.png', 'sameAs': [facts['app_store_url']]},
            {'@type': 'WebSite', 'name': name},
            {'@type': 'SoftwareApplication', 'name': name, 'publisher': {'@id': organization_id}, 'author': {'@id': organization_id}},
            {'@type': 'MobileApplication', 'name': name, 'publisher': {'@type': 'Organization', 'name': name}},
        ]}
        sample = '<div class="topbar"></div><script type="application/ld+json">' + json.dumps(graph) + '</script>'
        sample += '<p>Published by ' + name + '.</p>'
        result = transform(ROOT / 'terms.html', sample)
        parsed = json.loads(SCHEMA_BLOCK.search(result)[2])
        check_identity(parsed)
        assert parsed['@graph'][2]['publisher'] == {'@id': publisher_id}
        assert parsed['@graph'][2]['author'] == {'@id': publisher_id}
        assert '<p>Published by ' + facts['publisher'] + '.</p>' in result
        assert transform(ROOT / 'terms.html', result) == result
    from seo_priority_pass import PAGES, schema_graph, methodology_schema
    for rel, page in PAGES.items():
        check_identity(json.loads(SCHEMA_BLOCK.search(schema_graph(rel, page))[2]))
    check_identity(json.loads(SCHEMA_BLOCK.search(methodology_schema())[2]))
    for key in schema_counts:
        schema_counts[key] = 0
    fixture = ('<div class="topbar"></div><p>GLPzy is made available by Steven Good.</p>'
               '<p>Steven Good, trading as GLPzy, provides GLPzy.</p>')
    corrected = transform(ROOT / 'terms.html', fixture)
    assert '<p>OneGLP is made available by Steven Good.</p>' in corrected
    assert '<p>Steven Good provides OneGLP.</p>' in corrected
    assert transform(ROOT / 'terms.html', corrected) == corrected
    assert set(DATA['notices']) == LOCALE_DIRS
    archive = tarfile.open(fileobj=io.BytesIO(subprocess.check_output(['git', 'archive', DATA['preservation_base']], cwd=ROOT)))
    count = 0
    for entry in archive.getmembers():
        if not entry.isfile():
            continue
        before = archive.extractfile(entry).read()
        path = ROOT / entry.name
        if entry.name.startswith('assets/'):
            assert path.read_bytes() == before, f'Existing asset changed: {entry.name}'
        if not entry.name.endswith('.html'):
            continue
        old, text = before.decode(), path.read_text()
        assert transform(path, text) == text, f'Rebrand drift: {entry.name}'
        a, b = Page(old), Page(text)
        for select in (
            lambda t, x: t == 'a' and 'apps.apple.com' in x.get('href', ''),
            lambda t, x: t in ('img', 'source'),
        ):
            old_tags, new_tags = a.selected(select), b.selected(select)
            if entry.name.startswith('th/'):
                old_tags = [dict(attrs, **{'aria-label': 'ดูราคาบน App Store'})
                            if attrs.get('aria-label') == 'See แอป Store pricing' else attrs
                            for attrs in old_tags]
            assert old_tags == new_tags, f'Protected markup changed: {entry.name}'
        legal = r'<p\b[^>]*>(?:(?!</p>).)*Steven Good(?:(?!</p>).)*</p>'
        expected_legal = [p.replace('GLPzy is made available', 'OneGLP is made available')
                          .replace('Steven Good, trading as GLPzy,', 'Steven Good')
                          for p in re.findall(legal, old, re.S)]
        actual_legal = [p for p in re.findall(legal, text, re.S) if 'Published by Steven Good.' not in p]
        assert expected_legal == actual_legal, entry.name
        assert 'trading as GLPzy' not in text and 'trading as OneGLP' not in text, entry.name
        assert 'GLPzy is made available' not in text, entry.name
        if entry.name in ('terms.html', 'en/terms.html', 'en-gb/terms.html'):
            assert 'OneGLP is made available by Steven Good' in text, entry.name
        assert text.count('data-i18n="site.rebrand.notice"') == 1, entry.name
        assert 'OneGLP' in re.search(r'<title>(.*?)</title>', text, re.S)[1], entry.name
        assert 'Published by OneGLP.' not in text and 'Published by GLPzy.' not in text, entry.name
        if 'Published by GLPzy.' in old:
            assert 'Published by Steven Good.' in text, entry.name
        for script in SCHEMA_BLOCK.finditer(text):
            check_identity(json.loads(script[2]))
        count += 1
    for name in ('CNAME', 'robots.txt', 'site-i18n.js', 'site-preflight.js'):
        assert (ROOT / name).read_bytes() == archive.extractfile(name).read(), name
    from locale_indexing_qa import audit
    assert not audit(), 'Indexability or language-link regression'
    print(f'PASS: {count} pages, all 53 locale notices, corrected terms product names, preserved legal identity/canonicals/App Store links/screenshots/storage files; valid JSON-LD; all translations indexable.')
    assert all(schema_counts.values()), schema_counts
    print(f'PASS: publisher/app identity separation, reference preservation and idempotence; schema entries: {schema_counts}')


if __name__ == '__main__':
    main()

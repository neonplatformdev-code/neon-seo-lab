"""Independent local fixture checks; never executes NEON or fetches a website."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

ROOT = Path(__file__).resolve().parents[1] / 'public'
ORIGIN = 'https://lab.neonplatform.online'
CASES = ('perfect', 'missing-title', 'missing-description', 'noindex', 'broken-html')
TITLE = 'NEON SEO Lab — Контрольная страница'
DESCRIPTION = 'Контрольная HTML-страница NEON SEO Lab для проверки доказательного технического SEO-отчёта.'
TAIL = '<!-- intentionally unfinished comment: <meta name="robots" content="noindex">'
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.stack, self.links, self.titles, self.h1, self.robots, self.descriptions, self.canonical = [], [], [], [], [], [], []
        self.ids = set()
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append((tag, attrs.get('rel'), attrs[key]))
        assert not any(key.startswith('on') for key in attrs), 'Inline handler'
        if tag == 'title': self.titles.append('')
        if tag == 'h1': self.h1.append('')
        if tag == 'meta':
            name = attrs.get('name', '').lower()
            if name == 'robots': self.robots.append(attrs.get('content'))
            if name == 'description': self.descriptions.append(attrs.get('content'))
        if tag == 'link' and attrs.get('rel') == 'canonical': self.canonical.append(attrs['href'])
        if tag not in VOID: self.stack.append(tag)
    def handle_endtag(self, tag):
        assert self.stack and self.stack[-1] == tag, ('Invalid nesting', tag, self.stack)
        self.stack.pop()
    def handle_data(self, data):
        if 'title' in self.stack: self.titles[-1] += data
        if 'h1' in self.stack: self.h1[-1] += data

pages = {}
for f in ROOT.rglob('*.html'):
    text = f.read_text(encoding='utf-8')
    assert text.startswith('<!doctype html>')
    assert '<html lang="ru">' in text and 'name="viewport"' in text
    page = Page(text)
    assert not page.stack, (f, page.stack)
    if f.parent.name == 'broken-html':
        assert page.rawdata == TAIL, 'Keep exactly the deliberate incomplete comment'
    else: assert not page.rawdata, (f, 'Incomplete markup')
    assert len(page.h1) == 1
    pages[f.relative_to(ROOT).as_posix()] = page
assert set(pages) == {'index.html', *(case + '/index.html' for case in CASES)}
for file, page in pages.items():
    for tag, rel, link in page.links:
        url = urlsplit(link)
        if url.netloc:
            assert tag == 'link' and rel == 'canonical' and link.startswith(ORIGIN + '/')
            continue
        assert not url.scheme and not link.startswith('//')
        path = url.path or '/' + file
        target = ROOT / path.lstrip('/')
        if path.endswith('/'): target = target / 'index.html'
        assert target.is_file(), (file, link)
        if url.fragment:
            assert url.fragment in pages[target.relative_to(ROOT).as_posix()].ids, (file, link)
assert not pages['index.html'].robots
manifest = json.loads((ROOT / 'scenarios.json').read_text(encoding='utf-8'))
assert manifest['approved_origin'] == ORIGIN
assert [x['id'] for x in manifest['scenarios']] == list(CASES)
perfect = (ROOT / 'perfect/index.html').read_text(encoding='utf-8')
findings = {'perfect': [], 'missing-title': ['title_not_observed'], 'missing-description': ['description_not_observed'], 'noindex': ['indexability_blocked'], 'broken-html': []}
for entry in manifest['scenarios']:
    case = entry['id'];page = pages[case + '/index.html'];expected = perfect.replace(ORIGIN + '/perfect/', ORIGIN + '/' + case + '/')
    if case == 'missing-title': expected = expected.replace('<title>' + TITLE + '</title>', '')
    if case == 'missing-description': expected = expected.replace('<meta name="description" content="' + DESCRIPTION + '">', '')
    if case == 'noindex': expected = expected.replace('</head>', '<meta name="robots" content="noindex"></head>')
    if case == 'broken-html': expected += TAIL
    assert (ROOT / case / 'index.html').read_text(encoding='utf-8') == expected, ('Unexpected fixture differences', case)
    assert page.titles == ([] if case == 'missing-title' else [TITLE])
    assert page.descriptions == ([] if case == 'missing-description' else [DESCRIPTION])
    assert page.robots == (['noindex'] if case == 'noindex' else [])
    assert page.canonical == [ORIGIN + '/' + case + '/']
    props = entry['expected_html']
    assert props['title'] == (None if case == 'missing-title' else TITLE)
    assert props['description'] == (None if case == 'missing-description' else DESCRIPTION)
    assert props['canonical'] == page.canonical[0] and props['meta_robots'] == page.robots
    assert props['h1'] == page.h1[0] and props['complete'] == (case != 'broken-html')
    report = entry['expected_report']
    assert report['finding_classes'] == findings[case]
    assert report['outcome'] == ('controlled_failure' if case == 'broken-html' else 'draft')
    assert report['failure_code'] == ('unsupported_html' if case == 'broken-html' else None)
    assert report['review_status'] == (None if case == 'broken-html' else 'not_independently_verified')
    assert entry['test_status'] == 'not_run' and entry['fixture_status'] == 'ready_for_testing'
css = (ROOT / 'assets/site.css').read_text(encoding='utf-8')
assert '@import' not in css and 'url(' not in css
assert '@media(max-width:620px)' in css and 'prefers-reduced-motion' in css
js = (ROOT / 'assets/site.js').read_text(encoding='utf-8')
assert not re.search(r'fetch\(|XMLHttpRequest|https?://|localStorage|cookie', js)
assert not (ROOT / 'robots.txt').exists() and not (ROOT / 'sitemap.xml').exists()
print('PASS: 6 HTML pages, 5 independent scenario expectations, exact fixture deltas, local links and fragments, JSON agreement, no external dependencies, responsive CSS.')

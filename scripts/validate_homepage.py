"""Check the rendered site without third-party Python dependencies."""

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

SITE = Path('_site')
ORIGIN = 'https://ejanadens.github.io'
BASE = '/LJT-Homepage'
EXPECTED_PAGES = {'index.html', 'publications/index.html'}
TITLES = [
    'SynLogic: Synthesizing Verifiable Reasoning Data at Scale for Learning Logical Reasoning and Beyond',
    'On the Perception Bottleneck of VLMs for Chart Understanding',
    'On the Universal Truthfulness Hyperplane Inside LLMs',
    'In-Context Sharpness as Alerts: An Inner Representation Perspective for Hallucination Mitigation',
    'C-Eval: A Multi-Level Multi-Discipline Chinese Evaluation Suite for Foundation Models',
    'Composing Parameter-Efficient Modules with Arithmetic Operations',
]
CONTACTS = {
    'mailto:jliugi@connect.ust.hk',
    'https://github.com/Vicent0205',
    'https://scholar.google.com/citations?hl=en&user=tbK9jl4AAAAJ&view_op=list_works&sortby=pubdate',
    'https://x.com/junteng88716710',
}


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.references = []
        self.ids = set()
        self.hidden_depth = 0
        self.publication_count = 0
        self.feed(source)
        self.text = ' '.join(''.join(self.parts).split())

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag in {'head', 'script', 'style'}:
            self.hidden_depth += 1
        if tag in {'p', 'br', 'li', 'div', 'h1', 'h2', 'h3'}:
            self.parts.append(' ')
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for name in ('href', 'src'):
            if attrs.get(name):
                self.references.append(attrs[name])
        if tag == 'meta' and (attrs.get('name') == 'twitter:url' or attrs.get('property') == 'og:url'):
            self.references.append(attrs['content'])
        if 'publication-title' in attrs.get('class', '').split():
            self.publication_count += 1

    def handle_endtag(self, tag):
        if tag in {'head', 'script', 'style'}:
            self.hidden_depth -= 1
        if tag in {'p', 'li', 'div', 'h1', 'h2', 'h3'}:
            self.parts.append(' ')

    def handle_data(self, data):
        if not self.hidden_depth:
            self.parts.append(data)


actual_pages = {path.relative_to(SITE).as_posix() for path in SITE.rglob('*.html')}
assert actual_pages == EXPECTED_PAGES, f'Unexpected/missing pages: {actual_pages ^ EXPECTED_PAGES}'
documents = {
    name: Document((SITE / name).read_text(encoding='utf-8'))
    for name in EXPECTED_PAGES
}
for name, document in documents.items():
    assert document.publication_count == 6, f'{name}: expected six publications'
    for title in TITLES:
        assert document.text.count(title) == 1, f'{name}: missing or duplicate publication: {title}'
    assert document.text.count('First author.') == 3, f'{name}: incorrect first-author roles'
    assert document.text.count('Co-author.') == 3, f'{name}: incorrect co-author roles'
    for venue in ('arXiv, 2025', 'EMNLP, 2024', 'ICML, 2024', 'NeurIPS, 2023'):
        assert venue in document.text, f'{name}: missing venue/year: {venue}'
    for repository in ('Vision4Chart', 'Universal_Truthfulness_Hyperplane'):
        assert repository in document.text, f'{name}: missing recorded code repository'
    assert CONTACTS <= set(document.references), f'{name}: missing recorded contact link'
    for placeholder in ('Your Name', 'Your Sidebar Name', 'Red Brick University', 'none@example.org', 'Paper Title Number', 'John Doe', 'Jane Doe'):
        assert placeholder not in document.text, f'{name}: template placeholder: {placeholder}'

about = documents['index.html']
for fact in (
    'Junteng Liu', 'first-year PhD candidate', 'HKUST NLP Group',
    'Hong Kong University of Science and Technology', 'Shanghai Jiao Tong University',
    'Professor Junxian He', 'June 2024', 'Ph.D. in Computer Science', '2024–Present',
    'B.Eng.', '2020–2024', 'Research Intern, MINIMAX', 'February 2025–Present',
    'Research Intern, Tencent WXG', 'June 2024–September 2024', 'Zifei Shan',
    'Research Intern, Shanghai AI Lab', 'June 2023–December 2023', 'Prof. Yu Cheng',
    'natural language processing', 'machine learning',
    'LLM Reasoning and Reinforcement Learning',
    'Hallucination in Vision-Language Models (VLM)',
    'LLM Truthfulness and Interpretability', 'Zhiyuan Honor Scholarship',
    'jliugi@connect.ust.hk', 'Vicent0205', '@junteng88716710',
):
    assert fact in about.text, f'About: missing recorded fact: {fact}'


def check_local_reference(reference, source):
    parsed = urlsplit(urljoin(f'{ORIGIN}{BASE}/{source}', reference))
    if parsed.scheme not in {'http', 'https'} or parsed.netloc != urlsplit(ORIGIN).netloc:
        return
    path = unquote(parsed.path)
    if path == BASE:
        path += '/'
    assert path.startswith(BASE + '/'), f'{source}: URL escapes project base path: {reference}'
    relative = path[len(BASE) + 1:]
    target = SITE / relative
    if target.is_dir():
        target /= 'index.html'
    assert target.is_file(), f'{source}: missing local target: {reference}'
    if parsed.fragment and target.suffix == '.html':
        target_name = target.relative_to(SITE).as_posix()
        assert unquote(parsed.fragment) in documents[target_name].ids, f'{source}: missing anchor: {reference}'


for name, document in documents.items():
    for reference in document.references:
        check_local_reference(reference, name)

manifest = json.loads((SITE / 'images/manifest.json').read_text(encoding='utf-8'))
assert manifest['name'] == 'Junteng Liu'
assert manifest['start_url'] == BASE + '/'
for icon in manifest['icons']:
    check_local_reference(icon['src'], 'images/manifest.json')
for excluded in ('files', 'talkmap', 'markdown_generator', 'scripts'):
    assert not (SITE / excluded).exists(), f'Template/support content unexpectedly published: {excluded}'

print('Validated: exactly two content pages, all six publications on both, recorded profile/contact facts, and project-relative links.')

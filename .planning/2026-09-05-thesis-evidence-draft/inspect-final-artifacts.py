import hashlib
import json
import re
import subprocess
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[2]
work = root / '.planning/2026-09-05-thesis-evidence-draft'
output = work / 'render-qa'
manuscript = root / 'paper/manuscript/thesis-ko.qmd'
bibliography = root / 'paper/manuscript/references-current-evidence.bib'
evidence = root / 'paper/manuscript/evidence/current-evidence-20260905'
figures = root / 'paper/manuscript/figures/current-evidence-20260905'
pdf_file = root / 'thesis-current-evidence-20260905.pdf'


def sha256(file_path):
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def load_json(file_path):
    return json.loads(file_path.read_text())


def verify_record(record, directory):
    file_path = directory / record['frozen_path']
    assert sha256(file_path) == record['sha256'], str(file_path)
    assert file_path.stat().st_size == record['bytes'], str(file_path)


text = manuscript.read_text()
keys = set(re.findall(r'@[^\s{]+\{([^,]+),', bibliography.read_text()))
citations = set(re.findall(r'@([A-Za-z][A-Za-z0-9:_.-]*)', text))
references = {key for key in citations if key.startswith(('fig-', 'tbl-', 'eq-'))}
citations -= references
labels = set(re.findall(r'\{#((?:fig|tbl|eq)-[\w-]+)', text))
assert citations == keys and len(keys) == 13, (citations - keys, keys - citations)
assert references <= labels, references - labels
assert len([label for label in labels if label.startswith('fig-')]) == 3
assert len([label for label in labels if label.startswith('tbl-')]) == 7
assert not re.search(r'(?i)prime.?agent|openresearch|\bexa\b|TODO|TBD|0\.000297', text)
assert text.count('```{=typst}') == 1 and text.count('```') == 2

source_records = load_json(evidence / 'sources.json')['sources']
assert {source['citation_key'] for source in source_records} == keys
for source in source_records:
    assert source['publication_status'] == 'published'
    verify_record(source, evidence)
    if 'text_extraction' in source:
        verify_record(source['text_extraction'], evidence)
snapshot = load_json(evidence / 'snapshot.json')
for receipt in snapshot['receipts'].values():
    verify_record(receipt, evidence)
graph = load_json(evidence / 'context-graph.json')
identifiers = {node['id'] for node in graph['nodes']}
assert len(identifiers) == len(graph['nodes'])
assert all(edge['source'] in identifiers and edge['target'] in identifiers for edge in graph['edges'])
assert graph['canonical_runtime_graph_modified'] is False
asset_checks = load_json(figures / 'asset-validation.json')
for asset in asset_checks['assets']:
    for filename, metadata in asset['files'].items():
        assert sha256(figures / filename) == metadata['sha256'], filename
backup = root / 'paper/manuscript/versions/2026-09-05-current-evidence/before/thesis-ko.qmd'
assert sha256(backup) == '4bb75d4eb3b400f1f7e435343eb76afd98ff56900d86c4c6d69bc5d6bbf152ac'

document = pymupdf.open(pdf_file)
pages = []
outside = []
page_texts = []
for page_number, page in enumerate(document, 1):
    page_text = page.get_text()
    page_texts.append(page_text)
    spans = [span for block in page.get_text('dict')['blocks'] if 'lines' in block for line in block['lines'] for span in line['spans']]
    for span in spans:
        if not span['text'].strip():
            continue
        bounds = pymupdf.Rect(span['bbox'])
        if bounds.x0 < -1 or bounds.y0 < -1 or bounds.x1 > page.rect.width + 1 or bounds.y1 > page.rect.height + 1:
            outside.append({'page': page_number, 'text': span['text'], 'bounds': list(bounds)})
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(1.35, 1.35), alpha=False)
    filename = output / f'final-page-{page_number:02d}.png'
    pixmap.save(filename)
    pages.append({'page': page_number, 'width_pt': page.rect.width, 'height_pt': page.rect.height, 'text_characters': len(page_text), 'raster_images': len(page.get_images()), 'min_text_size_pt': min(span['size'] for span in spans if span['text'].strip()), 'preview': str(filename.relative_to(root))})
assert not outside, outside
pdf_text = '\n'.join(page_texts)
assert '\ufffd' not in pdf_text
assert not re.search(r'(?i)@(?:fig|tbl)-|TODO|TBD|prime.?agent|openresearch|\bexa\b', pdf_text)
assert all(f'[{number}]' in pdf_text for number in range(1, 14))
(output / 'final-text.txt').write_text(pdf_text)

for start in range(0, len(pages), 4):
    sheet = Image.new('RGB', (1120, 1640), '#dddddd')
    draw = ImageDraw.Draw(sheet)
    for offset in range(min(4, len(pages) - start)):
        page_number = start + offset + 1
        preview = Image.open(output / f'final-page-{page_number:02d}.png')
        preview.thumbnail((545, 785))
        horizontal = (offset % 2) * 560 + (560 - preview.width) // 2
        vertical = (offset // 2) * 820 + 25
        sheet.paste(preview, (horizontal, vertical))
        draw.text((horizontal, vertical - 18), f'PAGE {page_number}', fill='black')
    sheet.save(output / f'final-contact-{start + 1:02d}-{min(start + 4, len(pages)):02d}.png')

fonts = subprocess.check_output(['pdffonts', str(pdf_file)], text=True)
font_rows = fonts.strip().splitlines()[2:]
assert font_rows and all(re.search(r'\byes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$', row) for row in font_rows), fonts
report = {'scope': 'static document/evidence checks and rendered PDF bounds; agent visual review recorded separately', 'pdf_sha256': sha256(pdf_file), 'manuscript_sha256': sha256(manuscript), 'page_count': len(pages), 'citation_count': len(keys), 'figure_count': 3, 'table_count': 7, 'source_and_receipt_hashes_valid': True, 'figure_asset_hashes_valid': True, 'cross_references_resolve': True, 'citation_keys_match_retained_published_sources': True, 'all_pdf_fonts_embedded': True, 'outside_page_text': outside, 'graph_nodes': len(graph['nodes']), 'graph_edges': len(graph['edges']), 'pre_edit_backup_unchanged': True, 'pdffonts': fonts, 'pages': pages}
(output / 'automated-checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: value for key, value in report.items() if key not in ['pages', 'pdffonts']}, ensure_ascii=False, indent=2))

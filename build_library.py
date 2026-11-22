#!/usr/bin/env python3
"""Build the offline SVG catalog from retained archives and downloaded manifests."""
import hashlib
import json
import re
from collections import Counter
from html import escape
from pathlib import Path
from urllib.parse import quote
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SVG = 'http://www.w3.org/2000/svg'


def write(relative, data):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f'Unsafe archive path: {relative}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode('utf-8'))


def build():
    records, sources, invalid = [], [], []
    for archive, repo in [('bioicons-main.zip', 'duerrsimon/bioicons'),
                          ('SiliCoDraw-main.zip', 'Alex-D-C/SiliCoDraw')]:
        path = ROOT / 'sources' / archive
        with ZipFile(path) as z:
            sources.append(dict(repository='https://github.com/' + repo,
                                archive='sources/' + archive,
                                commit=z.comment.decode(),
                                sha256=hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()))
            if repo.endswith('/bioicons'):
                prefix = 'bioicons-main/static/icons/'
                indexed = json.loads(z.read(prefix + 'icons.json'))
                authors = json.loads(z.read(prefix + 'authors.json'))
                def normalized(path):
                    return path.replace(' ', '_').replace('.drawio.svg', '.svg').replace('.min.svg', '.svg').casefold()
                by_path = {normalized('/'.join([r['license'], r['category'], r['author'], r['name'] + '.svg'])): r for r in indexed}
                found = set()
                for n in z.namelist():
                    if not n.startswith(prefix) or n.endswith('/'):
                        continue
                    rel = n[len(prefix):]
                    local = 'icons/Bioicons-original/' + rel
                    write(local, z.read(n))
                    if not rel.endswith('.svg'):
                        continue
                    found.add(normalized(rel))
                    try:
                        ET.fromstring(z.read(n))
                    except ET.ParseError as error:
                        invalid.append(dict(path=local, error=str(error)))
                        continue
                    parts = rel.split('/')
                    r = by_path.get(normalized(rel), dict(license=parts[0], category=parts[1], author=parts[2], name=Path(rel).stem))
                    records.append(dict(name=r['name'], category=r['category'], collection='Bioicons original',
                                        author=r['author'], license=r['license'], tags=r['name'].replace('_', ' '),
                                        path=local, source='https://github.com/' + repo + '/blob/' + sources[-1]['commit'] + '/static/icons/' + quote(rel),
                                        credit=r['name'] + ' — ' + r['author'] + ' ' + authors.get(r['author'], '') + ' — ' + r['license']))
                write('notices/Bioicons/catalog-missing-files.json', json.dumps(sorted(set(by_path) - found), ensure_ascii=False, indent=2))
                assert len(found) == sum(n.startswith(prefix) and n.endswith('.svg') for n in z.namelist())
                for name in ['LICENSE', 'README.md', 'CITATION.cff']:
                    write('notices/Bioicons/' + name, z.read('bioicons-main/' + name))
            else:
                prefix = 'SiliCoDraw-main/icon-expansions/'
                packs = json.loads(z.read(prefix + 'index.json'))['packs']
                write('notices/SiliCoDraw/README.md', z.read(prefix + 'README.md'))
                for pack in packs:
                    pack_prefix = prefix + pack['id'] + '/'
                    for name in ['LICENSE.txt', 'ATTRIBUTION.md', 'pack.json', 'names.json']:
                        write('notices/' + pack['id'] + '/' + name, z.read(pack_prefix + name))
                    count = 0
                    for chunk in pack['chunks']:
                        data = json.loads(z.read(pack_prefix + chunk['file']))
                        for key, r in data.items():
                            local = 'icons/' + pack['id'] + '/' + key.split(':', 1)[-1] + '.svg'
                            credit = r.get('credit') or ' — '.join(str(v) for v in [r['n'], r.get('by'), r.get('src'), r.get('lic', pack['license']), 'adapted by SiliCoDraw', pack.get('credit')] if v)
                            svg = '<svg xmlns="' + SVG + '" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 100 100" width="512" height="512"><title>' + escape(r['n']) + '</title><desc>' + escape(credit) + '</desc>' + r['svg'] + '</svg>'
                            ET.fromstring(svg)
                            write(local, svg)
                            records.append(dict(name=r['n'], category=r.get('cat', chunk['cat']), collection=pack['name'],
                                                author=r.get('by', pack.get('by', '')), license=r.get('lic', pack['license']),
                                                tags=r.get('t', ''), path=local, source=r.get('src', pack['url']), credit=credit))
                            count += 1
                    assert count == pack['count'], (pack['id'], count, pack['count'])
    extra_path = ROOT / 'expanded-catalog.json'
    if extra_path.exists():
        records.extend(json.loads(extra_path.read_text()))
        for name in ['biocartoon-assets.sqlite.gz', 'phylopic-index.json', 'extras-coverage.json', 'arcadia-organisms-v1.2.zip']:
            file = ROOT / 'sources' / name
            if file.exists():
                with file.open('rb') as handle:
                    digest = hashlib.file_digest(handle, 'sha256').hexdigest()
                sources.append(dict(archive='sources/' + name, sha256=digest))
    assert len({r['path'] for r in records}) == len(records)
    assert all((ROOT / r['path']).is_file() for r in records)
    all_count = len(records)
    before_counts = dict(Counter(r['collection'] for r in records))
    unique, duplicates, rejected = {}, [], []
    for r in records:
        data = (ROOT / r['path']).read_bytes()
        node = ET.fromstring(data)
        if any(e.tag.split('}')[-1] in {'script', 'iframe'} or any(re.fullmatch(r'on[a-z]+', k.lower()) for k in e.attrib) for e in node.iter()):
            rejected.append(dict(path=r['path'], reason='Active SVG content; original preserved'))
            continue
        r['contains_raster'] = any(e.tag.split('}')[-1] == 'image' for e in node.iter())
        r['sha256'] = hashlib.sha256(data).hexdigest()
        r['kind'] = 'AI生成（来源标记）' if r.get('generative_ai_used') else ('通用符号' if r.get('source_group') in {'noto', 'openmoji'} or 'OpenMoji' in r['collection'] else '科研与技术')
        previous = unique.get(r['sha256'])
        if previous:
            previous['also_available_from'].append({k: v for k, v in r.items() if k not in {'sha256', 'contains_raster', 'kind'}})
            if r.get('generative_ai_used'):
                previous['generative_ai_used'] = True
                previous['kind'] = 'AI生成（来源标记）'
            duplicates.append(dict(path=r['path'], same_as=previous['path'], sha256=r['sha256']))
        else:
            r['also_available_from'] = []
            unique[r['sha256']] = r
    records = list(unique.values())
    # shortcut: exact byte deduplication; recolored or re-exported drawings remain separate.
    counts = dict(Counter(r['collection'] for r in records))
    write('catalog.json', json.dumps(records, ensure_ascii=False, indent=2))
    write('notices/invalid-originals.json', json.dumps(invalid, ensure_ascii=False, indent=2))
    write('notices/exact-duplicates.json', json.dumps(duplicates, ensure_ascii=False, indent=2))
    write('notices/active-svg-exclusions.json', json.dumps(rejected, ensure_ascii=False, indent=2))
    write('sources.json', json.dumps(dict(sources=sources, counts=counts, before_deduplication_counts=before_counts,
          downloaded_valid_svg_records=all_count, usable_files=len(records), exact_duplicates=len(duplicates), active_svg_exclusions=len(rejected),
          kind_counts=dict(Counter(r['kind'] for r in records)), raster_containing_svg=sum(r['contains_raster'] for r in records),
          invalid_original_files=len(invalid)), ensure_ascii=False, indent=2))
    payload = json.dumps(records, ensure_ascii=False).replace('<', '\\u003c')
    write('catalog.js', 'const ICONS = ' + payload + ';\n')
    print(json.dumps(dict(total_files=len(records), collections=counts), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    build()

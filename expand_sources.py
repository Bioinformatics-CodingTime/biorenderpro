#!/usr/bin/env python3
"""Download published SVG catalogs; preserve metadata, originals and HTTP outcomes."""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
import sqlite3
import subprocess
from urllib.parse import quote, urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
ALLOWED = {'assets.biocartoon.com', 'api.phylopic.org', 'images.phylopic.org'}


def local(path):
    result = (ROOT / path).resolve()
    if not result.is_relative_to(ROOT):
        raise ValueError('Path leaves library: ' + path)
    result.parent.mkdir(parents=True, exist_ok=True)
    return result


def save(path, obj):
    local(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2))


def downloads(items, label):
    # API pagination stays at five requests; static CDN files use sixteen connections.
    parallel = 5 if label.endswith('pages') else 16
    config = ['parallel', f'parallel-max = {parallel}', 'location', 'fail', 'silent', 'show-error',
              'connect-timeout = 15', 'max-time = 90', 'retry = 2', 'retry-max-time = 180',
              'proto = "=https"', 'proto-redir = "=https"',
              'user-agent = "ScientificIconLibrary/1.0"',
              'write-out = "%{filename_effective}\\t%{http_code}\\t%{exitcode}\\n"']
    pending = []
    for item in items:
        url, path = item['download_url'], local(item['path'])
        parsed = urlparse(url)
        if parsed.scheme != 'https' or parsed.hostname not in ALLOWED:
            raise ValueError('Unexpected download origin: ' + url)
        if path.exists() and path.stat().st_size:
            continue
        pending.append(item)
        # JSON quoting is also valid for these curl config strings, never shell-evaluated.
        config += ['url = ' + json.dumps(url), 'output = ' + json.dumps(str(path) + '.part')]
    config_path = local('diagnostics/' + label + '-curl.conf')
    config_path.write_text('\n'.join(config) + '\n')
    print(f'{label}: {len(items)} expected, {len(pending)} downloads pending', flush=True)
    if pending:
        with local('diagnostics/' + label + '-http.log').open('w') as out, local('diagnostics/' + label + '-errors.log').open('w') as err:
            subprocess.run(['curl', '--config', str(config_path)], stdout=out, stderr=err, check=False)
        success = set()
        for line in local('diagnostics/' + label + '-http.log').read_text().splitlines():
            fields = line.rsplit('\t', 2)
            if len(fields) == 3 and fields[1] == '200' and fields[2] == '0':
                success.add(fields[0])
        for item in pending:
            path = local(item['path'])
            part = Path(str(path) + '.part')
            if str(part) in success and part.is_file() and part.stat().st_size:
                part.replace(path)
    return [item for item in items if not local(item['path']).is_file()]


def biocartoon():
    c = sqlite3.connect('file:' + str(ROOT / 'sources/biocartoon-assets.sqlite') + '?mode=ro', uri=True)
    c.row_factory = sqlite3.Row
    records, excluded = [], []
    for r in c.execute('SELECT * FROM assets ORDER BY source,id'):
        if not r['svg_key']:
            excluded.append(dict(id=r['id'], source=r['source'], reason='No published SVG'))
            continue
        record = dict(name=r['title'] or r['id'], category=r['category'] or 'Uncategorized',
                      collection=r['source_name'] + ' · original', author=r['author'] or '',
                      license=r['license'], license_url=r['license_url'], credit=r['credit'],
                      source=r['source_url'] or 'https://www.biocartoon.com/',
                      tags=' '.join(json.loads(r['tags'] or '[]')) + ' ' + (r['description'] or '') + ' ' + (r['variant'] or ''),
                      path='icons/expanded/' + r['svg_key'],
                      download_url='https://assets.biocartoon.com/' + quote(r['svg_key']),
                      upstream_id=r['id'], variant=r['variant'], generative_ai_used=r['generative_ai_used'],
                      generative_ai_details=r['generative_ai_details'], mirrored_by='BioCartoon',
                      source_group=r['source'])
        records.append(record)
    case_counts = collections.Counter(r['path'].casefold() for r in records)
    for record in records:
        if case_counts[record['path'].casefold()] > 1:
            record['original_path'] = record['path']
            record['path'] = record['path'][:-4] + '--' + record['upstream_id'] + '.svg'
    assert len({r['path'].casefold() for r in records}) == len(records)
    save('sources/biocartoon-svg-manifest.json', records)
    save('notices/no-svg-available.json', excluded)
    missing = downloads(records, 'biocartoon')
    save('diagnostics/biocartoon-missing.json', missing)
    print('BioCartoon complete; missing:', len(missing), flush=True)


def phylopic():
    index = json.loads((ROOT / 'sources/phylopic-index.json').read_text())
    build = index['build']
    pages = [dict(path=f'sources/phylopic-{build}/page-{n}.json', download_url=f'https://api.phylopic.org/images?build={build}&page={n}&embed_items=true') for n in range(index['totalPages'])]
    missing = downloads(pages, 'phylopic-pages')
    if missing:
        save('diagnostics/phylopic-missing-pages.json', missing)
        raise RuntimeError(f'{len(missing)} PhyloPic metadata pages missing; no completeness claim')
    records = []
    license_counts = collections.Counter()
    for page in pages:
        data = json.loads(local(page['path']).read_text())
        assert data['build'] == build
        for r in data['_embedded']['items']:
            links = r['_links']
            name = links['specificNode']['title']
            lic = links['license']['href']
            license_counts[lic] += 1
            source_file = links.get('sourceFile', {})
            vector = source_file if source_file.get('type') == 'image/svg+xml' else links.get('vectorFile')
            if not vector:
                continue
            records.append(dict(name=name, category='Organism silhouettes', collection='PhyloPic · original',
                                author=r.get('attribution') or links['contributor'].get('title', ''),
                                license=lic.replace('https://creativecommons.org/', '').rstrip('/'), license_url=lic,
                                source='https://www.phylopic.org/images/' + r['uuid'],
                                credit=' — '.join([name, r.get('attribution') or links['contributor'].get('title', ''), 'PhyloPic', lic]),
                                tags=' '.join(n.get('title', '') for n in links['nodes']),
                                path='icons/expanded/phylopic/' + r['uuid'] + '.svg', download_url=vector['href'],
                                upstream_id=r['uuid'], variant='source SVG' if vector is source_file else 'PhyloPic vectorized SVG', source_group='phylopic'))
    assert len({r['upstream_id'] for r in records}) == len(records)
    save('sources/phylopic-svg-manifest.json', records)
    save('sources/phylopic-coverage.json', dict(build=build, total_items=index['totalItems'], pages=len(pages), svg_records=len(records), licenses=dict(license_counts)))
    missing = downloads(records, 'phylopic-svg')
    save('diagnostics/phylopic-missing.json', missing)
    print('PhyloPic complete; missing:', len(missing), flush=True)


def validate():
    records, failures = [], []
    for name in ['biocartoon', 'phylopic', 'extras', 'arcadia']:
        path = ROOT / f'sources/{name}-svg-manifest.json'
        if not path.exists():
            continue
        for record in json.loads(path.read_text()):
            file = local(record['path'])
            try:
                data = file.read_bytes()
                svg = ET.fromstring(data)
                if svg.tag.split('}')[-1] != 'svg':
                    raise ValueError('Not an SVG root')
                for e in svg.iter():
                    if e.tag.split('}')[-1] in {'script', 'iframe'} or any(re.fullmatch(r'on[a-z]+', k.lower()) for k in e.attrib):
                        raise ValueError('Active content in SVG')
                record['sha256'] = hashlib.sha256(data).hexdigest()
                record['contains_raster'] = any(e.tag.split('}')[-1] == 'image' for e in svg.iter())
                records.append(record)
            except (OSError, ValueError, ET.ParseError) as error:
                failures.append(dict(path=record['path'], source=record['source'], error=str(error)))
    save('expanded-catalog.json', records)
    save('diagnostics/expanded-validation-failures.json', failures)
    print(json.dumps(dict(valid=len(records), failures=len(failures), sources=dict(collections.Counter(r['collection'] for r in records))), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('step', choices=['biocartoon', 'phylopic', 'validate'])
    step = parser.parse_args().step
    {'biocartoon': biocartoon, 'phylopic': phylopic, 'validate': validate}[step]()

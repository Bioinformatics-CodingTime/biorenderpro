#!/usr/bin/env python3
"""Collect free public Sciicons entries, SwissBioPics, and Colony Care SVGs."""
import collections
import json
import re
import urllib.parse
import urllib.request
from zipfile import ZipFile
from expand_sources import ROOT, ALLOWED, downloads, save, local

ALLOWED.update({'www.swissbiopics.org', 'smubvijycgraopzxvdjl.supabase.co', 'www.sciicons.com', 'sciicons.com'})


def collect():
    records, excluded = [], []
    js = (ROOT / 'sources/sciicons-site.js').read_text()
    fields = re.search(r'\bmf="([^"]+)"', js).group(1)
    origin = re.search(r'const V6="([^"]+)"', js).group(1)
    public_key = re.search(r',W6="([^"]+)"', js).group(1)
    page = 0
    all_rows = []
    while True:
        query = urllib.parse.urlencode(dict(select=fields, is_pro='eq.false', order='id', limit=1000, offset=page * 1000))
        request = urllib.request.Request(origin + '/rest/v1/icons_gdrive?' + query,
                                        headers={'apikey': public_key, 'Authorization': 'Bearer ' + public_key, 'Prefer': 'count=exact'})
        with urllib.request.urlopen(request, timeout=30) as response:
            rows = json.load(response)
            total = int(response.headers['Content-Range'].split('/')[-1])
        save(f'sources/sciicons-free-page-{page}.json', rows)
        all_rows.extend(rows)
        if len(all_rows) >= total:
            break
        assert rows, 'Sciicons pagination stopped early'
        page += 1
    assert len(all_rows) == total and len({r['id'] for r in all_rows}) == total
    page_urls = json.loads((ROOT / 'sources/sciicons-page-urls.json').read_text())
    for r in all_rows:
        assert r['is_pro'] is False
        url = r.get('download_url') or ''
        license = (r.get('license') or '').strip()
        if (r.get('file_type') or r.get('type') or '').lower() != 'svg':
            excluded.append(dict(id=r['id'], reason='Not SVG'))
            continue
        if not re.search(r'^(CC[ -]?(?:0|BY)|Public domain|MIT|BSD|Apache)', license, re.I):
            excluded.append(dict(id=r['id'], reason='License needs separate review', license=license))
            continue
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != 'https' or parsed.hostname not in ALLOWED or ('supabase.co' in parsed.hostname and '/storage/v1/object/public/' not in parsed.path):
            excluded.append(dict(id=r['id'], reason='No verified public download URL'))
            continue
        credit = ' — '.join(str(v) for v in [r['title'], r.get('author'), r.get('courtesy'), license, r.get('citation')] if v)
        records.append(dict(name=r['title'], collection=(r.get('courtesy') or 'Sciicons') + ' · via Sciicons',
                            category=r.get('category_name') or r.get('subject') or 'Uncategorized',
                            author=r.get('author') or r.get('courtesy') or '', license=license,
                            credit=credit, tags=' '.join(str(r.get(k) or '') for k in ['keywords', 'subject', 'areas', 'meta_description']),
                            source=page_urls[r['id']],
                            path='icons/expanded/sciicons/' + r['id'] + '.svg', download_url=url,
                            upstream_id=r['id'], source_group='sciicons', mirrored_by='Sciicons'))
    html = (ROOT / 'sources/swissbiopics.html').read_text()
    names = sorted(set(re.findall(r'data-name="([^"]+)"', html)))
    for name in names:
        name = name.removesuffix('.svg')
        title = name.replace('_', ' ')
        records.append(dict(name=title, collection='SwissBioPics · original', category='Cell structures',
                            author='SwissBioPics, SIB Swiss Institute of Bioinformatics', license='CC-BY-4.0',
                            license_url='https://creativecommons.org/licenses/by/4.0/',
                            credit=title + ' — SwissBioPics, SIB Swiss Institute of Bioinformatics — CC BY 4.0 https://creativecommons.org/licenses/by/4.0/',
                            tags=title, source='https://www.swissbiopics.org/name/' + urllib.parse.quote(name),
                            path='icons/expanded/swissbiopics/' + name + '.svg',
                            download_url='https://www.swissbiopics.org/api/image/' + urllib.parse.quote(name) + '.svg', source_group='swissbiopics'))
    save('sources/extras-svg-manifest.json', records)
    save('notices/extras-excluded.json', excluded)
    save('sources/extras-coverage.json', dict(sciicons_total_free=total, swissbiopics_cells=len(names), selected_by_collection=dict(collections.Counter(r['collection'] for r in records))))
    missing = downloads(records, 'extras')
    save('diagnostics/extras-missing.json', missing)
    with ZipFile(ROOT / 'sources/colony-lab-icons.zip') as z:
        prefix = 'lab-icons-main/'
        for name in ['README.md', 'LICENSE', 'LICENSE-CODE', 'metadata/icons.json']:
            local('notices/colony-care/' + name).write_bytes(z.read(prefix + name))
        for n in z.namelist():
            if not n.startswith(prefix + 'icons/') or not n.endswith('.svg'):
                continue
            rel = n[len(prefix + 'icons/'):]
            path = 'icons/expanded/colony-care/' + rel
            local(path).write_bytes(z.read(n))
            title = rel[:-4].replace('/', ' · ').replace('-', ' ')
            records.append(dict(name=title, collection='Colony Care · original', category='Laboratory animals and equipment',
                                author='Colony Care', license='CC-BY-4.0', license_url='https://creativecommons.org/licenses/by/4.0/',
                                source='https://github.com/Colony-Care/lab-icons/blob/' + z.comment.decode() + '/icons/' + urllib.parse.quote(rel),
                                path=path, tags=title, credit='Icons: Colony Care (https://colony.care/en/icons), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)', source_group='colony-care'))
    save('sources/extras-svg-manifest.json', records)
    print('Extras collected:', len(records), 'missing downloads:', len(missing))


if __name__ == '__main__':
    collect()

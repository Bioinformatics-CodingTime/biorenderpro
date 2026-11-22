#!/usr/bin/env python3
"""Package the gallery, indexed SVGs, licenses and source metadata for transfer."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / 'biorenderpro-svg.zip'


def main():
    catalog = json.loads((ROOT / 'catalog.json').read_text())
    hashes = {}
    for record in catalog:
        for origin in [record, *record['also_available_from']]:
            path = origin['path']
            assert (ROOT / path).resolve().is_relative_to(ROOT)
            digest = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            assert digest == record['sha256'], path
            hashes[path] = digest
    assert len({p.casefold() for p in hashes}) == len(hashes), 'Case-insensitive path collision'
    files = set(hashes)
    files.update(['index.html', 'catalog.js', 'catalog.json', 'sources.json',
                  'README.md', 'COVERAGE.md', '打开图标库.command'])
    files.update(str(p.relative_to(ROOT)) for p in (ROOT / 'notices').rglob('*')
                 if p.is_file() and not any(s.startswith('.') for s in p.relative_to(ROOT).parts))
    files.update(str(p.relative_to(ROOT)) for p in (ROOT / 'sources').glob('*.json'))
    files.update(['sources/biocartoon-NOTICE.md', 'sources/biocartoon-README.md',
                  'diagnostics/browser-check.json', 'diagnostics/expanded-validation-failures.json'])
    for path in files - hashes.keys():
        hashes[path] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    sums = ''.join(f'{hashes[path]}  {path}\n' for path in sorted(hashes))
    (ROOT / 'SHA256SUMS').write_text(sums)
    files.add('SHA256SUMS')
    temporary = OUTPUT.with_suffix('.zip.part')
    print(f'Packaging {len(catalog)} unique SVG entries, {len(files)} files', flush=True)
    with ZipFile(temporary, 'w', ZIP_DEFLATED, compresslevel=4) as archive:
        for path in sorted(files):
            archive.write(ROOT / path, 'biorenderpro/' + path)
    with ZipFile(temporary) as archive:
        assert archive.testzip() is None, 'ZIP integrity check failed'
        assert len(archive.namelist()) == len(files)
    temporary.replace(OUTPUT)
    with OUTPUT.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    OUTPUT.with_suffix('.zip.sha256').write_text(digest + '  ' + OUTPUT.name + '\n')
    report = dict(unique_svg_entries=len(catalog), packaged_files=len(files),
                  zip_bytes=OUTPUT.stat().st_size, zip_sha256=digest, crc_check='passed',
                  indexed_svg_sha256_check='passed', case_insensitive_paths='passed')
    (ROOT / 'diagnostics/package-check.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()

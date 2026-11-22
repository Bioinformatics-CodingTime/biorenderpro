#!/usr/bin/env python3
"""Package only audited artwork and the evidence actually used by those records."""
import hashlib,json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from audit_library import rebuild
ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT.parent/'biorenderpro-svg.zip'

def main():
    rebuild()
    catalog=json.loads((ROOT/'catalog.json').read_text())
    files={'index.html','catalog.js','catalog.json','sources.json','README.md','COVERAGE.md','打开图标库.command',
           'audit_library.py','build_library.py','package_library.py','test_gallery.cjs',
           'notices/license-audit/approved-records.json','notices/license-audit/report.json',
           'notices/license-audit/archived-summary.json','diagnostics/browser-check.json',
           'notices/license-audit/official/swiss-live-verification.json'}
    for r in catalog:
        files.add(r['path']);files.update(r['evidence_files'])
    hashes={}
    for name in sorted(files):
        path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
        hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    assert len({p.casefold() for p in files})==len(files)
    (ROOT/'SHA256SUMS').write_text(''.join(f'{v}  {k}\n' for k,v in hashes.items()))
    files.add('SHA256SUMS');temporary=OUTPUT.with_suffix('.zip.part')
    print(f'Packaging {len(catalog)} approved SVGs',flush=True)
    with ZipFile(temporary,'w',ZIP_DEFLATED,compresslevel=4) as z:
        for name in sorted(files):z.write(ROOT/name,'biorenderpro/'+name)
    with ZipFile(temporary) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(files)
        assert sum(n.endswith('.svg') for n in z.namelist())==len(catalog)
    temporary.replace(OUTPUT)
    with OUTPUT.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    OUTPUT.with_suffix('.zip.sha256').write_text(sha+'  '+OUTPUT.name+'\n')
    report=dict(unique_svg_entries=len(catalog),packaged_files=len(files),zip_bytes=OUTPUT.stat().st_size,zip_sha256=sha,
                crc_check='passed',indexed_svg_sha256_check='passed',unapproved_svgs_in_package=0)
    (ROOT/'diagnostics/package-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':main()

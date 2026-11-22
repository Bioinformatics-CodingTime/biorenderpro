#!/usr/bin/env python3
"""Keep source-verifiable artwork; quarantine everything else without deleting it."""
import argparse, collections, hashlib, json, re, shutil
from pathlib import Path
from urllib.parse import quote
from zipfile import ZipFile
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parent
AUDIT = ROOT / 'notices/license-audit'
ARCHIVE = ROOT.parent / 'biorender-library-archive/20261122-before-license-audit'

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2))

def digest(data):
    return hashlib.sha256(data).hexdigest()

def local(path):
    p = (ROOT / path).resolve()
    assert p.is_relative_to(ROOT), path
    return p

def rebuild():
    records = json.loads((AUDIT / 'approved-records.json').read_text())
    seen = set()
    for r in records:
        assert r['sha256'] not in seen
        seen.add(r['sha256'])
        assert digest(local(r['path']).read_bytes()) == r['sha256'], r['path']
        assert r['source'].startswith('https://') and r['license_url'].startswith('https://')
        assert r['author'] and r['credit'] and r['license_verification']
        assert not r['also_available_from'], 'Unreviewed duplicate origin'
        for p in r['evidence_files']:
            assert local(p).is_file(), p
    actual = {str(p.relative_to(ROOT)) for p in (ROOT/'icons').rglob('*.svg')}
    assert {p.casefold() for p in actual} == {r['path'].casefold() for r in records}, 'Unapproved or missing SVG in active folder'
    write(ROOT/'catalog.json', records)
    (ROOT/'catalog.js').write_text('const ICONS = '+json.dumps(records,ensure_ascii=False).replace('<','\\u003c')+';\n')
    report=json.loads((AUDIT/'report.json').read_text())
    write(ROOT/'sources.json',dict(usable_files=len(records),counts=dict(collections.Counter(r['collection'] for r in records)),
         kind_counts=dict(collections.Counter(r['kind'] for r in records)),
         raster_containing_svg=sum(r['contains_raster'] for r in records),license_audit=report))
    print(json.dumps(dict(active=len(records),all_hashes_and_evidence='passed',unapproved_active_svgs=0)))

def audit(apply=False):
    assert not (AUDIT/'approved-records.json').exists(), 'Already audited: use build_library.py to validate/rebuild'
    records=json.loads((ROOT/'catalog.json').read_text())
    git_matches={}
    specs=[('health','CC0-1.0','https://creativecommons.org/publicdomain/zero/1.0/','Resolve to Save Lives','health--LICENSE'),
           ('openmoji','CC-BY-SA-4.0','https://creativecommons.org/licenses/by-sa/4.0/','OpenMoji contributors','openmoji--LICENSE.txt'),
           ('crop','CC0-1.0','https://creativecommons.org/publicdomain/zero/1.0/','Open Crop Icons contributors','crop--README.md'),
           ('weather','CC-BY-4.0','https://creativecommons.org/licenses/by/4.0/','OGC Met Ocean DWG contributors','weather--LICENSE.md'),
           ('electric','CC0-1.0','https://creativecommons.org/publicdomain/zero/1.0/','Inkscape Electric Symbols contributors','electric--LICENSE'),
           ('anatomogram','CC-BY-4.0','https://creativecommons.org/licenses/by/4.0/','EMBL-EBI Expression Atlas','anatomogram--README.md'),
           ('janosh','MIT','https://opensource.org/license/mit','Janosh Riebesell','janosh--license'),
           ('noto','Apache-2.0','https://www.apache.org/licenses/LICENSE-2.0','Google LLC','noto-svg-LICENSE')]
    for key,lic,url,author,licensefile in specs:
        evidence=json.loads((AUDIT/f'official/{key}-evidence.json').read_text())
        tree=json.loads((AUDIT/f'official/{key}-tree.json').read_text())
        assert not tree.get('truncated')
        assert (AUDIT/'official'/licensefile).stat().st_size>100
        for entry in tree['tree']:
            p=entry['path']
            if entry['type']!='blob' or not p.lower().endswith('.svg'):continue
            if key=='noto' and not p.startswith('2D/svg/'):continue
            if key=='anatomogram' and not p.startswith('src/svg/'):continue
            if key=='janosh' and not p.startswith('assets/'):continue
            if key=='openmoji' and not p.startswith(('color/svg/','black/svg/')):continue
            git_matches.setdefault(entry['sha'],(key,lic,url,author,licensefile,evidence,p))
    phylo={}
    for p in sorted((ROOT/'sources/phylopic-564').glob('*.json')):
        d=json.loads(p.read_text())
        assert d['build']==564
        for row in d['_embedded']['items']:phylo[row['uuid']]=(row,p)
    bio=ZipFile(ROOT/'sources/bioicons-main.zip')
    bioauthors=json.loads(bio.read('bioicons-main/static/icons/authors.json'))
    colony=ZipFile(ROOT/'sources/colony-lab-icons.zip')
    arcadia=ZipFile(ROOT/'sources/arcadia-organisms-v1.2.zip')
    arcadia_hash={digest(arcadia.read(n)):n for n in arcadia.namelist() if n.endswith('.svg')}
    zenodo=json.loads((ROOT/'sources/arcadia-zenodo.json').read_text())
    arcadia_bytes=(ROOT/'sources/arcadia-organisms-v1.2.zip').read_bytes()
    assert any(f.get('checksum')=='md5:'+hashlib.md5(arcadia_bytes).hexdigest() for f in zenodo['files'])
    approved=[];rejected=[];evidence_copies={}
    for r in records:
        origins=[{k:v for k,v in r.items() if k!='also_available_from'},*r.get('also_available_from',[])]
        chosen=None;why='No verified original-file mapping and applicable license; aggregator labels alone not accepted'
        for o in origins:
            data=local(o['path']).read_bytes()
            assert digest(data)==r['sha256']
            e=[];method='';license_url=o.get('license_url');lic=o.get('license');credit=o.get('credit','');author=o.get('author','')
            source=o.get('source','');collection=o['collection']
            # Repository path-level licenses cover these exact bytes, not the website's code license.
            if o['path'].startswith('icons/Bioicons-original/'):
                rel=o['path'].removeprefix('icons/Bioicons-original/')
                parts=rel.split('/');lp='bioicons-main/static/icons/'+parts[0]+'/LICENSE'
                if bio.read('bioicons-main/static/icons/'+rel)==data and lp in bio.namelist():
                    licenses={'cc-0':'https://creativecommons.org/publicdomain/zero/1.0/','cc-by-3.0':'https://creativecommons.org/licenses/by/3.0/','cc-by-4.0':'https://creativecommons.org/licenses/by/4.0/','cc-by-sa-3.0':'https://creativecommons.org/licenses/by-sa/3.0/','cc-by-sa-4.0':'https://creativecommons.org/licenses/by-sa/4.0/','mit':'https://opensource.org/license/mit'}
                    license_url=licenses.get(parts[0])
                    if license_url:
                        target='notices/license-audit/bioicons/'+parts[0]+'-LICENSE'
                        evidence_copies[target]=bio.read(lp)
                        for name in ['icons.json','authors.json']:
                            evidence_copies['notices/license-audit/bioicons/'+name]=bio.read('bioicons-main/static/icons/'+name)
                        e=[target,'notices/Bioicons/README.md','notices/license-audit/bioicons/icons.json','notices/license-audit/bioicons/authors.json']
                        method='Exact bytes in pinned Bioicons archive; per-icon author and license directory'
            elif o.get('source_group')=='phylopic' and o.get('upstream_id') in phylo:
                raw,p=phylo[o['upstream_id']];links=raw['_links'];lu=links['license']['href']
                downloads=[links.get(k,{}).get('href') for k in ['sourceFile','vectorFile']]
                if license_url==lu and o.get('download_url') in downloads and source=='https://www.phylopic.org/images/'+raw['uuid']:
                    author=raw.get('attribution') or links['contributor'].get('title','')
                    if author:
                        target='notices/license-audit/phylopic/'+p.name
                        evidence_copies[target]=p.read_bytes();e=[target]
                        method='Official PhyloPic build 564 per-image author, license and download URL'
            elif o.get('source_group')=='swissbiopics' and o.get('download_url','').startswith('https://www.swissbiopics.org/api/image/'):
                e=['notices/license-audit/official/swiss-help-current.html','sources/extras-svg-manifest.json']
                method='Direct SwissBioPics API download; official artwork CC BY 4.0 statement'
            elif o.get('source_group')=='colony-care':
                rel=o['path'].removeprefix('icons/expanded/colony-care/')
                if colony.read('lab-icons-main/icons/'+rel)==data:
                    e=['notices/colony-care/LICENSE','notices/colony-care/README.md'];method='Exact bytes in pinned Colony Care archive; artwork-specific license'
            elif o.get('source_group')=='arcadia' and digest(data) in arcadia_hash:
                e=['sources/arcadia-zenodo.json','sources/arcadia-svg-manifest.json'];method='Exact bytes in Zenodo archive verified against official checksum; CC0 artwork declaration'
            if not method:
                sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
                hit=git_matches.get(sha)
                if hit:
                    key,lic,license_url,author,lf,ev,p=hit
                    source='https://github.com/'+ev['repository']+'/blob/'+ev['ref']+'/'+quote(p)
                    collection=ev['repository']+' · verified original'
                    e=['notices/license-audit/official/'+key+'-tree.json','notices/license-audit/official/'+key+'-evidence.json','notices/license-audit/official/'+lf]
                    method='Exact Git blob SHA-1 matches official repository tree; scoped artwork license'
                    o=dict(o,upstream_blob_sha1=sha,upstream_blob_url='https://api.github.com/repos/'+ev['repository']+'/git/blobs/'+sha)
                    credit=f'{o["name"]} — {author} — {lic} — {license_url} — {source}; unchanged source SVG'
            if method and author and license_url:
                chosen=dict(o,collection=collection,source=source,author=author,license=lic,license_url=license_url,
                            credit=credit+'; license: '+license_url,license_verification=method,evidence_files=e,
                            sha256=r['sha256'],contains_raster=r['contains_raster'],kind=r['kind'],also_available_from=[])
                break
        if chosen:
            approved.append(chosen)
        else:rejected.append(dict(r,archive_reason=why))
    active_paths={r['path'].casefold() for r in approved}
    archive_files=[]
    for p in (ROOT/'icons').rglob('*.svg'):
        rel=str(p.relative_to(ROOT))
        if rel.casefold() not in active_paths:archive_files.append(dict(path=rel,sha256=digest(p.read_bytes())))
    report=dict(before_unique_entries=len(records),approved_unique_entries=len(approved),archived_unique_entries=len(rejected),
                archived_svg_files=len(archive_files),approved_collections=dict(collections.Counter(r['collection'] for r in approved)),
                archived_collections=dict(collections.Counter(r['collection'] for r in rejected)),
                policy='Require original-file mapping, author, explicit applicable license, and retained evidence; archive unresolved items without calling them infringements',
                limits='Metadata and byte-level provenance audit; not an independent legal warranty or scientific accuracy review',date='2026-11-22')
    write(ROOT/'diagnostics/license-audit-plan.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    if not apply:return
    assert not ARCHIVE.exists(),'Archive already exists; inspect it before applying again'
    ARCHIVE.mkdir(parents=True)
    for name in ['catalog.json','catalog.js','sources.json','README.md','COVERAGE.md','index.html','SHA256SUMS','build_library.py','package_library.py','test_gallery.cjs','expanded-catalog.json']:
        shutil.copy2(ROOT/name,ARCHIVE/('original-README.md' if name=='README.md' else name))
    for name in ['biorenderpro-svg.zip','biorenderpro-svg.zip.sha256','biorender-library-svg.zip']:
        p=ROOT.parent/name
        if p.exists():shutil.move(str(p),str(ARCHIVE/name))
    write(ARCHIVE/'archived-records.json',rejected);write(ARCHIVE/'moved-files.json',archive_files)
    for r in archive_files:
        src=local(r['path']);dst=ARCHIVE/r['path'];dst.parent.mkdir(parents=True,exist_ok=True)
        assert digest(src.read_bytes())==r['sha256']
        src.rename(dst)
        assert digest(dst.read_bytes())==r['sha256']
    for path,data in evidence_copies.items():
        p=local(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    write(AUDIT/'approved-records.json',approved);write(AUDIT/'report.json',report)
    write(AUDIT/'archived-summary.json',[{k:r.get(k) for k in ['name','collection','path','sha256','archive_reason']} for r in rejected])
    (ARCHIVE/'README.md').write_text('# 未通过本轮来源与许可核查的归档\n\n保留旧索引、旧下载包和移出的原始 SVG，不删除。归档不等于认定侵权；这些素材暂不用于新图或公开下载。\n归档明细见 archived-records.json 与 moved-files.json。原始下载档案仍保留在 /Users/wa/biorender-library/sources/。\n')
    rebuild()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');parser.add_argument('--rebuild',action='store_true');args=parser.parse_args()
    rebuild() if args.rebuild else audit(args.apply)

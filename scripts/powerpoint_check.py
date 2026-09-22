"""Native PowerPoint validation on temporary copies, with capability detection.

Exit 0=passed; 1=failed; 3=unavailable. Never turn an observed failure into SKIP.
"""
import argparse
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZipFile

P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'


def capability():
    if os.name != 'nt':
        return None, 'PowerPoint COM requires Windows'
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'PowerPoint.Application\CLSID'):
            pass
    except FileNotFoundError:
        return None, 'PowerPoint COM is not registered'
    shell = shutil.which('pwsh') or shutil.which('powershell')
    return (shell, '') if shell else (None, 'PowerShell unavailable')


def expected_slides(source):
    records = []
    with ZipFile(source) as z:
        rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
        pres = ET.fromstring(z.read('ppt/presentation.xml'))
        for slide in pres.findall('{%s}sldIdLst/{%s}sldId' % (P, P)):
            target = posixpath.normpath(posixpath.join('ppt', rels[slide.get('{%s}id' % R)])).lstrip('/')
            tree = ET.fromstring(z.read(target)).find('{%s}cSld/{%s}spTree' % (P, P))
            kinds = {'{%s}%s' % (P, k) for k in ('sp', 'pic', 'grpSp', 'graphicFrame', 'cxnSp', 'contentPart')}
            texts = []
            for shape in tree.iter():
                body = shape.find('{%s}txBody' % P)
                if shape.tag not in kinds or body is None or body.find('.//{%s}fld' % A) is not None:
                    continue  # Dynamic date/page fields may legitimately change.
                prop = next((e for child in shape for e in child if e.tag == '{%s}cNvPr' % P), None)
                if prop is None:
                    continue
                lines = []
                # Explicit DrawingML breaks must separate adjacent runs.
                for para in body.findall('{%s}p' % A):
                    lines.append(''.join('\n' if e.tag == '{%s}br' % A else (e.text or '') if e.tag == '{%s}t' % A else '' for e in para.iter()))
                text = re.sub(r'\s+', ' ', '\n'.join(lines)).strip()
                if text:
                    texts.append({'id': int(prop.get('id')), 'text': text})
            records.append({'shapes': sum(e.tag in kinds for e in tree.iter()),
                            'pictures': sum(e.tag == '{%s}pic' % P for e in tree.iter()), 'texts': texts})
    return records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source', type=Path)
    ap.add_argument('--out-dir', type=Path)
    ap.add_argument('--timeout', type=int, default=120)
    args = ap.parse_args()
    shell, reason = capability()
    if not shell:
        print('POWERPOINT UNAVAILABLE: '+reason)
        return 3
    source = args.source.resolve()
    parent = args.out_dir or source.with_suffix('.powerpoint-qa')
    parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='run-', dir=parent.resolve()))
    shutil.copy2(source, work / 'input.pptx')
    (work / 'expected.json').write_text(json.dumps(expected_slides(source)), encoding='utf-8')
    cmd = [shell, '-NoProfile', '-NonInteractive', '-File', str(Path(__file__).with_suffix('.ps1')), '-WorkDir', str(work)]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print('POWERPOINT FAIL: timeout; inspect Office state; no PowerPoint process was killed. Evidence: '+str(work))
        return 1
    log = result.stdout.decode('utf-8', errors='replace')
    (work / 'native.log').write_text(log, encoding='utf-8')
    if result.returncode or 'POWERPOINT PASS' not in log:
        print(log.strip())
        print('POWERPOINT FAIL; evidence: '+str(work))
        return 1
    print('POWERPOINT PASS: images + slides + save/reopen; evidence: '+str(work))
    for image in sorted(work.glob('input-slide-*.png')):
        if '-image-' not in image.name:
            print(image)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

"""Behavioral checks for lossless normalization; no Office installation required."""
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile
import zlib

from normalize_png import SIGNATURE, chunks, inflate, normalize, normalize_package
from powerpoint_check import expected_slides
from theme_compatibility import isolate_notes_themes


def chunk(kind, data):
    return struct.pack('>I', len(data))+kind+data+struct.pack('>I', zlib.crc32(kind+data) & 0xffffffff)


def fixture(animated=False):
    # Two RGBA test pixels; split IDAT tests concatenation rather than each chunk
    # incorrectly being treated as a separate zlib stream.
    raw = b'\x00\x12\x34\x56\x78\xff\x00\x00\x00'
    data = zlib.compress(raw, 0)
    png = SIGNATURE+chunk(b'IHDR', struct.pack('>IIBBBBB', 2,1,8,6,0,0,0))
    png += chunk(b'pHYs', struct.pack('>IIB', 2835,2835,1))
    if animated:
        png += chunk(b'acTL', struct.pack('>II', 1,0))
    return png+chunk(b'IDAT',data[:5])+chunk(b'IDAT',data[5:])+chunk(b'IEND',b''), raw


class CompatibilityTests(unittest.TestCase):
    def test_notes_theme_isolation_preserves_content_and_is_idempotent(self):
        r='http://schemas.openxmlformats.org/package/2006/relationships'
        rel=f'<Relationships xmlns="{r}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>'.encode()
        data={'ppt/slideMasters/_rels/slideMaster1.xml.rels':rel,
              'ppt/notesMasters/_rels/notesMaster1.xml.rels':rel,
              'ppt/theme/theme1.xml':b'<original-theme/>',
              'ppt/theme/_rels/theme1.xml.rels':b'<image-relationships/>',
              'ppt/notesMasters/notesMaster1.xml':b'<notes-content/>',
              '[Content_Types].xml':b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>'}
        self.assertEqual(len(isolate_notes_themes(data)),1)
        self.assertEqual(data['ppt/theme/themeNotes1.xml'],data['ppt/theme/theme1.xml'])
        self.assertEqual(data['ppt/theme/_rels/themeNotes1.xml.rels'],data['ppt/theme/_rels/theme1.xml.rels'])
        self.assertEqual(data['ppt/notesMasters/notesMaster1.xml'],b'<notes-content/>')
        self.assertEqual(data['ppt/slideMasters/_rels/slideMaster1.xml.rels'],rel)
        self.assertEqual(isolate_notes_themes(data),[])

    def test_lossless_metadata_multi_idat_and_idempotence(self):
        original, raw = fixture()
        fixed, info = normalize(original)
        self.assertNotEqual(original, fixed)
        self.assertEqual(raw, inflate(b''.join(d for k,d,_ in chunks(fixed) if k == b'IDAT')))
        self.assertEqual([(k,d) for k,d,_ in chunks(original) if k != b'IDAT'], [(k,d) for k,d,_ in chunks(fixed) if k != b'IDAT'])
        self.assertEqual(normalize(fixed)[0], fixed)
        self.assertEqual(info['scanlines_sha256'], hashlib.sha256(raw).hexdigest())

    def test_apng_is_not_rewritten(self):
        original, _ = fixture(True)
        fixed, info = normalize(original)
        self.assertEqual(original, fixed)
        self.assertEqual(info['status'], 'skipped_apng')

    def test_crc_rejected_before_in_place_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d)/'input.pptx'
            bad = bytearray(fixture()[0]); bad[40] ^= 1
            with ZipFile(file,'w') as z: z.writestr('ppt/media/a.png',bad)
            before = file.read_bytes()
            with self.assertRaises(ValueError): normalize_package(file,file,True)
            self.assertEqual(file.read_bytes(),before)

    def test_package_keeps_other_parts_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            source, output = Path(d)/'in.pptx', Path(d)/'out.pptx'
            with ZipFile(source,'w') as z:
                z.writestr('ppt/media/a.png',fixture()[0])
                z.writestr('ppt/slides/slide1.xml',b'<test/>')
                z.writestr('ppt/media/b.jpeg',b'unchanged image bytes')
            before=source.read_bytes()
            result=normalize_package(source,output)
            self.assertEqual(result['changed'],1)
            self.assertEqual(source.read_bytes(),before)
            with ZipFile(source) as a, ZipFile(output) as b:
                self.assertEqual([n for n in a.namelist() if a.read(n)!=b.read(n)],['ppt/media/a.png'])
            with self.assertRaises(FileExistsError): normalize_package(source,output)

    def test_source_counts_include_grouped_pictures(self):
        p='http://schemas.openxmlformats.org/presentationml/2006/main'
        r='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/'groups.pptx'
            with ZipFile(file,'w') as z:
                z.writestr('ppt/presentation.xml', f'<p:presentation xmlns:p="{p}" xmlns:r="{r}"><p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst></p:presentation>')
                z.writestr('ppt/_rels/presentation.xml.rels','<Relationships><Relationship Id="rId1" Target="slides/slide1.xml"/></Relationships>')
                z.writestr('ppt/slides/slide1.xml',f'<p:sld xmlns:p="{p}"><p:cSld><p:spTree><p:sp/><p:grpSp><p:sp/><p:pic/></p:grpSp></p:spTree></p:cSld></p:sld>')
            self.assertEqual(expected_slides(file),[{'shapes':4,'pictures':1,'texts':[]}])

    def test_native_failure_must_not_fall_back_to_alternate_renderer(self):
        import build
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            gen, out = Path(d)/'generator.js', Path(d)/'out.pptx'
            gen.write_text('// control-flow fixture',encoding='utf-8')
            calls=[]
            def runner(cmd, **kwargs):
                calls.append(cmd)
                if cmd[0]=='node':
                    out.write_bytes(b'fixture')
                    return 0,'generated'
                name=Path(cmd[1]).name
                return {'postprocess.py':(0,'DONE'), 'normalize_png.py':(0,'PNG NORMALIZE PASS'),
                        'check_pptx.py':(0,'All validations PASSED'),
                        'powerpoint_check.py':(1,'native export failed')}[name]
            with patch.object(build,'run',side_effect=runner), patch.object(build,'load_env',return_value={}), patch('sys.argv',['build.py',str(gen),str(out)]), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as failure: build.main()
            self.assertEqual(failure.exception.code,1)
            self.assertFalse(any(len(c)>1 and Path(c[1]).name=='render.py' for c in calls))


if __name__ == '__main__':
    unittest.main()

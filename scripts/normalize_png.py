"""Lossless static-PNG normalization for generated PPTX packages (stdlib only).

Recompress IDAT without changing scanlines, color, alpha, or metadata. This is a
compatibility mitigation, not a guarantee that every Office version can render.
APNG and digitally signed packages are not silently rewritten.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import struct
import tempfile
from zipfile import ZipFile
import zlib

SIGNATURE = b'\x89PNG\r\n\x1a\n'
MAX_RAW = 256 * 1024 * 1024


def chunks(data):
    if data[:8] != SIGNATURE:
        raise ValueError('Invalid PNG signature')
    result, offset = [], 8
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError('Truncated PNG chunk')
        size = struct.unpack_from('>I', data, offset)[0]
        end = offset + size + 12
        if end > len(data):
            raise ValueError('Truncated PNG payload')
        kind, body = data[offset + 4:offset + 8], data[offset + 8:end - 4]
        if zlib.crc32(kind + body) & 0xffffffff != struct.unpack_from('>I', data, end - 4)[0]:
            raise ValueError('PNG CRC mismatch: %r' % kind)
        result.append((kind, body, data[offset:end]))
        offset = end
    if not result or result[0][0] != b'IHDR' or result[-1][0] != b'IEND':
        raise ValueError('Missing PNG boundary chunks')
    return result


def inflate(data):
    decoder = zlib.decompressobj()
    raw = decoder.decompress(data, MAX_RAW + 1)
    if len(raw) > MAX_RAW or decoder.unconsumed_tail:
        raise ValueError('PNG exceeds normalization memory limit')
    if not decoder.eof or decoder.unused_data:
        raise ValueError('Incomplete or trailing PNG compressed data')
    return raw


def normalize(data):
    parts = chunks(data)
    if any(k in (b'acTL', b'fcTL', b'fdAT') for k, _, _ in parts):
        return data, {'status': 'skipped_apng'}
    payloads = [p for k, p, _ in parts if k == b'IDAT']
    if not payloads:
        raise ValueError('Missing PNG image data')
    raw = inflate(b''.join(payloads))
    compressed = zlib.compress(raw, 9)
    if inflate(compressed) != raw:
        raise ValueError('Lossless verification failed')
    payload = b'IDAT' + compressed
    idat = struct.pack('>I', len(compressed)) + payload + struct.pack('>I', zlib.crc32(payload) & 0xffffffff)
    output, inserted = [SIGNATURE], False
    for kind, _, original in parts:
        if kind != b'IDAT':
            output.append(original)
        elif not inserted:
            output.append(idat)
            inserted = True
    result = b''.join(output)
    if [(k, p) for k, p, _ in chunks(result) if k != b'IDAT'] != [(k, p) for k, p, _ in parts if k != b'IDAT']:
        raise ValueError('PNG metadata changed')
    return result, {'status': 'changed' if result != data else 'unchanged',
                    'scanlines_sha256': hashlib.sha256(raw).hexdigest()}


def normalize_package(source, output, in_place=False):
    source, output = Path(source).resolve(), Path(output).resolve()
    if source == output and not in_place:
        raise ValueError('Use --in-place only for an authorized/generated file')
    if source != output and output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.png-normalize-', suffix='.pptx', dir=output.parent)
    os.close(fd)
    records = []
    try:
        with ZipFile(source) as src:
            if len(src.namelist()) != len(set(src.namelist())):
                raise ValueError('Duplicate ZIP entries')
            if any(n.startswith('_xmlsignatures/') for n in src.namelist()):
                raise ValueError('Signed package: rewriting would invalidate its signature')
            with ZipFile(temp, 'w') as dst:
                dst.comment = src.comment
                for info in src.infolist():
                    data = src.read(info.filename)
                    if info.filename.lower().startswith('ppt/media/') and info.filename.lower().endswith('.png'):
                        data, record = normalize(data)
                        records.append(dict(part=info.filename, **record))
                    dst.writestr(copy.copy(info), data)
        with ZipFile(source) as src, ZipFile(temp) as dst:
            if dst.testzip() is not None or src.namelist() != dst.namelist():
                raise ValueError('Package verification failed')
            changed = {r['part'] for r in records if r['status'] == 'changed'}
            if {n for n in src.namelist() if src.read(n) != dst.read(n)} != changed:
                raise ValueError('Unexpected package-part change')
        os.replace(temp, output)
    finally:
        if os.path.exists(temp):
            os.remove(temp)
    return {'output': str(output), 'png_count': len(records),
            'changed': sum(r['status'] == 'changed' for r in records),
            'non_png_parts_unchanged': True, 'images': records}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source')
    ap.add_argument('output', nargs='?')
    ap.add_argument('--in-place', action='store_true')
    ap.add_argument('--report')
    args = ap.parse_args()
    if not args.output and not args.in_place:
        ap.error('provide a new output, or --in-place for generated files')
    report = normalize_package(args.source, args.output or args.source, args.in_place)
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print('PNG NORMALIZE PASS: %d PNG, %d changed; pixels/metadata and other parts preserved' % (report['png_count'], report['changed']))
    skipped = [r['part'] for r in report['images'] if r['status'] == 'skipped_apng']
    if skipped:
        print('APNG unchanged (animation preserved): '+', '.join(skipped))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] if 'tools' in Path(__file__).parts else Path.cwd()
OUT = ROOT / 'artifacts' / 'graphics' / 'aegislash'
if len(sys.argv) > 1:
    OUT = Path(sys.argv[1])

def frame_to_4bpp(img):
    if img.mode != 'P' or img.size != (64, 64):
        raise ValueError(f'expected indexed 64x64 PNG, got {img.mode} {img.size}')
    px = img.load(); out = bytearray()
    for ty in range(8):
        for tx in range(8):
            for y in range(8):
                for x in range(0, 8, 2):
                    a = px[tx * 8 + x, ty * 8 + y]
                    b = px[tx * 8 + x + 1, ty * 8 + y]
                    if a > 15 or b > 15:
                        raise ValueError('palette index exceeds 4bpp')
                    out.append(a | (b << 4))
    assert len(out) == 0x800
    return bytes(out)

def gba_lz77(data):
    out = bytearray([0x10, len(data) & 0xff, (len(data) >> 8) & 0xff, (len(data) >> 16) & 0xff])
    pos = 0
    while pos < len(data):
        flag_pos = len(out); out.append(0); flags = 0; chunk = bytearray()
        for bit in range(8):
            if pos >= len(data): break
            best_len = best_disp = 0
            for j in range(pos - 1, max(-1, pos - 0x1000 - 1), -1):
                disp = pos - j; length = 0
                while length < 18 and pos + length < len(data) and data[pos - disp + (length % disp)] == data[pos + length]:
                    length += 1
                if length >= 3 and length > best_len:
                    best_len, best_disp = length, disp
                    if length == 18: break
            if best_len >= 3:
                flags |= 1 << (7 - bit); disp = best_disp - 1
                chunk += bytes([((best_len - 3) << 4) | ((disp >> 8) & 0xf), disp & 0xff])
                pos += best_len
            else:
                chunk.append(data[pos]); pos += 1
        out[flag_pos] = flags; out += chunk
    while len(out) % 4: out.append(0)
    return bytes(out)

def gba_lz77_decode(data):
    if data[0] != 0x10: raise ValueError('not GBA LZ77')
    size = data[1] | data[2] << 8 | data[3] << 16; pos = 4; out = bytearray()
    while len(out) < size:
        flags = data[pos]; pos += 1
        for bit in range(8):
            if len(out) >= size: break
            if flags & (1 << (7 - bit)):
                a, b = data[pos], data[pos + 1]; pos += 2
                length = (a >> 4) + 3; disp = ((a & 0xf) << 8 | b) + 1
                for _ in range(length): out.append(out[-disp])
            else:
                out.append(data[pos]); pos += 1
    return bytes(out)

forms = {}
for form in ('shield', 'blade'):
    front = Image.open(OUT / f'{form}_front_anim.png')
    back = Image.open(OUT / f'{form}_back.png')
    if front.size != (64, 128) or back.size != (64, 64): raise ValueError('unexpected sprite dimensions')
    frames = []
    for i in range(2):
        frame = front.crop((0, i * 64, 64, (i + 1) * 64))
        frame.info['transparency'] = 0
        frame.save(OUT / f'{form}_front_{i}.png', transparency=0)
        raw = frame_to_4bpp(frame); (OUT / f'{form}_front_{i}.4bpp').write_bytes(raw); frames.append(raw)
    back.info['transparency'] = 0
    back.save(OUT / f'{form}_back_0.png', transparency=0)
    braw = frame_to_4bpp(back); (OUT / f'{form}_back_0.4bpp').write_bytes(braw)
    forms[form] = (frames, braw)

front_raw = b''.join(forms['shield'][0] + forms['blade'][0])
back_raw = forms['shield'][1] + forms['blade'][1]
front_lz, back_lz = gba_lz77(front_raw), gba_lz77(back_raw)
assert gba_lz77_decode(front_lz) == front_raw
assert gba_lz77_decode(back_lz) == back_raw
for name, data in [('aegislash_front.4bpp', front_raw), ('aegislash_back.4bpp', back_raw), ('aegislash_front.4bpp.lz', front_lz), ('aegislash_back.4bpp.lz', back_lz)]:
    (OUT / name).write_bytes(data)

files = {}
for p in sorted(OUT.iterdir()):
    if p.is_file() and p.name not in {'manifest.json', 'SHA256SUMS.tsv'}:
        data = p.read_bytes(); files[p.name] = {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
manifest = {
    'source': {'repository': 'rh-hideout/pokeemerald-expansion', 'commit': '4c680433909c7fb2219cc9e755f05cdd081d4778'},
    'target': {'front_uncompressed': 0x2000, 'back_uncompressed': 0x1000, 'forms': {'shield': 0, 'blade': 1}, 'front_frames': ['shield_0','shield_1','blade_0','blade_1'], 'back_frames': ['shield_0','blade_0']},
    'files': files,
}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(OUT / 'SHA256SUMS.tsv').write_text('sha256\tsize\tfile\n' + ''.join(f"{v['sha256']}\t{v['size']}\t{k}\n" for k, v in files.items()))

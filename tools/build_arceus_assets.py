#!/usr/bin/env python3
import hashlib
import json
import shutil
import struct
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1] if "tools" in Path(__file__).parts else Path.cwd()
BASE = ROOT / "artifacts" / "graphics" / "arceus"
SOURCE = BASE / "source"
OUT = BASE / "generated"

if len(sys.argv) > 1:
    OUT = Path(sys.argv[1])

FORMS = [
    ("normal", 0, "Normal"),
    ("fighting", 1, "Fighting"),
    ("flying", 2, "Flying"),
    ("poison", 3, "Poison"),
    ("ground", 4, "Ground"),
    ("rock", 5, "Rock"),
    ("bug", 6, "Bug"),
    ("ghost", 7, "Ghost"),
    ("steel", 8, "Steel"),
    ("fire", 9, "Fire"),
    ("water", 10, "Water"),
    ("grass", 11, "Grass"),
    ("electric", 12, "Electric"),
    ("psychic", 13, "Psychic"),
    ("ice", 14, "Ice"),
    ("dragon", 15, "Dragon"),
    ("dark", 16, "Dark"),
    ("fairy", 17, "Fairy"),
]

SOURCE_REPOSITORY = "rh-hideout/pokeemerald-expansion"
SOURCE_COMMIT = "4c680433909c7fb2219cc9e755f05cdd081d4778"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jasc_palette(path):
    lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if len(lines) < 3 or lines[0] != "JASC-PAL" or lines[1] != "0100":
        raise ValueError(f"unsupported palette format: {path}")
    count = int(lines[2])
    if count != 16:
        raise ValueError(f"expected 16 colors, got {count}: {path}")
    if len(lines) != 3 + count:
        raise ValueError(f"palette line count mismatch: {path}")

    colors = []
    for line in lines[3:]:
        rgb = tuple(map(int, line.split()))
        if len(rgb) != 3 or any(v < 0 or v > 255 for v in rgb):
            raise ValueError(f"invalid RGB entry {line!r}: {path}")
        colors.append(rgb)
    return colors


def palette_to_pillow(colors):
    flat = [component for rgb in colors for component in rgb]
    return flat + [0] * (768 - len(flat))


def palette_to_gbapal(colors):
    out = bytearray()
    for r, g, b in colors:
        value = (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)
        out += struct.pack("<H", value)
    if len(out) != 32:
        raise AssertionError("GBA palette must be 32 bytes")
    return bytes(out)


def validate_indexed_image(img, expected_size, label):
    if img.mode != "P":
        raise ValueError(f"{label}: expected indexed PNG (P), got {img.mode}")
    if img.size != expected_size:
        raise ValueError(f"{label}: expected {expected_size}, got {img.size}")
    used = set(img.getdata())
    if used and max(used) > 15:
        raise ValueError(f"{label}: palette index exceeds 4bpp: {max(used)}")


def frame_to_4bpp(img):
    validate_indexed_image(img, (64, 64), "frame")
    px = img.load()
    out = bytearray()
    for ty in range(8):
        for tx in range(8):
            for y in range(8):
                for x in range(0, 8, 2):
                    a = px[tx * 8 + x, ty * 8 + y]
                    b = px[tx * 8 + x + 1, ty * 8 + y]
                    out.append(a | (b << 4))
    if len(out) != 0x800:
        raise AssertionError("64x64 4bpp frame must be 0x800 bytes")
    return bytes(out)


def gba_lz77(data):
    out = bytearray([0x10, len(data) & 0xFF, (len(data) >> 8) & 0xFF, (len(data) >> 16) & 0xFF])
    pos = 0
    while pos < len(data):
        flag_pos = len(out)
        out.append(0)
        flags = 0
        chunk = bytearray()
        for bit in range(8):
            if pos >= len(data):
                break
            best_len = best_disp = 0
            for j in range(pos - 1, max(-1, pos - 0x1000 - 1), -1):
                disp = pos - j
                length = 0
                while (
                    length < 18
                    and pos + length < len(data)
                    and data[pos - disp + (length % disp)] == data[pos + length]
                ):
                    length += 1
                if length >= 3 and length > best_len:
                    best_len, best_disp = length, disp
                    if length == 18:
                        break
            if best_len >= 3:
                flags |= 1 << (7 - bit)
                disp = best_disp - 1
                chunk += bytes([
                    ((best_len - 3) << 4) | ((disp >> 8) & 0xF),
                    disp & 0xFF,
                ])
                pos += best_len
            else:
                chunk.append(data[pos])
                pos += 1
        out[flag_pos] = flags
        out += chunk
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def gba_lz77_decode(data):
    if data[0] != 0x10:
        raise ValueError("not GBA LZ77")
    size = data[1] | data[2] << 8 | data[3] << 16
    pos = 4
    out = bytearray()
    while len(out) < size:
        flags = data[pos]
        pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (1 << (7 - bit)):
                a, b = data[pos], data[pos + 1]
                pos += 2
                length = (a >> 4) + 3
                disp = ((a & 0xF) << 8 | b) + 1
                for _ in range(length):
                    out.append(out[-disp])
            else:
                out.append(data[pos])
                pos += 1
    return bytes(out)


def write_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def recolor_indexed(source_img, colors, dest):
    img = source_img.copy()
    img.putpalette(palette_to_pillow(colors))
    img.info["transparency"] = 0
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, transparency=0)


def main():
    front = Image.open(SOURCE / "anim_front.png")
    back = Image.open(SOURCE / "back.png")
    validate_indexed_image(front, (64, 128), "anim_front.png")
    validate_indexed_image(back, (64, 64), "back.png")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    front_frames = []
    for i in range(2):
        frame = front.crop((0, i * 64, 64, (i + 1) * 64))
        validate_indexed_image(frame, (64, 64), f"front frame {i}")
        front_frames.append(frame_to_4bpp(frame))
    front_raw = b"".join(front_frames)
    back_raw = frame_to_4bpp(back)

    if len(front_raw) != 0x1000 or len(back_raw) != 0x800:
        raise AssertionError("unexpected common sprite size")

    front_lz = gba_lz77(front_raw)
    back_lz = gba_lz77(back_raw)
    if gba_lz77_decode(front_lz) != front_raw:
        raise AssertionError("front LZ77 round trip failed")
    if gba_lz77_decode(back_lz) != back_raw:
        raise AssertionError("back LZ77 round trip failed")

    write_bytes(OUT / "arceus_front.4bpp", front_raw)
    write_bytes(OUT / "arceus_front.4bpp.lz", front_lz)
    write_bytes(OUT / "arceus_back.4bpp", back_raw)
    write_bytes(OUT / "arceus_back.4bpp.lz", back_lz)

    form_manifest = []
    for form_name, form_id, type_name in FORMS:
        src_dir = SOURCE / form_name
        dst_dir = OUT / "forms" / form_name
        variants = {}

        for variant in ("normal", "shiny"):
            pal_path = src_dir / f"{variant}.pal"
            colors = read_jasc_palette(pal_path)
            gbapal = palette_to_gbapal(colors)
            pal_lz = gba_lz77(gbapal)
            if gba_lz77_decode(pal_lz) != gbapal:
                raise AssertionError(f"{form_name} {variant} palette LZ77 round trip failed")

            recolor_indexed(front, colors, dst_dir / f"{variant}_front_anim.png")
            recolor_indexed(back, colors, dst_dir / f"{variant}_back.png")
            write_bytes(dst_dir / f"{variant}.gbapal", gbapal)
            write_bytes(dst_dir / f"{variant}.gbapal.lz", pal_lz)

            variants[variant] = {
                "source_palette": str(pal_path.relative_to(ROOT)),
                "gbapal": str((dst_dir / f"{variant}.gbapal").relative_to(ROOT)),
                "gbapal_lz": str((dst_dir / f"{variant}.gbapal.lz").relative_to(ROOT)),
            }

        form_manifest.append({
            "form": form_name,
            "form_id": form_id,
            "type": type_name,
            "variants": variants,
        })

    source_files = {}
    for p in sorted(SOURCE.rglob("*")):
        if p.is_file():
            source_files[str(p.relative_to(ROOT))] = {
                "size": p.stat().st_size,
                "sha256": sha256(p),
            }

    generated_files = {}
    for p in sorted(OUT.rglob("*")):
        if p.is_file() and p.name not in {"manifest.json", "SHA256SUMS.tsv"}:
            generated_files[str(p.relative_to(OUT))] = {
                "size": p.stat().st_size,
                "sha256": sha256(p),
            }

    manifest = {
        "source": {
            "repository": SOURCE_REPOSITORY,
            "commit": SOURCE_COMMIT,
            "files": source_files,
        },
        "representation": {
            "palette_only_form_change": True,
            "front_source_size": [64, 128],
            "front_frames": 2,
            "back_source_size": [64, 64],
            "palette_index_0_transparent": True,
            "max_palette_index": 15,
            "front_4bpp_size": len(front_raw),
            "back_4bpp_size": len(back_raw),
        },
        "forms": form_manifest,
        "generated_files": generated_files,
    }

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    (OUT / "SHA256SUMS.tsv").write_text(
        "sha256\tsize\tfile\n"
        + "".join(
            f"{meta['sha256']}\t{meta['size']}\t{name}\n"
            for name, meta in sorted(generated_files.items())
        )
    )

    print(f"generated {len(generated_files)} files for {len(FORMS)} Arceus forms")


if __name__ == "__main__":
    main()

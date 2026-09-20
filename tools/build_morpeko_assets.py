#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "graphics" / "morpeko"


def read_jasc(path):
    lines = path.read_text().splitlines()
    if lines[:3] != ["JASC-PAL", "0100", "16"]:
        raise ValueError(f"{path}: expected JASC-PAL 0100 with 16 entries")
    colors = [tuple(map(int, line.split())) for line in lines[3:19]]
    if len(colors) != 16:
        raise ValueError(f"{path}: expected 16 colors")
    return colors


def gba_palette(colors):
    out = bytearray()
    for r, g, b in colors:
        value = (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)
        out += bytes((value & 0xFF, value >> 8))
    return bytes(out)


def frame_to_4bpp(path):
    image = Image.open(path)
    if image.mode != "P" or image.size != (64, 64):
        raise ValueError(f"{path}: expected indexed 64x64 PNG, got {image.mode} {image.size}")

    px = image.load()
    raw = bytearray()
    used = set()

    for tile_y in range(8):
        for tile_x in range(8):
            for y in range(8):
                for x in range(0, 8, 2):
                    lo = px[tile_x * 8 + x, tile_y * 8 + y]
                    hi = px[tile_x * 8 + x + 1, tile_y * 8 + y]
                    used.update((lo, hi))
                    if lo > 15 or hi > 15:
                        raise ValueError(f"{path}: palette index exceeds 4bpp")
                    raw.append(lo | (hi << 4))

    if len(raw) != 0x800:
        raise AssertionError("64x64 4bpp frame must be 0x800 bytes")

    return bytes(raw), sorted(used)


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

            best_len = 0
            best_disp = 0
            window_start = max(0, pos - 0x1000)

            for candidate in range(pos - 1, window_start - 1, -1):
                disp = pos - candidate
                length = 0
                while (
                    length < 18
                    and pos + length < len(data)
                    and data[pos - disp + (length % disp)] == data[pos + length]
                ):
                    length += 1

                if length >= 3 and length > best_len:
                    best_len = length
                    best_disp = disp
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

    size = data[1] | (data[2] << 8) | (data[3] << 16)
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
                disp = (((a & 0xF) << 8) | b) + 1
                for _ in range(length):
                    out.append(out[-disp])
            else:
                out.append(data[pos])
                pos += 1

    return bytes(out)


def main():
    source_frames = ["full_front", "full_back", "hangry_front", "hangry_back"]
    raw = {}
    used = {}

    for name in source_frames:
        raw[name], used[name] = frame_to_4bpp(OUT / f"{name}.png")
        (OUT / f"{name}.4bpp").write_bytes(raw[name])

    front = raw["full_front"] + raw["hangry_front"]
    back = raw["full_back"] + raw["hangry_back"]

    for name, data in [
        ("morpeko_front.4bpp", front),
        ("morpeko_back.4bpp", back),
    ]:
        (OUT / name).write_bytes(data)
        compressed = gba_lz77(data)
        if gba_lz77_decode(compressed) != data:
            raise AssertionError(f"{name}: LZ77 round-trip failed")
        (OUT / f"{name}.lz").write_bytes(compressed)

    for name in ["full_normal", "full_shiny", "hangry_normal", "hangry_shiny"]:
        palette = read_jasc(OUT / f"{name}.pal")
        (OUT / f"{name}.gbapal").write_bytes(gba_palette(palette))

    files = {}
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name not in {"manifest.json", "SHA256SUMS.tsv"}:
            data = path.read_bytes()
            files[path.name] = {
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }

    manifest = {
        "source": {
            "repository": "rh-hideout/pokeemerald-expansion",
            "commit": "c7d7ec67b0ca8134e5c290e624780a29440ee09c",
            "paths": "graphics/pokemon/morpeko/{front.png,back.png,normal.pal,shiny.pal,hangry/*}",
        },
        "target": {
            "platform": "GBA",
            "canvas": "64x64",
            "tile_format": "4bpp",
            "palette_entries": 16,
            "transparent_index": 0,
            "battle_forms": {"full_belly": 0, "hangry": 1},
            "front_frame_order": ["full_belly", "hangry"],
            "back_frame_order": ["full_belly", "hangry"],
        },
        "palette_indices": used,
        "files": files,
    }

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (OUT / "SHA256SUMS.tsv").write_text(
        "sha256\tsize\tfile\n"
        + "".join(f"{meta['sha256']}\t{meta['size']}\t{name}\n" for name, meta in files.items())
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Census Nintendo DS Pokémon font archives without shipping ROM data.

Usage:
    python tools/extract_korean_font_census.py game.nds

The script lists font-like filesystem entries, parses NARC members, and prints
the compact 16-byte font header used by Gen IV main text-font members.
"""

from __future__ import annotations
import hashlib
import struct
import sys
from pathlib import Path


def u16(buf: bytes, off: int) -> int:
    return struct.unpack_from("<H", buf, off)[0]


def u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def nds_files(path: Path):
    rom = path.read_bytes()
    fnt_off, fnt_size = u32(rom, 0x40), u32(rom, 0x44)
    fat_off, fat_size = u32(rom, 0x48), u32(rom, 0x4C)
    fnt = rom[fnt_off:fnt_off + fnt_size]
    fat = rom[fat_off:fat_off + fat_size]

    num_dirs = u16(fnt, 6)
    dirs = [struct.unpack_from("<IHH", fnt, i * 8) for i in range(num_dirs)]
    files = {}

    def walk(dir_id: int, prefix: str = ""):
        subtable, file_id, _ = dirs[dir_id - 0xF000]
        pos = subtable
        while True:
            kind = fnt[pos]
            pos += 1
            if kind == 0:
                return
            name_len = kind & 0x7F
            name = fnt[pos:pos + name_len].decode("ascii", "replace")
            pos += name_len
            if kind & 0x80:
                child = u16(fnt, pos)
                pos += 2
                walk(child, prefix + name + "/")
            else:
                start, end = struct.unpack_from("<II", fat, file_id * 8)
                files[prefix + name] = (file_id, rom[start:end])
                file_id += 1

    walk(0xF000)
    return rom, files


def narc_members(data: bytes):
    if data[:4] != b"NARC":
        return None

    pos = u16(data, 0x0C)
    section_count = u16(data, 0x0E)
    entries = None
    gmif = None

    for _ in range(section_count):
        magic = data[pos:pos + 4]
        size = u32(data, pos + 4)
        if magic in (b"BTAF", b"FATB"):
            count = u16(data, pos + 8)
            entries = [
                struct.unpack_from("<II", data, pos + 12 + i * 8)
                for i in range(count)
            ]
        elif magic in (b"GMIF", b"FIMG"):
            gmif = pos + 8
        pos += size

    if entries is None or gmif is None:
        return None
    return [data[gmif + start:gmif + end] for start, end in entries]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: extract_korean_font_census.py game.nds", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    rom, files = nds_files(path)
    print("title:", rom[:12].rstrip(b"\0").decode("ascii", "replace"))
    print("game_code:", rom[12:16].decode("ascii", "replace"))

    candidates = []
    for name in files:
        low = name.lower()
        if "font" in low or name == "a/0/1/6":
            candidates.append(name)

    for name in sorted(candidates):
        file_id, data = files[name]
        print()
        print(file_id, len(data), hashlib.sha1(data).hexdigest(), name)

        members = narc_members(data)
        if not members:
            continue

        print("members:", len(members))
        for i, member in enumerate(members):
            line = [
                str(i),
                "bytes=" + str(len(member)),
                "sha1=" + hashlib.sha1(member).hexdigest(),
            ]
            if len(member) >= 16:
                header = struct.unpack_from("<III4B", member, 0)
                header_size, width_start, glyph_count, fw, fh, gw, gh = header
                if (
                    header_size == 16
                    and gw in (1, 2)
                    and gh in (1, 2)
                    and glyph_count > 0
                    and width_start <= len(member)
                ):
                    line += [
                        "glyphs=" + str(glyph_count),
                        "cell=" + str(gw * 8) + "x" + str(gh * 8),
                        "fixed=" + str(fw) + "x" + str(fh),
                        "glyph_bytes=" + str(16 * gw * gh),
                        "tail_bytes=" + str(len(member) - width_start),
                    ]
            print("  " + " ".join(line))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build the first FRLG-style Johto GBA remake map from Japanese retail ROM evidence.

GSC supplies topology/semantic placement. Japanese Emerald supplies the visible
GBA metatiles and their packed collision/elevation entries. ROMs are inputs only
and are never emitted or committed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

GSC_BLOCK_OFFSET = 0xACDB5
GSC_BLOCK_W = 10
GSC_BLOCK_H = 9
TARGET_W = 20
TARGET_H = 18
EMERALD_MAP_GROUPS = 0x45E998
EMERALD_GROUP = 0
EMERALD_LITTLEROOT = 9
EMERALD_ROUTE102 = 17

TREE_BLOCKS = {0x05, 0x62, 0x65}
WATER_BLOCKS = {0x54, 0x58}
GROUND_DETAIL_BLOCKS = {0x02, 0x04}
BUILDING_BLOCKS = {0x14, 0x15, 0x16, 0x18, 0x19, 0x1C, 0x1E, 0x1F, 0x77}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u32(data: bytes, off: int) -> int:
    return int.from_bytes(data[off:off + 4], "little")


def gba_ptr(data: bytes, off: int) -> int:
    value = u32(data, off)
    if value >> 24 not in (0x08, 0x09):
        raise ValueError(f"not a GBA ROM pointer at {off:#x}: {value:#x}")
    return value & 0x01FFFFFF


def emerald_map(rom: bytes, map_num: int) -> dict:
    group = gba_ptr(rom, EMERALD_MAP_GROUPS + EMERALD_GROUP * 4)
    header = gba_ptr(rom, group + map_num * 4)
    layout = gba_ptr(rom, header)
    width = int.from_bytes(rom[layout:layout + 4], "little", signed=True)
    height = int.from_bytes(rom[layout + 4:layout + 8], "little", signed=True)
    map_off = gba_ptr(rom, layout + 12)
    size = width * height * 2
    raw = rom[map_off:map_off + size]
    cells = [int.from_bytes(raw[i:i + 2], "little") for i in range(0, len(raw), 2)]
    return {
        "map_num": map_num,
        "header": header,
        "layout": layout,
        "map_offset": map_off,
        "width": width,
        "height": height,
        "raw": raw,
        "cells": cells,
    }


def rect(m: dict, x: int, y: int, w: int, h: int) -> list[list[int]]:
    return [m["cells"][(y + yy) * m["width"] + x:(y + yy) * m["width"] + x + w] for yy in range(h)]


def paste(grid: list[int], x: int, y: int, patch: list[list[int]]) -> None:
    for yy, row in enumerate(patch):
        for xx, value in enumerate(row):
            tx, ty = x + xx, y + yy
            if 0 <= tx < TARGET_W and 0 <= ty < TARGET_H:
                grid[ty * TARGET_W + tx] = value


def source_cell(blocks: bytes, x: int, y: int) -> tuple[int, str]:
    block = blocks[(y // 2) * GSC_BLOCK_W + (x // 2)]
    q = ("NW", "NE", "SW", "SE")[(y & 1) * 2 + (x & 1)]
    return block, q


def compose_new_bark(gsc_rom: bytes, emerald_rom: bytes) -> tuple[bytes, dict]:
    blocks = gsc_rom[GSC_BLOCK_OFFSET:GSC_BLOCK_OFFSET + GSC_BLOCK_W * GSC_BLOCK_H]
    if len(blocks) != 90:
        raise ValueError("short GSC New Bark block read")

    littleroot = emerald_map(emerald_rom, EMERALD_LITTLEROOT)
    route102 = emerald_map(emerald_rom, EMERALD_ROUTE102)
    if (littleroot["width"], littleroot["height"]) != (20, 20):
        raise ValueError("unexpected Littleroot dimensions")
    if (route102["width"], route102["height"]) != (50, 20):
        raise ValueError("unexpected Route102 dimensions")

    # Exact Japanese Emerald donor entries, extracted from the retail ROM map data.
    ground = littleroot["cells"][3 * 20 + 3]  # General normal ground, 0x3001.
    ground_detail = littleroot["cells"][10 * 20 + 1]  # General decorative ground, 0x3004.
    sign = littleroot["cells"][13 * 20 + 15]  # Littleroot town sign, metatile 0x003.

    # GSC says where the semantic classes are. Emerald says how they look/behave.
    tree = {
        "NW": littleroot["cells"][0 * 20 + 0],
        "NE": littleroot["cells"][0 * 20 + 1],
        "SW": littleroot["cells"][1 * 20 + 0],
        "SE": littleroot["cells"][1 * 20 + 1],
    }

    grid = [ground] * (TARGET_W * TARGET_H)
    for y in range(TARGET_H):
        for x in range(TARGET_W):
            block, q = source_cell(blocks, x, y)
            if block in TREE_BLOCKS:
                grid[y * TARGET_W + x] = tree[q]
            elif block in GROUND_DETAIL_BLOCKS:
                grid[y * TARGET_W + x] = ground_detail
            elif block in WATER_BLOCKS:
                # Filled below from the Japanese Emerald Route 102 pond template.
                grid[y * TARGET_W + x] = ground
            elif block in BUILDING_BLOCKS:
                # GSC building graphics are deliberately discarded. The building
                # footprints below are supplied by Emerald instead.
                grid[y * TARGET_W + x] = ground

    # Route 102 pond: 4x4 GBA shoreline/water grammar, replacing the old GSC water art.
    pond = rect(route102, 40, 2, 4, 4)
    paste(grid, 16, 6, pond)

    # Littleroot donor exteriors, anchored to the four canonical GSC doorway coords.
    lab = rect(littleroot, 3, 13, 7, 4)       # door at donor (7,16), rel (4,3)
    house_b = rect(littleroot, 13, 5, 5, 4)  # door at donor (14,8), rel (1,3)
    paste(grid, 2, 0, lab)       # Elm Lab door -> (6,3)
    paste(grid, 12, 2, house_b)  # NE house door -> (13,5)
    paste(grid, 2, 8, house_b)   # SW house door -> (3,11)
    paste(grid, 10, 10, house_b) # SE house door -> (11,13)

    # Use Emerald sign art at GSC/HGSS-semantic sign locations. Elm Lab's exterior
    # footprint needs the one documented relocation shown below.
    target_signs = [(8, 8), (11, 5), (9, 13), (5, 4)]
    for x, y in target_signs:
        grid[y * TARGET_W + x] = sign

    expected_doors = {
        "elm_lab": (6, 3, littleroot["cells"][16 * 20 + 7]),
        "northeast_house": (13, 5, littleroot["cells"][8 * 20 + 14]),
        "southwest_house": (3, 11, littleroot["cells"][8 * 20 + 14]),
        "southeast_house": (11, 13, littleroot["cells"][8 * 20 + 14]),
    }
    for name, (x, y, value) in expected_doors.items():
        if grid[y * TARGET_W + x] != value:
            raise AssertionError(f"door anchor mismatch: {name}")

    out = b"".join(v.to_bytes(2, "little") for v in grid)
    manifest = {
        "schema": 1,
        "policy": "FRLG-style remake: GSC topology/semantics, Japanese Emerald visual/behavior donors; no GSC graphics are emitted.",
        "target": {"map": "New Bark Town", "width": TARGET_W, "height": TARGET_H, "bytes": len(out), "sha256": sha256(out)},
        "source": {"gsc_block_offset": hex(GSC_BLOCK_OFFSET), "block_sha256": sha256(blocks), "gsc_rom_sha256": sha256(gsc_rom)},
        "emerald": {
            "rom_sha256": sha256(emerald_rom),
            "map_groups_offset": hex(EMERALD_MAP_GROUPS),
            "littleroot": {k: (hex(v) if k in {"header", "layout", "map_offset"} else v) for k, v in littleroot.items() if k not in {"raw", "cells"}},
            "route102": {k: (hex(v) if k in {"header", "layout", "map_offset"} else v) for k, v in route102.items() if k not in {"raw", "cells"}},
            "littleroot_map_sha256": sha256(littleroot["raw"]),
            "route102_map_sha256": sha256(route102["raw"]),
        },
        "donor_templates": [
            {"semantic": "elm_lab_exterior", "source_map": "LittlerootTown", "source_rect": [3, 13, 7, 4], "target_origin": [2, 0], "door": [6, 3]},
            {"semantic": "house_exterior_ne", "source_map": "LittlerootTown", "source_rect": [13, 5, 5, 4], "target_origin": [12, 2], "door": [13, 5]},
            {"semantic": "house_exterior_sw", "source_map": "LittlerootTown", "source_rect": [13, 5, 5, 4], "target_origin": [2, 8], "door": [3, 11]},
            {"semantic": "house_exterior_se", "source_map": "LittlerootTown", "source_rect": [13, 5, 5, 4], "target_origin": [10, 10], "door": [11, 13]},
            {"semantic": "pond_shore", "source_map": "Route102", "source_rect": [40, 2, 4, 4], "target_origin": [16, 6]},
        ],
        "event_relocations": [{"kind": "bg/sign", "source": [3, 3], "target": [5, 4], "reason": "Emerald Birch-lab exterior footprint"}],
        "preserved_warp_anchors": [[6, 3], [13, 5], [3, 11], [11, 13]],
        "target_signs": [list(p) for p in target_signs],
    }
    return out, manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold-rom", required=True, type=Path)
    ap.add_argument("--emerald-rom", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    args = ap.parse_args()
    gsc = args.gold_rom.read_bytes()
    emerald = args.emerald_rom.read_bytes()
    out, manifest = compose_new_bark(gsc, emerald)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "new_bark_town.map.bin").write_bytes(out)
    (args.out_dir / "new_bark_town.remake.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["target"], indent=2))


if __name__ == "__main__":
    main()

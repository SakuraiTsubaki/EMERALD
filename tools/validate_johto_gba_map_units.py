#!/usr/bin/env python3
"""Gen II -> GBA map-unit conversion helpers for Johto remake maps."""
from __future__ import annotations
import argparse, json
from pathlib import Path

GEN2_METATILE_PX = 32
GBA_METATILE_PX = 16
SCALE = GEN2_METATILE_PX // GBA_METATILE_PX

def gba_layout_size(width_blocks: int, height_blocks: int) -> tuple[int, int]:
    if width_blocks <= 0 or height_blocks <= 0:
        raise ValueError("map dimensions must be positive")
    return width_blocks * SCALE, height_blocks * SCALE

def gba_connection_offset(source_offset_blocks: int) -> int:
    return source_offset_blocks * SCALE

def gba_event_coord(source_step_coord: int) -> int:
    # Gen II object/warp/coord/bg positions already use the 16px movement grid.
    return source_step_coord

def validate_map(entry: dict) -> None:
    w,h=gba_layout_size(entry["source"]["widthBlocks"],entry["source"]["heightBlocks"])
    if (w,h)!=(entry["target"]["widthMetatiles"],entry["target"]["heightMetatiles"]):
        raise ValueError(f'{entry["id"]}: target layout dimensions do not match unit conversion')
    for c in entry["connections"]:
        if gba_connection_offset(c["sourceOffset"]) != c["targetOffset"]:
            raise ValueError(f'{entry["id"]}: bad connection offset for {c["direction"]}')

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("spec",type=Path)
    args=ap.parse_args()
    data=json.loads(args.spec.read_text(encoding="utf-8"))
    for entry in data["maps"]:
        validate_map(entry)
    print(json.dumps({
        "maps":len(data["maps"]),
        "scale":SCALE,
        "validated":[m["id"] for m in data["maps"]]
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())

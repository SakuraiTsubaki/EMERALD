#!/usr/bin/env python3
"""Render all currently committed Johto GBA remake slice maps to PNG."""
from __future__ import annotations
import argparse
from pathlib import Path
from render_johto_gba_map_preview import render_file

MAPS = (
    ("new_bark_town", 20, 18, 9),
    ("route_29", 60, 18, 10),
    ("cherrygrove_city", 40, 18, 10),
    ("route_30", 20, 54, 10),
    ("route_31", 40, 18, 3),
    ("violet_city", 40, 36, 3),
)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emerald-rom", required=True, type=Path)
    ap.add_argument("--artifact-dir", type=Path, default=Path("artifacts/johto-gba-remake-slice"))
    ap.add_argument("--out-dir", type=Path, default=Path("artifacts/johto-gba-remake-preview"))
    args = ap.parse_args()
    for name, width, height, profile in MAPS:
        source = args.artifact_dir / f"{name}.map.bin"
        output = args.out_dir / f"{name}.png"
        if not source.exists():
            print(f"skip {name}: {source} not found")
            continue
        render_file(args.emerald_rom, source, width, height, profile, output)
        print(output)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

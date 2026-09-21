#!/usr/bin/env python3
"""Locate signature-stable special-encounter structures in Japanese Gen I-II ROMs.

ROM binaries are inputs only and are never written to the repository.
"""

from __future__ import annotations
import argparse, csv
from pathlib import Path

GEN1_GOOD_ROD = bytes([10, 0x9D, 10, 0x47])
GEN1_RBY_GROUP1 = bytes([2, 15, 0x18, 15, 0x47])
GEN1_YELLOW_FIRST = bytes([0x00, 0x1B, 10, 0x18, 10, 0x1B, 5, 0x18, 20])

GEN2_CONTEST = bytes([
    20,10,7,18, 20,13,7,18, 10,11,9,18, 10,14,9,18,
    5,12,12,15, 5,15,12,15, 10,48,10,16, 10,46,10,17,
    5,123,13,14, 5,127,13,14, 0xFF,49,30,40
])
GEN2_ROCK_SET = bytes([90,98,15,10,213,15,0xFF])
GEN2_UNOWN = bytes(list(range(1,12))+[0xFF]+list(range(12,19))+[0xFF]+list(range(19,24))+[0xFF]+list(range(24,27))+[0xFF])
GEN2_SHORE_OLD = bytes([0xB3,129,10,0xD9,129,10,0xFF,98,10])
GEN2_DUNSPARCE = bytes([3,74,3,206,2,41,2,74,2,206,4,206,4,206]) * 3
GEN2_WATER_SWARM = bytes([20,118,20,183,20,119])

def find(data: bytes, sig: bytes):
    pos = data.find(sig)
    return None if pos < 0 else pos

def classify(path: Path):
    n = path.name
    if "Pikachu" in n: return "gen1-yellow"
    if path.suffix.lower() == ".gb": return "gen1-rby"
    if "Crystal" in n: return "gen2-crystal"
    if path.suffix.lower() == ".gbc": return "gen2-gs"
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roms", nargs="+", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ns = ap.parse_args()
    rows = []

    for path in ns.roms:
        data = path.read_bytes()
        kind = classify(path)
        if kind is None:
            continue

        if kind.startswith("gen1"):
            good = find(data, GEN1_GOOD_ROD)
            rows.append([path.name, "good_rod_body", good])
            if kind == "gen1-rby":
                group1 = find(data, GEN1_RBY_GROUP1)
                rows.append([path.name, "super_rod_first_group", group1])
                rows.append([path.name, "super_rod_root", None if group1 is None else group1 - 0x64])
            else:
                root = find(data, GEN1_YELLOW_FIRST)
                rows.append([path.name, "super_rod_root", root])

        else:
            shore = find(data, GEN2_SHORE_OLD)
            rows.append([path.name, "fishgroups_shore_old_body", shore])
            if shore is not None:
                rows.append([path.name, "fishgroups_root", shore - 0x5B])

            contest = find(data, GEN2_CONTEST)
            rows.append([path.name, "bug_contest", contest])

            rock = find(data, GEN2_ROCK_SET)
            rows.append([path.name, "treemon_rock_body", rock])

            unown = find(data, GEN2_UNOWN)
            rows.append([path.name, "unown_unlock_sets", unown])

            duns = find(data, GEN2_DUNSPARCE)
            rows.append([path.name, "dunsparce_swarm_body", duns])

            water = find(data, GEN2_WATER_SWARM)
            rows.append([path.name, "water_swarm_body", water])

    fields = ["filename", "structure", "offset_hex"]
    output = []
    for filename, structure, offset in rows:
        output.append({
            "filename": filename,
            "structure": structure,
            "offset_hex": "" if offset is None else f"0x{offset:X}",
        })

    if ns.output:
        with ns.output.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(output)
    else:
        import sys
        w = csv.DictWriter(sys.stdout, fieldnames=fields); w.writeheader(); w.writerows(output)

if __name__ == "__main__":
    main()

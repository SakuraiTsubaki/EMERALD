#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

CLEAN_SHA256 = "33f5610b9186b4add09fef68895deb00f552b997b3d133b5a961e5123506343c"

FORM_ORDER = [
    "normal", "fighting", "flying", "poison", "ground", "rock",
    "bug", "ghost", "steel", "fire", "water", "grass", "electric",
    "psychic", "ice", "dragon", "dark", "fairy",
]

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def parse_args():
    p = argparse.ArgumentParser(description="Patch clean Japanese Emerald BPEJ Rev.00 with Arceus Stage-2.")
    p.add_argument("clean_rom", type=Path)
    p.add_argument("output_rom", type=Path)
    p.add_argument("--runtime", type=Path, required=True)
    p.add_argument("--assets", type=Path, default=Path("artifacts/graphics/arceus/generated"))
    p.add_argument("--ruleset", type=int, default=2, choices=range(7),
                   help="0 Gen4, 1 Gen5, 2 Gen6, 3 Gen7, 4 BDSP, 5 PLA, 6 Gen9")
    p.add_argument("--report", type=Path)
    return p.parse_args()

def main():
    args = parse_args()
    rom = bytearray(args.clean_rom.read_bytes())

    if len(rom) != 0x1000000:
        raise SystemExit(f"expected 16 MiB BPEJ ROM, got 0x{len(rom):X}")
    source_sha = sha256(rom)
    if source_sha != CLEAN_SHA256:
        raise SystemExit(f"clean BPEJ SHA-256 mismatch: {source_sha}")
    if rom[0xAC:0xB0] != b"BPEJ" or rom[0xBC] != 0:
        raise SystemExit("expected Pocket Monsters Emerald BPEJ Rev.00")

    hook_before = bytes.fromhex("164a17490b781801")
    if bytes(rom[0x45DAC:0x45DB4]) != hook_before:
        raise SystemExit("unexpected bytes at BPEJ attack-canceler hook")
    if set(rom[0x91C000:0x91EA41]) - {0xFF}:
        raise SystemExit("Arceus Stage-2 reservation is not clean FF space")

    runtime = args.runtime.read_bytes()
    front = (args.assets / "arceus_front.4bpp").read_bytes()
    back = (args.assets / "arceus_back.4bpp").read_bytes()
    palettes = b"".join(
        (args.assets / "forms" / form / "normal.gbapal").read_bytes()
        for form in FORM_ORDER
    )

    if len(runtime) >= 0x1000:
        raise SystemExit(f"runtime too large: {len(runtime)} bytes")
    if len(front) != 0x1000:
        raise SystemExit(f"front 4bpp must be 0x1000 bytes, got 0x{len(front):X}")
    if len(back) != 0x800:
        raise SystemExit(f"back 4bpp must be 0x800 bytes, got 0x{len(back):X}")
    if len(palettes) != 18 * 32:
        raise SystemExit(f"palette bank must be 0x240 bytes, got 0x{len(palettes):X}")

    rom[0x91C000:0x91C000 + len(runtime)] = runtime
    rom[0x91D000:0x91E000] = front
    rom[0x91E000:0x91E800] = back
    rom[0x91E800:0x91EA40] = palettes
    rom[0x91EA40] = args.ruleset

    # ldr r3,[pc,#0]; bx r3; .word 0x0891C001
    hook_after = bytes.fromhex("004b184701c09108")
    rom[0x45DAC:0x45DB4] = hook_after

    # Temporary Arceus test species: 253 / OLD_UNOWN_C.
    base_stats = 0x2F0D54 + 253 * 0x1C
    entry = bytearray(rom[base_stats:base_stats + 0x1C])
    entry[0:6] = bytes([120] * 6)
    entry[6:8] = bytes([0, 0])
    entry[8] = 3
    entry[9] = 255
    entry[0x10] = 0xFF
    entry[0x11] = 120
    entry[0x12] = 0
    entry[0x16] = 0
    entry[0x17] = 0
    rom[base_stats:base_stats + 0x1C] = entry

    # Temporary Judgment test move: 354 / Psycho Boost.
    move_offset = 0x2ED220 + 354 * 12
    rom[move_offset:move_offset + 6] = bytes([0, 100, 0, 100, 10, 0])

    args.output_rom.write_bytes(rom)
    report = {
        "source_sha256": source_sha,
        "output_sha256": sha256(rom),
        "ruleset": args.ruleset,
        "runtime": {
            "offset": "0x91C000",
            "address": "0x0891C000",
            "size": len(runtime),
            "sha256": sha256(runtime),
        },
        "resources": {
            "front": {"offset": "0x91D000", "size": len(front), "sha256": sha256(front)},
            "back": {"offset": "0x91E000", "size": len(back), "sha256": sha256(back)},
            "palettes": {"offset": "0x91E800", "size": len(palettes), "sha256": sha256(palettes)},
            "ruleset_byte": "0x91EA40",
        },
        "hook": {
            "offset": "0x45DAC",
            "before": hook_before.hex(),
            "after": hook_after.hex(),
            "entry": "0x0891C001",
        },
        "temporary_ids": {"species": 253, "move_judgment": 354, "items": "377-413"},
        "base_stats_offset": hex(base_stats),
        "move_offset": hex(move_offset),
    }

    report_path = args.report or args.output_rom.with_suffix(".stage2.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()

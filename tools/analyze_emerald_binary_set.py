#!/usr/bin/env python3
"""Analyze original Pokémon Emerald ROM/save pairs without copying ROM data.

The output is a structural/hash manifest only. ROM and SAV binaries are never
written into the repository by this tool.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path

ROM_SIZE = 16 * 1024 * 1024
SAVE_SIZE = 128 * 1024
SECTOR_SIZE = 4096
SECTOR_DATA_SIZE = 3968
FOOTER_EXTENSION_START = 0xF80
FOOTER_FIELDS_START = 0xFF4
SECTOR_SIGNATURE = 0x08012025
NUM_SECTORS_PER_SLOT = 14

# Exact vanilla Emerald logical payload sizes at the pinned pret/pokeemerald base.
SECTION_SIZES = [
    0xF2C,
    3968, 3968, 3968, 0x3D88 - (3968 * 3),
    3968, 3968, 3968, 3968, 3968, 3968, 3968, 3968, 0x83D0 - (3968 * 8),
]

REGIONS = {
    "BPEJ": ("ja", "Japan"),
    "BPEE": ("en", "USA_Europe"),
    "BPED": ("de", "Germany"),
    "BPEF": ("fr", "France"),
    "BPEI": ("it", "Italy"),
    "BPES": ("es", "Spain"),
}
LANGUAGE_ORDER = {"ja": 0, "ko": 1, "en": 2, "de": 3, "fr": 4, "it": 5, "es": 6}


@dataclass
class SaveSlot:
    index: int
    complete: bool
    counter: int | None
    sections: dict[int, bytes]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def emerald_checksum(data: bytes) -> int:
    if len(data) % 4:
        raise ValueError("checksum payload must be a multiple of four bytes")
    checksum = 0
    for offset in range(0, len(data), 4):
        checksum = (checksum + int.from_bytes(data[offset:offset + 4], "little")) & 0xFFFFFFFF
    return ((checksum >> 16) + checksum) & 0xFFFF


def parse_slot(save: bytes, slot_index: int) -> SaveSlot:
    sections: dict[int, bytes] = {}
    counters: set[int] = set()
    valid = True
    for physical_sector in range(slot_index * NUM_SECTORS_PER_SLOT, (slot_index + 1) * NUM_SECTORS_PER_SLOT):
        sector = save[physical_sector * SECTOR_SIZE:(physical_sector + 1) * SECTOR_SIZE]
        section_id, stored_checksum = struct.unpack_from("<HH", sector, FOOTER_FIELDS_START)
        signature, counter = struct.unpack_from("<II", sector, FOOTER_FIELDS_START + 4)
        if signature != SECTOR_SIGNATURE or not (0 <= section_id < NUM_SECTORS_PER_SLOT):
            valid = False
            continue
        expected = emerald_checksum(sector[:SECTION_SIZES[section_id]])
        if expected != stored_checksum or section_id in sections:
            valid = False
        sections[section_id] = sector
        counters.add(counter)

    complete = valid and len(sections) == NUM_SECTORS_PER_SLOT and len(counters) == 1
    return SaveSlot(slot_index, complete, next(iter(counters)) if complete else None, sections)


def analyze_save(path: Path) -> dict[str, int]:
    save = path.read_bytes()
    if len(save) != SAVE_SIZE:
        raise ValueError(f"{path}: expected {SAVE_SIZE} byte Flash save, got {len(save)}")

    slots = [parse_slot(save, 0), parse_slot(save, 1)]
    valid_slots = [slot for slot in slots if slot.complete]
    if not valid_slots:
        raise ValueError(f"{path}: no complete checksum-valid Emerald save slot")
    active = max(valid_slots, key=lambda slot: slot.counter if slot.counter is not None else -1)

    logical_slack_nonzero = 0
    footer_extension_nonzero = 0
    for section_id, sector in active.sections.items():
        logical_slack_nonzero += sum(byte != 0 for byte in sector[SECTION_SIZES[section_id]:SECTOR_DATA_SIZE])
        footer_extension_nonzero += sum(byte != 0 for byte in sector[FOOTER_EXTENSION_START:FOOTER_FIELDS_START])

    return {
        "valid_save_slots": len(valid_slots),
        "active_slot": active.index,
        "active_counter": int(active.counter),
        "active_logical_slack_bytes": sum(SECTOR_DATA_SIZE - size for size in SECTION_SIZES),
        "active_logical_slack_nonzero": logical_slack_nonzero,
        "active_footer_extension_bytes": NUM_SECTORS_PER_SLOT * (FOOTER_FIELDS_START - FOOTER_EXTENSION_START),
        "active_footer_extension_nonzero": footer_extension_nonzero,
    }


def analyze_rom(path: Path) -> dict[str, object]:
    rom = path.read_bytes()
    if len(rom) != ROM_SIZE:
        raise ValueError(f"{path}: expected {ROM_SIZE} byte Emerald ROM, got {len(rom)}")

    game_code = rom[0xAC:0xB0].decode("ascii")
    if game_code not in REGIONS:
        raise ValueError(f"{path}: unexpected game code {game_code!r}")
    language, region = REGIONS[game_code]

    header_checksum = rom[0xBD]
    calculated = (-(sum(rom[0xA0:0xBD]) + 0x19)) & 0xFF
    if header_checksum != calculated:
        raise ValueError(f"{path}: invalid GBA header checksum")

    end = len(rom)
    while end and rom[end - 1] == 0xFF:
        end -= 1

    return {
        "language": language,
        "region": region,
        "rom_sha256": sha256(rom),
        "rom_size": len(rom),
        "game_code": game_code,
        "revision": rom[0xBC],
        "rom_last_non_ff": f"0x{end - 1:06X}" if end else "none",
        "rom_tail_ff_bytes": len(rom) - end,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path, help="Directory containing matching .gba/.sav file stems")
    parser.add_argument("--out", type=Path, default=Path("manifests/emerald-binary-baseline.csv"))
    args = parser.parse_args()

    rows = []
    for rom_path in sorted(args.directory.glob("*.gba")):
        save_path = rom_path.with_suffix(".sav")
        if not save_path.is_file():
            continue
        rom_info = analyze_rom(rom_path)
        save_info = analyze_save(save_path)
        rows.append({
            **rom_info,
            "rom_file": rom_path.name,
            "save_file": save_path.name,
            "save_sha256": sha256(save_path.read_bytes()),
            "save_size": save_path.stat().st_size,
            **save_info,
        })

    expected_codes = set(REGIONS)
    actual_codes = {str(row["game_code"]) for row in rows}
    if actual_codes != expected_codes:
        missing = sorted(expected_codes - actual_codes)
        extra = sorted(actual_codes - expected_codes)
        raise SystemExit(f"expected six Emerald regions; missing={missing}, extra={extra}")

    rows.sort(key=lambda row: LANGUAGE_ORDER[str(row["language"])])
    fieldnames = [
        "language", "region", "rom_file", "rom_sha256", "rom_size", "game_code", "revision",
        "rom_last_non_ff", "rom_tail_ff_bytes", "save_file", "save_sha256", "save_size",
        "valid_save_slots", "active_slot", "active_counter", "active_logical_slack_bytes",
        "active_logical_slack_nonzero", "active_footer_extension_bytes", "active_footer_extension_nonzero",
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} ROM/save pairs -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

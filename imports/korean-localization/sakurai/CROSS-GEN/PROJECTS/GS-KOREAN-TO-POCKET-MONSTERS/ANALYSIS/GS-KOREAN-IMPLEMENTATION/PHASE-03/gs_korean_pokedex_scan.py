#!/usr/bin/env python3
"""Lossless Pokédex entry extractor for official Korean Gold/Silver.

ROM bytes are the authority.  The script verifies the 251-entry pointer table,
the Bank 11 bank-selection routine, the Bank 68/69 entry layout, the codec
round trip, bank padding, and a full-ROM in-memory reconstruction.  It never
writes a ROM image.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from gs_korean_codec import BANK_SIZE, TERMINATOR, build_maps, decode_text, encode_text, extract_bank_6c


POINTER_BANK = 0x11
POINTER_TABLE_BANK_OFFSET = 0x02FF
POINTER_TABLE_FILE_OFFSET = POINTER_BANK * BANK_SIZE + POINTER_TABLE_BANK_OFFSET
POINTER_TABLE_CPU_ADDRESS = 0x4000 + POINTER_TABLE_BANK_OFFSET
POINTER_COUNT = 251
DISPATCH_FILE_OFFSET = POINTER_BANK * BANK_SIZE + 0x02E8
DISPATCH_CPU_ADDRESS = 0x42E8
DISPATCH_BYTES = bytes.fromhex("47 50 21 ff 42 78 3d 06 00 4f 09 09 07 e6 01 c6 68 47 2a 66 6f c9")
DEX_BANKS = ((0x68, 1, 128), (0x69, 129, 251))


def digest(data: bytes, algorithm: str = "sha256") -> str:
    return hashlib.new(algorithm, data).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pokemon_names(rom: bytes, maps) -> list[str]:
    rows, _ = extract_bank_6c(rom, maps)
    return [row["decoded_text"] for row in rows if row["category"] == "POKEMON_NAME_SLOTS"][:251]


def find_terminator(bank: bytes, start: int, label: str) -> int:
    end = bank.find(bytes([TERMINATOR]), start)
    if end < 0:
        raise ValueError(f"Missing terminator in {label} at bank offset 0x{start:04X}")
    return end


def extract_version(version: str, rom: bytes) -> tuple[list[dict], list[dict], dict, bytes]:
    maps = build_maps(rom)
    names = pokemon_names(rom, maps)
    if rom[DISPATCH_FILE_OFFSET : DISPATCH_FILE_OFFSET + len(DISPATCH_BYTES)] != DISPATCH_BYTES:
        raise AssertionError(f"{version}: Bank 11 Pokédex dispatch routine mismatch")

    pointer_region = rom[POINTER_TABLE_FILE_OFFSET : POINTER_TABLE_FILE_OFFSET + POINTER_COUNT * 2]
    rom_pointers = [int.from_bytes(pointer_region[i * 2 : i * 2 + 2], "little") for i in range(POINTER_COUNT)]
    entries: list[dict] = []
    pointers: list[dict] = []
    computed_pointers: list[int] = []
    rebuilt_rom = bytearray(rom)
    bank_summaries: dict[str, dict] = {}

    for bank_number, first_dex, last_dex in DEX_BANKS:
        bank_start = bank_number * BANK_SIZE
        bank = rom[bank_start : bank_start + BANK_SIZE]
        rebuilt = bytearray(bank)
        cursor = 0
        for dex_number in range(first_dex, last_dex + 1):
            entry_start = cursor
            category_end = find_terminator(bank, cursor, f"#{dex_number} category")
            category_raw = bank[cursor:category_end]
            if category_end + 4 > BANK_SIZE:
                raise ValueError(f"{version}: truncated metrics for #{dex_number}")
            height_dm = bank[category_end + 1]
            weight_hg = int.from_bytes(bank[category_end + 2 : category_end + 4], "little")
            description_start = category_end + 4
            description_end = find_terminator(bank, description_start, f"#{dex_number} description")
            description_raw = bank[description_start:description_end]
            cursor = description_end + 1

            category, category_unknown = decode_text(category_raw, maps)
            description, description_unknown = decode_text(description_raw, maps)
            if category_unknown or description_unknown:
                raise ValueError(f"{version}: undefined codec value in Pokédex #{dex_number}")
            rebuilt_entry = (
                encode_text(category, maps)
                + bytes([TERMINATOR, height_dm])
                + weight_hg.to_bytes(2, "little")
                + encode_text(description, maps)
                + bytes([TERMINATOR])
            )
            original_entry = bank[entry_start:cursor]
            if rebuilt_entry != original_entry:
                raise AssertionError(f"{version}: entry round-trip failed for #{dex_number}")
            rebuilt[entry_start:cursor] = rebuilt_entry

            pointer_index = dex_number - 1
            cpu_address = 0x4000 + entry_start
            computed_pointers.append(cpu_address)
            pointer_matches = rom_pointers[pointer_index] == cpu_address
            if not pointer_matches:
                raise AssertionError(
                    f"{version}: pointer mismatch for #{dex_number}: "
                    f"0x{rom_pointers[pointer_index]:04X} != 0x{cpu_address:04X}"
                )
            entries.append(
                {
                    "version": version,
                    "dex_number": dex_number,
                    "pokemon_name_gs_korean": names[dex_number - 1],
                    "bank_hex": f"0x{bank_number:02X}",
                    "bank_offset_hex": f"0x{entry_start:04X}",
                    "cpu_address_hex": f"0x{cpu_address:04X}",
                    "file_offset_hex": f"0x{bank_start + entry_start:06X}",
                    "entry_length": len(original_entry),
                    "category": category,
                    "height_dm": height_dm,
                    "height_m": f"{height_dm / 10:.1f}",
                    "weight_hg": weight_hg,
                    "weight_kg": f"{weight_hg / 10:.1f}",
                    "description": description,
                    "description_next_count": description.count("<NEXT>"),
                    "category_raw_hex": category_raw.hex(" "),
                    "metrics_raw_hex": bank[category_end + 1 : category_end + 4].hex(" "),
                    "description_raw_hex": description_raw.hex(" "),
                    "entry_raw_hex": original_entry.hex(" "),
                }
            )
            pointers.append(
                {
                    "version": version,
                    "dex_number": dex_number,
                    "pointer_index_zero_based": pointer_index,
                    "pointer_table_bank_hex": f"0x{POINTER_BANK:02X}",
                    "pointer_table_cpu_address_hex": f"0x{POINTER_TABLE_CPU_ADDRESS + pointer_index * 2:04X}",
                    "pointer_table_file_offset_hex": f"0x{POINTER_TABLE_FILE_OFFSET + pointer_index * 2:06X}",
                    "pointer_raw_hex": pointer_region[pointer_index * 2 : pointer_index * 2 + 2].hex(" "),
                    "target_bank_hex": f"0x{bank_number:02X}",
                    "target_cpu_address_hex": f"0x{cpu_address:04X}",
                    "target_file_offset_hex": f"0x{bank_start + entry_start:06X}",
                    "verified": True,
                }
            )

        last_nonzero = max((i for i, value in enumerate(bank) if value), default=-1) + 1
        if cursor != last_nonzero:
            raise AssertionError(
                f"{version}: Bank {bank_number:02X} parsed end 0x{cursor:04X} "
                f"!= last nonzero end 0x{last_nonzero:04X}"
            )
        if any(bank[cursor:]):
            raise AssertionError(f"{version}: Bank {bank_number:02X} padding is not zero-filled")
        if bytes(rebuilt) != bank:
            raise AssertionError(f"{version}: Bank {bank_number:02X} lossless rebuild failed")
        rebuilt_rom[bank_start : bank_start + BANK_SIZE] = rebuilt
        bank_summaries[f"0x{bank_number:02X}"] = {
            "first_dex_number": first_dex,
            "last_dex_number": last_dex,
            "entry_count": last_dex - first_dex + 1,
            "used_bytes": cursor,
            "free_zero_bytes": BANK_SIZE - cursor,
            "used_sha256": digest(bank[:cursor]),
            "whole_bank_sha256": digest(bank),
        }

    rebuilt_pointer_region = b"".join(value.to_bytes(2, "little") for value in computed_pointers)
    if rebuilt_pointer_region != pointer_region:
        raise AssertionError(f"{version}: pointer table lossless rebuild failed")
    rebuilt_rom[POINTER_TABLE_FILE_OFFSET : POINTER_TABLE_FILE_OFFSET + len(pointer_region)] = rebuilt_pointer_region
    if bytes(rebuilt_rom) != rom:
        raise AssertionError(f"{version}: full-ROM in-memory reconstruction failed")

    summary = {
        "rom_sha1": digest(rom, "sha1"),
        "entry_count": len(entries),
        "pointer_count": len(pointers),
        "pointer_table_bank_hex": f"0x{POINTER_BANK:02X}",
        "pointer_table_cpu_address_hex": f"0x{POINTER_TABLE_CPU_ADDRESS:04X}",
        "pointer_table_file_offset_hex": f"0x{POINTER_TABLE_FILE_OFFSET:06X}",
        "pointer_table_sha256": digest(pointer_region),
        "dispatch_bank_hex": f"0x{POINTER_BANK:02X}",
        "dispatch_cpu_address_hex": f"0x{DISPATCH_CPU_ADDRESS:04X}",
        "dispatch_file_offset_hex": f"0x{DISPATCH_FILE_OFFSET:06X}",
        "dispatch_raw_hex": DISPATCH_BYTES.hex(" "),
        "dispatch_verified": True,
        "pointer_table_lossless": rebuilt_pointer_region == pointer_region,
        "full_rom_roundtrip_sha1": digest(bytes(rebuilt_rom), "sha1"),
        "full_rom_lossless": bytes(rebuilt_rom) == rom,
        "banks": bank_summaries,
    }
    return entries, pointers, summary, pointer_region


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_rom", type=Path)
    parser.add_argument("silver_rom", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    gold = args.gold_rom.read_bytes()
    silver = args.silver_rom.read_bytes()
    gold_entries, gold_pointers, gold_summary, gold_pointer_bytes = extract_version("KOREAN_GOLD", gold)
    silver_entries, silver_pointers, silver_summary, silver_pointer_bytes = extract_version("KOREAN_SILVER", silver)

    comparisons: list[dict] = []
    for g, s in zip(gold_entries, silver_entries, strict=True):
        if g["dex_number"] != s["dex_number"]:
            raise AssertionError("Gold/Silver Pokédex order mismatch")
        comparisons.append(
            {
                "dex_number": g["dex_number"],
                "pokemon_name_gs_korean": g["pokemon_name_gs_korean"],
                "category_same": g["category"] == s["category"],
                "height_same": g["height_dm"] == s["height_dm"],
                "weight_same": g["weight_hg"] == s["weight_hg"],
                "description_same": g["description"] == s["description"],
                "gold_category": g["category"],
                "silver_category": s["category"],
                "height_dm": g["height_dm"],
                "weight_hg": g["weight_hg"],
                "gold_description": g["description"],
                "silver_description": s["description"],
                "gold_bank_hex": g["bank_hex"],
                "silver_bank_hex": s["bank_hex"],
                "gold_cpu_address_hex": g["cpu_address_hex"],
                "silver_cpu_address_hex": s["cpu_address_hex"],
            }
        )

    args.output.mkdir(parents=True, exist_ok=True)
    entries = gold_entries + silver_entries
    pointers = gold_pointers + silver_pointers
    write_csv(args.output / "pokedex_entries_ko.csv", entries)
    write_json(args.output / "pokedex_entries_ko.json", entries)
    write_csv(args.output / "pokedex_pointer_table.csv", pointers)
    write_json(args.output / "pokedex_pointer_table.json", pointers)
    write_csv(args.output / "pokedex_gold_silver_diff.csv", comparisons)
    write_json(args.output / "pokedex_gold_silver_diff.json", comparisons)
    summary = {
        "gold": gold_summary,
        "silver": silver_summary,
        "gold_silver": {
            "pointer_table_identical": gold_pointer_bytes == silver_pointer_bytes,
            "same_category_count": sum(row["category_same"] for row in comparisons),
            "same_height_count": sum(row["height_same"] for row in comparisons),
            "same_weight_count": sum(row["weight_same"] for row in comparisons),
            "same_description_count": sum(row["description_same"] for row in comparisons),
            "different_description_count": sum(not row["description_same"] for row in comparisons),
        },
        "output_rows": {
            "pokedex_entries_ko": len(entries),
            "pokedex_pointer_table": len(pointers),
            "pokedex_gold_silver_diff": len(comparisons),
        },
        "rom_output_written": False,
    }
    write_json(args.output / "phase3_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

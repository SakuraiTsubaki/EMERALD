#!/usr/bin/env python3
"""Lossless Bank 6D move-description extractor for Korean Gold/Silver.

The original ROMs are read only.  This script verifies all 256 pointer slots,
extracts the 251 real move descriptions, checks the five unused slots and the
printing routine, and performs an in-memory full-ROM round trip without writing
a ROM image.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from gs_korean_codec import BANK_SIZE, TERMINATOR, build_maps, decode_text, encode_text, extract_bank_6c


BANK_NUMBER = 0x6D
POINTER_SLOT_COUNT = 256
MOVE_COUNT = 251
POINTER_TABLE_SIZE = POINTER_SLOT_COUNT * 2
DUMMY_ADDRESS = 0x4200
DUMMY_BANK_OFFSET = DUMMY_ADDRESS - 0x4000
FIRST_DESCRIPTION_ADDRESS = 0x4202
FIRST_DESCRIPTION_BANK_OFFSET = FIRST_DESCRIPTION_ADDRESS - 0x4000
PRINT_ROUTINE_FILE_OFFSET = 0x02C952
PRINT_ROUTINE_BANK = 0x0B
PRINT_ROUTINE_CPU_ADDRESS = 0x4952
PRINT_ROUTINE_BYTES = bytes.fromhex(
    "e5 21 00 40 fa f9 c1 3d 4f 06 00 09 09 3e 6d cd e4 31 54 5d e1 3e 6d c3 87 12"
)


def digest(data: bytes, algorithm: str = "sha256") -> str:
    return hashlib.new(algorithm, data).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_move_names(rom: bytes, maps) -> list[str]:
    rows, _ = extract_bank_6c(rom, maps)
    names = [row["decoded_text"] for row in rows if row["category"] == "MOVE_NAMES"]
    if len(names) != MOVE_COUNT:
        raise AssertionError(f"Expected {MOVE_COUNT} move names, got {len(names)}")
    return names


def extract_version(version: str, rom: bytes) -> tuple[list[dict], list[dict], dict, bytes]:
    maps = build_maps(rom)
    names = get_move_names(rom, maps)
    routine = rom[PRINT_ROUTINE_FILE_OFFSET : PRINT_ROUTINE_FILE_OFFSET + len(PRINT_ROUTINE_BYTES)]
    if routine != PRINT_ROUTINE_BYTES:
        raise AssertionError(f"{version}: move-description print routine mismatch")

    bank_start = BANK_NUMBER * BANK_SIZE
    bank = rom[bank_start : bank_start + BANK_SIZE]
    pointer_region = bank[:POINTER_TABLE_SIZE]
    pointer_values = [
        int.from_bytes(pointer_region[i * 2 : i * 2 + 2], "little")
        for i in range(POINTER_SLOT_COUNT)
    ]
    if pointer_values[0] != FIRST_DESCRIPTION_ADDRESS:
        raise AssertionError(f"{version}: unexpected first description pointer")
    if pointer_values[MOVE_COUNT:] != [DUMMY_ADDRESS] * (POINTER_SLOT_COUNT - MOVE_COUNT):
        raise AssertionError(f"{version}: unused pointer slots do not target 0x{DUMMY_ADDRESS:04X}")

    dummy_raw = bank[DUMMY_BANK_OFFSET:FIRST_DESCRIPTION_BANK_OFFSET]
    dummy_text, dummy_unknown = decode_text(dummy_raw, maps)
    if dummy_unknown or dummy_raw != bytes([0xE6, TERMINATOR]) or dummy_text != "<?>@":
        raise AssertionError(f"{version}: unexpected dummy description")

    entries: list[dict] = []
    pointers: list[dict] = []
    computed_pointers: list[int] = []
    cursor = FIRST_DESCRIPTION_BANK_OFFSET
    rebuilt = bytearray(bank)
    for move_index in range(MOVE_COUNT):
        move_id = move_index + 1
        expected_address = 0x4000 + cursor
        actual_address = pointer_values[move_index]
        if actual_address != expected_address:
            raise AssertionError(
                f"{version}: move {move_id} pointer 0x{actual_address:04X} "
                f"!= parsed address 0x{expected_address:04X}"
            )
        end = bank.find(bytes([TERMINATOR]), cursor)
        if end < 0:
            raise ValueError(f"{version}: missing terminator for move {move_id}")
        raw = bank[cursor:end]
        text, unknown = decode_text(raw, maps)
        if unknown:
            raise ValueError(f"{version}: undefined code in move {move_id}: {unknown}")
        rebuilt_record = encode_text(text, maps) + bytes([TERMINATOR])
        original_record = bank[cursor : end + 1]
        if rebuilt_record != original_record:
            raise AssertionError(f"{version}: move {move_id} round-trip mismatch")
        rebuilt[cursor : end + 1] = rebuilt_record
        computed_pointers.append(expected_address)
        entries.append(
            {
                "version": version,
                "move_id": move_id,
                "move_name_gs_korean": names[move_index],
                "bank_hex": f"0x{BANK_NUMBER:02X}",
                "bank_offset_hex": f"0x{cursor:04X}",
                "cpu_address_hex": f"0x{expected_address:04X}",
                "file_offset_hex": f"0x{bank_start + cursor:06X}",
                "record_length": len(original_record),
                "description": text,
                "next_count": text.count("<NEXT>"),
                "raw_hex": raw.hex(" "),
                "record_raw_hex": original_record.hex(" "),
                "undefined_code_count": 0,
            }
        )
        cursor = end + 1

    for slot_index, address in enumerate(pointer_values):
        is_real = slot_index < MOVE_COUNT
        target_offset = address - 0x4000
        pointers.append(
            {
                "version": version,
                "slot_index_zero_based": slot_index,
                "move_id_if_real": slot_index + 1 if is_real else "",
                "slot_kind": "MOVE_DESCRIPTION" if is_real else "UNUSED_DUMMY",
                "pointer_bank_hex": f"0x{BANK_NUMBER:02X}",
                "pointer_cpu_address_hex": f"0x{0x4000 + slot_index * 2:04X}",
                "pointer_file_offset_hex": f"0x{bank_start + slot_index * 2:06X}",
                "pointer_raw_hex": pointer_region[slot_index * 2 : slot_index * 2 + 2].hex(" "),
                "target_cpu_address_hex": f"0x{address:04X}",
                "target_bank_offset_hex": f"0x{target_offset:04X}",
                "target_file_offset_hex": f"0x{bank_start + target_offset:06X}",
                "verified": True,
            }
        )

    last_nonzero = max((i for i, value in enumerate(bank) if value), default=-1) + 1
    if cursor != last_nonzero:
        raise AssertionError(
            f"{version}: parsed end 0x{cursor:04X} != last nonzero end 0x{last_nonzero:04X}"
        )
    if any(bank[cursor:]):
        raise AssertionError(f"{version}: trailing bank area is not zero-filled")
    rebuilt_pointer_values = computed_pointers + [DUMMY_ADDRESS] * (POINTER_SLOT_COUNT - MOVE_COUNT)
    rebuilt_pointer_region = b"".join(value.to_bytes(2, "little") for value in rebuilt_pointer_values)
    if rebuilt_pointer_region != pointer_region:
        raise AssertionError(f"{version}: pointer table round-trip mismatch")
    rebuilt[:POINTER_TABLE_SIZE] = rebuilt_pointer_region
    rebuilt[DUMMY_BANK_OFFSET:FIRST_DESCRIPTION_BANK_OFFSET] = encode_text("<?>@", maps)
    if bytes(rebuilt) != bank:
        raise AssertionError(f"{version}: Bank 6D lossless rebuild mismatch")
    rebuilt_rom = rom[:bank_start] + bytes(rebuilt) + rom[bank_start + BANK_SIZE :]
    if rebuilt_rom != rom:
        raise AssertionError(f"{version}: full-ROM in-memory reconstruction mismatch")

    summary = {
        "rom_sha1": digest(rom, "sha1"),
        "bank_hex": f"0x{BANK_NUMBER:02X}",
        "bank_sha256": digest(bank),
        "pointer_slot_count": POINTER_SLOT_COUNT,
        "real_move_pointer_count": MOVE_COUNT,
        "unused_dummy_pointer_count": POINTER_SLOT_COUNT - MOVE_COUNT,
        "dummy_target_cpu_address_hex": f"0x{DUMMY_ADDRESS:04X}",
        "dummy_raw_hex": dummy_raw.hex(" "),
        "dummy_decoded": dummy_text,
        "first_description_cpu_address_hex": f"0x{FIRST_DESCRIPTION_ADDRESS:04X}",
        "used_bytes": cursor,
        "free_zero_bytes": BANK_SIZE - cursor,
        "pointer_table_lossless": rebuilt_pointer_region == pointer_region,
        "bank_lossless": bytes(rebuilt) == bank,
        "full_rom_roundtrip_sha1": digest(rebuilt_rom, "sha1"),
        "full_rom_lossless": rebuilt_rom == rom,
        "print_routine": {
            "bank_hex": f"0x{PRINT_ROUTINE_BANK:02X}",
            "cpu_address_hex": f"0x{PRINT_ROUTINE_CPU_ADDRESS:04X}",
            "file_offset_hex": f"0x{PRINT_ROUTINE_FILE_OFFSET:06X}",
            "raw_hex": PRINT_ROUTINE_BYTES.hex(" "),
            "verified": True,
        },
    }
    return entries, pointers, summary, bank


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_rom", type=Path)
    parser.add_argument("silver_rom", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    gold = args.gold_rom.read_bytes()
    silver = args.silver_rom.read_bytes()
    gold_entries, gold_pointers, gold_summary, gold_bank = extract_version("KOREAN_GOLD", gold)
    silver_entries, silver_pointers, silver_summary, silver_bank = extract_version("KOREAN_SILVER", silver)
    normalized_gold = [{k: v for k, v in row.items() if k != "version"} for row in gold_entries]
    normalized_silver = [{k: v for k, v in row.items() if k != "version"} for row in silver_entries]
    if normalized_gold != normalized_silver:
        raise AssertionError("Gold/Silver move descriptions differ")
    if gold_bank != silver_bank:
        raise AssertionError("Gold/Silver Bank 6D differs")

    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "move_descriptions_ko.csv", gold_entries)
    write_json(args.output / "move_descriptions_ko.json", gold_entries)
    write_csv(args.output / "move_description_pointer_table.csv", gold_pointers)
    write_json(args.output / "move_description_pointer_table.json", gold_pointers)
    master = [
        {
            "move_id": row["move_id"],
            "original_gs_korean_name": row["move_name_gs_korean"],
            "latest_official_korean_name": "",
            "original_gs_korean_description": row["description"],
            "final_korean_description": "",
            "official_name_source": "",
            "description_translation_source": "",
            "verification_status": "PENDING_OFFICIAL_CROSSCHECK",
            "change_reason": "",
            "bank_hex": row["bank_hex"],
            "cpu_address_hex": row["cpu_address_hex"],
        }
        for row in gold_entries
    ]
    write_csv(args.output / "official_move_name_description_master.csv", master)
    write_json(args.output / "official_move_name_description_master.json", master)
    summary = {
        "gold": gold_summary,
        "silver": silver_summary,
        "gold_silver_bank_6d_identical": gold_bank == silver_bank,
        "gold_silver_entries_identical": all(
            {k: v for k, v in g.items() if k != "version"}
            == {k: v for k, v in s.items() if k != "version"}
            for g, s in zip(gold_entries, silver_entries, strict=True)
        ),
        "description_count": len(gold_entries),
        "undefined_code_count": sum(row["undefined_code_count"] for row in gold_entries),
        "next_count_distribution": {
            str(count): sum(row["next_count"] == count for row in gold_entries)
            for count in sorted({row["next_count"] for row in gold_entries})
        },
        "official_crosscheck_rows_created": len(master),
        "rom_output_written": False,
    }
    write_json(args.output / "phase4_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

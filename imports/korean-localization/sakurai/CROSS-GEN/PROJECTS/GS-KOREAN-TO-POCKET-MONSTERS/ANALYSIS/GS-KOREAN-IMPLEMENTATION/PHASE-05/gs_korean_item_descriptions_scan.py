#!/usr/bin/env python3
"""Lossless Bank 6E item-description extractor for Korean Gold/Silver.

The tool preserves all 256 lookup slots, resolves their shared pointers into a
198-record string pool, joins each slot to its Bank 6C item name, verifies the
TM/HM dispatch routine, and performs an in-memory full-ROM round trip.  It does
not write a ROM image.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from gs_korean_codec import BANK_SIZE, TERMINATOR, build_maps, decode_text, encode_text, extract_bank_6c


BANK_NUMBER = 0x6E
POINTER_SLOT_COUNT = 256
POINTER_TABLE_SIZE = POINTER_SLOT_COUNT * 2
POOL_START = 0x0200
TM01_ITEM_ID = 0xBF
PRINT_ROUTINE_FILE_OFFSET = 0x02C000
PRINT_ROUTINE_BANK = 0x0B
PRINT_ROUTINE_CPU_ADDRESS = 0x4000
PRINT_ROUTINE_BYTES = bytes.fromhex(
    "fa f9 c1 fe bf 38 12 ea be d0 d5 cd c1 45 e1 fa 0e d2 ea f9 c1 cd 52 49 c9 "
    "d5 21 00 40 fa f9 c1 3d 4f 06 00 09 09 3e 6e cd e4 31 54 5d e1 3e 6e c3 87 12"
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


def get_item_names(rom: bytes, maps) -> list[str]:
    rows, _ = extract_bank_6c(rom, maps)
    names = [row["decoded_text"] for row in rows if row["category"] == "ITEM_NAMES"]
    if len(names) != POINTER_SLOT_COUNT:
        raise AssertionError(f"Expected 256 item-name slots, got {len(names)}")
    return names


def extract_version(version: str, rom: bytes) -> tuple[list[dict], list[dict], list[dict], dict, bytes]:
    maps = build_maps(rom)
    names = get_item_names(rom, maps)
    routine = rom[PRINT_ROUTINE_FILE_OFFSET : PRINT_ROUTINE_FILE_OFFSET + len(PRINT_ROUTINE_BYTES)]
    if routine != PRINT_ROUTINE_BYTES:
        raise AssertionError(f"{version}: item-description print routine mismatch")

    bank_start = BANK_NUMBER * BANK_SIZE
    bank = rom[bank_start : bank_start + BANK_SIZE]
    pointer_region = bank[:POINTER_TABLE_SIZE]
    pointer_values = [
        int.from_bytes(pointer_region[i * 2 : i * 2 + 2], "little")
        for i in range(POINTER_SLOT_COUNT)
    ]
    if any(not 0x4000 <= value < 0x8000 for value in pointer_values):
        raise AssertionError(f"{version}: out-of-bank item description pointer")
    unique_addresses = sorted(set(pointer_values))
    if unique_addresses[0] != 0x4000 + POOL_START:
        raise AssertionError(f"{version}: unexpected item description pool start")

    references: dict[int, list[int]] = defaultdict(list)
    for slot_index, address in enumerate(pointer_values):
        references[address].append(slot_index)

    pool_rows: list[dict] = []
    decoded_by_address: dict[int, tuple[str, bytes, bytes]] = {}
    rebuilt_pool = bytearray()
    cursor = POOL_START
    for pool_index, address in enumerate(unique_addresses):
        offset = address - 0x4000
        if offset != cursor:
            raise AssertionError(
                f"{version}: non-contiguous pool at 0x{offset:04X}; expected 0x{cursor:04X}"
            )
        end = bank.find(bytes([TERMINATOR]), offset)
        if end < 0:
            raise ValueError(f"{version}: missing terminator at pool address 0x{address:04X}")
        raw = bank[offset:end]
        record = bank[offset : end + 1]
        text, unknown = decode_text(raw, maps)
        if unknown:
            raise ValueError(f"{version}: undefined code at 0x{address:04X}: {unknown}")
        rebuilt_record = encode_text(text, maps) + bytes([TERMINATOR])
        if rebuilt_record != record:
            raise AssertionError(f"{version}: pool record round-trip mismatch at 0x{address:04X}")
        rebuilt_pool.extend(rebuilt_record)
        ref_slots = references[address]
        ref_item_ids = [((slot + 1) & 0xFF) for slot in ref_slots]
        pool_rows.append(
            {
                "version": version,
                "pool_record_index_zero_based": pool_index,
                "bank_hex": f"0x{BANK_NUMBER:02X}",
                "bank_offset_hex": f"0x{offset:04X}",
                "cpu_address_hex": f"0x{address:04X}",
                "file_offset_hex": f"0x{bank_start + offset:06X}",
                "record_length": len(record),
                "description": text,
                "next_count": text.count("<NEXT>"),
                "reference_count": len(ref_slots),
                "referencing_slots": " ".join(str(slot) for slot in ref_slots),
                "referencing_item_ids_hex": " ".join(f"0x{item_id:02X}" for item_id in ref_item_ids),
                "raw_hex": raw.hex(" "),
                "record_raw_hex": record.hex(" "),
                "undefined_code_count": 0,
            }
        )
        decoded_by_address[address] = (text, raw, record)
        cursor = end + 1

    last_nonzero = max((i for i, value in enumerate(bank) if value), default=-1) + 1
    if cursor != last_nonzero:
        raise AssertionError(
            f"{version}: pool end 0x{cursor:04X} != last nonzero end 0x{last_nonzero:04X}"
        )
    if bytes(rebuilt_pool) != bank[POOL_START:cursor]:
        raise AssertionError(f"{version}: description pool lossless rebuild mismatch")
    if any(bank[cursor:]):
        raise AssertionError(f"{version}: trailing area is not zero-filled")

    slots: list[dict] = []
    pointers: list[dict] = []
    for slot_index, address in enumerate(pointer_values):
        item_id = (slot_index + 1) & 0xFF
        text, raw, record = decoded_by_address[address]
        delegates = item_id >= TM01_ITEM_ID
        slot_kind = "NO_ITEM_UNDERFLOW_SLOT" if item_id == 0 else "ITEM_ID"
        slots.append(
            {
                "version": version,
                "slot_index_zero_based": slot_index,
                "item_id_decimal": item_id,
                "item_id_hex": f"0x{item_id:02X}",
                "slot_kind": slot_kind,
                "item_name_gs_korean": names[slot_index],
                "is_placeholder_name": names[slot_index] in {"?", "<?>"},
                "engine_description_source": "MOVE_DESCRIPTION_BANK_6D" if delegates else "ITEM_DESCRIPTION_BANK_6E",
                "bank_hex": f"0x{BANK_NUMBER:02X}",
                "description_cpu_address_hex": f"0x{address:04X}",
                "description_file_offset_hex": f"0x{bank_start + address - 0x4000:06X}",
                "shared_pointer_reference_count": len(references[address]),
                "description": text,
                "next_count": text.count("<NEXT>"),
                "description_raw_hex": raw.hex(" "),
                "description_record_raw_hex": record.hex(" "),
            }
        )
        pointers.append(
            {
                "version": version,
                "slot_index_zero_based": slot_index,
                "item_id_decimal": item_id,
                "item_id_hex": f"0x{item_id:02X}",
                "pointer_cpu_address_hex": f"0x{0x4000 + slot_index * 2:04X}",
                "pointer_file_offset_hex": f"0x{bank_start + slot_index * 2:06X}",
                "pointer_raw_hex": pointer_region[slot_index * 2 : slot_index * 2 + 2].hex(" "),
                "target_cpu_address_hex": f"0x{address:04X}",
                "target_bank_offset_hex": f"0x{address - 0x4000:04X}",
                "target_file_offset_hex": f"0x{bank_start + address - 0x4000:06X}",
                "target_reference_count": len(references[address]),
                "verified_record_boundary": True,
            }
        )

    rebuilt_pointer_region = b"".join(value.to_bytes(2, "little") for value in pointer_values)
    if rebuilt_pointer_region != pointer_region:
        raise AssertionError(f"{version}: pointer table lossless rebuild mismatch")
    rebuilt_bank = pointer_region + bytes(rebuilt_pool) + bank[cursor:]
    if rebuilt_bank != bank:
        raise AssertionError(f"{version}: Bank 6E lossless rebuild mismatch")
    rebuilt_rom = rom[:bank_start] + rebuilt_bank + rom[bank_start + BANK_SIZE :]
    if rebuilt_rom != rom:
        raise AssertionError(f"{version}: full-ROM in-memory reconstruction mismatch")

    summary = {
        "rom_sha1": digest(rom, "sha1"),
        "bank_hex": f"0x{BANK_NUMBER:02X}",
        "bank_sha256": digest(bank),
        "pointer_slot_count": len(pointer_values),
        "unique_description_count": len(unique_addresses),
        "shared_pointer_excess_count": len(pointer_values) - len(unique_addresses),
        "description_pool_start_cpu_hex": f"0x{0x4000 + POOL_START:04X}",
        "description_pool_end_exclusive_cpu_hex": f"0x{0x4000 + cursor:04X}",
        "used_bytes": cursor,
        "free_zero_bytes": BANK_SIZE - cursor,
        "tm01_threshold_item_id_hex": f"0x{TM01_ITEM_ID:02X}",
        "move_description_dispatch_slot_count": sum(row["engine_description_source"] == "MOVE_DESCRIPTION_BANK_6D" for row in slots),
        "item_description_dispatch_slot_count": sum(row["engine_description_source"] == "ITEM_DESCRIPTION_BANK_6E" for row in slots),
        "placeholder_name_slot_count": sum(row["is_placeholder_name"] for row in slots),
        "pointer_table_lossless": rebuilt_pointer_region == pointer_region,
        "description_pool_lossless": bytes(rebuilt_pool) == bank[POOL_START:cursor],
        "bank_lossless": rebuilt_bank == bank,
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
    return slots, pool_rows, pointers, summary, bank


def normalize(rows: list[dict]) -> list[dict]:
    return [{key: value for key, value in row.items() if key != "version"} for row in rows]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_rom", type=Path)
    parser.add_argument("silver_rom", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    gold = args.gold_rom.read_bytes()
    silver = args.silver_rom.read_bytes()
    gold_slots, gold_pool, gold_pointers, gold_summary, gold_bank = extract_version("KOREAN_GOLD", gold)
    silver_slots, silver_pool, silver_pointers, silver_summary, silver_bank = extract_version("KOREAN_SILVER", silver)
    if normalize(gold_slots) != normalize(silver_slots) or normalize(gold_pool) != normalize(silver_pool):
        raise AssertionError("Gold/Silver item descriptions differ")
    if normalize(gold_pointers) != normalize(silver_pointers) or gold_bank != silver_bank:
        raise AssertionError("Gold/Silver Bank 6E pointer data differs")

    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "item_description_slots_ko.csv", gold_slots)
    write_json(args.output / "item_description_slots_ko.json", gold_slots)
    write_csv(args.output / "item_description_pool_ko.csv", gold_pool)
    write_json(args.output / "item_description_pool_ko.json", gold_pool)
    write_csv(args.output / "item_description_pointer_table.csv", gold_pointers)
    write_json(args.output / "item_description_pointer_table.json", gold_pointers)
    master = [
        {
            "slot_index_zero_based": row["slot_index_zero_based"],
            "item_id_decimal": row["item_id_decimal"],
            "item_id_hex": row["item_id_hex"],
            "slot_kind": row["slot_kind"],
            "original_gs_korean_name": row["item_name_gs_korean"],
            "latest_official_korean_name": "",
            "original_gs_korean_description": row["description"],
            "final_korean_description": "",
            "engine_description_source": row["engine_description_source"],
            "official_name_source": "",
            "description_translation_source": "",
            "verification_status": "PENDING_OFFICIAL_CROSSCHECK",
            "change_reason": "",
            "description_cpu_address_hex": row["description_cpu_address_hex"],
        }
        for row in gold_slots
    ]
    write_csv(args.output / "official_item_name_description_master.csv", master)
    write_json(args.output / "official_item_name_description_master.json", master)
    summary = {
        "gold": gold_summary,
        "silver": silver_summary,
        "gold_silver_bank_6e_identical": gold_bank == silver_bank,
        "gold_silver_slots_identical": normalize(gold_slots) == normalize(silver_slots),
        "slot_count": len(gold_slots),
        "unique_description_count": len(gold_pool),
        "undefined_code_count": sum(row["undefined_code_count"] for row in gold_pool),
        "unique_pool_next_count_distribution": dict(sorted(Counter(row["next_count"] for row in gold_pool).items())),
        "slot_next_count_distribution": dict(sorted(Counter(row["next_count"] for row in gold_slots).items())),
        "official_crosscheck_rows_created": len(master),
        "rom_output_written": False,
    }
    write_json(args.output / "phase5_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

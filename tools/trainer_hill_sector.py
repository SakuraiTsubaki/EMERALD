#!/usr/bin/env python3
"""Inspect and extract Pokémon Emerald Trainer Hill e-Reader save data.

Emerald stores the e-Reader-generated Trainer Hill challenge in special
flash sector 30 (physical offset 0x1E000 in a 128 KiB save).

This tool does not require or distribute ROM/card dump data.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

SECTOR_SIZE = 0x1000
TRAINER_HILL_SECTOR = 30
SECTOR_OFFSET = TRAINER_HILL_SECTOR * SECTOR_SIZE
SPECIAL_SECTOR_SENTINEL = 0x0000B39D

CHALLENGE_HEADER_SIZE = 0x8
NUM_FLOORS = 4
FLOOR_SIZE = 0x3B8
FLOOR_DATA_SIZE = NUM_FLOORS * FLOOR_SIZE
CHALLENGE_SIZE = CHALLENGE_HEADER_SIZE + FLOOR_DATA_SIZE

TRAINER_SIZE = 0x148
FLOOR_MAP_SIZE = 0x124
FLOOR_TRAINER0_OFFSET = 0x4
FLOOR_TRAINER1_OFFSET = FLOOR_TRAINER0_OFFSET + TRAINER_SIZE
FLOOR_MAP_OFFSET = FLOOR_TRAINER1_OFFSET + TRAINER_SIZE

EREADER_ENTRY_SIZE = 0x274
EREADER_ENTRY_BODY_SIZE = EREADER_ENTRY_SIZE - 4


def byte_sum(data: bytes) -> int:
    return sum(data) & 0xFFFFFFFF


def load_sector(path: Path) -> bytes:
    data = path.read_bytes()
    required = SECTOR_OFFSET + SECTOR_SIZE
    if len(data) < required:
        raise ValueError(
            f"save is too small: 0x{len(data):X} bytes; need at least 0x{required:X}"
        )
    return data[SECTOR_OFFSET : SECTOR_OFFSET + SECTOR_SIZE]


def parse_challenge(sector: bytes) -> dict:
    sentinel = struct.unpack_from("<I", sector, 0)[0]
    if sentinel != SPECIAL_SECTOR_SENTINEL:
        return {
            "valid": False,
            "reason": "trainer_hill_sector_empty_or_invalid",
            "sentinel": f"0x{sentinel:08X}",
            "expected_sentinel": f"0x{SPECIAL_SECTOR_SENTINEL:08X}",
        }

    challenge = sector[4 : 4 + CHALLENGE_SIZE]
    num_trainers = challenge[0]
    generation = challenge[1]
    num_floors = challenge[2]
    stored_checksum = struct.unpack_from("<I", challenge, 4)[0]
    floor_data = challenge[CHALLENGE_HEADER_SIZE : CHALLENGE_HEADER_SIZE + FLOOR_DATA_SIZE]
    computed_checksum = byte_sum(floor_data)

    floors = []
    for floor_id in range(NUM_FLOORS):
        off = CHALLENGE_HEADER_SIZE + floor_id * FLOOR_SIZE
        floor = challenge[off : off + FLOOR_SIZE]
        floors.append(
            {
                "floor": floor_id + 1,
                "trainer_num_1": floor[0],
                "trainer_num_2": floor[1],
            }
        )

    return {
        "valid": (
            1 <= num_trainers <= 8
            and 1 <= num_floors <= 4
            and stored_checksum == computed_checksum
        ),
        "sentinel": f"0x{sentinel:08X}",
        "num_trainers": num_trainers,
        "generation": generation,
        "num_floors": num_floors,
        "stored_checksum": f"0x{stored_checksum:08X}",
        "computed_checksum": f"0x{computed_checksum:08X}",
        "floors": floors,
    }


def reconstruct_first_card_entry(challenge: bytes, floor_id: int) -> tuple[int, bytes] | None:
    """Reconstruct the first scanned card on one floor.

    TryWriteTrainerHill keeps the first card's map, so this entry is complete.
    The second card's own map is discarded and cannot be reconstructed from the
    resulting save sector alone.
    """
    off = CHALLENGE_HEADER_SIZE + floor_id * FLOOR_SIZE
    floor = challenge[off : off + FLOOR_SIZE]
    trainer_num = floor[0]
    if trainer_num == 0:
        return None

    trainer = floor[FLOOR_TRAINER0_OFFSET : FLOOR_TRAINER0_OFFSET + TRAINER_SIZE]
    floor_map = floor[FLOOR_MAP_OFFSET : FLOOR_MAP_OFFSET + FLOOR_MAP_SIZE]

    entry = bytearray()
    entry.append(trainer_num)
    entry += b"\x00\x00\x00"  # alignment before struct TrainerHillTrainer
    entry += trainer
    entry += floor_map
    assert len(entry) == EREADER_ENTRY_BODY_SIZE

    entry += struct.pack("<I", byte_sum(entry))
    assert len(entry) == EREADER_ENTRY_SIZE
    return trainer_num, bytes(entry)


def extract_first_cards(sector: bytes, out_dir: Path) -> list[dict]:
    challenge = sector[4 : 4 + CHALLENGE_SIZE]
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    for floor_id in range(NUM_FLOORS):
        result = reconstruct_first_card_entry(challenge, floor_id)
        if result is None:
            continue
        trainer_num, entry = result
        path = out_dir / f"trainer_{trainer_num:03d}_floor_{floor_id + 1}.bin"
        path.write_bytes(entry)
        written.append(
            {
                "floor": floor_id + 1,
                "trainer_num": trainer_num,
                "path": str(path),
                "size": len(entry),
                "checksum": f"0x{struct.unpack_from('<I', entry, EREADER_ENTRY_BODY_SIZE)[0]:08X}",
            }
        )
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("save", type=Path)
    parser.add_argument(
        "--extract-first-cards",
        type=Path,
        metavar="DIR",
        help="reconstruct complete 0x274 entries for the first scanned card on each floor",
    )
    args = parser.parse_args()

    sector = load_sector(args.save)
    info = parse_challenge(sector)

    if args.extract_first_cards and info.get("valid"):
        info["extracted"] = extract_first_cards(sector, args.extract_first_cards)

    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0 if info.get("valid") else 2


if __name__ == "__main__":
    raise SystemExit(main())

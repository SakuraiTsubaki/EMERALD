#!/usr/bin/env python3
"""Verify EMERALD future-generation capacity against the pinned expansion checkout."""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from reference_pins import load_expansion_pin


def git_head(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def read_macros(path: Path) -> dict[str, str]:
    macros: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\\s*#define\\s+([A-Z0-9_]+)\\s+(.+?)\\s*$", line)
        if match:
            macros[match.group(1)] = match.group(2).split("//", 1)[0].strip()
    return macros


def resolve(name: str, macros: dict[str, str], stack: tuple[str, ...] = ()) -> int:
    if name in stack:
        raise ValueError(f"recursive macro chain: {' -> '.join((*stack, name))}")
    expr = macros.get(name)
    if expr is None:
        raise ValueError(f"missing macro: {name}")
    if re.fullmatch(r"\\d+", expr):
        return int(expr)
    alias = re.fullmatch(r"([A-Z0-9_]+)", expr)
    if alias:
        return resolve(alias.group(1), macros, (*stack, name))
    plus = re.fullmatch(r"([A-Z0-9_]+)\\s*\\+\\s*(\\d+)", expr)
    if plus:
        return resolve(plus.group(1), macros, (*stack, name)) + int(plus.group(2))
    raise ValueError(f"unsupported expression for {name}: {expr!r}")


def literal_int(name: str, macros: dict[str, str]) -> int:
    expr = macros.get(name)
    if expr is None:
        raise SystemExit(f"missing macro: {name}")
    try:
        return int(expr, 0)
    except ValueError as exc:
        raise SystemExit(f"{name} must be a literal integer, got {expr!r}") from exc


def require_regex(text: str, pattern: str, message: str) -> re.Match[str]:
    match = re.search(pattern, text, re.M | re.S)
    if not match:
        raise SystemExit(message)
    return match


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("expansion_root", type=Path)
    args = ap.parse_args()
    root = args.expansion_root.resolve()

    expected_ref = load_expansion_pin()
    head = git_head(root)
    if head != expected_ref:
        raise SystemExit(f"expansion revision mismatch: expected {expected_ref}, got {head}")

    general = root / "include" / "config" / "general.h"
    pokemon_h = root / "include" / "pokemon.h"
    global_h = root / "include" / "global.h"
    save_h = root / "include" / "save.h"
    save_c = root / "src" / "save.c"
    linker = root / "ld_script_modern.ld"
    for path in (general, pokemon_h, global_h, save_h, save_c, linker):
        if not path.is_file():
            raise SystemExit(f"missing required source: {path}")

    macros = read_macros(general)
    expected_values = {
        "GEN_9": 8,
        "GEN_CHAMPIONS": 9,
        "GEN_10": 10,
        "GEN_COUNT": 11,
    }
    for name, expected in expected_values.items():
        actual = resolve(name, macros)
        if actual != expected:
            raise SystemExit(f"{name}: expected {expected}, got {actual} ({macros.get(name)!r})")
    if macros.get("GEN_LATEST") != "GEN_9":
        raise SystemExit(f"GEN_LATEST must remain GEN_9, got {macros.get('GEN_LATEST')!r}")

    pokemon = pokemon_h.read_text(encoding="utf-8")
    species_bits = int(require_regex(
        pokemon,
        r"enum\\s+Species\\s+species:(\\d+);",
        "BoxPokemon species field not found",
    ).group(1))
    item_bits = int(require_regex(
        pokemon,
        r"enum\\s+Item\\s+heldItem:(\\d+);",
        "BoxPokemon held-item field not found",
    ).group(1))
    move_bits = int(require_regex(
        pokemon,
        r"enum\\s+Move\\s+move1:(\\d+);",
        "BoxPokemon move field not found",
    ).group(1))

    if species_bits != 11:
        raise SystemExit(f"species save width changed unexpectedly: {species_bits}")
    if move_bits != 11:
        raise SystemExit(f"move save width changed unexpectedly: {move_bits}")
    if item_bits != 16:
        raise SystemExit(f"held-item save width must be 16 bits, got {item_bits}")
    if re.search(r"\\bunused_02\\s*:\\s*6\\s*;", pokemon):
        raise SystemExit("old six-bit held-item padding still present")

    save_macros = read_macros(save_h)
    sector_data = literal_int("SECTOR_DATA_SIZE", save_macros)
    saveblock3_chunk = literal_int("SAVE_BLOCK_3_CHUNK_SIZE", save_macros)
    footer_size = literal_int("SECTOR_FOOTER_SIZE", save_macros)
    save_slots = literal_int("NUM_SAVE_SLOTS", save_macros)
    sectors_per_slot = literal_int("NUM_SECTORS_PER_SLOT", save_macros)
    sectors_count = literal_int("SECTORS_COUNT", save_macros)
    sector_signature = literal_int("SECTOR_SIGNATURE", save_macros)
    hof_1 = literal_int("SECTOR_ID_HOF_1", save_macros)
    hof_2 = literal_int("SECTOR_ID_HOF_2", save_macros)
    trainer_hill = literal_int("SECTOR_ID_TRAINER_HILL", save_macros)
    recorded_battle = literal_int("SECTOR_ID_RECORDED_BATTLE", save_macros)

    if sector_data != 3968:
        raise SystemExit(f"unexpected sector data size: {sector_data}")
    if saveblock3_chunk != 116:
        raise SystemExit(f"SaveBlock3 chunk must remain 116 bytes, got {saveblock3_chunk}")
    if footer_size != 12:
        raise SystemExit(f"save footer metadata must remain 12 bytes, got {footer_size}")
    if sector_data + saveblock3_chunk + footer_size != 4096:
        raise SystemExit("save sector no longer totals 4096 bytes")
    if save_slots != 2 or sectors_per_slot != 14 or sectors_count != 32:
        raise SystemExit(
            "Emerald Flash layout changed: expected 2 slots, 14 gameplay sectors per slot, 32 sectors total"
        )
    if sector_signature != 0x08012025:
        raise SystemExit(f"unexpected Emerald sector signature: 0x{sector_signature:08X}")
    if (hof_1, hof_2, trainer_hill, recorded_battle) != (28, 29, 30, 31):
        raise SystemExit(
            "special save sectors moved or were repurposed; expected HOF 28-29, Trainer Hill 30, Recorded Battle 31"
        )

    footer_metadata_offset = sector_data + saveblock3_chunk
    if footer_metadata_offset != 0xFF4:
        raise SystemExit(
            f"footer metadata moved: expected 0xFF4, got 0x{footer_metadata_offset:X}"
        )

    save_h_text = save_h.read_text(encoding="utf-8")
    require_regex(
        save_h_text,
        r"struct\\s+SaveSector\\s*\\{.*?"
        r"u8\\s+data\\[SECTOR_DATA_SIZE\\];\\s*"
        r"u8\\s+saveBlock3Chunk\\[SAVE_BLOCK_3_CHUNK_SIZE\\];\\s*"
        r"u16\\s+id;\\s*u16\\s+checksum;\\s*u32\\s+signature;\\s*u32\\s+counter;",
        "SaveSector no longer keeps SaveBlock3 inside the vanilla unused footer area",
    )

    global_text = global_h.read_text(encoding="utf-8")
    require_regex(
        global_text,
        r"struct\\s+SaveBlock3\\s*\\{",
        "SaveBlock3 definition missing",
    )

    save_c_text = save_c.read_text(encoding="utf-8")
    require_regex(
        save_c_text,
        r"STATIC_ASSERT\\s*\\(\\s*sizeof\\(struct\\s+SaveBlock3\\)\\s*<=\\s*"
        r"SAVE_BLOCK_3_CHUNK_SIZE\\s*\\*\\s*NUM_SECTORS_PER_SLOT\\s*,\\s*"
        r"SaveBlock3FreeSpace\\s*\\);",
        "SaveBlock3 capacity guard missing",
    )
    require_regex(
        save_c_text,
        r"CopyToSaveBlock3\\(id,\\s*gReadWriteSector\\);",
        "SaveBlock3 is not restored with checksum-valid gameplay sectors",
    )
    require_regex(
        save_c_text,
        r"CopyFromSaveBlock3\\(sectorId,\\s*gReadWriteSector\\);",
        "SaveBlock3 is not written with gameplay sectors",
    )

    linker_text = linker.read_text(encoding="utf-8")
    require_regex(
        linker_text,
        r"ROM\\s+\\(rx\\)\\s*:\\s*ORIGIN\\s*=\\s*0x8000000\\s*,\\s*LENGTH\\s*=\\s*32M",
        "modern linker is not configured for the 32 MiB GBA ROM address space",
    )

    saveblock3_capacity = saveblock3_chunk * sectors_per_slot
    flash_bytes = sectors_count * 4096

    print("Future-generation capacity verified")
    print("  generation order : GEN_9 < GEN_CHAMPIONS < GEN_10 < GEN_COUNT")
    print("  GEN_LATEST       : GEN_9")
    print(f"  species width    : {species_bits} bits ({(1 << species_bits) - 1} max)")
    print(f"  move width       : {move_bits} bits ({(1 << move_bits) - 1} max)")
    print(f"  held-item width  : {item_bits} bits ({(1 << item_bits) - 1} max)")
    print(f"  save flash       : {sectors_count} x 4096 = {flash_bytes} bytes")
    print(f"  SaveBlock3 space : {sectors_per_slot} x {saveblock3_chunk} = {saveblock3_capacity} bytes per slot")
    print(f"  footer metadata  : unchanged at 0x{footer_metadata_offset:X}")
    print("  special sectors  : HOF 28-29, Trainer Hill 30, Recorded Battle 31")
    print("  linker ROM space : 32 MiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

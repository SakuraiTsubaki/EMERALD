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
        match = re.match(r"^\s*#define\s+([A-Z0-9_]+)\s+(.+?)\s*$", line)
        if match:
            macros[match.group(1)] = match.group(2).split("//", 1)[0].strip()
    return macros


def resolve(name: str, macros: dict[str, str], stack: tuple[str, ...] = ()) -> int:
    if name in stack:
        raise ValueError(f"recursive macro chain: {' -> '.join((*stack, name))}")
    expr = macros.get(name)
    if expr is None:
        raise ValueError(f"missing macro: {name}")
    if re.fullmatch(r"\d+", expr):
        return int(expr)
    alias = re.fullmatch(r"([A-Z0-9_]+)", expr)
    if alias:
        return resolve(alias.group(1), macros, (*stack, name))
    plus = re.fullmatch(r"([A-Z0-9_]+)\s*\+\s*(\d+)", expr)
    if plus:
        return resolve(plus.group(1), macros, (*stack, name)) + int(plus.group(2))
    raise ValueError(f"unsupported expression for {name}: {expr!r}")


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
    save_h = root / "include" / "save.h"
    linker = root / "ld_script_modern.ld"
    for path in (general, pokemon_h, save_h, linker):
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
        r"enum\s+Species\s+species:(\d+);",
        "BoxPokemon species field not found",
    ).group(1))
    item_bits = int(require_regex(
        pokemon,
        r"enum\s+Item\s+heldItem:(\d+);",
        "BoxPokemon held-item field not found",
    ).group(1))
    move_bits = int(require_regex(
        pokemon,
        r"enum\s+Move\s+move1:(\d+);",
        "BoxPokemon move field not found",
    ).group(1))

    if species_bits != 11:
        raise SystemExit(f"species save width changed unexpectedly: {species_bits}")
    if move_bits != 11:
        raise SystemExit(f"move save width changed unexpectedly: {move_bits}")
    if item_bits != 16:
        raise SystemExit(f"held-item save width must be 16 bits, got {item_bits}")
    if re.search(r"\bunused_02\s*:\s*6\s*;", pokemon):
        raise SystemExit("old six-bit held-item padding still present")

    save_macros = read_macros(save_h)
    if int(save_macros.get("SECTOR_DATA_SIZE", "0")) != 3968:
        raise SystemExit("unexpected sector data size")
    if int(save_macros.get("SAVE_BLOCK_3_CHUNK_SIZE", "0")) != 116:
        raise SystemExit("SaveBlock3 chunk must remain 116 bytes")
    if int(save_macros.get("NUM_SECTORS_PER_SLOT", "0")) != 14:
        raise SystemExit("Emerald save slot must remain 14 sectors")

    linker_text = linker.read_text(encoding="utf-8")
    require_regex(
        linker_text,
        r"ROM\s+\(rx\)\s*:\s*ORIGIN\s*=\s*0x8000000\s*,\s*LENGTH\s*=\s*32M",
        "modern linker is not configured for the 32 MiB GBA ROM address space",
    )

    print("Future-generation capacity verified")
    print("  generation order : GEN_9 < GEN_CHAMPIONS < GEN_10 < GEN_COUNT")
    print("  GEN_LATEST       : GEN_9")
    print(f"  species width    : {species_bits} bits ({(1 << species_bits) - 1} max)")
    print(f"  move width       : {move_bits} bits ({(1 << move_bits) - 1} max)")
    print(f"  held-item width  : {item_bits} bits ({(1 << item_bits) - 1} max)")
    print("  SaveBlock3 space : 14 x 116 = 1624 bytes per save slot")
    print("  linker ROM space : 32 MiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

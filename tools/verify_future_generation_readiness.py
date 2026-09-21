#!/usr/bin/env python3
"""Verify EMERALD's reserved Generation 10 capacity against an expansion checkout."""
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
        if not match:
            continue
        value = match.group(2).split("//", 1)[0].strip()
        macros[match.group(1)] = value
    return macros

def resolve(name: str, macros: dict[str, str], stack: tuple[str, ...] = ()) -> int:
    if name in stack:
        raise ValueError(f"recursive macro chain: {' -> '.join((*stack, name))}")
    if name not in macros:
        raise ValueError(f"missing macro: {name}")

    expr = macros[name]
    if re.fullmatch(r"\d+", expr):
        return int(expr)

    alias = re.fullmatch(r"([A-Z0-9_]+)", expr)
    if alias:
        return resolve(alias.group(1), macros, (*stack, name))

    plus = re.fullmatch(r"([A-Z0-9_]+)\s*\+\s*(\d+)", expr)
    if plus:
        return resolve(plus.group(1), macros, (*stack, name)) + int(plus.group(2))

    raise ValueError(f"unsupported generation expression for {name}: {expr!r}")

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
    if not general.is_file():
        raise SystemExit(f"missing expansion generation config: {general}")

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
        raise SystemExit(
            "GEN_LATEST must remain GEN_9 during capacity-only work; "
            f"got {macros.get('GEN_LATEST')!r}"
        )

    if not (
        resolve("GEN_9", macros)
        < resolve("GEN_CHAMPIONS", macros)
        < resolve("GEN_10", macros)
        < resolve("GEN_COUNT", macros)
    ):
        raise SystemExit("generation ordering invariant failed")

    print("Generation 10 capacity scaffold verified")
    print("  GEN_9         =", resolve("GEN_9", macros))
    print("  GEN_CHAMPIONS =", resolve("GEN_CHAMPIONS", macros))
    print("  GEN_10        =", resolve("GEN_10", macros))
    print("  GEN_COUNT     =", resolve("GEN_COUNT", macros))
    print("  GEN_LATEST    =", macros["GEN_LATEST"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

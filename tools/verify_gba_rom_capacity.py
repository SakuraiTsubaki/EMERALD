#!/usr/bin/env python3
"""Verify EMERALD stays within the standard GBA 32 MiB linear ROM window."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

MIB = 1024 * 1024
MAX_LINEAR_ROM_BYTES = 32 * MIB
ROM_ORIGIN = 0x08000000
ROM_END_EXCLUSIVE = ROM_ORIGIN + MAX_LINEAR_ROM_BYTES

def verify_linker(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"ROM\s*\(rx\)\s*:\s*ORIGIN\s*=\s*(0x[0-9A-Fa-f]+)\s*,\s*LENGTH\s*=\s*([0-9]+)([KkMm])",
        text,
    )
    if not match:
        raise SystemExit(f"ROM MEMORY declaration not found in {path}")

    origin = int(match.group(1), 16)
    value = int(match.group(2))
    unit = match.group(3).upper()
    length = value * (1024 if unit == "K" else MIB)

    if origin != ROM_ORIGIN:
        raise SystemExit(f"unexpected ROM origin: 0x{origin:08X}")
    if length != MAX_LINEAR_ROM_BYTES:
        raise SystemExit(
            f"normal profile must expose exactly 32 MiB; got {length / MIB:.2f} MiB"
        )

    print(f"linker ROM window: 0x{origin:08X}-0x{origin + length - 1:08X} ({length // MIB} MiB)")

def verify_rom(path: Path) -> None:
    size = path.stat().st_size
    if size > MAX_LINEAR_ROM_BYTES:
        raise SystemExit(
            f"{path}: {size} bytes exceeds the standard GBA linear ROM limit "
            f"of {MAX_LINEAR_ROM_BYTES} bytes (32 MiB)"
        )
    print(f"ROM size: {size} bytes ({size / MIB:.3f} MiB)")
    print(f"linear capacity remaining: {(MAX_LINEAR_ROM_BYTES - size) / MIB:.3f} MiB")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("linker", type=Path)
    parser.add_argument("--rom", type=Path)
    args = parser.parse_args()

    verify_linker(args.linker)
    if args.rom is not None:
        verify_rom(args.rom)

    print("standard GBA linear ROM ceiling: 32 MiB")
    print(f"address range: 0x{ROM_ORIGIN:08X}-0x{ROM_END_EXCLUSIVE - 1:08X}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

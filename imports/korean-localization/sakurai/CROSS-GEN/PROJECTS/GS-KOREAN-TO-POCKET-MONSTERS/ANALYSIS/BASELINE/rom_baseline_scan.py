#!/usr/bin/env python3
"""Create a reproducible, read-only baseline survey for Game Boy ROMs.

The scanner never writes beside or modifies an input ROM.  It emits only
metadata, hashes, per-bank statistics, and revision-difference ranges.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path


BANK_SIZE = 0x4000
NINTENDO_LOGO = bytes.fromhex(
    "CEED6666CC0D000B03730083000C000D"
    "0008111F8889000EDCCC6EE6DDDDD999"
    "BBBB67636E0EECCCDDDC999FBBB9333E"
)
ROM_SIZE_CODES = {
    **{code: 32768 << code for code in range(0x09)},
    0x52: 72 * BANK_SIZE,
    0x53: 80 * BANK_SIZE,
    0x54: 96 * BANK_SIZE,
}
CART_TYPES = {
    0x00: "ROM ONLY",
    0x01: "MBC1",
    0x02: "MBC1+RAM",
    0x03: "MBC1+RAM+BATTERY",
    0x0F: "MBC3+TIMER+BATTERY",
    0x10: "MBC3+TIMER+RAM+BATTERY",
    0x11: "MBC3",
    0x12: "MBC3+RAM",
    0x13: "MBC3+RAM+BATTERY",
    0x19: "MBC5",
    0x1A: "MBC5+RAM",
    0x1B: "MBC5+RAM+BATTERY",
    0x1C: "MBC5+RUMBLE",
    0x1D: "MBC5+RUMBLE+RAM",
    0x1E: "MBC5+RUMBLE+RAM+BATTERY",
}


@dataclass(frozen=True)
class Identity:
    generation: str
    game: str
    language_region: str
    revision: str

    @property
    def comparison_key(self) -> str:
        return f"{self.generation}|{self.game}|{self.language_region}"


def classify(filename: str) -> Identity:
    n = filename.lower()
    if "midori" in n:
        rev = "REV-A" if "rev-a" in n or "rev a" in n else "REV-0"
        return Identity("GENERATION-I", "GREEN", "JAPAN-JA", rev)
    if "aka" in n:
        rev = "REV-A" if "rev-a" in n or "rev a" in n else "REV-0"
        return Identity("GENERATION-I", "RED", "JAPAN-JA", rev)
    if "ao" in n and "japan" in n:
        return Identity("GENERATION-I", "BLUE", "JAPAN-JA", "REV-0")
    if "pikachu" in n:
        match = re.search(r"rev[ -]([0-9a-z]+)", n)
        rev = f"REV-{match.group(1).upper()}" if match else "REV-0"
        return Identity("GENERATION-I", "PIKACHU", "JAPAN-JA", rev)
    if "pokemon-red" in n or "pokemon - red" in n:
        return Identity("GENERATION-I", "RED", "USA-EUROPE-EN", "REV-0")
    if "pokemon-blue" in n or "pokemon - blue" in n:
        return Identity("GENERATION-I", "BLUE", "USA-EUROPE-EN", "REV-0")
    if "pokemon-yellow" in n or "pokemon - yellow" in n:
        return Identity("GENERATION-I", "YELLOW", "USA-EUROPE-EN", "REV-0")
    if "kin-" in n or "kin-japan" in n or "kin (japan" in n:
        rev = "REV-A" if "rev-a" in n or "rev a" in n else "REV-0"
        return Identity("GENERATION-II", "GOLD", "JAPAN-JA", rev)
    if "gin-" in n or "gin-japan" in n or "gin (japan" in n:
        rev = "REV-A" if "rev-a" in n or "rev a" in n else "REV-0"
        return Identity("GENERATION-II", "SILVER", "JAPAN-JA", rev)
    if "eun" in n and "korea" in n:
        return Identity("GENERATION-II", "SILVER", "KOREA-KO", "REV-0")
    if "geum" in n:
        return Identity("GENERATION-II", "GOLD", "KOREA-KO", "REV-0")
    if "pokemon-gold" in n or "pokemon - gold" in n:
        return Identity("GENERATION-II", "GOLD", "USA-EUROPE-EN", "REV-0")
    if "pokemon-silver" in n or "pokemon - silver" in n:
        return Identity("GENERATION-II", "SILVER", "USA-EUROPE-EN", "REV-0")
    if "crystal" in n and "japan" in n:
        rev = "REV-A" if "rev-a" in n or "rev a" in n else "REV-0"
        return Identity("GENERATION-II", "CRYSTAL", "JAPAN-JA", rev)
    if "crystal" in n:
        rev = "REV-A" if "rev-a" in n or "rev a" in n else "REV-0"
        return Identity("GENERATION-II", "CRYSTAL", "USA-EUROPE-EN", rev)
    return Identity("UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN")


def sha(data: bytes, algorithm: str) -> str:
    return hashlib.new(algorithm, data).hexdigest()


def header_checksum(data: bytes) -> int:
    value = 0
    for byte in data[0x134:0x14D]:
        value = (value - byte - 1) & 0xFF
    return value


def global_checksum(data: bytes) -> int:
    return (sum(data[:0x14E]) + sum(data[0x150:])) & 0xFFFF


def text_ascii(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("ascii", "replace").rstrip()


def entropy(data: bytes) -> float:
    counts = Counter(data)
    total = len(data)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def longest_uniform_run(data: bytes) -> tuple[int, int, int]:
    best_byte = data[0]
    best_start = 0
    best_len = 1
    start = 0
    for i in range(1, len(data) + 1):
        if i == len(data) or data[i] != data[start]:
            length = i - start
            if length > best_len:
                best_byte, best_start, best_len = data[start], start, length
            start = i
    return best_byte, best_start, best_len


def differing_ranges(a: bytes, b: bytes) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start: int | None = None
    limit = max(len(a), len(b))
    for i in range(limit):
        differs = i >= len(a) or i >= len(b) or a[i] != b[i]
        if differs and start is None:
            start = i
        elif not differs and start is not None:
            ranges.append((start, i - 1))
            start = None
    if start is not None:
        ranges.append((start, limit - 1))
    return ranges


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def scan(input_dir: Path, output_dir: Path) -> None:
    paths = sorted(p for p in input_dir.rglob("*") if p.suffix.lower() in {".gb", ".gbc"})
    if not paths:
        raise SystemExit(f"No .gb/.gbc files found under {input_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict] = []
    banks: list[dict] = []
    roms: dict[str, bytes] = {}
    identities: dict[str, Identity] = {}

    for path in paths:
        data = path.read_bytes()
        if len(data) < 0x150:
            raise ValueError(f"ROM too small: {path}")
        ident = classify(path.name)
        roms[path.name] = data
        identities[path.name] = ident
        declared = ROM_SIZE_CODES.get(data[0x148])
        stored_global = int.from_bytes(data[0x14E:0x150], "big")
        row = {
            "filename": path.name,
            **asdict(ident),
            "size_bytes": len(data),
            "bank_count": math.ceil(len(data) / BANK_SIZE),
            "sha1": sha(data, "sha1"),
            "sha256": sha(data, "sha256"),
            "header_title": text_ascii(data[0x134:0x143]),
            "cgb_flag_hex": f"0x{data[0x143]:02X}",
            "sgb_flag_hex": f"0x{data[0x146]:02X}",
            "cartridge_type_hex": f"0x{data[0x147]:02X}",
            "cartridge_type": CART_TYPES.get(data[0x147], "UNKNOWN"),
            "rom_size_code_hex": f"0x{data[0x148]:02X}",
            "declared_size_bytes": declared if declared is not None else "UNKNOWN",
            "size_matches_header": declared == len(data),
            "destination_code_hex": f"0x{data[0x14A]:02X}",
            "mask_rom_version": data[0x14C],
            "nintendo_logo_valid": data[0x104:0x134] == NINTENDO_LOGO,
            "header_checksum_stored_hex": f"0x{data[0x14D]:02X}",
            "header_checksum_calculated_hex": f"0x{header_checksum(data):02X}",
            "header_checksum_valid": data[0x14D] == header_checksum(data),
            "global_checksum_stored_hex": f"0x{stored_global:04X}",
            "global_checksum_calculated_hex": f"0x{global_checksum(data):04X}",
            "global_checksum_valid": stored_global == global_checksum(data),
        }
        manifest.append(row)

        for bank_no, offset in enumerate(range(0, len(data), BANK_SIZE)):
            bank = data[offset:offset + BANK_SIZE]
            run_byte, run_start, run_len = longest_uniform_run(bank)
            banks.append({
                "filename": path.name,
                **asdict(ident),
                "bank_hex": f"0x{bank_no:02X}",
                "bank_decimal": bank_no,
                "file_start_hex": f"0x{offset:06X}",
                "file_end_hex": f"0x{offset + len(bank) - 1:06X}",
                "size_bytes": len(bank),
                "sha1": sha(bank, "sha1"),
                "entropy_bits_per_byte": f"{entropy(bank):.6f}",
                "zero_bytes": bank.count(0x00),
                "ff_bytes": bank.count(0xFF),
                "distinct_byte_values": len(set(bank)),
                "longest_uniform_byte_hex": f"0x{run_byte:02X}",
                "longest_uniform_run_start_hex": f"0x{offset + run_start:06X}",
                "longest_uniform_run_length": run_len,
            })

    diffs: list[dict] = []
    revision_bank_diffs: list[dict] = []
    by_key: dict[str, list[str]] = {}
    for filename, ident in identities.items():
        by_key.setdefault(ident.comparison_key, []).append(filename)
    for key, filenames in sorted(by_key.items()):
        for left, right in combinations(sorted(filenames), 2):
            a, b = roms[left], roms[right]
            ranges = differing_ranges(a, b)
            differing_bytes = sum(end - start + 1 for start, end in ranges)
            differing_banks = sorted({start // BANK_SIZE for start, end in ranges} |
                                     {end // BANK_SIZE for start, end in ranges})
            comparison_id = hashlib.sha1(
                f"{key}\0{left}\0{right}".encode("utf-8")
            ).hexdigest()[:12]
            diffs.append({
                "comparison_id": comparison_id,
                "comparison_key": key,
                "left_filename": left,
                "right_filename": right,
                "left_revision": identities[left].revision,
                "right_revision": identities[right].revision,
                "left_size_bytes": len(a),
                "right_size_bytes": len(b),
                "identical": a == b,
                "differing_byte_count": differing_bytes,
                "difference_range_count": len(ranges),
                "differing_bank_count": len(differing_banks),
                "differing_banks_hex": " ".join(f"0x{x:02X}" for x in differing_banks),
            })
            for bank_no in differing_banks:
                bank_start = bank_no * BANK_SIZE
                left_bank = a[bank_start:bank_start + BANK_SIZE]
                right_bank = b[bank_start:bank_start + BANK_SIZE]
                bank_ranges = differing_ranges(left_bank, right_bank)
                bank_diff_bytes = sum(end - start + 1 for start, end in bank_ranges)
                revision_bank_diffs.append({
                    "comparison_id": comparison_id,
                    "comparison_key": key,
                    "bank_hex": f"0x{bank_no:02X}",
                    "bank_decimal": bank_no,
                    "left_bank_sha1": sha(left_bank, "sha1") if left_bank else "MISSING",
                    "right_bank_sha1": sha(right_bank, "sha1") if right_bank else "MISSING",
                    "differing_byte_count": bank_diff_bytes,
                    "difference_range_count": len(bank_ranges),
                    "first_difference_file_offset_hex": (
                        f"0x{bank_start + bank_ranges[0][0]:06X}" if bank_ranges else ""
                    ),
                    "last_difference_file_offset_hex": (
                        f"0x{bank_start + bank_ranges[-1][1]:06X}" if bank_ranges else ""
                    ),
                })

    write_csv(output_dir / "rom_manifest.csv", manifest)
    write_csv(output_dir / "bank_inventory.csv", banks)
    write_csv(output_dir / "revision_diffs.csv", diffs)
    write_csv(output_dir / "revision_bank_diffs.csv", revision_bank_diffs)
    (output_dir / "rom_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "bank_inventory.json").write_text(
        json.dumps(banks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "revision_diffs.json").write_text(
        json.dumps(diffs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "revision_bank_diffs.json").write_text(
        json.dumps(revision_bank_diffs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    valid_headers = sum(bool(row["header_checksum_valid"]) for row in manifest)
    valid_globals = sum(bool(row["global_checksum_valid"]) for row in manifest)
    summary = [
        "# ROM baseline survey",
        "",
        "This survey was generated directly from the supplied read-only ROM files.",
        "No ROM bytes or extracted copyrighted payloads are included.",
        "",
        "## Scope",
        "",
        f"- ROM files scanned: {len(manifest)}",
        f"- 16 KiB banks scanned: {len(banks)}",
        f"- Valid header checksums: {valid_headers}/{len(manifest)}",
        f"- Valid global checksums: {valid_globals}/{len(manifest)}",
        f"- Same-title revision comparisons: {len(diffs)}",
        "",
        "## Outputs",
        "",
        "- `rom_manifest.csv/json`: identities, cryptographic hashes, cartridge header fields, and checksum validation",
        "- `bank_inventory.csv/json`: one record per 16 KiB bank with hashes and structural statistics",
        "- `revision_diffs.csv/json`: compact summaries of same-title revision comparisons",
        "- `revision_bank_diffs.csv/json`: per-bank changed-byte and changed-range counts",
        "",
        "## Reproduction",
        "",
        "```bash",
        "python3 rom_baseline_scan.py /path/to/project_sources /path/to/output",
        "```",
        "",
        "The filenames are classification inputs; SHA-1/SHA-256 values are the durable identities.",
    ]
    (output_dir / "README.md").write_text("\n".join(summary) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    scan(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()

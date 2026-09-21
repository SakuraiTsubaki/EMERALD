#!/usr/bin/env python3
"""Inventory a local PKHeX checkout and emit EMERALD reference manifests.

This tool does not copy PKHeX source or artwork. It records provenance and classifies
files so downstream extractors can translate facts into EMERALD-owned CSV/JSON/YAML.
The expected source revision is read from manifests/pkhex-source-pin.yml.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
from pathlib import Path

from reference_pins import load_pkhex_pin

PIN = load_pkhex_pin()

def git_rev(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()

def bucket(p: str) -> str:
    rules = [
        ("PKHeX.Core/Resources/", "core_resources"),
        ("PKHeX.Core/Legality/", "core_legality"),
        ("PKHeX.Core/Saves/", "core_saves"),
        ("PKHeX.Core/PKM/", "core_pkm"),
        ("PKHeX.Core/Editing/", "core_editing"),
        ("PKHeX.Core/Items/", "core_items"),
        ("PKHeX.Core/PersonalInfo/", "core_personal"),
        ("PKHeX.Core/Game/", "core_game"),
        ("PKHeX.Core/MysteryGifts/", "core_mystery_gifts"),
        ("PKHeX.Core/Ribbons/", "core_ribbons"),
        ("PKHeX.Core/Moves/", "core_moves"),
        ("PKHeX.Core/", "core_other"),
        ("PKHeX.Drawing.PokeSprite/", "drawing_pokesprite"),
        ("PKHeX.Drawing.Misc/", "drawing_misc"),
        ("PKHeX.WinForms/", "winforms_ui"),
        ("Tests/", "tests"),
    ]
    for prefix, name in rules:
        if p.startswith(prefix):
            return name
    return "repo_meta"

def policy(bucket_name: str) -> str:
    if bucket_name.startswith("core_"):
        return "extract_semantics_and_metadata"
    if bucket_name == "tests":
        return "reference_for_validation"
    if bucket_name.startswith("drawing_"):
        return "reference_only_do_not_copy_assets"
    if bucket_name == "winforms_ui":
        return "reference_only_ui_not_target_runtime"
    return "reference_only"

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkhex", type=Path)
    ap.add_argument("--out", type=Path, default=Path("manifests/pkhex-local-inventory.csv"))
    ap.add_argument("--allow-different-revision", action="store_true")
    args = ap.parse_args()

    rev = git_rev(args.pkhex)
    if rev != PIN and not args.allow_different_revision:
        raise SystemExit(f"PKHeX revision mismatch: expected {PIN}, got {rev}")

    rows = []
    for file in sorted(x for x in args.pkhex.rglob("*") if x.is_file() and ".git" not in x.parts):
        rel = file.relative_to(args.pkhex).as_posix()
        sha256 = hashlib.sha256(file.read_bytes()).hexdigest()
        bucket_name = bucket(rel)
        rows.append((rel, file.stat().st_size, sha256, bucket_name, policy(bucket_name)))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(["path", "size", "sha256", "bucket", "policy"])
        writer.writerows(rows)

    print(f"{len(rows)} files -> {args.out}")

if __name__ == "__main__":
    main()

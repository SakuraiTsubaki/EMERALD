#!/usr/bin/env python3
"""Inventory a local PKHeX checkout and emit EMERALD reference manifests.

This tool does not copy PKHeX source or artwork. It records provenance and classifies
files so downstream extractors can translate facts into EMERALD-owned CSV/JSON/YAML.
Expected source revision: 8ad201e80244f630ab5a46922ab72fb79c5ad4f4
"""
from __future__ import annotations
import argparse, csv, hashlib, subprocess
from pathlib import Path

PIN = "8ad201e80244f630ab5a46922ab72fb79c5ad4f4"

def git_rev(root: Path) -> str:
    return subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"], text=True).strip()

def bucket(p: str) -> str:
    rules = [
        ("PKHeX.Core/Resources/","core_resources"),
        ("PKHeX.Core/Legality/","core_legality"),
        ("PKHeX.Core/Saves/","core_saves"),
        ("PKHeX.Core/PKM/","core_pkm"),
        ("PKHeX.Core/Editing/","core_editing"),
        ("PKHeX.Core/Items/","core_items"),
        ("PKHeX.Core/PersonalInfo/","core_personal"),
        ("PKHeX.Core/Game/","core_game"),
        ("PKHeX.Core/MysteryGifts/","core_mystery_gifts"),
        ("PKHeX.Core/Ribbons/","core_ribbons"),
        ("PKHeX.Core/Moves/","core_moves"),
        ("PKHeX.Core/","core_other"),
        ("PKHeX.Drawing.PokeSprite/","drawing_pokesprite"),
        ("PKHeX.Drawing.Misc/","drawing_misc"),
        ("PKHeX.WinForms/","winforms_ui"),
        ("Tests/","tests"),
    ]
    for prefix, name in rules:
        if p.startswith(prefix): return name
    return "repo_meta"

def policy(b: str) -> str:
    if b.startswith("core_"): return "extract_semantics_and_metadata"
    if b == "tests": return "reference_for_validation"
    if b.startswith("drawing_"): return "reference_only_do_not_copy_assets"
    if b == "winforms_ui": return "reference_only_ui_not_target_runtime"
    return "reference_only"

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("pkhex", type=Path)
    ap.add_argument("--out", type=Path, default=Path("manifests/pkhex-local-inventory.csv"))
    ap.add_argument("--allow-different-revision", action="store_true")
    a=ap.parse_args()
    rev=git_rev(a.pkhex)
    if rev != PIN and not a.allow_different_revision:
        raise SystemExit(f"PKHeX revision mismatch: expected {PIN}, got {rev}")
    rows=[]
    for f in sorted(x for x in a.pkhex.rglob("*") if x.is_file() and ".git" not in x.parts):
        rel=f.relative_to(a.pkhex).as_posix()
        h=hashlib.sha256(f.read_bytes()).hexdigest()
        b=bucket(rel)
        rows.append((rel,f.stat().st_size,h,b,policy(b)))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", newline="", encoding="utf-8") as fp:
        w=csv.writer(fp); w.writerow(["path","size","sha256","bucket","policy"]); w.writerows(rows)
    print(f"{len(rows)} files -> {a.out}")

if __name__ == "__main__":
    main()

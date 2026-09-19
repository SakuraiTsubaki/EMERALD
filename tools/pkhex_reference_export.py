#!/usr/bin/env python3
"""Generate EMERALD reference manifests from a pinned local PKHeX checkout.

This tool does not copy PKHeX runtime source into the Emerald engine. It reads
reference data and source metadata and emits normalized CSV/YAML inputs.

Usage:
    python tools/pkhex_reference_export.py /path/to/PKHeX --out manifests/pkhex

Pinned upstream:
    kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
from pathlib import Path

PIN = "8ad201e80244f630ab5a46922ab72fb79c5ad4f4"
CORE = Path("PKHeX.Core")

def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()

def read_lines(root: Path, rel: str) -> list[str]:
    return (root / rel).read_text(encoding="utf-8-sig").replace("\r", "").split("\n")

def write_csv(path: Path, header: list[str], rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def export_names(root: Path, out: Path) -> None:
    specs = {
        "species": "PKHeX.Core/Resources/text/other/{lang}/text_Species_{lang}.txt",
        "moves": "PKHeX.Core/Resources/text/other/{lang}/text_Moves_{lang}.txt",
        "abilities": "PKHeX.Core/Resources/text/other/{lang}/text_Abilities_{lang}.txt",
        "items": "PKHeX.Core/Resources/text/items/text_Items_{lang}.txt",
    }
    for domain, template in specs.items():
        data = {lang: read_lines(root, template.format(lang=lang)) for lang in ("ja", "ko", "en")}
        count = max(map(len, data.values()))
        rows = []
        for i in range(count):
            vals = [data[x][i] if i < len(data[x]) else "" for x in ("ja", "ko", "en")]
            if i == count - 1 and not any(vals):
                continue
            rows.append([i, *vals, "kwsch/PKHeX", PIN,
                         template.format(lang="ja"), template.format(lang="ko"), template.format(lang="en")])
        write_csv(out / f"{domain}.csv",
                  ["id","name_ja","name_ko","name_en","source_repo","source_commit",
                   "source_path_ja","source_path_ko","source_path_en"], rows)

def classify(path: str) -> tuple[str, str]:
    if path.startswith("PKHeX.Core/PersonalInfo/") or "Resources/byte/personal/" in path:
        return "personal", "extract_normalize"
    if re.search(r"FormConverter|FormInfo|FormChange|FormArgument", path):
        return "forms", "extract_rules"
    if path.startswith("PKHeX.Core/Items/") or re.search(r"ItemConverter|ItemVerifier|ItemRestrictions", path) or "Resources/text/items/" in path:
        return "items", "extract_normalize"
    if re.search(r"/Moves?/|Move\.cs$|Moves_|lvlmove_|eggmove_", path):
        return "moves", "extract_normalize"
    if "Ability" in path or "Abilities_" in path:
        return "abilities", "extract_normalize"
    if "Evolution" in path:
        return "evolutions", "extract_normalize"
    if "Legality/Encounters" in path or "Encounter" in path:
        return "encounters", "extract_normalize"
    if path.startswith("PKHeX.Core/Saves/") or "SaveFile" in path:
        return "save_structures", "document_extract"
    if path.startswith("PKHeX.Core/Legality/"):
        return "legality", "behavior_reference"
    if "/PKM/Util/Conversion/" in path or "Transfer" in path:
        return "conversions", "behavior_reference"
    if path.startswith("PKHeX.Core/MysteryGifts/"):
        return "mystery_gifts", "extract_normalize"
    if re.search(r"Ribbon|Mark", path):
        return "ribbons_marks", "extract_normalize"
    if re.search(r"Location|MetLocation", path):
        return "locations", "extract_normalize"
    if path.startswith("PKHeX.Core/Resources/text/"):
        return "localization", "cross_check"
    if path.startswith("PKHeX.Core/PKM/"):
        return "pkm_formats", "document_extract"
    if path.startswith("PKHeX.Core/Game/"):
        return "game_metadata", "extract_normalize"
    if path.startswith("PKHeX.Core/Resources/byte/"):
        return "binary_resources", "extract_with_decoder"
    return "other_core", "reference_only"

def export_inventory(root: Path, out: Path) -> None:
    rows = []
    base = root / CORE
    for p in sorted(x for x in base.rglob("*") if x.is_file()):
        rel = p.relative_to(root).as_posix()
        domain, mode = classify(rel)
        rows.append([rel, p.stat().st_size, domain, mode, PIN])
    write_csv(out / "core-file-inventory.csv",
              ["path","bytes","domain","ingestion_mode","source_commit"], rows)

def export_personal_sources(root: Path, out: Path) -> None:
    src = (root / "PKHeX.Core/PersonalInfo/PersonalTable.cs").read_text(encoding="utf-8")
    rx = re.compile(r'public static readonly\s+([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+)\s*=\s*new\(GetTable\("([^"]+)"\)')
    rows = []
    for cls, field, key in rx.findall(src):
        rows.append([field, cls, key, f"PKHeX.Core/Resources/byte/personal/personal_{key}",
                     "PKHeX.Core/PersonalInfo/PersonalTable.cs", PIN])
    write_csv(out / "personal-sources.csv",
              ["field","parser_class","resource_key","resource_path","source_path","source_commit"], rows)

def parse_numeric_array(src: str, name: str, nan: int | None = None) -> list[int]:
    m = re.search(rf"{re.escape(name)}\s*=>\s*\[(.*?)\];", src, re.S)
    if not m:
        return []
    body = re.sub(r"//.*$", "", m.group(1), flags=re.M)
    result = []
    for tok in filter(None, (x.strip() for x in body.split(","))):
        if tok == "NaN":
            if nan is None:
                raise ValueError(f"{name}: NaN token with no replacement")
            result.append(nan)
        else:
            result.append(int(tok.lstrip("+")))
    return result

def export_item_conversion(root: Path, out: Path) -> None:
    rel = "PKHeX.Core/PKM/Util/Conversion/ItemConverter.cs"
    src = (root / rel).read_text(encoding="utf-8")
    rows = []
    for gen, name in ((2, "Item2to4"), (3, "Item3to4")):
        arr = parse_numeric_array(src, name, nan=128)
        for i, dst in enumerate(arr):
            rows.append([gen, i, 4, dst, "yes" if dst != 128 and i > 0 else "no", rel, PIN])
    write_csv(out / "item-conversions.csv",
              ["source_generation","source_item_id","destination_generation","destination_item_id",
               "transferable","source_path","source_commit"], rows)

    arr = parse_numeric_array(src, "RemapTechnicalMachineItemName9a")
    write_csv(out / "gen9a-tm-remap.csv",
              ["old_tm_index","display_tm_index_gen9a","delta","source_commit"],
              ([i, i + d, d, PIN] for i, d in enumerate(arr)))

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkhex_root", type=Path)
    ap.add_argument("--out", type=Path, default=Path("manifests/pkhex"))
    ap.add_argument("--allow-unpinned", action="store_true")
    args = ap.parse_args()

    head = git_head(args.pkhex_root)
    if head != PIN and not args.allow_unpinned:
        raise SystemExit(f"PKHeX commit mismatch: expected {PIN}, got {head}")

    export_names(args.pkhex_root, args.out)
    export_inventory(args.pkhex_root, args.out)
    export_personal_sources(args.pkhex_root, args.out)
    export_item_conversion(args.pkhex_root, args.out)
    print(f"Exported PKHeX reference manifests from {head}")

if __name__ == "__main__":
    main()

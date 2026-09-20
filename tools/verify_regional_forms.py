#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "manifests" / "regional-forms" / "regional_forms_master.json"

TEXT_SUFFIXES = {".c", ".h", ".inc", ".s", ".json", ".txt", ".md"}


def load_text_corpus(source_root: Path) -> str:
    chunks = []
    roots = [
        source_root / "include",
        source_root / "src",
        source_root / "graphics" / "pokemon",
    ]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    return "\n".join(chunks)


def macro_value(text: str, name: str) -> str | None:
    m = re.search(rf"^\s*#define\s+{re.escape(name)}\s+([^\s/]+)", text, re.M)
    return m.group(1) if m else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path, help="pokeemerald-expansion working tree")
    args = ap.parse_args()
    source = args.source.resolve()

    if not MASTER.is_file():
        print(f"missing master: {MASTER}", file=sys.stderr)
        return 2

    data = json.loads(MASTER.read_text(encoding="utf-8"))
    forms = data["regionalForms"]
    evolutions = data["regionalEvolutions"]

    errors: list[str] = []

    if len(forms) != 58:
        errors.append(f"regionalForms count: expected 58, got {len(forms)}")
    if len(evolutions) != 11:
        errors.append(f"regionalEvolutions parameter rows: expected 11, got {len(evolutions)}")
    if len(forms) + len(evolutions) != 69:
        errors.append("master row total is not 69")

    cfg_path = source / "include" / "config" / "species_enabled.h"
    if not cfg_path.is_file():
        errors.append(f"missing expansion config: {cfg_path}")
        cfg = ""
    else:
        cfg = cfg_path.read_text(encoding="utf-8", errors="ignore")

    expected_macros = {
        "P_REGIONAL_FORMS": "TRUE",
        "P_ALOLAN_FORMS": "P_REGIONAL_FORMS",
        "P_GALARIAN_FORMS": "P_REGIONAL_FORMS",
        "P_HISUIAN_FORMS": "P_REGIONAL_FORMS",
        "P_PALDEAN_FORMS": "P_REGIONAL_FORMS",
        "P_CROSS_GENERATION_EVOS": "TRUE",
        "P_NEW_EVOS_IN_REGIONAL_DEX": "TRUE",
    }
    for name, expected in expected_macros.items():
        got = macro_value(cfg, name)
        if got != expected:
            errors.append(f"{name}: expected {expected}, got {got}")

    corpus = load_text_corpus(source)

    symbol_fields = (
        "key",
        "levelUpLearnset",
        "teachableLearnset",
        "eggMoveLearnset",
        "frontPic",
        "backPic",
        "palette",
        "shinyPalette",
        "iconSprite",
    )

    for entry in forms + evolutions:
        label = entry["key"]
        for field in symbol_fields:
            symbol = entry.get(field)
            if not symbol:
                continue
            if symbol not in corpus:
                errors.append(f"{label}: missing {field} symbol {symbol}")

        stats = [
            entry["hp"], entry["attack"], entry["defense"],
            entry["spAttack"], entry["spDefense"], entry["speed"],
        ]
        if sum(stats) != entry["bst"]:
            errors.append(f"{label}: BST mismatch ({sum(stats)} != {entry['bst']})")

    nested = data.get("nestedBattleForms", [])
    for entry in nested:
        if entry["key"] not in corpus:
            errors.append(f"nested battle form missing: {entry['key']}")

    if errors:
        print("regional-form verification FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("regional-form verification OK")
    print(f"- regional form rows: {len(forms)}")
    print(f"- regional evolution parameter rows: {len(evolutions)}")
    print(f"- total master rows: {len(forms) + len(evolutions)}")
    print(f"- nested battle forms checked: {len(nested)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Extract PKHeX PersonalInfo binary resources into normalized CSV.

This is an independent reader for the pinned PKHeX resource layout. It does not
import or execute PKHeX code. The source checkout is used as a reference/data input.

Pinned reference used when this tool was authored:
  kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

PINNED_COMMIT = "8ad201e80244f630ab5a46922ab72fb79c5ad4f4"

@dataclass(frozen=True)
class Schema:
    size: int
    max_species: int
    hp: int
    atk: int
    deff: int
    spe: int
    spa: int
    spd: int
    type1: int
    type2: int
    gender: Optional[int]
    growth: int
    ability1: Optional[int] = None
    ability2: Optional[int] = None
    abilityh: Optional[int] = None
    ability_width: int = 1
    form_index: Optional[int] = None
    form_count: Optional[int] = None

SCHEMAS = {
    "g1": Schema(0x1C, 151, 0x01,0x02,0x03,0x04,0x05,0x05,0x06,0x07,None,0x13),
    "g2": Schema(0x20, 251, 0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x0D,0x16),
    "g3": Schema(0x1C, 386, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x10,0x13,0x16,0x17),
    "g4": Schema(0x2C, 493, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x10,0x13,0x16,0x17,form_index=0x2A,form_count=0x29),
    "g5bw": Schema(0x3C, 649, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x12,0x15,0x18,0x19,0x1A,1,0x1C,0x20),
    "g5b2w2": Schema(0x4C, 649, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x12,0x15,0x18,0x19,0x1A,1,0x1C,0x20),
    "g6xy": Schema(0x40, 721, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x12,0x15,0x18,0x19,0x1A,1,0x1C,0x20),
    "g6ao": Schema(0x50, 721, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x12,0x15,0x18,0x19,0x1A,1,0x1C,0x20),
    "g7": Schema(0x54, 807, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x12,0x15,0x18,0x19,0x1A,1,0x1C,0x20),
    "g7gg": Schema(0x54, 809, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x12,0x15,0x18,0x19,0x1A,1,0x1C,0x20),
    "g8swsh": Schema(0xB0, 898, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x12,0x15,0x18,0x1A,0x1C,2,0x1E,0x20),
    "g8bdsp": Schema(0x44, 493, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x12,0x15,0x18,0x1A,0x1C,2,0x1E,0x20),
    "g8la": Schema(0xB0, 905, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x12,0x15,0x18,0x1A,0x1C,2,0x1E,0x20),
    "g9sv": Schema(0x50, 1025, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x0C,0x0F,0x12,0x14,0x16,2,0x18,0x1A),
    "g9za": Schema(0x50, 1000, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x0C,0x0F,0x12,0x14,0x16,2,0x18,0x1A),
}

TABLES = {
    "rb": ("personal_rb", "g1"),
    "y": ("personal_y", "g1"),
    "gs": ("personal_gs", "g2"),
    "c": ("personal_c", "g2"),
    "rs": ("personal_rs", "g3"),
    "e": ("personal_e", "g3"),
    "fr": ("personal_fr", "g3"),
    "lg": ("personal_lg", "g3"),
    "dp": ("personal_dp", "g4"),
    "pt": ("personal_pt", "g4"),
    "hgss": ("personal_hgss", "g4"),
    "bw": ("personal_bw", "g5bw"),
    "b2w2": ("personal_b2w2", "g5b2w2"),
    "xy": ("personal_xy", "g6xy"),
    "ao": ("personal_ao", "g6ao"),
    # SM uses the same record layout as USUM but a lower species ceiling.
    "sm": ("personal_sm", "g7"),
    "uu": ("personal_uu", "g7"),
    "gg": ("personal_gg", "g7gg"),
    "swsh": ("personal_swsh", "g8swsh"),
    "bdsp": ("personal_bdsp", "g8bdsp"),
    "la": ("personal_la", "g8la"),
    "sv": ("personal_sv", "g9sv"),
    "za": ("personal_za", "g9za"),
}

# SM ends at Marshadow (802), while the shared g7 schema ceiling covers USUM (807).
MAX_SPECIES_OVERRIDE = {"sm": 802}

def u16(data: bytes, off: int) -> int:
    return data[off] | (data[off + 1] << 8)

def read_int(data: bytes, off: Optional[int], width: int = 1) -> Optional[int]:
    if off is None:
        return None
    return data[off] if width == 1 else u16(data, off)

def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8-sig").splitlines()

def name_at(values: list[str], index: Optional[int]) -> str:
    if index is None or index < 0 or index >= len(values):
        return ""
    return values[index]

def language_tables(root: Path, lang: str) -> dict[str, list[str]]:
    base = root / "PKHeX.Core" / "Resources" / "text" / "other" / lang
    return {
        "species": read_lines(base / f"text_Species_{lang}.txt"),
        "types": read_lines(base / f"text_Types_{lang}.txt"),
        "abilities": read_lines(base / f"text_Abilities_{lang}.txt"),
    }

def form_map(entries: list[bytes], schema: Schema, max_species: int) -> dict[int, tuple[int, int]]:
    result: dict[int, tuple[int, int]] = {}
    if schema.form_index is None or schema.form_count is None:
        return result
    upper = min(max_species, len(entries) - 1)
    for species in range(1, upper + 1):
        base = entries[species]
        count = base[schema.form_count]
        first = u16(base, schema.form_index)
        if count <= 1 or first <= 0:
            continue
        for form in range(1, count):
            table_index = first + form - 1
            if 0 <= table_index < len(entries):
                result.setdefault(table_index, (species, form))
    return result

def extract_table(root: Path, game: str, langs: dict[str, dict[str, list[str]]]) -> list[dict[str, object]]:
    filename, schema_name = TABLES[game]
    schema = SCHEMAS[schema_name]
    max_species = MAX_SPECIES_OVERRIDE.get(game, schema.max_species)
    path = root / "PKHeX.Core" / "Resources" / "byte" / "personal" / filename
    raw = path.read_bytes()
    if len(raw) % schema.size:
        raise ValueError(f"{game}: {path} length {len(raw)} is not divisible by 0x{schema.size:X}")
    entries = [raw[i:i+schema.size] for i in range(0, len(raw), schema.size)]
    fmap = form_map(entries, schema, max_species)

    rows: list[dict[str, object]] = []
    for index, data in enumerate(entries):
        if index <= max_species:
            species, form, mapping = index, 0, "base_species"
        elif index in fmap:
            species, form = fmap[index]
            mapping = "form_stats_index"
        else:
            species, form, mapping = None, None, "unmapped_table_entry"

        a1 = read_int(data, schema.ability1, schema.ability_width)
        a2 = read_int(data, schema.ability2, schema.ability_width)
        ah = read_int(data, schema.abilityh, schema.ability_width)
        t1, t2 = data[schema.type1], data[schema.type2]

        row: dict[str, object] = {
            "game": game,
            "table_file": filename,
            "table_index": index,
            "entry_size": schema.size,
            "species_id": "" if species is None else species,
            "form": "" if form is None else form,
            "mapping": mapping,
            "hp": data[schema.hp],
            "atk": data[schema.atk],
            "def": data[schema.deff],
            "spe": data[schema.spe],
            "spa": data[schema.spa],
            "spd": data[schema.spd],
            "type1_id": t1,
            "type2_id": t2,
            "gender_ratio": "" if schema.gender is None else data[schema.gender],
            "growth_rate": data[schema.growth],
            "ability1_id": "" if a1 is None else a1,
            "ability2_id": "" if a2 is None else a2,
            "ability_hidden_id": "" if ah is None else ah,
            "form_stats_index": "" if schema.form_index is None else u16(data, schema.form_index),
            "form_count": "" if schema.form_count is None else data[schema.form_count],
            "source_commit": PINNED_COMMIT,
        }
        for lang in ("ja", "ko", "en"):
            tbl = langs[lang]
            row[f"species_{lang}"] = name_at(tbl["species"], species)
            row[f"type1_{lang}"] = name_at(tbl["types"], t1)
            row[f"type2_{lang}"] = name_at(tbl["types"], t2)
            row[f"ability1_{lang}"] = name_at(tbl["abilities"], a1)
            row[f"ability2_{lang}"] = name_at(tbl["abilities"], a2)
            row[f"ability_hidden_{lang}"] = name_at(tbl["abilities"], ah)
        rows.append(row)
    return rows

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkhex_root", type=Path, help="Path to a PKHeX checkout at the pinned commit")
    ap.add_argument("-o", "--output", type=Path, default=Path("pokemon-personal-by-game.csv"))
    ap.add_argument("--game", choices=sorted(TABLES), action="append", help="Limit to one or more game tables")
    args = ap.parse_args()

    root = args.pkhex_root.resolve()
    langs = {lang: language_tables(root, lang) for lang in ("ja", "ko", "en")}
    selected = args.game or list(TABLES)
    rows: list[dict[str, object]] = []
    for game in selected:
        rows.extend(extract_table(root, game, langs))

    fields = [
        "game","table_file","table_index","entry_size","species_id","form","mapping",
        "species_ja","species_ko","species_en",
        "hp","atk","def","spe","spa","spd",
        "type1_id","type1_ja","type1_ko","type1_en",
        "type2_id","type2_ja","type2_ko","type2_en",
        "gender_ratio","growth_rate",
        "ability1_id","ability1_ja","ability1_ko","ability1_en",
        "ability2_id","ability2_ja","ability2_ko","ability2_en",
        "ability_hidden_id","ability_hidden_ja","ability_hidden_ko","ability_hidden_en",
        "form_stats_index","form_count","source_commit",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.output}")

if __name__ == "__main__":
    main()

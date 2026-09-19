# PKHeX PersonalInfo extraction

Pinned reference: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

The project now has an independent extractor:

`tools/pkhex_personal_extract.py`

It reads the pinned PKHeX `Resources/byte/personal/personal_*` tables and emits a normalized CSV without importing or executing PKHeX code.

## Fields extracted

- table index
- species / form mapping where the personal table exposes `FormStatsIndex`
- HP / Attack / Defense / Speed / Special Attack / Special Defense
- type IDs
- gender ratio byte
- growth-rate ID
- ability 1 / ability 2 / hidden ability IDs
- form stats index / form count
- Japanese / Korean / English species, type and ability names

## Mapping rule

For games with appended personal-form records, PKHeX's documented relation is:

`table_index = FormStatsIndex + form - 1`

when `form > 0`, `FormStatsIndex > 0` and `form < FormCount`.

Base species use their National species ID as the table index.

Some identities do not own separate personal records (for example purely cosmetic or procedural forms); those remain represented in `pokemon-form-census.csv` rather than being invented as personal-table rows.

## Usage

```bash
python tools/pkhex_personal_extract.py /path/to/PKHeX \
  -o manifests/pokemon-personal-by-game.csv
```

The PKHeX checkout should match the pinned commit. The output is reference data and must still be reconciled against exact target ROM/source evidence before an EMERALD implementation overrides existing Emerald mechanics.

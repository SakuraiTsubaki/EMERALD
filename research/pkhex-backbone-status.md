# PKHeX reference backbone status

Pinned reference: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

## Completed ingestion infrastructure

- PKHeX.Core file inventory: **3,549 files**
- Species localized ID table: **1,026 rows**
- Move localized ID table: **921 rows**
- Ability localized ID table: **311 rows**
- Item localized ID table: **2,685 rows**
- PersonalTable source registry: **23 game/context tables**
- PKM format source registry: **17 sources**
- Save format source registry: **37 sources**
- ItemStorage source registry: **24 sources**
- Encounter data source registry: **37 sources**
- Evolution source registry: **39 sources**
- Conversion source registry: **10 sources**
- Mystery Gift source registry: **21 sources**
- Ribbon/Mark source registry: **55 sources**
- Gen2/Gen3 -> Gen4 item conversion mappings: **595 rows**
- Legends: Z-A TM display remap: **162 rows**

## Files

Core:
- `manifests/pkhex/reference-lock.yml`
- `manifests/pkhex/core-file-inventory.csv`
- `tools/pkhex_reference_export.py`

Normalized identifiers:
- `manifests/pkhex/species.csv`
- `manifests/pkhex/moves.csv`
- `manifests/pkhex/abilities.csv`
- `manifests/pkhex/items.csv`

Source registries:
- `manifests/pkhex/personal-sources.csv`
- `manifests/pkhex/pkm_formats-sources.csv`
- `manifests/pkhex/saves-sources.csv`
- `manifests/pkhex/item_storage-sources.csv`
- `manifests/pkhex/encounters-sources.csv`
- `manifests/pkhex/evolutions-sources.csv`
- `manifests/pkhex/conversions-sources.csv`
- `manifests/pkhex/mystery_gifts-sources.csv`
- `manifests/pkhex/ribbons_marks-sources.csv`

Conversions:
- `manifests/pkhex/item-conversions.csv`
- `manifests/pkhex/gen9a-tm-remap.csv`

## Next extraction layer

The remaining large payloads are mostly PKHeX binary resources plus behavior encoded in C#:
- PersonalInfo binary tables
- level-up learnsets
- egg moves / tutors / TM compatibility
- encounter binary tables where applicable
- per-generation save block offsets and PKM field maps
- detailed legality constraints
- locations
- ribbons/marks numeric tables
- Mystery Gift field layouts

GitHub's connector does not expose binary blobs as raw bytes in this environment, so these should be decoded by the repository exporter against a local pinned PKHeX checkout. The exporter is deliberately Python-only and does not require linking PKHeX into the Emerald runtime.

## License boundary

PKHeX is GPLv3. EMERALD uses it as a pinned **reference oracle**. Runtime C# source is not vendored into the ROM project. Every normalized output keeps source commit/path provenance so facts can be independently checked against original games and the project's Japanese-first sources.

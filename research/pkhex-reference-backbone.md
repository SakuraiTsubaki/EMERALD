# PKHeX reference backbone

Pinned source: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

## Inventory status

The pinned PKHeX tree has been inventoried file-by-file for EMERALD.

- total inventoried files: **11634**
- critical/high-priority reference files: **3612**
- classified domains: **16**

Largest domains:

- sprites_third_party: 6460 files
- resources: 1731 files
- drawing: 866 files
- legality_encounters_evolution: 642 files
- save_structures: 617 files
- ui: 501 files
- verification_tests: 264 files
- entity_formats: 183 files
- editing_semantics: 160 files
- items: 49 files
- personal_data: 48 files
- game_metadata: 41 files
- mystery_gifts: 21 files
- ribbons_marks: 20 files
- moves: 16 files
- project_infra: 15 files

## Policy

PKHeX is GPLv3. EMERALD will not blindly copy PKHeX source code.

PKHeX is used as a pinned reference oracle:
1. extract factual schemas, IDs, tables and behavior into EMERALD-owned CSV/JSON/YAML;
2. independently implement required ROM/runtime behavior in EMERALD;
3. retain PKHeX commit + source-path provenance;
4. translate useful PKHeX tests into independent regression vectors;
5. keep UI/rendering code reference-only;
6. do not import PKHeX.Drawing.PokeSprite binary assets because their provenance/licenses are separate.

## High-value extraction targets

- `PKHeX.Core/PKM`: PK1-PK9, PA8/PA9 layouts, encryption/checksum, conversion semantics.
- `PKHeX.Core/PersonalInfo`: species/form stats, types, Abilities, form indexing.
- `PKHeX.Core/Saves`: SAV1-SAV9 structures, blocks, inventory, Pokédex, events, time.
- `PKHeX.Core/Items`: per-title item storage and valid IDs.
- `PKHeX.Core/Moves`: generation-specific move metadata.
- `PKHeX.Core/Legality`: forms, evolution, encounters, learnsets, RNG and transfer rules.
- `PKHeX.Core/MysteryGifts`: PGT/PCD/PGF/WC structures and conversion/validation.
- `PKHeX.Core/Ribbons`: ribbons and marks.
- `PKHeX.Core/Resources`: personal/evolution/level-up/egg-move resources and localization.
- `Tests`: regression-oracle material.

## Reference-only areas

- `PKHeX.WinForms`: desktop UI.
- `PKHeX.Drawing*`: rendering helpers.
- `PKHeX.Drawing.PokeSprite`: third-party sprite binaries — do not import.
- `.github`: PKHeX project infrastructure.

## Normalized outputs to build

- `manifests/pkhex/species-forms.csv`
- `manifests/pkhex/personal-parameters.csv`
- `manifests/pkhex/items.csv`
- `manifests/pkhex/moves.csv`
- `manifests/pkhex/abilities.csv`
- `manifests/pkhex/entity-formats.csv`
- `manifests/pkhex/save-formats.csv`
- `manifests/pkhex/evolutions.csv`
- `manifests/pkhex/learnsets.csv`
- `manifests/pkhex/encounters.csv`
- `manifests/pkhex/mystery-gifts.csv`
- `manifests/pkhex/ribbons-marks.csv`
- `manifests/pkhex/transfer-conversion.csv`
- `manifests/pkhex/legality-rules.csv`

The inventory is the map; the files above are the extraction layer.

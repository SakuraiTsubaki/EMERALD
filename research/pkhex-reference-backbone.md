# PKHeX reference backbone

Pinned source: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

## Inventory status

The pinned PKHeX tree has now been inventoried file-by-file for EMERALD.

- total inventoried files: **0**
- critical/high-priority reference files: **0**
- classified domains: **0**

Largest domains:



## Policy

PKHeX is GPLv3. EMERALD will not blindly copy PKHeX source code.

PKHeX is used as a pinned **reference oracle**:

1. extract factual schemas, IDs, tables and behavior into EMERALD-owned CSV/JSON/YAML;
2. reimplement the ROM/runtime behavior independently in EMERALD;
3. retain PKHeX commit + source-path provenance for every extracted artifact;
4. translate useful PKHeX tests into independent regression vectors;
5. keep UI/rendering code reference-only;
6. do not import PKHeX.Drawing.PokeSprite binary assets, because PKHeX itself documents third-party sprite provenance.

## High-value extraction targets

### Entity formats
`PKHeX.Core/PKM`

Use PK1-PK9, PA8/PA9 and conversion helpers to document field layouts, form storage, encryption/checksum and cross-generation entity semantics.

### Personal data
`PKHeX.Core/PersonalInfo`

Primary cross-generation source for species/form stats, types, Abilities, form counts and personal-table indexing.

### Saves
`PKHeX.Core/Saves`

Map SAV1-SAV9 blocks, party/box storage, inventory, Pokédex, event flags, Mystery Gift, time and title-specific structures.

### Items
`PKHeX.Core/Items`

Extract title-specific valid item IDs, bag/storage grouping and compatibility.

### Moves
`PKHeX.Core/Moves`

Extract generation-specific move metadata and availability.

### Legality
`PKHeX.Core/Legality`

Use as the behavioral reference for forms, evolution, encounters, RNG, learnsets and transfer restrictions. Reimplement rules rather than copying implementation.

### Mystery Gifts
`PKHeX.Core/MysteryGifts`

Document PGT/PCD/PGF/WC format structures and validation/conversion behavior.

### Ribbons and marks
`PKHeX.Core/Ribbons`

Normalize cross-generation ribbon/mark state.

### Resources
`PKHeX.Core/Resources`

Extract factual personal/evolution/level-up/egg-move resources and localization tables with provenance.

### Tests
`Tests`

Use expected results as regression-oracle material for EMERALD's independently implemented logic.

## Reference-only areas

- `PKHeX.WinForms`: desktop UI.
- `PKHeX.Drawing*`: rendering helpers.
- `PKHeX.Drawing.PokeSprite`: third-party sprite binaries — do not import.
- `.github`: PKHeX CI/project setup.

## Planned normalized outputs

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

The inventory is the map; these outputs are the actual extraction layer.

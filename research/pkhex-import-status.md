# PKHeX import status

Pinned source: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

## Completed now

### Repository/reference layer
- entire PKHeX repository cataloged by domain
- all 11664 repository files available through the pinned tree
- PKHeX.Core detailed inventory committed
- GPLv3/reference-only policy documented

### Normalized multilingual catalogs
Japanese -> Korean -> English columns:

- Species: 1,026 rows
- Moves: 921 rows
- Abilities: 311 rows
- Forms: 1,142 rows
- Types: 19 rows
- Natures: 25 rows
- Ribbons: 164 rows
- Games: 54 rows
- Items:
  - global: 2,685 rows
  - Gen I: 256
  - Gen II: 255
  - Gen III: 377

These are direct line-index normalizations from the pinned PKHeX resource files, with the source commit retained.

## Indexed extraction queue

- eggmove: 13
- encounter_logic: 292
- encounter_wild: 60
- evolution: 13
- evolution_logic: 36
- general_strings: 160
- item_logic: 49
- item_strings: 68
- learnset_logic: 62
- legality_resource: 126
- levelup: 24
- localization: 60
- locations: 399
- move_logic: 16
- mystery_gift_db: 14
- mystery_gift_format: 21
- personal: 28
- pkm_format: 18
- save_format: 40

The queue is stored in `manifests/pkhex-resource-inputs.csv`.

## Next decode layers

The remaining PKHeX knowledge is mostly binary resources and C# schema/rule code rather than plain text:

1. personal tables (RB/Y -> ZA)
2. evolution tables
3. level-up learnsets
4. egg moves
5. wild encounters
6. Mystery Gift databases
7. PK1-PK9/PA8/PA9 entity schemas
8. SAV1-SAV9 save/block schemas
9. legality/RNG/transfer restrictions
10. item and move rule code

These should be decoded to EMERALD-owned manifests while preserving `source_path + source_commit`.

## Authority

PKHeX supplies breadth and cross-generation semantics. Exact target Japanese ROM/decomp data remains authoritative when implementation details disagree.

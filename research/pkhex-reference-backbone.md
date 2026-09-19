# PKHeX reference backbone

Pinned upstream: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

License: **GPL-3.0**.

## Goal

Use PKHeX as the project's cross-generation reference backbone without blindly copying its implementation into the Emerald ROM codebase.

The project extracts factual/reference data into EMERALD-owned manifests and uses PKHeX logic as a verification oracle for:
- Pokémon entity formats (PK1-PK9, PA/PB formats);
- species/forms/personal data;
- items and bag/storage rules;
- moves and learnsets;
- Abilities/form logic via legality/personal data;
- save structures from Gen I through Gen IX;
- encounters, evolution, RNG and legality;
- transfer/conversion behavior;
- Mystery Gift/Wonder Card structures;
- ribbons/marks;
- localized game strings and identifiers.

## Inventory

The pinned repository contains **11664 files** in this inventory.

`manifests/pkhex-reference-inventory.csv` records every file with:
- upstream path;
- blob SHA;
- size;
- category;
- action policy;
- source commit.

`manifests/pkhex-extraction-plan.csv` summarizes the import/reference strategy by category.

## Import policy

### Extract reference data
Binary/text resources that encode factual game tables are converted into EMERALD-owned CSV/JSON/YAML with explicit provenance.

Examples:
- personal tables;
- level-up learnsets;
- evolution tables;
- egg moves;
- localized names;
- legality/encounter resources.

### Reimplement behavior
C# logic is treated as a schema/behavior reference unless the project explicitly elects GPL-compatible code reuse.

Examples:
- save parsing;
- PKM encryption/decryption;
- form legality;
- transfers/conversions;
- item/form update logic.

### Do not import UI
`PKHeX.WinForms` and drawing projects are not required for Emerald ROM/source normalization.

### Tests as verification
PKHeX tests are useful to derive expected behavior and regression cases, but are not copied wholesale.

## Language priority

When textual labels are needed:
1. Japanese
2. Korean
3. English
4. other official languages

Machine identifiers remain stable English/source symbols where appropriate.

## Immediate extraction order

1. Personal tables + forms
2. Species/form names and IDs
3. Items
4. Moves / level-up / egg moves
5. Evolution tables
6. Abilities and form-change rules
7. Save/entity layouts
8. Encounter/legality data
9. Mystery Gifts
10. Ribbons/marks and transfer restrictions

This turns PKHeX into a pinned reference database while keeping the Emerald implementation independently structured.

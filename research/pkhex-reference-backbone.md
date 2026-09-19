# PKHeX reference backbone

Pinned upstream:
- repository: `kwsch/PKHeX`
- commit: `8ad201e80244f630ab5a46922ab72fb79c5ad4f4`
- license: GPLv3

## Decision

PKHeX is the cross-generation **reference backbone** for EMERALD.

We do **not** vendor/copy the PKHeX source tree into EMERALD. Instead:

1. pin a known PKHeX commit;
2. inventory every relevant PKHeX.Core file;
3. extract facts/data into EMERALD-owned CSV/JSON/YAML manifests;
4. record the PKHeX source path + commit for provenance;
5. cross-check important behavior against game decompilation/disassembly and retail ROMs;
6. implement Emerald-side mechanics independently.

This keeps the Emerald implementation native to the project while using PKHeX as a mature cross-generation oracle.

## Coverage discovered

PKHeX.Core pinned revision contains **3528 files** across the following domains:

- PKM: 183
- PersonalInfo: 48
- Items: 49
- Moves: 16
- Saves: 617
- Legality: 642
- MysteryGifts: 21
- Ribbons: 20
- Game: 41
- Resources: 1731
- Editing: 160

## What this gives us

### Pokémon entity formats
`PK1` through `PK9`, plus formats such as `PA8`, `PA9`, `PB7`, `PB8`, and GameCube entity formats.

Use for:
- field layout;
- encryption/checksum rules;
- form storage;
- ribbon/mark flags;
- Tera/Gigantamax/Alpha/etc. auxiliary state;
- generation conversion.

### Personal data
`PersonalTable` exposes game-specific personal tables for:
- RB / Yellow
- GS / Crystal
- RS / Emerald / FR / LG
- DP / Pt / HGSS
- BW / B2W2
- XY / ORAS
- SM / USUM / LGPE
- SwSh / BDSP / PLA
- SV / Z-A

Use for:
- stats;
- types;
- abilities;
- gender ratios;
- growth/egg data;
- form counts and form-table lookup;
- game-specific differences.

### Save structures
PKHeX includes generation-specific save classes from Gen I through Gen IX plus substructures for:
- blocks;
- inventory;
- Pokédex;
- mystery gifts;
- daycare;
- time;
- records;
- mail;
- battle videos;
- rentals and other title-specific state.

For this project, `SAV3E`, Gen III save blocks and save substructures are especially important.

### Legality / mechanics metadata
The legality tree supplies:
- encounter definitions;
- evolution rules;
- learnsets;
- move-source logic;
- form rules;
- RNG restrictions;
- transfer restrictions;
- legality verification.

This is valuable as a **behavioral index**, but legality decisions must not be mistaken for ROM implementation code.

### Items / moves / ribbons / gifts
Use these to build cross-generation ID maps and behavior manifests:
- item storage / legal pocket sets;
- move metadata;
- ribbons/marks;
- Mystery Gift file formats and conversion.

### Resources
PKHeX bundles machine-readable resources for:
- personal data;
- level-up learnsets;
- evolution data;
- egg moves;
- Pokédex research data;
- localized species/item/move/form/location strings.

Project language priority remains:
**Japanese -> Korean -> English -> other languages.**

## Licensing boundary

PKHeX itself is GPLv3.

The project should avoid blindly copying code if the intent is to keep EMERALD's implementation independent. Facts and normalized game data should be extracted with provenance, while actual source-code reuse would require GPLv3 compliance.

PKHeX's README also identifies sprite/image collections with separate upstream provenance/licenses. Therefore:
- do not auto-import `PKHeX.Drawing.PokeSprite` assets;
- keep sprite acquisition/conversion in the project's existing asset pipeline;
- record asset provenance separately.

## Next extraction targets

The reference inventory is now in:
- `manifests/pkhex-core-reference-files.csv`
- `manifests/pkhex-reference-sections.csv`

The next actual data extraction should proceed in this order:

1. personal tables / forms;
2. species IDs and entity field layouts;
3. item IDs + storage/pocket legality;
4. move IDs + parameters;
5. ability IDs;
6. evolution + learnset + egg-move resources;
7. save layouts;
8. Pokédex;
9. Mystery Gift/event formats;
10. encounters/RNG/transfer rules;
11. ribbons/marks;
12. localization strings.

Each extracted table should preserve:
- PKHeX commit;
- source path/resource;
- game/context;
- original index;
- normalized EMERALD-facing semantic key.

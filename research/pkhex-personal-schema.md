# PKHeX personal-table reference

Pinned upstream: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

## Structural result

PKHeX carries personal tables for every core generation/game family from Gen I through Gen IX.

The important form-system transition is explicit in the schema:

- **Gen I-III:** no generic `FormCount` / `FormStatsIndex` fields in the personal record classes.
- **Gen IV onward:** the personal record exposes a form count plus an index to the alternate-form personal-data block.

Verified offsets from PKHeX's `PersonalInfo*` classes:

- Gen IV: `FormCount @ 0x29`, `FormStatsIndex @ 0x2A`
- Gen V-VII: `FormCount @ 0x20`, `FormStatsIndex @ 0x1C`
- Gen VIII SWSH/BDSP/LA: `FormCount @ 0x20`, `FormStatsIndex @ 0x1E`
- Gen IX SV/Z-A: `FormCount @ 0x1A`, `FormStatsIndex @ 0x18`

## Record sizes

The packed personal-record sizes expand substantially across generations:

- Gen I / III: 0x1C
- Gen II: 0x20
- Gen IV: 0x2C
- Gen V BW: 0x3C
- Gen V B2W2: 0x4C
- Gen VI XY: 0x40
- Gen VI ORAS: 0x50
- Gen VII: 0x54
- Gen VIII SWSH / LA: 0xB0
- Gen VIII BDSP: 0x44
- Gen IX SV / Z-A: 0x50

This validates the EMERALD design decision to keep later-generation form metadata in an extension layer rather than attempting to force all newer fields into the stock Gen III personal struct.

## Resource coverage

`manifests/pkhex-personal-resources.csv` records every pinned personal resource with:
- generation/game family;
- file size;
- record size;
- calculated record count;
- form field offsets;
- source commit.

The next extraction layer should decode each resource into a row-per-personal-entry table with:
- base stats;
- types;
- gender ratio;
- growth rate;
- abilities;
- held-item data;
- EV yield;
- form count/index;
- generation-specific flags.

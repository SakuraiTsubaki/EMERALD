# Emerald ROM form / appearance audit

This audit inspects the actual retail Emerald ROM binaries available to the project and cross-checks the behavior against the pinned `pret/pokeemerald` source.

## ROMs inspected

### Japanese — primary reference

- Game code: `BPEJ`
- Version byte: `0`
- Size: 16 MiB
- SHA-256: `33f5610b9186b4add09fef68895deb00f552b997b3d133b5a961e5123506343c`

The Game Freak ROM header at `0x108` points to:

- front-pic table: `0x082DDA1C`
- back-pic table: `0x082D6148`
- species-name table: `0x082EA31C`

### English — comparison reference

- Game code: `BPEE`
- Version byte: `0`
- Size: 16 MiB
- SHA-256: `a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af`

The Game Freak ROM header at `0x108` points to:

- front-pic table: `0x0830A18C`
- back-pic table: `0x083028B8`
- species-name table: `0x083185C8`

The Japanese and English ROMs use the same special-form graphics payloads even though table locations differ.

## Cases

### Castform — true in-battle form change

Internal species ID: **385**

The front and back graphics blobs both decompress to **0x2000 bytes**, i.e. four 0x800-byte 64x64 4bpp pictures.

Japanese front pointer:
- table entry: `0x082DDA1C + 385 * 8`
- graphics pointer: `0x08B8824C`
- decompressed size: `0x2000`

English front pointer:
- table entry: `0x0830A18C + 385 * 8`
- graphics pointer: `0x08B8824C`
- decompressed size: `0x2000`

The four 0x800-byte front chunks are distinct and have the same hashes in both ROMs:

1. `0b52edc03458d12f...`
2. `7b185e2a2e602c88...`
3. `6ee88d1164abf31e...`
4. `cf20ce1d4ce2dba4...`

The pinned source build rules identify these as Normal / Sunny / Rainy / Snowy. Battle code changes Castform type and graphics according to weather.

Classification: **runtime form change**.

### Unown — personality-selected 28 forms

Base Unown internal species ID: **201**

Form A uses the normal Unown slot. The other 27 graphics-only form slots are:

- `SPECIES_UNOWN_B = 413`
- through `SPECIES_UNOWN_QMARK = 439`

Direct ROM scan confirms all 27 entries are present, have unique front-picture pointers, and valid `0x800` sprite-sheet allocation tags in both Japanese and English ROMs.

The form is calculated from the Pokémon personality value modulo 28.

Classification: **persistent personality-derived form**.

### Deoxys — Emerald-local Speed Forme

Internal species ID: **410**

The normal species base-stat table contains:

- HP 50
- Atk 150
- Def 50
- Speed 150
- Sp. Atk 150
- Sp. Def 50

However Emerald also contains a unique six-u16 runtime stat vector:

- HP 50
- Atk 95
- Def 90
- Speed 180
- Sp. Atk 95
- Sp. Def 90

ROM locations:

- Japanese: `0x002FA6D6`
- English: `0x00329D48`

This vector occurs once in each inspected ROM and is used by `GetDeoxysStat` for the Emerald-local Speed Forme outside link-battle handling.

The front graphic is a two-frame `0x1000` payload. Unlike normal Pokémon, the two frames represent Deoxys forms rather than ordinary animation frames. The decompression path copies the second 0x800-byte frame over the first when Emerald should display its local form. The back graphic similarly decompresses to `0x1000`, while normal species back sprites are `0x800`.

Classification: **game-version-selected form**, not a normal player-triggered form switch in Emerald.

### Spinda — personality-generated markings

Internal species ID: **308**

Spinda does not have a table of discrete form sprites. Its base graphics use the ordinary single-picture layout, and four spot masks are applied at runtime according to personality-value nibbles.

Classification: **procedural appearance variation**, not a discrete form ID.

## Result

For the stock Emerald engine, the special appearance/form cases worth preserving separately are:

1. **Castform** — 4 actual weather forms
2. **Unown** — 28 personality-selected forms
3. **Deoxys** — Normal data plus Emerald-local Speed Forme handling
4. **Spinda** — PID/personality-generated spot pattern

Shiny coloration is a palette variant and is not treated as a form here.

Gen IV Pokémon such as Giratina, Shaymin, Rotom, and Arceus are not present in the stock Emerald species table. Adding their Gen IV item-driven forms will therefore require a new generalized form system rather than merely importing item parameters.

## Source cross-check

Pinned source: `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`

Relevant source behavior:
- `include/constants/species.h`: Unown graphics-only pseudo-species IDs 413-439
- `include/pokemon.h`: 28-form Unown personality calculation and Spinda spot structure
- `src/decompress.c`: Unown form graphics selection, Deoxys frame handling, Spinda spot rendering
- `src/pokemon.c`: Emerald Speed Deoxys runtime base-stat vector
- `src/battle_util.c`: Castform weather/type form changes

# JAPAN trainer survey — Generation I–III

All twenty Japanese source ROMs have now been parsed at the trainer-party layer.

## Generation I

Aka, Midori and Ao use the same trainer table at `0x3A0AC`.
Pikachu uses `0x3A142`.

The table contains 47 trainer-class pointers. Parties use the original two Gen I encodings:

- common level followed by a species list;
- `0xFF` followed by explicit level/species pairs.

Aka, Midori and Ao each resolve to 391 trainers and are semantically identical at this layer.
Pikachu resolves to 396 trainers. All four Japanese Pikachu revisions are identical to each other.

Ao vs Pikachu has 60 class/index-aligned party differences, including Yellow-only additions and title-specific party edits.

## Generation II

Kin/Gin use `0x3995C` with 66 class pointers and 495 trainers.
Crystal uses `0x399BA` with 67 class pointers and 541 trainers.

The parser preserves all four Gen II trainer-party forms: normal, moves, held item, and held item + moves.

Kin and Gin are identical. Their Rev A releases also do not change trainer-party semantics.
Crystal expands the trainer set and changes parties; 65 class/index-aligned entries differ from Kin/Gin. Because Crystal inserts content, this count is structural and must not be treated as a final identity-mapped change count.

## Generation III — Japanese ABI finding

The Japanese GBA ROMs do **not** use the 40-byte trainer record layout seen in the English decompilation output.

Direct pointer reconstruction establishes a 32-byte Japanese trainer record:

- 0x00 party flags
- 0x01 trainer class
- 0x02 encounter music / gender
- 0x03 trainer picture
- 0x04 trainer name, 6 bytes
- 0x0A four u16 trainer items
- 0x12 double-battle flag
- 0x14 u32 AI flags
- 0x18 party size
- 0x1C party pointer

This was independently recovered from known trainer-party pointers in the Japanese ROMs.

Table locations and counts:

- Ruby `0x1C4C94` — 694
- Sapphire `0x1C4C24` — 694
- Emerald `0x2E383C` — 855
- FireRed Rev0 `0x1FDFD8` — 743
- FireRed Rev1 `0x1F97F0` — 743
- LeafGreen `0x1FDFB4` — 743

Ruby and Sapphire are identical at the trainer-record and party layers.
FireRed and LeafGreen are also identical.
FireRed Rev0 and Rev1 have zero trainer-record/party semantic changes.

Emerald substantially expands and reorders trainer content relative to Ruby/Sapphire, so simple numeric-index comparison is not a final identity mapping.

## Remake consequence

Trainer data can be shared between Aka/Midori/Ao and between Kin/Gin at this layer, while Yellow and Crystal require title profiles.
FR/LG provide a stable official Kanto GBA trainer baseline, but source-game trainer identity must be mapped by class/name/context rather than by binary address.

Machine-readable evidence:
- `manifests/japan-trainer-table-locations.csv`
- `manifests/japan-trainer-semantic-diff.json`

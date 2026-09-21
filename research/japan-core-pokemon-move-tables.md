# JAPAN core Pokémon/move tables — first semantic pass

The twenty Japanese Generation I–III ROMs were scanned directly.

## Located tables

See `manifests/japan-core-table-locations.csv`.

Important layout results:

- Aka/Midori: base stats at `0x38000`; moves at `0x39658`.
- Ao/Pikachu: moves at `0x38000`; base stats at `0x383DE`.
- Generation I Mew is a separate base-stat record:
  - Aka/Midori: `0x4200`
  - Ao: `0x425B`
  - Pikachu: `0x39446`
- Kin/Gin: moves at `0x41C6C`; base stats at `0x51AA9`.
- Crystal: moves at `0x41C69`; base stats at `0x514BA`.
- R/S/E/FR/LG use common record formats but the tables relocate between builds and FireRed revisions.

This rules out fixed-address conversion. Remake tooling must resolve structures/symbols instead of assuming one address map.

## Record formats verified against the ROMs

- Gen I base-stat record: 28 bytes; 150-record main table plus separate Mew.
- Gen I move record: 6 bytes; 165 moves.
- Gen II base-stat record: 32 bytes; 251 records.
- Gen II move record: 7 bytes; 251 moves.
- Gen III base-stat record: 28 bytes; 412 table slots including species index 0.
- Gen III move record: 12 bytes; 355 table slots including MOVE_NONE.

## Revision result

For parsed gameplay fields, all tested within-title revisions have **zero semantic changes** in the base-stat and move tables:

- Aka Rev0 -> RevA
- Midori Rev0 -> RevA
- Pikachu 0A -> B -> C -> D
- Kin Rev0 -> RevA
- Gin Rev0 -> RevA
- FireRed Rev0 -> Rev1

Large raw revision diffs therefore belong to other code/data/layout areas.

## Version-family result

- Aka/Midori/Ao: no parsed semantic differences in these two tables.
- Ao -> Pikachu: National Dex 148 catch rate 45 -> 27; National Dex 149 catch rate 45 -> 9.
- Kin vs Gin: no parsed semantic differences.
- Ruby vs Sapphire: no parsed semantic differences.
- FireRed vs LeafGreen: no parsed semantic differences.

## Next layers

1. evolutions and level-up learnsets;
2. item attributes;
3. trainer parties;
4. wild encounters;
5. maps / warps / NPCs / scripts;
6. save and RTC state;
7. Gen I -> FRLG official-remake correspondence;
8. Gen II -> GBA remake requirements.

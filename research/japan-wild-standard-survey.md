# JAPAN standard wild-encounter survey

The standard map encounter layer has been parsed directly from all twenty Japanese Generation I–III ROMs.

## Generation I

Aka, Midori and Ao expose 248 map pointers through `WildDataPointers`; Pikachu exposes 249.
Each non-empty grass/water table uses an encounter rate plus ten level/species slots.

All inspected revisions are semantically identical in this layer.
Version identity matters strongly: Aka vs Midori differs in 175 normalized slots, Aka vs Ao in 122, and Ao vs Pikachu in 563.

Generation I rod encounters are stored separately and are covered by the special-encounter survey, not folded into these map rows.

## Generation II

The standard layer is split into four sequential tables:

- Johto grass: 61 entries
- Johto water: 38 entries
- Kanto grass: 30 entries
- Kanto water: 10 entries in Kin/Gin, 24 in Crystal

Grass entries preserve independent morning/day/night encounter rates and seven slots per time period.
Water entries contain one encounter rate and three slots.

Kin/Gin revisions are unchanged. Kin and Gin differ in 277 normalized standard slots.
Crystal substantially revises the encounter layer, so final cross-title conversion must map by named map identity rather than raw group/index.

Fishing, swarms, headbutt trees, Bug-Catching Contest, roaming Pokémon and unlocked-Unown behavior are distinct subsystems and are surveyed separately.

## Generation III

Direct ROM reconstruction located `gWildMonHeaders` in every Japanese GBA input:

- Ruby: `0x379304`
- Sapphire: `0x3792FC`
- Emerald: `0x52D9F4`
- FireRed Rev0: `0x390B34`
- FireRed Rev1: `0x38C2F4`
- LeafGreen: `0x3909A4`

Each header is 20 bytes: map group/number plus pointers for land, water, rock-smash and fishing info.
The parser follows the pointers into encounter-rate records and then into the actual min-level/max-level/species slots.

Counts:

- Ruby/Sapphire: 97 headers, 1,631 slots each
- Emerald: 124 headers, 1,975 slots
- FireRed/LeafGreen: 132 headers, 2,176 slots each

FireRed Rev0 -> Rev1 has zero semantic changes in this layer.
Ruby/Sapphire differ in 190 slots; FireRed/LeafGreen differ in 537.

Machine-readable evidence:
- `manifests/japan-wild-standard-locations.csv`
- `manifests/japan-wild-standard-semantic-diff.json`

The normalized extraction contains 27,502 rows across the 20 ROM inputs.

# JAPAN evolution and level-up learnset survey

All 20 Japanese Gen I-III ROMs were parsed directly.

## Generation I

The evolution and level-up learnset data share one per-species record.

- Aka / Midori / Ao pointer table: `0x3B427`
- Pikachu pointer table: `0x3B59C`
- 190 internal species indexes are represented.

Aka, Midori and Ao are semantically identical in this layer.
All four Japanese Pikachu revisions are also identical to each other.

Ao -> Pikachu changes level-up learnsets for 23 internal species, but does not change the evolution table.
The starter Pikachu evolution refusal therefore belongs to special-case code, not the generic evolution records.

## Generation II

- Kin / Gin pointer table: `0x4295F`
- Crystal pointer table: `0x42753`
- 251 National Dex species are represented.

Kin and Gin are identical in both evolution and learnset data.
Crystal keeps the same evolution definitions but changes level-up learnsets for 15 species:
Dugtrio, Magneton, Cloyster, Eevee, Spinarak, Ariados, Hoppip, Skiploom, Jumpluff, Yanma, Qwilfish, Sneasel, Swinub, Piloswine and Suicune.

## Generation III

Evolution data and level-up learnsets are separate.

Evolution rows contain five ABI slots. Each semantic entry is three u16 values
(method, parameter, target), but the compiled ROM uses an 8-byte slot due to ABI layout.

Level-up moves are packed u16 values:
- lower 9 bits: move
- upper 7 bits: level
- `0xFFFF`: end

Ruby and Sapphire are identical in this layer.
Emerald differs from Ruby/Sapphire only in Deoxys' level-up learnset.
FireRed Rev0 and Rev1 are identical.
FireRed vs LeafGreen differs in Dugtrio's level-1 move order and Deoxys' learnset.

## Remake consequence

Revision profiles do not need separate Pokémon evolution/learnset datasets for the currently inspected Japanese revisions.
Version profiles still matter:

- Yellow needs its 23-species learnset profile and special Pikachu logic.
- Crystal needs its 15-species learnset profile.
- Gen III Deoxys must remain title/profile aware.
- Fixed ROM addresses must never be used as canonical identities; every version relocates tables differently.

Machine-readable evidence:
- `manifests/japan-evolution-learnset-locations.csv`
- `manifests/japan-evolution-learnset-semantic-diff.json`

# Aegislash / ギルガルド — Gen VI reference

Implementation target is the debut-generation behavior, not the later 140-stat revision.

## Form stats

| Form | HP | Atk | Def | Spe | SpA | SpD |
|---|---:|---:|---:|---:|---:|---:|
| Shield | 60 | 50 | 150 | 60 | 50 | 150 |
| Blade | 60 | 150 | 50 | 60 | 150 | 50 |

Type: Steel / Ghost. Ability: Stance Change / バトルスイッチ.

## Battle transitions

- Start / send-out: Shield.
- Directly use a damaging physical or special move: change to Blade before the move.
- Directly use King's Shield: change to Shield before the move.
- Ordinary status moves: no change.
- Switch out, faint, battle end: Shield.
- A King's Shield called by Sleep Talk does not trigger the stance change in the reference implementation/test used for this port.

## King's Shield (Gen VI)

- Steel, status, PP 10, priority +4.
- Protect-family success chain.
- Blocks damaging moves that are affected by Protect; status moves are not blocked merely by King's Shield.
- If a blocked move makes contact, the attacker loses two Attack stages.

## Reference implementation inspected

`rh-hideout/pokeemerald-expansion@4c680433909c7fb2219cc9e755f05cdd081d4778`

Relevant paths:

- `src/data/pokemon/form_change_tables.h`
- `src/data/pokemon/species_info/gen_6_families.h`
- `src/data/moves_info.h`
- `src/data/abilities.h`
- `test/battle/ability/stance_change.c`

This project does **not** copy the expansion's two-species Shield/Blade representation. It keeps one persistent species and borrows the verified trigger semantics/tests.

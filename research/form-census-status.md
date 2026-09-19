# Pokémon form census status

Updated: 2026-09-19

## Cross-generation identity/state census

**Completed at the reference-data level.**

- master Pokémon form/state rows: **809**
- normalized numeric-index gaps: **0**
- PKHeX `BattleForms` families missing from census: **0**
- PKHeX `FormChange` families missing from census: **0**
- PKHeX `BattleMegas` families missing from census: **0**
- non-Pokémon Pokéstar Studio actors are separated from the Pokémon census
- Alcremie 63 cream/Sweet combinations are expanded
- Koraidon and Miraidon five form/mode values are included
- Ogerpon battle-only form IDs 4-7 are included
- procedural Spinda appearance is tracked as non-discrete

Rows by introduction generation:

- Gen 1: 58
- Gen 2: 44
- Gen 3: 34
- Gen 4: 55
- Gen 5: 47
- Gen 6: 168
- Gen 7: 100
- Gen 8: 200
- Gen 9: 103

## Parameter and trigger manifests

- `manifests/pokemon-form-game-parameters.csv`
- `manifests/pokemon-form-trigger-matrix.csv`
- `manifests/pokemon-form-transformation-systems.csv`

The parameter manifest stores the normalized reference stats/types/Abilities and form/sub-identity values. The trigger matrix stores item/move/Ability/Tera/change-from evidence and links the remaining behavior to generation research.

## Separate target-ROM verification layer

The remaining work is **not finding more form identities**. It is proving each row against exact retail binaries and historical versions:

- select exact Japanese release/revision/update for repositories still marked `identity_status: unselected`;
- verify exact personal-table form index/offset;
- record historical stat/type/Ability changes by game;
- record exact trigger/reset routine addresses;
- record graphics/model/icon/cry archive indexes;
- record Pokédex/transfer/save behavior by title/revision.

Until that binary layer is completed, use the wording:
**"form identity census complete; per-title ROM verification in progress."**

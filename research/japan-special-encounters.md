# JAPAN special encounter survey — Generations I–III

This layer covers encounter systems that are **not** represented completely by the standard map wild tables already normalized in `japan-wild-standard-*`.

Scripted static Pokémon and gift Pokémon are intentionally excluded here and will be handled in the Scripts layer.

## Generation I

### Good Rod

All Japanese Gen I titles use the same semantic Good Rod payload: a random choice between level-10 Goldeen and level-10 Poliwag.

Direct ROM locations:

- Aka/Midori: `0xE3CE`
- Ao: `0xE3F3`
- Pikachu Rev0A: `0xE241`
- Pikachu RevB/C/D: `0xE238`

The Pikachu location shift is layout-only; the data is unchanged.

### Super Rod

Aka/Midori/Ao use a reusable-group model: 33 map entries point into 10 fishing groups.
The direct table starts at:

- Aka/Midori: `0xEC24`
- Ao: `0xEC49`

Pikachu replaces that layout with 31 per-map records, each carrying four explicit species/level slots. The table is at `0xA4C7D` in all four Japanese Pikachu revisions.

No Japanese Gen I revision changes the Good Rod or Super Rod semantics.

## Generation II

### Fishing

Kin/Gin/Crystal use 13 `FishGroups`. Each group has Old, Good and Super Rod data, and selected slots can redirect through `TimeFishGroups` for day/night substitutions.

Direct Japanese ROM starts:

- Kin/Gin: `0x92946`
- Crystal: `0x929FB`

The canonical Gold and Crystal source tables are semantically identical at this layer; Crystal's address shift is layout-only.

### Swarms

Kin/Gin define four grass swarm profiles — Yanma, Snubbull, Dunsparce and Marill — and one surfing swarm profile for Marill.

Crystal reduces the grass swarm data to Dunsparce and Yanma and has no surfing swarm table entries.

Direct grass-table starts:

- Kin/Gin: `0x2BF02`
- Crystal: `0x2B8F3`

This is a title-level behavior difference and must remain a separate Crystal profile in the remake.

### Headbutt trees

Kin/Gin define six pointer-set identities: None, Forest, Canyon, Rock, Unused and City.

Crystal restructures this into eight defined identities: None, Canyon, Town, Route, Kanto, Lake, Forest and Rock, followed by an additional unused trailing pointer.

Direct pointer-table starts:

- Kin/Gin: `0xBA470`
- Crystal: `0xB82C8`

The species composition also changes, so Crystal headbutt encounters cannot be produced by merely reusing the Gold/Silver tables.

### Bug-Catching Contest

The contest species/weight/min-level/max-level table is semantically identical between Gold/Silver and Crystal.

Direct locations:

- Kin/Gin: `0x97BDC`
- Crystal: `0x97D49`

### Roaming Pokémon

Gold/Silver and Crystal use the same 16-entry route movement graph. The graph is separate from the actual roaming Pokémon state stored in save data.

### Unown unlocking

All three titles retain four semantic unlock groups:

1. A–K
2. L–R
3. S–W
4. X–Z

Direct letter-list locations:

- Kin/Gin: `0x3EA07`
- Crystal: `0x3EBB8`

Source syntax differs slightly, but the four letter sets are the same.

### Revision result

Kin/Gin Rev A do not change the parsed fishing, swarm, headbutt, Bug-Catching Contest or Unown unlock data.

## Generation III

### Feebas

Ruby, Sapphire and Emerald implement Route 119 Feebas as a separate algorithm, not as an ordinary fishing slot.

The implementation selects six fishing spots from the valid Route 119 fishing positions and checks the player's current fishing tile against those selected spots.

The Japanese ROMs contain the Feebas wild record `level 20–25 / Feebas` at:

- Ruby: `0x379AAC`
- Sapphire: `0x379AA4`
- Emerald: `0x52E724`

For remake architecture this must remain a special-condition encounter provider layered over ordinary fishing.

### Mass outbreaks

Ruby/Sapphire contain five outbreak candidates:

- Surskit — Route 102
- Surskit — Route 114
- Surskit — Route 117
- Surskit — Route 120
- Skitty — Route 116

The Japanese candidate lists begin at:

- Ruby: `0x3A68CC`
- Sapphire: `0x3A68B0`

Emerald changes the candidates to:

- Seedot — Route 102
- Nuzleaf — Route 114
- Seedot — Route 117
- Seedot — Route 120
- Skitty — Route 116

The Japanese Emerald list begins at `0x568B40`.

At runtime the TV system materializes an outbreak into save state. The ordinary land encounter flow checks that state and can replace a normal encounter on the matching map.

### Roaming Pokémon

- Ruby: Latios, level 40
- Sapphire: Latias, level 40
- Emerald: player-selected Latias or Latios, level 40
- FireRed/LeafGreen: level 50, chosen from the player's starter:
  - Bulbasaur -> Entei
  - Charmander -> Suicune
  - Squirtle -> Raikou

The roamer carries persistent state such as HP/status and moves through a route graph, so it belongs partly to the encounter layer and partly to the later Save/RTC/state survey.

### Emerald facility wild encounters

Battle Pike and Battle Pyramid use dedicated wild-header paths rather than the ordinary `gWildMonHeaders` flow.

Their detailed generation rules are intentionally deferred to the Battle Logic layer, but the architectural distinction is recorded here so they are not lost when converting standard wild tables.

## Remake consequence

The seven remake projects need an encounter abstraction with at least these providers:

- standard map encounters;
- Gen I rod-provider profiles;
- Gen II time-aware fishing;
- Gen II swarm override;
- headbutt/tree encounters;
- contest encounters;
- roaming-state encounters;
- Unown unlock filtering;
- Route-119-style conditional fishing;
- Gen III mass-outbreak override;
- facility-specific wild generation where applicable.

These providers should be data-driven and title-profiled. Collapsing everything into a single `wild_encounters` table would lose original behavior.

Machine-readable evidence:

- `manifests/japan-special-encounter-systems.json`
- `manifests/japan-special-encounter-revision-diff.json`

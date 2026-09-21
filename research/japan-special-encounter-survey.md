# JAPAN special encounter survey — Generation I–III

This layer covers encounter systems that are not fully represented by the standard map encounter tables.

## Generation I — fishing is a separate subsystem

Old Rod is code-driven: it always produces Magikarp at level 5.

Good Rod uses the same two-choice profile in every inspected Japanese Gen I ROM:
- Goldeen Lv10
- Poliwag Lv10

Direct ROM locations:
- Aka/Midori: `0xE3CE`
- Ao: `0xE3F3`
- Pikachu Rev0A: `0xE241`
- Pikachu RevB/C/D: `0xE238`

Super Rod has two genuinely different storage designs.

Aka/Midori/Ao:
- 33 map records
- each map points to one of 10 shared fishing groups
- Aka/Midori table root: `0xEC24`; first group body: `0xEC88`
- Ao table root: `0xEC49`; first group body: `0xECAD`
- semantic Super Rod data is identical across Aka/Midori/Ao despite relocation

Pikachu:
- 31 map records
- each map stores four direct species/level slots
- all four Japanese revisions: table root `0xA4C7D`
- all four revisions are semantically identical

Yellow therefore needs a separate fishing importer/profile rather than a relocated Red/Green/Blue parser.

## Generation II — multiple independent wild subsystems

### Rod fishing

Kin/Gin and Crystal retain the same 13-FishGroup model with Old/Good/Super Rod tables and time-dependent substitutions.

Direct ROM locations:
- Kin/Gin FishGroups root: `0x92946`; Shore Old body: `0x929A1`
- Crystal FishGroups root: `0x929FB`; Shore Old body: `0x92A56`

The core fish-group semantics are the same between Gold/Silver and Crystal.

### Swarms

Kin/Gin:
- grass swarm root: `0x2BF02`
- four grass profiles: Yanma, Snubbull, Dunsparce, Marill
- first Yanma encounter body: `0x2BF07`
- water swarm root: `0x2BFBF`
- one surfing swarm profile: Marill
- Marill encounter body: `0x2BFC2`

Crystal:
- grass swarm root: `0x2B8F3`
- two grass profiles: Dunsparce and Yanma
- Dunsparce body: `0x2B8F8`
- Yanma body: `0x2B927`
- no active surfing-swarm records

Crystal therefore has a distinct swarm profile, not a simple Gold/Silver copy.

### Headbutt trees / rocks

Kin/Gin:
- TreeMonMaps: `0xBA3E6` — 34 map mappings
- RockMonMaps: `0xBA44D` — 4 map mappings
- TreeMons pointer table: `0xBA470`
- six pointer slots, with shared aliases for several sets
- Canyon data: `0xBA4C2`
- Rock data: `0xBA4E8`

Crystal:
- TreeMonMaps: `0xB823E` — 34 map mappings
- RockMonMaps: `0xB82A5` — 4 map mappings
- TreeMons pointer table: `0xB82C8`
- eight functional semantic set slots, plus an unused alias
- Canyon data: `0xB82DA`
- Rock data: `0xB83BE`

Crystal substantially redesigns both the set family and the map-to-set assignments.

### Bug-Catching Contest

The ten active weighted encounter entries are identical across Kin/Gin/Crystal.

ROM locations:
- Kin/Gin: `0x97BDC`
- Crystal: `0x97D49`

### Roaming Pokémon route graph

Kin/Gin and Crystal share the same 16-node Johto route-transition graph.

Direct ROM locations:
- Kin/Gin: `0x2AA0E`
- Crystal: `0x2A3FF`

The graph semantics are identical; only placement differs. Routes 40 and 41 are excluded because they are water routes.

### Unown unlock sets

All three titles preserve four semantic unlock groups:
- A–K
- L–R
- S–W
- X–Z

ROM locations:
- Kin/Gin: `0x3EA07`
- Crystal: `0x3EBB8`

## Generation III — engine-level special encounters

### Feebas

Ruby, Sapphire and Emerald implement Route 119 Feebas outside the normal fishing header.

Verified behavior:
- 447 candidate fishing spots
- six selected spots
- deterministic selection from the Dewford-trend random seed
- 50% Feebas check on a selected spot
- Feebas level range 20–25

Direct Japanese ROM Feebas records:
- Ruby: `0x379AAC`
- Sapphire: `0x379AA4`
- Emerald: `0x52E724`

This must remain a runtime subsystem rather than being flattened into an ordinary fishing table.

### TV mass outbreaks

Ruby/Sapphire and Emerald use save-backed outbreak state containing species, location, level, moves and probability.

Ruby/Sapphire built-in templates:
- Surskit Lv3 — Route 102
- Surskit Lv15 — Route 114
- Surskit Lv15 — Route 117
- Surskit Lv28 — Route 120
- Skitty Lv15 — Route 116

Emerald built-in templates:
- Seedot Lv3 — Route 102
- Nuzleaf Lv15 — Route 114
- Seedot Lv13 — Route 117
- Seedot Lv25 — Route 120
- Skitty Lv8 — Route 116

Direct Japanese ROM outbreak-template roots:
- Ruby: `0x3A68CC`
- Sapphire: `0x3A68B0`
- Emerald: `0x568B40`

The encounter engine checks an active outbreak before falling back to the normal land table. Emerald uses a 50% outbreak replacement probability and stores a two-day active duration after the broadcast starts.

### Roamers

Ruby:
- Latios Lv40

Sapphire:
- Latias Lv40

Emerald:
- post-game TV choice selects Latias or Latios, Lv40

FireRed/LeafGreen:
- Bulbasaur starter -> Entei
- Charmander starter -> Suicune
- Squirtle starter -> Raikou
- roamer level 50

Gen III persists roamer identity/state including personality, IVs, HP and status. When the active roamer occupies the player's eligible map, the encounter branch uses a 1-in-4 check.

### Emerald Battle Pike / Battle Pyramid

Emerald also has facility-specific wild generation paths for Battle Pike and Battle Pyramid. These do not use the ordinary `gWildMonHeaders` path. Their detailed generation rules are deferred to the Battle Logic survey, but this distinction is retained so facility encounters are not lost in the standard-wild conversion.

## Revision result

No semantic special-encounter changes were found in the inspected same-title Japanese revisions.

The observed differences are relocations only, such as Pikachu Good Rod Rev0A vs later revisions.

## Remake consequence

The modern GBA remake core must keep separate adapters/state machines for:

- standard map wild tables
- rod fishing
- time-of-day encounter substitution
- swarm/outbreak overrides
- Headbutt tree/rock sets
- Bug-Catching Contest encounters
- roaming state and movement graphs
- Unown unlock filters
- seed/tile-driven special fishing such as Feebas

Static Pokémon, gifts and scripted legendary encounters are intentionally deferred to the map/script survey because their identity is event-driven rather than wild-table driven.

Machine-readable evidence:
- `manifests/japan-special-encounter-locations.csv`
- `manifests/japan-special-encounter-systems.csv`
- `manifests/japan-special-encounter-semantic-summary.json`

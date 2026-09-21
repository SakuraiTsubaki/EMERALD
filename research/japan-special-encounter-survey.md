# JAPAN special encounter survey — Generation I–III

This layer covers encounter systems that are not fully represented by the standard grass/water/rock-smash/fishing header census.

## Generation I — fishing is a separate subsystem

Old Rod is code-driven and does not use a species table: it produces Magikarp at level 5.

Good Rod uses the same two-choice semantic profile across the inspected Japanese Gen I titles:
- Goldeen Lv10
- Poliwag Lv10

Direct ROM locations:
- Aka/Midori: `0xE3CE`
- Ao: `0xE3F3`
- Pikachu Rev0A: `0xE241`
- Pikachu RevB/C/D: `0xE238`

Super Rod has two different storage designs.

Aka/Midori/Ao:
- 33 map records
- each map points to one of 10 shared fishing groups
- Aka/Midori table `0xEC24`, group data `0xEC88`
- Ao table `0xEC49`, group data `0xECAD`

Pikachu:
- 31 map records
- each map contains four direct species/level slots
- all four Japanese revisions: `0xA4C7D`

This is a real format change, not just relocation, so Yellow fishing needs its own importer/profile.

## Generation II — multiple independent wild subsystems

### Rod fishing

Gold/Silver and Crystal retain the same 13 FishGroups design, including time-dependent substitutions.

ROM signature locations for the primary Shore Old-Rod body:
- Kin/Gin: `0x929A1`
- Crystal: `0x92A56`

The disassembly-level fish data is semantically identical between Gold/Silver and Crystal.

### Swarms

Gold/Silver:
- four grass swarm profiles: Yanma, Snubbull, Dunsparce, Marill
- one water/surf swarm profile: Marill
- Yanma body at `0x2BF04`
- water Marill body at `0x2BFC1`

Crystal:
- two grass swarm profiles: Dunsparce and Yanma
- no active surf swarm table
- Dunsparce body at `0x2B8F5`
- Yanma body at `0x2B924`

Crystal therefore does not simply inherit the Gold/Silver outbreak profile.

### Headbutt trees / rocks

Gold/Silver use a six-set family, with version-dependent Forest contents.
Representative ROM data:
- common None/City data `0xBA47C`
- rock set `0xBA4E8`

Crystal redesigns the family to eight semantic sets:
- Canyon
- Town
- Route
- Kanto
- Lake
- Forest
- Rock
- None

Representative Crystal Canyon data starts at `0xB82DA`; rock data at `0xB83BE`.

### Bug-Catching Contest

Gold/Silver and Crystal have the same ten active weighted entries.

ROM locations:
- Kin/Gin: `0x97BDC`
- Crystal: `0x97D49`

### Roaming Pokémon route graph

Gold/Silver and Crystal share the same 16-node Johto route-transition graph.
Routes 40 and 41 are deliberately absent because they are water routes.

The roamer state itself belongs in the save/RTC/state survey; this section records the encounter routing behavior.

### Unown unlock sets

Both profiles use four semantic letter sets:
- A–K
- L–R
- S–W
- X–Z

ROM signatures:
- Kin/Gin: `0x3EA07`
- Crystal: `0x3EBB8`

The source text differs slightly because Crystal names the constants differently, but the actual four unlock groups are the same.

## Generation III — engine-level special encounters

### Feebas

Ruby, Sapphire and Emerald implement Route 119 Feebas as a special fishing check rather than a normal fishing-table slot.

Verified behavior:
- 447 candidate fishing spots
- six spots selected from a deterministic seed
- on a selected spot, the Feebas check itself succeeds 50% of the time
- Feebas level range: 20–25

This logic must be preserved separately from ordinary fishing headers if Gen III behavior is used as the GBA reference.

### TV mass outbreaks

Ruby/Sapphire/Emerald have a save-backed outbreak system. An outbreak stores:
- species
- map
- level
- four moves
- probability

The wild-encounter engine checks the active outbreak before falling back to the normal land table.

Emerald's built-in generated profiles are:
- Seedot Lv3 — Route 102
- Nuzleaf Lv15 — Route 114
- Seedot Lv13 — Route 117
- Seedot Lv25 — Route 120
- Skitty Lv8 — Route 116

Emerald sets outbreak probability to 50% and the active duration to two days once the broadcast starts.

### Roamers

Ruby:
- Latios Lv40

Sapphire:
- Latias Lv40

Emerald:
- the post-game TV choice selects Latias or Latios, Lv40

FireRed/LeafGreen:
- Squirtle starter -> Raikou
- Bulbasaur starter -> Entei
- Charmander starter -> Suicune
- roamer level 50

The Gen III roamer object preserves identity/state such as personality, IVs, HP and status between encounters.
When the roamer is on the player's current eligible map, the encounter test succeeds with a 1-in-4 check.

## Revision result

No semantic special-encounter changes have been found in the inspected same-title Japanese revisions.
A few tables relocate, notably Pikachu Good Rod Rev0A vs later revisions, but their semantics remain unchanged.

## Remake consequence

Do not flatten these systems into one generic encounter list.

The modern GBA remake core needs separate adapters for:
- standard map wild tables
- rods
- time-of-day tables
- swarm/outbreak overrides
- Headbutt tree/rock sets
- contest encounters
- roaming state
- Unown unlock filters
- tile-seeded special fishing such as Feebas

Static/scripted encounters are intentionally deferred to the map/script survey because their identity is event-script driven rather than wild-table driven.

Machine-readable evidence:
- `manifests/japan-special-encounter-systems.csv`
- `manifests/japan-special-encounter-semantic-summary.json`

# JAPAN map / warp / NPC survey — Generations I–III

All twenty Japanese source ROMs have been traversed at the map-topology and map-event layer.

The detailed normalized extraction contains 6,479 map rows. ROM binaries are not committed; the extraction is reproducible from the JAPAN source set.

## Generation I

Direct ROM table roots:

- Aka Rev0: MapHeaderPointers `0x1BCB`
- Aka RevA: `0x1BB9`
- Midori Rev0: `0x1BCB`
- Midori RevA: `0x1BB9`
- Ao: `0x0167`
- Pikachu Rev0A/B/C/D: `0xFC1F2`

MapHeaderBanks:

- Aka/Midori: `0xC883`
- Ao: `0xC275`
- Pikachu: `0xFC3E4`

Twenty-two `UNUSED_MAP_*` IDs are excluded from event totals because several point to aliases or non-map data.

Aka/Midori/Ao use 248 map-ID slots and 226 active map IDs. Pikachu uses 249 slots / 227 active IDs; the extra map is `SUMMER_BEACH_HOUSE`.

Aka and Midori are topologically identical. Aka vs Ao differs on four active maps:

- ROUTE_18_GATE_2F
- VERMILION_TRADE_HOUSE
- CERULEAN_CAVE_2F
- CERULEAN_CAVE_B1F

All four Japanese Pikachu revisions are topologically identical to each other. Ao vs Pikachu changes 100 of the 226 shared active map IDs, so Yellow must remain a title-level content profile.

## Generation II

The 26-entry `MapGroupPointers` table was recovered directly from every Japanese ROM:

- Kin/Gin Rev0/RevA: `0x940ED`
- Crystal: `0x94000`

The relative pointer spacing exactly matches each group's map count times the 9-byte map record size.

Kin/Gin each contain 368 maps. Crystal contains 388.

Direct event totals:

| Title family | Maps | Connections | Warps | Coord | BG | Objects |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Kin/Gin | 368 | 142 | 1,241 | 102 | 761 | 1,343 |
| Crystal | 388 | 142 | 1,312 | 114 | 810 | 1,471 |

Kin vs Gin and all same-title revisions have zero normalized map-profile/topology/event changes.

Crystal adds 20 map keys. On the 368 common group/map keys, an index-aligned structural comparison finds 349 map-profile changes, 58 topology changes and 148 event changes. Final remake mapping must therefore use map identity rather than numeric index alone.

## Generation III

Japanese `gMapGroups` roots recovered directly from the GBA ROMs:

- Ruby: `0x2E09F0`
- Sapphire: `0x2E0980`
- Emerald: `0x45E998`
- FireRed Rev0: `0x316758`
- FireRed Rev1: `0x311F70`
- LeafGreen: `0x316738`

Counts:

| Title family | Groups | Maps | Connections | Warps | Coord | BG | Objects |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ruby/Sapphire | 34 | 394 | 134 | 1,156 | 312 | 676 | 2,268 |
| Emerald | 34 | 518 | 148 | 1,313 | 377 | 720 | 2,942 |
| FireRed/LeafGreen | 43 | 425 | 116 | 1,294 | 228 | 702 | 1,647 |

Ruby/Sapphire are identical at normalized map-header profile, connection and event-topology level.
FireRed Rev0/Rev1 are also identical, as are FireRed/LeafGreen.

Emerald substantially expands/reorders Ruby/Sapphire content. An index-aligned comparison is retained only as a structural diagnostic; final cross-title correspondence must be name-based.

## Comparison boundary

This layer compares map structure and event topology, not script semantics.

- script pointers are deliberately excluded from semantic equality because builds relocate them;
- Gen III BG-event payload unions are not treated as a single pointer type because the payload can encode a script, hidden item or secret-base value;
- static/gift Pokémon and one-off story battles are deferred to the Scripts layer.

Machine-readable summaries:

- `manifests/japan-map-event-census-summary.csv`
- `manifests/japan-map-event-semantic-summary.json`
- `manifests/japan-map-event-extraction.json`

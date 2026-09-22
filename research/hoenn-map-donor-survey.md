# Hoenn → Johto GBA map donor survey

## Decision

Johto is **not** rebuilt on an empty GBA canvas, and Hoenn geography is **not** transplanted into Johto.

The source hierarchy is:

1. Japanese Gold / Silver / Crystal ROMs — authoritative topology, map/event state, title differences.
2. HeartGold / SoulSilver — official later interpretation for modernization decisions.
3. Japanese Ruby / Sapphire / Emerald ROMs — direct GBA map-system evidence; Emerald is the preferred reusable engine/asset donor.
4. `pret/pokeruby` and `pret/pokeemerald` — pinned named source trees used to inventory and audit reusable assets.
5. Japanese FireRed / LeafGreen — first-choice GBA donor for the Generation II Kanto half.

ROM binaries are never committed.

## Direct Japanese ROM baseline

| Title | Size | SHA-256 | Direct map evidence |
| --- | ---: | --- | --- |
| Ruby (AXVJ) | 8 MiB | `e911caa1ffbf8704cd45bbe064ade40e24efa50dfdce82adf4b2899b5f733852` | `gMapGroups 0x2E09F0`; 394 maps |
| Sapphire (AXPJ) | 8 MiB | `6a5ff7656531ab41d1ea9cd8f2d045ab6228405b43f3ee09ea3ff5077c0f60c9` | `gMapGroups 0x2E0980`; 394 maps |
| Emerald (BPEJ) | 16 MiB | `33f5610b9186b4add09fef68895deb00f552b997b3d133b5a961e5123506343c` | `gMapGroups 0x45E998`; 518 maps |

The existing direct twenty-ROM census finds **zero normalized map-header-profile, connection, or event-topology changes between Japanese Ruby and Sapphire**. They can therefore share one RS donor profile while each Japanese ROM remains independently identified.

Gold and Silver likewise have zero normalized map-profile/topology/event changes and each contains 368 maps. Crystal contains 388 maps and adds 20 map keys; on the 368 common keys the census records 349 map-profile changes, 58 topology changes, and 148 event changes. Crystal therefore uses its own source map/event state.

## Pinned named-source references

- `pret/pokeruby@63a8cbf0016b351a4e68f7036fa0b77e23d2f2c1`
- `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`

These pins are used for names, source structure, and reusable asset inventory. They do **not** replace the Japanese retail ROMs as the master reference.

## Exhaustive Hoenn donor inventory

### Tilesets

Both source families have the same three primary families:

- `general`
- `building`
- `secret_base`

Secondary inventory:

| Family | Secondary directories |
| --- | ---: |
| Ruby / Sapphire | 50 |
| Emerald | 67 |
| Common names | 48 |
| RS-only | 2 |
| Emerald-only | 19 |

The RS-only directories are `battle_tower` and `ship`.

Emerald-only additions include the Battle Frontier facility families, `inside_ship`, `island_harbor`, `mirage_tower`, `mossdeep_game_corner`, `mystery_events_house`, `navel_rock`, `trainer_hill`, and `union_room`.

Across primary + secondary names, the union is **72 tileset directories**.

The exhaustive inventory records source availability, subtree identity, file counts, palette counts, animation PNG counts, and presence of `tiles.png`, `metatiles.bin`, and `metatile_attributes.bin`.

### Layouts

At the pinned source trees:

| Family | Top-level layout directories |
| --- | ---: |
| Ruby / Sapphire | 332 |
| Emerald | 441 |
| Common names | 274 |
| RS-only | 58 |
| Emerald-only | 167 |
| Union | 499 |

The previous draft's “443 Emerald layout directories” count is superseded by this recursive-tree census. The correct count at the pinned Emerald commit is **441 actual top-level layout directories**.

### Palettes

Under `data/tilesets`:

- Ruby / Sapphire tree: **928** palette source files.
- Emerald tree: **1,200** palette source files.
- Union of palette paths: **1,232**.

The palette inventory stores path availability and Git blob SHA. These are source-file records; they are not claims that every file is a visually unique palette.

### Metatile / behavior ABI

Emerald's GBA map model provides:

- a 16×16 metatile grid;
- 10-bit metatile ID + 2-bit collision + 4-bit elevation in each map-grid entry;
- an 8-bit behavior + layer type in metatile attributes;
- primary and secondary tilesets;
- MapLayout, MapHeader, connections, object/warp/coord/bg events, music, weather, cave/map type and script pointers.

The reusable behavior range is `0x00..0xEF`, **240 slots**. The pinned RS and Emerald headers have **41 name/activation differences at the same numeric slots**.

Important Emerald upgrades for the Johto conversion include:

- `MB_CAVE` at 0x08 where RS labels the slot unused;
- `MB_DEEP_WATER` at 0x12;
- `MB_EASTWARD_CURRENT` at 0x50, completing four named current directions;
- `MB_EAST_ARROW_WARP` at 0x62;
- explicit ocean/pond bridge levels and bridge-edge behaviors in the 0x70 range;
- named Trainer Hill / wireless / Sky Pillar behavior slots at the high end.

This is one reason Emerald is the preferred implementation donor even when Ruby/Sapphire remain valuable structural cross-checks.

## Reuse classes

**Outdoor / town / forest:** `General` is the base. Petalburg, Rustboro, Mauville, Slateport, Lilycove, Dewford, Fallarbor, Lavaridge, Fortree, Ever Grande and Sootopolis contribute GBA-scale terrain, elevation, bridge, coast and city composition. GSC still defines Johto geometry.

**Caves:** `Cave`, Granite Cave and Rusturf Tunnel provide common cave grammar. Meteor Falls is the preferred vertical/waterfall donor. Shoal Cave plus Sootopolis Gym provide Ice Path ice/slide behavior.

**Water:** General water, Pacifidlog log/current behavior, Meteor Falls waterfall behavior and Emerald bridge families are reusable. Whirlpool itself remains a Johto-specific field-move mechanic.

**Interiors:** Building, Pokémon Center, Shop, Generic Building, Lab, Day Care, School, Bike Shop, Game Corner and Facility are high-value direct or structural donors.

**Special facilities:** Aqua/Magma Hideout and New Mauville support Rocket/technical areas. Abandoned Ship + Emerald `inside_ship` support S.S. Aqua. Emerald Battle Frontier/Battle Tower is the preferred Crystal Battle Tower skeleton.

## GOLD / SILVER / CRYSTAL mapping rule

Gold and Silver use the same Hoenn donor assignment matrix because their direct Japanese-ROM map topology is identical. They remain separate title profiles for other content.

Crystal uses the same donor library for common areas, but Crystal's own 388-map state wins wherever it differs. Its Battle Tower maps are Crystal-only and map directly to Emerald's Battle Frontier/Battle Tower implementation family, with the RS Battle Tower retained as a useful earlier-GBA cross-check.

## Kanto boundary

Generation II Kanto remains:

`GSC three-years-later Kanto + FireRed/LeafGreen GBA Kanto donor assets`

Hoenn is only a fallback for generic behaviors or interiors where needed. Kanto is not rebuilt from Hoenn.

## Machine-readable outputs

- `manifests/rse-hoenn-map-donor-audit.json` — ROM identities, source pins, census totals and policy.
- `manifests/rse-hoenn-tileset-inventory.json` — all 72 primary/secondary donor directories.
- `manifests/rse-hoenn-palette-inventory.json` — 1,232 palette-path records.
- `manifests/rse-hoenn-layout-inventory.json` — all 499 layout-name records.
- `manifests/rse-hoenn-metatile-behavior-donors.json` — all 240 behavior slots.
- `manifests/gsc-hoenn-donor-matrix.json` — Gold/Silver/Crystal donor mapping by Johto area.
- `manifests/hoenn-to-johto-map-donors.csv` — curated high-value donor shortlist.
- `manifests/johto-gba-map-plan.csv` — existing Johto area implementation plan.

## First implementation slice

The first playable conversion slice remains:

**New Bark Town → Route 29 → Cherrygrove City**

Use GSC geometry/events as authoritative data, with Emerald `General` for the outdoor GBA foundation, Lab/Building for New Bark interiors, Pokémon Center/Shop for Cherrygrove, and Littleroot/Oldale only as GBA composition/scale references.

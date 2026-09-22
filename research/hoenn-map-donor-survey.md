# Hoenn → Johto GBA map donor survey

## Decision

Johto will **not** be rebuilt on an empty GBA canvas.

The source hierarchy is:

1. Japanese Gold/Silver/Crystal — exact original topology, warps, NPC/event placement, title differences.
2. HeartGold/SoulSilver — official later interpretation when a modernization decision is useful.
3. Japanese Ruby/Sapphire/Emerald — especially Emerald — GBA map engine and reusable asset donor.
4. Japanese FireRed/LeafGreen — first-choice donor for the Gen II Kanto half.

Hoenn assets are donors, not replacement geography.

## Pinned evidence

- `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`
- `pret/pokegold@656583c939d30f920a316177311a502dd222b57c`
- `pret/pokecrystal@7a7881d0d62e0ddbd82dcf10e7116807487ac651`

At the pinned Emerald source:

- 3 primary tileset families;
- 67 secondary tileset directories;
- 443 layout directories.

The main outdoor donor is `data/tilesets/primary/general`, already carrying GBA grass, water, waterfall, land/water-edge and related animations.

## What gets reused

**Direct functional reuse:** Pokémon Center, Mart, generic interiors, lab, Day Care, school, Bike Shop, Game Corner, common cave implementation, ship interiors, League-room grammar, Battle Tower framework.

**Visual/structural reuse:** Hoenn city tilesets and layouts provide building scale, elevation, coast, bridges and GBA map composition. They do not replace Johto geography.

**Behavior reuse:** Emerald already exposes ice, thin/cracked ice, four slide directions, waterfall, four water-current directions, multiple bridge levels/reflections, ladders, door types, tall/long grass and other field behaviors.

That means Ice Path can use the existing GBA ice/slide machinery while keeping the source puzzle geometry. Whirl Islands can use cave/water/current machinery, while Whirlpool itself remains a Johto-specific field-move extension.

## High-value layout donors

- Granite Cave / Meteor Falls / Rusturf Tunnel → cave grammar
- Shoal Cave ice room → Ice Path
- Mt. Pyre / Sky Pillar → multi-floor tower grammar
- Ancient Tomb / Desert Ruins / Island Cave → Ruins of Alph chambers
- Aqua/Magma Hideout / New Mauville → Team Rocket Base and industrial interiors
- Abandoned Ship → S.S. Aqua room/corridor grammar
- Safari Zone → National Park large natural-area grammar
- Emerald Battle Tower → Crystal Battle Tower skeleton

These are structural references, not coordinates to copy.

## Region split

Johto:

`GSC topology + HGSS interpretation + Emerald GBA assets/engine`

Kanto:

`GSC three-years-later topology/events + FireRed/LeafGreen GBA Kanto assets`

Hoenn is only a fallback donor for missing behaviors or generic interiors on the Kanto side.

## First implementation slice

Start with:

**New Bark Town → Route 29 → Cherrygrove City**

using General outdoor tiles, Littleroot/Oldale GBA layout grammar, Lab/Building/Pokémon Center/Shop interiors, and the original Kin/Gin map/event topology.

After that, Violet → Azalea → Goldenrod can reuse the same conversion pipeline without changing architecture.

Machine-readable files:

- `manifests/hoenn-to-johto-map-donors.csv`
- `manifests/johto-gba-map-plan.csv`

# Johto GBA first vertical slice

The first playable conversion slice is fixed as:

**New Bark Town → Route 29 → Cherrygrove City**

This is intentionally small enough to validate the conversion pipeline while exercising nearly every important overworld system: town/route connections, buildings, coord triggers, object events, RTC/day-of-week logic, a tutorial battle, a rival battle, gifts and flypoint state.

## Unit conversion

Gold/Silver's renderer expands each source map metatile as a **4×4 set of 8px tiles**, i.e. 32×32 px.

Emerald's map grid uses 16×16 px metatiles. Therefore a source map of W×H Gen II blocks becomes a **2W×2H GBA layout** when physical geometry is preserved.

For the first slice:

- New Bark Town: 10×9 → **20×18**
- Route 29: 30×9 → **60×18**
- Cherrygrove City: 20×9 → **40×18**

GSC event positions are already expressed on the 16px movement grid. Their coordinates therefore remain unchanged. Connection offsets are block-based and are multiplied by two.

This is a major simplification: the event topology can be imported without inventing a coordinate-remapping heuristic.

## Visual conversion

The visual source is **not Hoenn**.

Gold/Silver already exposes native Johto source assets such as:

- `gfx/tilesets/johto.png`
- `data/tilesets/johto_metatiles.bin`
- `data/tilesets/johto_collision.asm`
- Johto roof graphics such as `gfx/tilesets/roofs/new_bark.png`

Those define the visual identity.

Emerald supplies the GBA implementation grammar:

- 16×16 metatile map grid
- primary/secondary tilesets
- palettes
- metatile attributes/behaviors
- animations
- map connections/events/scripts

So the conversion is:

`GSC Johto visual/metatile intent → rebuilt GBA tiles/metatiles → Emerald field engine`

rather than `Hoenn town copied into Johto`.

## Donor assignments

New Bark uses General as its outdoor GBA foundation, Littleroot only as town-scale/layout grammar, and the GBA Lab/Building sets for interiors.

Route 29 uses General for outdoor terrain and Route 102 as an east-west route composition reference.

Cherrygrove uses General plus Oldale's small-town grammar, with Pokémon Center/Shop/GenericBuilding interiors.

## Semantic gates

New Bark must retain the pre-starter teacher block, rival outside Elm's Lab and flypoint callback.

Route 29 must retain the catching tutorial, Tuesday-only Tuscany logic, time-of-day dialogue, fruit tree and Potion.

Cherrygrove must retain the Guide Gent tour/Map Card, starter-dependent rival battle, flypoint and Mystic Water gift.

These semantics are acceptance criteria, not optional polish.

Machine-readable spec:

- `manifests/johto-gba-first-slice.json`

Validation helper:

- `tools/validate_johto_gba_map_units.py`

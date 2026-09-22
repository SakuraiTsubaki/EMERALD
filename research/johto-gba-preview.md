# Johto GBA remake map previews

The committed `*.map.bin` files are GBA map-grid binaries, not images. GitHub
cannot show them as a map by itself.

Use the Japanese retail Emerald ROM as a local rendering input:

```bash
python tools/render_johto_gba_remake_previews.py \
  --emerald-rom "/path/to/Pocket Monsters - Emerald (Japan).gba"
```

The command renders the current slice to:

- `artifacts/johto-gba-remake-preview/new_bark_town.png`
- `route_29.png`
- `cherrygrove_city.png`
- `route_30.png`
- `route_31.png`
- `violet_city.png`

The renderer reads the actual Japanese Emerald primary/secondary Tileset
structures, GBA 4bpp tile graphics, palettes, and metatile definitions directly
from the ROM. The ROM remains an input only and is never copied into the repo.

Current visual profiles:

- New Bark through Route 30: General + Petalburg (Littleroot/Oldale grammar)
- Route 31 and Violet: General + Rustboro

A preview flattens Emerald's two metatile background layers into one PNG.
Collision/elevation/event semantics remain in the map data and manifests; the PNG
is for human visual review only.

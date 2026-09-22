#!/usr/bin/env python3
"""Render a committed Johto GBA remake map.bin with Japanese Emerald tiles.

ROM is an input only. Nothing from the ROM is written to the repository by this
tool. The renderer reads the map profile's primary/secondary Tileset structs,
GBA 4bpp tiles, palettes, and metatile definitions directly from the ROM.
"""
from __future__ import annotations
import argparse, binascii, struct, zlib
from pathlib import Path

MAP_GROUPS = 0x45E998
NUM_TILES_PRIMARY = 512
NUM_METATILES_PRIMARY = 512
NUM_PALS_PRIMARY = 6
NUM_PALS_TOTAL = 13

def u32(data: bytes, off: int) -> int:
    return int.from_bytes(data[off:off + 4], "little")

def ptr(data: bytes, off: int) -> int:
    value = u32(data, off)
    if value >> 24 not in (8, 9):
        raise ValueError(f"bad GBA pointer {value:#x} at {off:#x}")
    return value & 0x1FFFFFF

def emerald_map(rom: bytes, map_num: int) -> dict:
    group = ptr(rom, MAP_GROUPS)
    header = ptr(rom, group + map_num * 4)
    layout = ptr(rom, header)
    width = int.from_bytes(rom[layout:layout + 4], "little", signed=True)
    height = int.from_bytes(rom[layout + 4:layout + 8], "little", signed=True)
    return {
        "map_num": map_num,
        "header": header,
        "layout": layout,
        "width": width,
        "height": height,
        "map": ptr(rom, layout + 12),
        "primary": ptr(rom, layout + 16),
        "secondary": ptr(rom, layout + 20),
    }

def lz77(data: bytes, off: int, expected: int | None = None) -> bytes:
    if data[off] != 0x10:
        raise ValueError(f"not GBA LZ77 at {off:#x}: {data[off]:#x}")
    size = data[off + 1] | data[off + 2] << 8 | data[off + 3] << 16
    out = bytearray()
    pos = off + 4
    while len(out) < size:
        flags = data[pos]
        pos += 1
        for bit in range(7, -1, -1):
            if len(out) >= size:
                break
            if flags & (1 << bit):
                a, b = data[pos], data[pos + 1]
                pos += 2
                length = (a >> 4) + 3
                distance = (((a & 0xF) << 8) | b) + 1
                if distance > len(out):
                    raise ValueError("invalid GBA LZ77 back-reference")
                for _ in range(length):
                    out.append(out[-distance])
            else:
                out.append(data[pos])
                pos += 1
    if expected is None:
        return bytes(out)
    if len(out) < expected:
        out.extend(b"\0" * (expected - len(out)))
    return bytes(out[:expected])

def read_tileset(rom: bytes, address: int, secondary: bool) -> tuple[bytes, bytes, bytes]:
    compressed = rom[address]
    tiles_ptr = ptr(rom, address + 4)
    palettes_ptr = ptr(rom, address + 8)
    metatiles_ptr = ptr(rom, address + 12)
    tile_bytes = NUM_TILES_PRIMARY * 32
    tiles = lz77(rom, tiles_ptr, tile_bytes) if compressed else rom[tiles_ptr:tiles_ptr + tile_bytes]
    if secondary:
        palettes = rom[
            palettes_ptr + NUM_PALS_PRIMARY * 32:
            palettes_ptr + NUM_PALS_TOTAL * 32
        ]
    else:
        palettes = rom[palettes_ptr:palettes_ptr + NUM_PALS_PRIMARY * 32]
    metatiles = rom[metatiles_ptr:metatiles_ptr + NUM_METATILES_PRIMARY * 8 * 2]
    return tiles, palettes, metatiles

def gba_color(value: int) -> tuple[int, int, int, int]:
    return (
        (value & 31) * 255 // 31,
        ((value >> 5) & 31) * 255 // 31,
        ((value >> 10) & 31) * 255 // 31,
        255,
    )

def palettes_for_layout(rom: bytes, primary: int, secondary: int) -> list[list[tuple[int,int,int,int]]]:
    _, primary_palettes, _ = read_tileset(rom, primary, False)
    _, secondary_palettes, _ = read_tileset(rom, secondary, True)
    raw = bytearray(NUM_PALS_TOTAL * 32)
    raw[:len(primary_palettes)] = primary_palettes
    raw[NUM_PALS_PRIMARY * 32:NUM_PALS_PRIMARY * 32 + len(secondary_palettes)] = secondary_palettes
    # Emerald forces BG palette entry 0 to black.
    raw[0:2] = b"\0\0"
    result = []
    for palette in range(NUM_PALS_TOTAL):
        row = []
        for color in range(16):
            pos = (palette * 16 + color) * 2
            row.append(gba_color(int.from_bytes(raw[pos:pos + 2], "little")))
        result.append(row)
    return result

def decode_tile(raw: bytes) -> list[list[int]]:
    pixels = []
    for value in raw:
        pixels.extend((value & 0xF, value >> 4))
    return [pixels[y * 8:(y + 1) * 8] for y in range(8)]

def render_rgba(rom: bytes, map_bin: bytes, width: int, height: int, profile_map_num: int) -> tuple[int,int,bytes]:
    profile = emerald_map(rom, profile_map_num)
    primary_tiles, _, primary_metatiles = read_tileset(rom, profile["primary"], False)
    secondary_tiles, _, secondary_metatiles = read_tileset(rom, profile["secondary"], True)
    palettes = palettes_for_layout(rom, profile["primary"], profile["secondary"])
    ptiles = [decode_tile(primary_tiles[i * 32:(i + 1) * 32]) for i in range(512)]
    stiles = [decode_tile(secondary_tiles[i * 32:(i + 1) * 32]) for i in range(512)]
    cells = [x[0] for x in struct.iter_unpack("<H", map_bin)]
    if len(cells) != width * height:
        raise ValueError(f"map has {len(cells)} cells, expected {width}x{height}")
    out_width, out_height = width * 16, height * 16
    rgba = bytearray(out_width * out_height * 4)
    for pos in range(0, len(rgba), 4):
        rgba[pos + 3] = 255

    def draw_tile(px: int, py: int, entry: int, transparent: bool) -> None:
        tile_id = entry & 0x3FF
        hflip = bool(entry & 0x400)
        vflip = bool(entry & 0x800)
        palette_id = (entry >> 12) & 0xF
        if palette_id >= len(palettes):
            return
        tiles = ptiles if tile_id < 512 else stiles
        local_id = tile_id if tile_id < 512 else tile_id - 512
        if local_id >= len(tiles):
            return
        tile = tiles[local_id]
        for y in range(8):
            sy = 7 - y if vflip else y
            for x in range(8):
                sx = 7 - x if hflip else x
                color_id = tile[sy][sx]
                if transparent and color_id == 0:
                    continue
                r, g, b, a = palettes[palette_id][color_id]
                dst = ((py + y) * out_width + px + x) * 4
                rgba[dst:dst + 4] = bytes((r, g, b, a))

    for map_y in range(height):
        for map_x in range(width):
            metatile_id = cells[map_y * width + map_x] & 0x3FF
            if metatile_id < 512:
                start = metatile_id * 16
                raw = primary_metatiles[start:start + 16]
            else:
                start = (metatile_id - 512) * 16
                raw = secondary_metatiles[start:start + 16]
            if len(raw) != 16:
                continue
            entries = struct.unpack("<8H", raw)
            base_x, base_y = map_x * 16, map_y * 16
            # A static preview can flatten the two metatile layers: layer-type
            # differences only change which BG layer interacts with sprites.
            for layer in (0, 1):
                for quadrant in range(4):
                    draw_tile(
                        base_x + (quadrant & 1) * 8,
                        base_y + (quadrant >> 1) * 8,
                        entries[layer * 4 + quadrant],
                        transparent=(layer == 1),
                    )
    return out_width, out_height, bytes(rgba)

def png_bytes(width: int, height: int, rgba: bytes) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
        )
    rows = b"".join(
        b"\0" + rgba[y * width * 4:(y + 1) * width * 4]
        for y in range(height)
    )
    return (
        b"\x89PNG\r\n\x1a\n" +
        chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) +
        chunk(b"IDAT", zlib.compress(rows, 9)) +
        chunk(b"IEND", b"")
    )

def render_file(emerald_rom: Path, map_bin: Path, width: int, height: int, profile_map_num: int, output: Path) -> None:
    rom = emerald_rom.read_bytes()
    w, h, rgba = render_rgba(rom, map_bin.read_bytes(), width, height, profile_map_num)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(png_bytes(w, h, rgba))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emerald-rom", required=True, type=Path)
    ap.add_argument("--map-bin", required=True, type=Path)
    ap.add_argument("--width", required=True, type=int)
    ap.add_argument("--height", required=True, type=int)
    ap.add_argument("--profile-map-num", required=True, type=int,
                    help="Emerald group-0 map whose primary/secondary tileset pair matches the remake map")
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    render_file(args.emerald_rom, args.map_bin, args.width, args.height, args.profile_map_num, args.output)
    print(args.output)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

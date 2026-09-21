#!/usr/bin/env python3
"""Scan Japanese Gen I-III source ROMs without storing ROM binaries."""

from __future__ import annotations
import argparse, csv, hashlib, re, zlib
from pathlib import Path

CART = {
    0x03: "MBC1+RAM+BATTERY",
    0x10: "MBC3+TIMER+RAM+BATTERY",
    0x13: "MBC3+RAM+BATTERY",
}
RAM = {0x00: 0, 0x01: 2048, 0x02: 8192, 0x03: 32768, 0x04: 131072, 0x05: 65536}

def hashes(data: bytes):
    return hashlib.sha1(data).hexdigest(), hashlib.sha256(data).hexdigest(), f"{zlib.crc32(data)&0xffffffff:08x}"

def gb_row(path: Path, data: bytes):
    sha1, sha256, crc32 = hashes(data)
    h = 0
    for x in data[0x134:0x14D]:
        h = (h - x - 1) & 0xFF
    g = (sum(data[:0x14E]) + sum(data[0x150:])) & 0xFFFF
    stored_g = (data[0x14E] << 8) | data[0x14F]
    cgb, sgb, ctype, ram = data[0x143], data[0x146], data[0x147], data[0x149]
    return {
        "filename": path.name, "size_bytes": len(data), "sha1": sha1, "sha256": sha256, "crc32": crc32,
        "platform": "GB/GBC", "game_code": "", "header_version": data[0x14C],
        "cartridge": CART.get(ctype, f"0x{ctype:02X}"),
        "save_type": f"{RAM.get(ram,0)//1024} KiB SRAM" if RAM.get(ram,0) else "none",
        "rtc": "TIMER" in CART.get(ctype, ""), "cgb_mode": "CGB-only" if cgb == 0xC0 else "CGB-compatible" if cgb == 0x80 else "DMG",
        "sgb": sgb == 3, "header_checksum_ok": h == data[0x14D], "global_checksum_ok": g == stored_g,
    }

def gba_row(path: Path, data: bytes):
    sha1, sha256, crc32 = hashes(data)
    chk = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF
    strings = [m.group().decode("ascii", "ignore") for m in re.finditer(rb"[ -~]{6,}", data)]
    flash = next((s for s in strings if s.startswith("FLASH1M_")), "")
    rtc = next((s for s in strings if s.startswith("SIIRTC_")), "")
    return {
        "filename": path.name, "size_bytes": len(data), "sha1": sha1, "sha256": sha256, "crc32": crc32,
        "platform": "GBA", "game_code": data[0xAC:0xB0].decode("ascii", "replace"), "header_version": data[0xBC],
        "cartridge": "GBA Game Pak", "save_type": "128 KiB Flash" if flash else "unknown",
        "rtc": bool(rtc), "cgb_mode": "", "sgb": "", "header_checksum_ok": chk == data[0xBD], "global_checksum_ok": "",
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roms", nargs="+", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ns = ap.parse_args()
    rows = []
    for path in ns.roms:
        data = path.read_bytes()
        rows.append(gba_row(path, data) if path.suffix.lower() == ".gba" else gb_row(path, data))
    fields = list(rows[0])
    if ns.output:
        with ns.output.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    else:
        w = csv.DictWriter(__import__("sys").stdout, fieldnames=fields); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    main()

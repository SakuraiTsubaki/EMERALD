#!/usr/bin/env python3
from pathlib import Path
import csv, struct

ROOT = Path(".")
ROMS = [
    (1, "RED", "Aka", "Rev 0", "Pocket Monsters - Aka (Japan) (SGB Enhanced).gb", 0x3B427),
    (1, "RED", "Aka", "Rev A", "Pocket Monsters - Aka (Japan) (Rev A) (SGB Enhanced).gb", 0x3B427),
    (1, "GREEN", "Midori", "Rev 0", "Pocket Monsters - Midori (Japan) (SGB Enhanced).gb", 0x3B427),
    (1, "GREEN", "Midori", "Rev A", "Pocket Monsters - Midori (Japan) (Rev A) (SGB Enhanced).gb", 0x3B427),
    (1, "BLUE", "Ao", "Rev 0", "Pocket Monsters - Ao (Japan) (SGB Enhanced).gb", 0x3B427),
    (1, "YELLOW", "Pikachu", "Rev 0A", "Pocket Monsters - Pikachu (Japan) (Rev 0A) (SGB Enhanced).gb", 0x3B59C),
    (1, "YELLOW", "Pikachu", "Rev B", "Pocket Monsters - Pikachu (Japan) (Rev B) (SGB Enhanced).gb", 0x3B59C),
    (1, "YELLOW", "Pikachu", "Rev C", "Pocket Monsters - Pikachu (Japan) (Rev C) (SGB Enhanced).gb", 0x3B59C),
    (1, "YELLOW", "Pikachu", "Rev D", "Pocket Monsters - Pikachu (Japan) (Rev D) (SGB Enhanced).gb", 0x3B59C),
    (2, "GOLD", "Kin", "Rev 0", "Pocket Monsters Kin (Japan).gbc", 0x4295F),
    (2, "GOLD", "Kin", "Rev A", "Pocket Monsters Kin (Japan) (Rev A).gbc", 0x4295F),
    (2, "SILVER", "Gin", "Rev 0", "Pocket Monsters Gin (Japan).gbc", 0x4295F),
    (2, "SILVER", "Gin", "Rev A", "Pocket Monsters Gin (Japan) (Rev A).gbc", 0x4295F),
    (2, "CRYSTAL", "Crystal", "Rev 0", "Pocket Monsters - Crystal Version (Japan).gbc", 0x42753),
]
GBA = [
    ("RUBY", "Ruby", "Rev 0", "Pocket Monsters - Ruby (Japan).gba", 0x1D591C, 0x1D997C),
    ("SAPPHIRE", "Sapphire", "Rev 0", "Pocket Monsters - Sapphire (Japan).gba", 0x1D58AC, 0x1D990C),
    ("EMERALD", "Emerald", "Rev 0", "Pocket Monsters - Emerald (Japan).gba", 0x2F5CA4, 0x2F9D04),
    ("FIRERED", "FireRed", "Rev 0", "Pocket Monsters - Fire Red (Japan).gba", 0x21615C, 0x21A1BC),
    ("FIRERED", "FireRed", "Rev 1", "Pocket Monsters - Fire Red (Japan) (Rev 1).gba", 0x211974, 0x2159D4),
    ("LEAFGREEN", "LeafGreen", "Rev 0", "Pocket Monsters - Leaf Green (Japan).gba", 0x21613C, 0x21A19C),
]

def ptr_to_offset(table_off, ptr):
    bank_base = (table_off // 0x4000) * 0x4000
    return bank_base + ptr - 0x4000

def parse_gen1_record(data, off):
    evos, p = [], off
    while data[p]:
        method = data[p]
        if method == 1:
            evos.append((method, data[p+1], data[p+2], None)); p += 3
        elif method == 2:
            evos.append((method, data[p+1], data[p+3], data[p+2])); p += 4
        elif method == 3:
            evos.append((method, data[p+1], data[p+2], None)); p += 3
        else:
            raise ValueError(("gen1 evolution method", method, hex(p)))
    p += 1
    learn = []
    while data[p]:
        learn.append((data[p], data[p+1])); p += 2
    return evos, learn

def parse_gen2_record(data, off):
    evos, p = [], off
    while data[p]:
        method = data[p]
        if method in (1, 2, 3, 4):
            evos.append((method, data[p+1], data[p+2], None)); p += 3
        elif method == 5:
            evos.append((method, data[p+1], data[p+3], data[p+2])); p += 4
        else:
            raise ValueError(("gen2 evolution method", method, hex(p)))
    p += 1
    learn = []
    while data[p]:
        learn.append((data[p], data[p+1])); p += 2
    return evos, learn

def main():
    evo_rows, learn_rows = [], []
    for gen, project, title, rev, filename, pointer_table in ROMS:
        data = (ROOT / filename).read_bytes()
        count = 190 if gen == 1 else 251
        for species in range(1, count + 1):
            ptr = struct.unpack_from("<H", data, pointer_table + (species - 1) * 2)[0]
            off = ptr_to_offset(pointer_table, ptr)
            evos, learn = parse_gen1_record(data, off) if gen == 1 else parse_gen2_record(data, off)
            for slot, (method, param, target, extra) in enumerate(evos):
                evo_rows.append([gen, project, title, rev, filename, species, slot, method, param, target, "" if extra is None else extra])
            for slot, (level, move) in enumerate(learn):
                learn_rows.append([gen, project, title, rev, filename, species, slot, level, move])

    for project, title, rev, filename, evo_off, learn_off in GBA:
        data = (ROOT / filename).read_bytes()
        for species in range(1, 412):
            for slot in range(5):
                method, param, target, pad = struct.unpack_from("<HHHH", data, evo_off + (species * 5 + slot) * 8)
                if method:
                    evo_rows.append([3, project, title, rev, filename, species, slot, method, param, target, pad])
            ptr = struct.unpack_from("<I", data, learn_off + species * 4)[0]
            off = ptr & 0x1FFFFFF
            slot = 0
            while True:
                value = struct.unpack_from("<H", data, off)[0]; off += 2
                if value == 0xFFFF:
                    break
                learn_rows.append([3, project, title, rev, filename, species, slot, value >> 9, value & 0x1FF])
                slot += 1

    with open("japan-20-evolutions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["generation","project","title","revision","filename","species_id","slot","method","parameter","target_species","extra"])
        w.writerows(evo_rows)

    with open("japan-20-levelup-learnsets.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["generation","project","title","revision","filename","species_id","slot","level","move_id"])
        w.writerows(learn_rows)

if __name__ == "__main__":
    main()

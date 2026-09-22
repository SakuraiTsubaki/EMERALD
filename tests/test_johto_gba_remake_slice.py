#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "johto-gba-remake-slice"
MAP_PATH = ARTIFACT_DIR / "new_bark_town.map.bin"
MANIFEST_PATH = ARTIFACT_DIR / "new_bark_town.remake.json"
LOGICAL_MAP_PATH = ROOT / "artifacts" / "johto-gba-first-slice" / "new_bark_town.map.bin"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_u16_le(data: bytes) -> list[int]:
    if len(data) % 2:
        raise AssertionError("map data must contain an even number of bytes")
    return [x[0] for x in struct.iter_unpack("<H", data)]


class JohtoGbaRemakeSliceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.data = MAP_PATH.read_bytes()
        cls.cells = read_u16_le(cls.data)
        cls.width = cls.manifest["target"]["width"]
        cls.height = cls.manifest["target"]["height"]

    def cell(self, x: int, y: int) -> int:
        return self.cells[y * self.width + x]

    def metatile_id(self, x: int, y: int) -> int:
        return self.cell(x, y) & 0x03FF

    def test_target_geometry_and_hash(self) -> None:
        target = self.manifest["target"]
        self.assertEqual((self.width, self.height), (20, 18))
        self.assertEqual(len(self.data), 720)
        self.assertEqual(len(self.cells), self.width * self.height)
        self.assertEqual(target["bytes"], len(self.data))
        self.assertEqual(target["sha256"], sha256(self.data))
        self.assertTrue(all(0 <= (v & 0x03FF) <= 0x03FF for v in self.cells))

    def test_actual_emerald_donor_door_anchors(self) -> None:
        # Japanese Emerald Littleroot exterior door metatiles, preserving GSC warp anchors.
        self.assertEqual(self.metatile_id(6, 3), 0x249)  # Birch lab exterior door
        for x, y in ((13, 5), (3, 11), (11, 13)):
            with self.subTest(x=x, y=y):
                self.assertEqual(self.metatile_id(x, y), 0x248)  # Littleroot house door
        self.assertEqual(self.manifest["preserved_warp_anchors"], [[6, 3], [13, 5], [3, 11], [11, 13]])

    def test_emerald_sign_art_and_documented_relocation(self) -> None:
        for x, y in self.manifest["target_signs"]:
            with self.subTest(x=x, y=y):
                self.assertEqual(self.metatile_id(x, y), 0x003)
        self.assertEqual(
            self.manifest["event_relocations"],
            [{
                "kind": "bg/sign",
                "source": [3, 3],
                "target": [5, 4],
                "reason": "Emerald Birch-lab exterior footprint",
            }],
        )

    def test_remake_is_not_the_old_gsc_quadrant_map(self) -> None:
        logical = LOGICAL_MAP_PATH.read_bytes()
        self.assertNotEqual(self.data, logical)
        logical_cells = read_u16_le(logical)
        # The old geometry proof can be losslessly collapsed to one GSC block byte
        # per 2x2 quartet. The remake must deliberately break that block*4 scheme.
        old_scheme_quartets = 0
        remake_scheme_quartets = 0
        for y in range(0, self.height, 2):
            for x in range(0, self.width, 2):
                i = y * self.width + x
                for cells, attr in ((logical_cells, "old"), (self.cells, "new")):
                    q = tuple(cells[j] & 0x03FF for j in (i, i + 1, i + self.width, i + self.width + 1))
                    base = q[0]
                    matches = base % 4 == 0 and q == (base, base + 1, base + 2, base + 3)
                    if attr == "old":
                        old_scheme_quartets += int(matches)
                    else:
                        remake_scheme_quartets += int(matches)
        self.assertEqual(old_scheme_quartets, (self.width // 2) * (self.height // 2))
        self.assertLess(remake_scheme_quartets, old_scheme_quartets // 4)

    def test_remake_contains_real_secondary_donor_metatiles(self) -> None:
        ids = [v & 0x03FF for v in self.cells]
        self.assertGreater(sum(i >= 0x200 for i in ids), 50)
        for expected in (0x248, 0x249, 0x217, 0x234, 0x20F):
            self.assertIn(expected, ids)

    def test_manifest_pins_japanese_rom_evidence_without_paths(self) -> None:
        self.assertEqual(
            self.manifest["source"]["gsc_rom_sha256"],
            "7cfeceae00737a1f0713c9ab0b3a9e6eb8d05ff6002eb81308072a6f85e385e7",
        )
        self.assertEqual(
            self.manifest["emerald"]["rom_sha256"],
            "33f5610b9186b4add09fef68895deb00f552b997b3d133b5a961e5123506343c",
        )
        self.assertEqual(
            self.manifest["source"]["block_sha256"],
            "41a1012a051d22ade1b6cdb14577c4b6ad3e195be7024d6f3a020a9f7f5fedd3",
        )
        raw = MANIFEST_PATH.read_text(encoding="utf-8")
        self.assertNotIn("/mnt/data", raw)
        self.assertNotIn(".gbc", raw)
        self.assertNotIn(".gba", raw)

    def test_policy_explicitly_rejects_gsc_graphics_as_output(self) -> None:
        policy = self.manifest["policy"]
        self.assertIn("GSC topology/semantics", policy)
        self.assertIn("Japanese Emerald visual/behavior donors", policy)
        self.assertIn("no GSC graphics are emitted", policy)


if __name__ == "__main__":
    unittest.main()

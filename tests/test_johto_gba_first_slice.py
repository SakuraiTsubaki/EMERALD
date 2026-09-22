#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "manifests" / "johto-gba-first-slice.json"
EXTRACT_PATH = ROOT / "manifests" / "johto-gba-first-slice-extracted.json"

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_u16_le(data: bytes) -> list[int]:
    if len(data) % 2:
        raise AssertionError("GBA map data must contain an even number of bytes")
    return [x[0] for x in struct.iter_unpack("<H", data)]

def reconstruct_source_blocks(values: list[int], width: int, height: int) -> bytes:
    if width % 2 or height % 2:
        raise AssertionError("expanded dimensions must be even")
    out = bytearray()
    for y in range(0, height, 2):
        for x in range(0, width, 2):
            i = y * width + x
            quad = (values[i], values[i + 1], values[i + width], values[i + width + 1])
            base = quad[0]
            if base % 4 != 0:
                raise AssertionError(f"NW logical metatile {base} is not block-aligned")
            if quad != (base, base + 1, base + 2, base + 3):
                raise AssertionError(f"bad logical-metatile quartet at ({x}, {y}): {quad}")
            block = base // 4
            if not 0 <= block <= 0xFF:
                raise AssertionError(f"reconstructed source block out of byte range: {block}")
            out.append(block)
    return bytes(out)

class JohtoGbaFirstSliceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
        cls.extract = json.loads(EXTRACT_PATH.read_text(encoding="utf-8"))
        cls.spec_maps = {m["id"]: m for m in cls.spec["maps"]}
        cls.extract_maps = {m["id"]: m for m in cls.extract["maps"]}

    def test_map_sets_match(self) -> None:
        self.assertEqual(set(self.spec_maps), set(self.extract_maps))

    def test_generated_map_geometry_roundtrips_to_direct_rom_blocks(self) -> None:
        for map_id, result in self.extract_maps.items():
            with self.subTest(map=map_id):
                target = result["target"]
                data = (ROOT / target["file"]).read_bytes()
                self.assertEqual(len(data), target["bytes"])
                self.assertEqual(sha256(data), target["sha256"])
                self.assertEqual(len(data), target["widthMetatiles"] * target["heightMetatiles"] * 2)
                values = read_u16_le(data)
                self.assertTrue(all(0 <= value <= 0x03FF for value in values))
                source = reconstruct_source_blocks(values, target["widthMetatiles"], target["heightMetatiles"])
                self.assertEqual(len(source), result["source"]["blockBytes"])
                self.assertEqual(sha256(source), result["source"]["blockSha256"])

    def test_all_five_japanese_revisions_agree_semantically(self) -> None:
        expected_roms = set(self.spec["sourceRoms"])
        for map_id, result in self.extract_maps.items():
            with self.subTest(map=map_id):
                rev = result["revisionEvidence"]
                self.assertTrue(rev["allFiveJapaneseRevisionsAgree"])
                self.assertEqual(set(rev["offsets"]), expected_roms)
                self.assertEqual(len(rev["semanticTopologySha256"]), 64)

    def test_event_counts_and_coordinates_match_spec_and_bounds(self) -> None:
        for map_id, result in self.extract_maps.items():
            with self.subTest(map=map_id):
                spec = self.spec_maps[map_id]
                target = result["target"]
                for kind in ("warps", "coord", "bg", "objects"):
                    self.assertEqual(len(result["events"][kind]), spec["events"][kind])
                    for event in result["events"][kind]:
                        self.assertGreaterEqual(event["x"], 0)
                        self.assertGreaterEqual(event["y"], 0)
                        self.assertLess(event["x"], target["widthMetatiles"])
                        self.assertLess(event["y"], target["heightMetatiles"])

    def test_connection_offset_conversion_matches_spec(self) -> None:
        for map_id, result in self.extract_maps.items():
            with self.subTest(map=map_id):
                expected = {row["direction"]: row for row in self.spec_maps[map_id]["connections"]}
                actual = {row["direction"]: row for row in result["connections"]}
                self.assertEqual(set(actual), set(expected))
                for direction, row in actual.items():
                    self.assertEqual(row["sourceOffsetBlocks"], expected[direction]["sourceOffset"])
                    self.assertEqual(row["targetOffsetMetatiles"], expected[direction]["targetOffset"])
                    self.assertEqual(row["targetOffsetMetatiles"], row["sourceOffsetBlocks"] * 2)

    def test_generated_manifest_contains_no_local_rom_paths(self) -> None:
        raw = EXTRACT_PATH.read_text(encoding="utf-8")
        self.assertNotIn("/mnt/data", raw)
        self.assertNotIn("\\", raw)

if __name__ == "__main__":
    unittest.main()

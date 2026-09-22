#!/usr/bin/env python3
import unittest
from tools.render_johto_gba_map_preview import lz77, png_bytes

class PreviewRendererTest(unittest.TestCase):
    def test_literal_lz77(self):
        # 0x10 header, 3-byte output, flag byte 0 => three literals.
        data = bytes((0x10, 3, 0, 0, 0, ord("A"), ord("B"), ord("C")))
        self.assertEqual(lz77(data, 0), b"ABC")

    def test_png_signature(self):
        image = png_bytes(1, 1, bytes((1, 2, 3, 255)))
        self.assertTrue(image.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertIn(b"IHDR", image)
        self.assertTrue(image.endswith(b"IEND\xaeB\x60\x82"))

if __name__ == "__main__":
    unittest.main()

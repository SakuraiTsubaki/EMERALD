#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "korean_text_codec.py"
spec = importlib.util.spec_from_file_location("korean_text_codec", TOOL)
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)

assert codec.encode_codepoint(ord("가")) == bytes.fromhex("FC 19 00 AC")
assert codec.encode_codepoint(ord("힣")) == bytes.fromhex("FC 19 A3 D7")
assert codec.encode_codepoint(ord("ㄱ")) == bytes.fromhex("FC 19 31 31")

sample = "가나다라"
encoded = codec.encode_text(sample, terminate=True)
assert encoded == bytes.fromhex(
    "FC 19 00 AC "
    "FC 19 98 B0 "
    "FC 19 E4 B2 "
    "FC 19 3C B7 "
    "FF"
)
assert codec.decode_korean_stream(encoded) == sample

# Payload bytes are opaque after FC 19. A low byte of FF must not act as EOS.
cp = 0xACFF
token = codec.encode_codepoint(cp)
assert token[2] == 0xFF
assert codec.decode_token(token) == chr(cp)

try:
    codec.encode_text("A")
except ValueError:
    pass
else:
    raise AssertionError("stock Emerald characters must not enter Korean codec")

assert codec.MODERN_END - codec.MODERN_START + 1 == 11172
assert codec.JAMO_END - codec.JAMO_START + 1 == 51
print("ALL KOREAN TEXT CODEC TESTS PASSED")

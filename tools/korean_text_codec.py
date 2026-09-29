#!/usr/bin/env python3
"""Codec helpers for the EMERALD Korean text-token extension.

The engine token is FC 19 LL HH where LL/HH are the little-endian bytes of a
BMP Unicode code point. This tool does not replace the stock pokeemerald
charmap; it generates/validates Korean token bytes for build-time assets and
tests while preserving the stock single-byte and control-code namespaces.
"""
from __future__ import annotations

import argparse
from pathlib import Path

PREFIX = 0xFC
KOREAN_CODE = 0x19
EOS = 0xFF
MODERN_START = 0xAC00
MODERN_END = 0xD7A3
JAMO_START = 0x3131
JAMO_END = 0x3163


def is_supported_codepoint(cp: int) -> bool:
    return MODERN_START <= cp <= MODERN_END or JAMO_START <= cp <= JAMO_END


def encode_codepoint(cp: int) -> bytes:
    if not is_supported_codepoint(cp):
        raise ValueError(f"unsupported Korean code point U+{cp:04X}")
    return bytes((PREFIX, KOREAN_CODE, cp & 0xFF, cp >> 8))


def encode_text(text: str, *, terminate: bool = False) -> bytes:
    out = bytearray()
    for ch in text:
        cp = ord(ch)
        if not is_supported_codepoint(cp):
            raise ValueError(
                f"non-Korean character {ch!r} U+{cp:04X}; "
                "encode stock Emerald characters with the stock charmap"
            )
        out += encode_codepoint(cp)
    if terminate:
        out.append(EOS)
    return bytes(out)


def decode_token(token: bytes) -> str:
    if len(token) != 4 or token[0] != PREFIX or token[1] != KOREAN_CODE:
        raise ValueError("not an FC 19 Korean token")
    cp = token[2] | (token[3] << 8)
    if not is_supported_codepoint(cp):
        raise ValueError(f"unsupported Korean token U+{cp:04X}")
    return chr(cp)


def decode_korean_stream(data: bytes, *, allow_eos: bool = True) -> str:
    out = []
    i = 0
    while i < len(data):
        if allow_eos and data[i] == EOS:
            if i != len(data) - 1:
                raise ValueError("data follows EOS")
            break
        if i + 4 > len(data):
            raise ValueError("truncated Korean token")
        out.append(decode_token(data[i:i + 4]))
        i += 4
    return "".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("text", nargs="?")
    ap.add_argument("--text-file")
    ap.add_argument("--output", "-o")
    ap.add_argument("--terminate", action="store_true")
    ap.add_argument("--hex", action="store_true")
    args = ap.parse_args()

    if (args.text is None) == (args.text_file is None):
        ap.error("provide exactly one of TEXT or --text-file")

    text = args.text
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")

    encoded = encode_text(text, terminate=args.terminate)
    if args.output:
        Path(args.output).write_bytes(encoded)
    if args.hex or not args.output:
        print(encoded.hex(" ").upper())


if __name__ == "__main__":
    main()

# Emerald Korean text engine — implementation baseline

Reference upstream: `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`

## Encoding

Korean printable characters use a dedicated four-byte token:

```text
FC 19 LL HH
```

`LL HH` is a little-endian BMP Unicode code point. The first supported ranges are:

- modern precomposed Hangul: U+AC00..U+D7A3 (11,172 syllables)
- KS X 1001 compatibility jamo source range: U+3131..U+3163 (51 code points)

The payload is opaque after `FC 19`; a payload byte equal to `FF` is not an EOS marker.

This allocation preserves the stock top-level byte namespace:

- F7 CHAR_DYNAMIC
- F8 CHAR_KEYPAD_ICON
- F9 CHAR_EXTRA_SYMBOL
- FA/FB prompt controls
- FC existing extended-control prefix
- FD placeholder prefix
- FE newline
- FF EOS

It also leaves the stock Japanese single-byte glyph space untouched. `0x19` is allocated only as a new subcode under `FC`; the pinned upstream defines extended controls through `0x18`.

## Engine touch points

The implementation patch must keep Korean tokens coherent in:

- `RenderText`
- `GetStringWidth`, including dynamic placeholder strings
- `RenderTextHandleBold`
- `StringExpandPlaceholders`
- `StringCopyN_Multibyte`
- `StringLength_Multibyte`
- `GetExtCtrlCodeLength`
- `SkipExtCtrlCode` / `StringCompareWithoutExtCtrlCodes`
- `StripExtCtrlCodes`

Ordinary `StringCopy` and `StringAppend` already preserve arbitrary bytes and do not need Korean-specific logic.

## 16-pixel rendering compatibility

Emerald's `TextGlyph` is already four 8x8 quadrants wide enough for a 16x16 glyph. Its normal >8-pixel source path consumes four 16-byte packed 2bpp tiles (64 bytes per glyph).

The Generation IV Korean font glyphs use the same 16x16/four-tile/64-byte packed organization. Emerald's glyph decompressor maps source 2-bit values 1 and 2 to foreground and shadow while treating 0/3 as background, matching the semantics required by the extracted Gen IV font pixels. Therefore the official Gen IV 64-byte glyph blocks can be used without vector rerasterization.

## Smoke slice

`patches/pokeemerald/0003-korean-multibyte-text-core-smoke.patch` embeds only four byte-exact Korean SoulSilver MESSAGE/member-1 glyphs:

- 가 U+AC00, source slot 1024
- 나 U+B098, source slot 1315
- 다 U+B2E4, source slot 1456
- 라 U+B77C, source slot 1670

The smoke fixture exists only to prove the token parser and 16x16 renderer on the pinned upstream. Unsupported Korean code points deliberately fall back to the stock question-mark glyph.

This is **not** the final glyph payload. The full integration replaces the sparse smoke lookup with generated full-modern tables whose provenance is recorded per glyph:

- 2,350 Wansung syllables: official Gen IV source pixels where available
- remaining modern syllables: explicitly marked project-derived glyphs
- compatibility jamo: official mapped Gen IV source where applicable

## Width policy

Confirmed Generation IV Korean fixed advances:

- Emerald FONT_NORMAL source / Gen IV member 1: 12 px
- FONT_SMALL / member 0: 11 px
- FONT_SHORT / member 2: 13 px
- FONT_NARROW project mapping / HGSS member 10: 11 px
- HGSS auxiliary UI member 4: 12 px

The smoke fixture currently validates FONT_NORMAL/member 1. Other font families are connected when their full generated assets are staged.

## Verification

`.github/workflows/korean-text-core.yml` performs, in order:

1. Python codec tests, including payload byte `FF` inside a Korean token.
2. Checkout of the exact pinned pokeemerald commit.
3. `git apply --check` and actual application of patch 0003.
4. symbol-presence checks.
5. a modern-toolchain build of the patched upstream.

Passing the apply check proves patch/revision compatibility; passing the build proves the current C implementation compiles and links. Runtime/mGBA rendering validation remains a separate next gate.

# Korean font census baseline

Date: 2026-09-22

This document records the current Korean font evidence used by EMERALD. It separates observed ROM facts, repository-derived assets, and still-unresolved implementation details.

## 1. Existing Korean material already imported into EMERALD

EMERALD already contains the Generation II Korean research and implementation subset under:

- imports/korean-localization/sakurai/
- imports/korean-localization/tsubaki/

The imported Sakurai material includes the GS Korean implementation phases, ROM-derived Korean charmap, official-name comparison material, Pokédex text, move text, item text, and current-name comparisons.

The imported Tsubaki material includes pokegold-kr implementation files such as the Korean charmap tables, Hangul constants/structure tables, gfx/hangul.asm, gfx/font.asm, and the Korean font-loading routines.

No Generation IV Korean font archive was found inside EMERALD at the time of this census.

## 2. Generation II Korean Gold / Silver

Direct ROM evidence and the Tsubaki/Sakurai preserved material agree on the following baseline.

- glyph cell: 8x16
- source representation: 1bpp
- bytes per glyph: 16
- ROM source region: 0x1E0000
- source banks: 0x78, 0x79, 0x7A
- source region size: 49,152 bytes
- raw slots: 3,072
- raw font-region SHA-1: 6e986d357a31a3fb5114c459a8e1f20163544eea
- Korean charmap is split across multiple two-byte pages and the runtime dynamically stages Hangul into VRAM.

Tsubaki canonical source:
GEN-02/GOLD/RELEASES/GBC/CART/AAUK-HV0/ASSETS/FONTS/GS-KOREAN-HANGUL-11TABLES/

Gold and Silver preserved copies are byte-identical according to:
CROSS-GEN/PROJECTS/GS-KOREAN-TO-POCKET-MONSTERS/CATALOGS/HANGUL-FONT-EQUALITY.json

## 3. Existing Generation III Korean tooling

Tsubaki already contains a Hangul glyph generator originally attached to the FireRed Korean-localization work:

GEN-03/FIRERED/PROJECTS/FIRERED-KR-LOCALIZATION/TOOLS/HANGUL-GLYPH-GENERATOR/

Its full-build manifest covers all modern precomposed Hangul syllables U+AC00..U+D7A3:

- 11,172 glyphs
- 8x8 and 16x16 atlases
- 1bpp output
- Game Boy-compatible 2bpp output
- Unicode/internal-ID mapping CSV and JSON
- subset generation and manual pixel overrides

This tool is useful as a coverage/fallback generator. It is not itself an official Pokémon Korean font source, because it rasterizes a system Korean font.

## 4. Generation IV direct ROM font census

### Platinum Korean (CPUK)

graphic/font.narc:
- ROM file size: 759,840 bytes
- SHA-1: 2b7218f8040f1fbdecd09eb8a0c916280911f012
- 10 members
- members 0/1/2: 3,440 glyphs each, 16x16, 64 bytes per glyph
- member 3: 509 glyphs, 16x16
- members 4-7: special-character / indicator / palette-class resources matching the normal Gen IV font archive layout
- members 8/9: Korean-release extension data; exact field semantics remain to be named from Korean executable code

graphic/pl_font.narc:
- ROM file size: 759,912 bytes
- SHA-1: bafa19e07e32984a8de280ef6ba633abb7f3da5e
- 10 members
- members 0/1/2: 3,440 glyphs each, 16x16
- member 3: 509 glyphs, 16x16
- the full members 0/1/2 differ from graphic/font.narc in their legacy/base region, but the Korean extension slots 1024..3439 are byte-identical between corresponding members. Platinum therefore keeps two archive variants while reusing the Korean glyph artwork byte-for-byte.

pret/pokeplatinum res/fonts/pl_font.order identifies the ordinary archive roles as:
0 system, 1 message, 2 subscreen, 3 Unown, followed by special characters, screen indicators, and palettes.

### SoulSilver Korean (IPGK)

Main HGSS font archive:
- filesystem path: a/0/1/6
- ROM file size: 1,201,508 bytes
- SHA-1: 20ba4bc2539851285e5426084c02f01498d789b4
- 13 members

HGSS executable-side font mapping in pret/pokeheartgold maps six Font IDs to archive members:
0, 1, 2, 3, 4, 10.

Observed Korean member sizes:
- 0: 3,440 glyphs, 16x16
- 1: 3,440 glyphs, 16x16
- 2: 3,440 glyphs, 16x16
- 3: 509 glyphs, 16x16; same Unown member SHA-1 as Korean Platinum
- 4: 3,440 glyphs, 16x16
- 10: 3,440 glyphs, 16x16

SoulSilver also contains:
pbr/font.narc

This archive has SHA-1 2b7218f8040f1fbdecd09eb8a0c916280911f012 and is byte-identical to Korean Platinum graphic/font.narc.

### Diamond / Pearl USA baseline

The supplied USA Diamond and Pearl ROMs contain byte-identical graphic/font.narc archives:
- size: 134,744 bytes
- SHA-1: 1122e901209b1047fbbacb1a47311c8bd529a647
- 8 members
- members 0/1/2/3 contain 509 glyphs

This is useful as a non-Korean baseline for identifying exactly which archive structures were enlarged or extended in the Korean releases. It is not a substitute for Korean Diamond/Pearl ROM evidence.

## 5. Korean large-font tail structure

For a 3,440-glyph 16x16 member:

- file header: 16 bytes
- glyph bitmap payload: 3,440 x 64 = 220,160 bytes
- width/extension start recorded in header: 220,176
- remaining tail: 541 bytes

The 541-byte tail and the Korean executable-side width routine are now decoded.

- +0x00: u32 payload size
- +0x04: u32 range count = 3
- +0x08: three 8-byte descriptors: u16 endExclusive, s16 widthModeOrValue, u32 tableOffset
- +0x20: 509 one-byte legacy widths

Runtime semantics, confirmed in both Korean Platinum and SoulSilver ARM9:
- 0xFFFF (-1): use the per-glyph width table
- 0xFFFE (-2): recursively use fallback glyph slot 0x01AB
- any other selector: return it directly as the fixed advance width

The localized 3,440-glyph members therefore use:
- slots 0..508: variable legacy widths
- slots 509..1023: fallback width
- slots 1024..3439: fixed Korean advance

Fixed Korean advances are member 0 = 11 px, member 1 = 12 px, member 2 = 13 px, member 4 = 12 px, and member 10 = 11 px.

The corresponding range-width function bodies are byte-identical between the supplied Korean Pt and SoulSilver executables (Pt runtime 0x02023AD4, SoulSilver runtime 0x02026514).

## 6. Separate shared font graphics

The supplied DP, Platinum Korean, and SoulSilver Korean ROMs all contain:

- data/nfont.NCGR: 32,816 bytes, SHA-1 5d5c14fcfa0f8534c2eec79ffa945d01f4c547b4
- data/nfont.NCLR: 552 bytes, SHA-1 9eae4f97e9e97b6cd427c95def1c166ea868da43

These are separate graphics/palette resources and must not be conflated with the main text-font NARC.

DP/Pt also contain graphic/fontoam.narc, a separate cell/OAM-related font resource.

## 7. EMERALD integration consequence

Use three independent sources rather than replacing one with another:

1. Generation II Korean Gold/Silver:
   runtime strategy reference for constrained hardware and Korean character paging/caching.

2. Generation IV Korean Platinum/HGSS:
   official Pokémon Korean bitmap-design reference and official Korean-era text rendering behavior.

3. Generation III Emerald:
   target renderer, Font IDs, menu geometry, width calculation, wrapping, and save/text constraints.

The Generation III Hangul generator is a full-coverage fallback and tooling base, not the visual master.

For Korean final strings, terminology should follow the project's current rule: latest official Korean names/terms are the implementation target, while Generation II/IV historical Korean wording is retained as provenance and comparison data.

## 8. Confirmed Korean character mapping and HGSS FontID roles

Localized message decryption in the supplied Korean Pt and SoulSilver ROMs confirms `glyph_slot = message_code - 1`.

- slots 1024..3373: 2,350 KS X 1001/Wansung syllables, EUC-KR B0A1..C8FE row-major
- slots 3376..3426: 51 KS X 1001 compatibility jamo, EUC-KR A4A1..A4D3
- slots 3427..3428: real non-fallback glyphs, identity still unresolved
- all other previously identified gap/tail slots remain fallback/unmapped

Species-name tables cross-check this directly in both games (이상해씨, 피카츄, 치코리타, 아르세우스).

The supplied Korean SoulSilver ARM9 plus all 129 ARM9 overlays were scanned for `FontID_Alloc`. All 83 call sites resolve statically:
- FontID 0: 1
- FontID 1: 1
- FontID 2: 13
- FontID 3: 1
- FontID 4: 65
- FontID 5: 2

FontID 5 / member 10 is not unused. Its two allocations are in OVY_112, the Pokéwalker connection application, where it is used for player-name and related Pokéwalker UI-string rendering. FontID 4 is a broad application/UI font.

## 9. Emerald integration status

The Gen IV-to-Emerald source mapping is now fixed for the first implementation pass:
- FONT_NORMAL <- member 1 / MESSAGE, 12 px advance
- FONT_SMALL <- member 0 / SYSTEM, 11 px advance
- FONT_SHORT <- member 2 / SUBSCREEN, 13 px advance
- FONT_NARROW <- member 10 / HGSS FontID 5 as a project mapping; original use remains Pokéwalker UI, 11 px advance
- FONT_SMALL_NARROW <- explicit project-derived compact variant
- member 4 is retained as an optional official HGSS application/UI source

The shared Hangul generator now accepts exact Gen IV source packs and preserves official 16x16 2bpp bytes for covered glyphs while labeling non-covered modern Hangul as project-derived.

Next executable target is the Emerald text engine: add a non-colliding multi-byte Korean token, 16-pixel Korean glyph lookup/rendering, and coherent byte-walking in width/copy/length/placeholder helpers without replacing existing Latin/Japanese behavior.

## 10. Still required

- add direct Korean Diamond/Pearl and HeartGold retail ROM evidence when supplied/available
- identify the two non-fallback slots 3427..3428
- publish the non-ROM Gen IV source-glyph asset pack to Tsubaki
- implement and build-test the Emerald multi-byte Korean text-engine patch across the target profiles/versions

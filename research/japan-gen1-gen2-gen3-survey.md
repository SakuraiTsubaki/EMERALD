# JAPAN Generation I-III ROM survey

This is the shared evidence baseline for the GBA remake work.

## Scope

- Generation I: 9 Japanese ROMs — Aka 2, Midori 2, Ao 1, Pikachu 4.
- Generation II: 5 Japanese ROMs — Kin 2, Gin 2, Crystal 1.
- Generation III: 6 Japanese ROMs — Ruby, Sapphire, Emerald, FireRed Rev 0/1, LeafGreen.
- Total: 20 ROMs.

Original ROM binaries remain local and are not committed.

## Verified hardware boundary

### Generation I

Aka, Midori and Ao are 512 KiB MBC1+RAM+BATTERY / 32 KiB SRAM / SGB profiles.
Pikachu is a 1 MiB MBC3+RAM+BATTERY / 32 KiB SRAM / SGB profile. Its four Japanese inputs map to header versions 0, 1, 2 and 3.

### Generation II

Kin and Gin are 1 MiB CGB-compatible MBC3+TIMER+RAM+BATTERY / 32 KiB SRAM profiles and retain SGB support.
Japanese Crystal is 2 MiB, CGB-only, RTC-equipped and exposes the 64 KiB SRAM profile associated with the Japanese Crystal MBC30-compatible arrangement.

### Generation III

Ruby/Sapphire are 8 MiB GBA images. Emerald/FireRed/LeafGreen are 16 MiB.
All six contain `FLASH1M_V103`, identifying the 128 KiB Flash save library.
Ruby, Sapphire and Emerald also contain `SIIRTC_V001`; FireRed and LeafGreen do not.
Japanese GBA game codes are AXVJ, AXPJ, BPEJ, BPRJ and BPGJ.

All 20 inputs passed their applicable ROM/header checksum validation.

## Why all three generations are investigated together

Generation I and II define the source games that RED/GREEN/BLUE/YELLOW/GOLD/SILVER/CRYSTAL must preserve.
Generation III defines the GBA execution boundary and data/runtime architecture.
FireRed/LeafGreen additionally provide the official Generation-I-to-GBA remake reference.

The project therefore does not treat Gen III as a later implementation detail. Source extraction and GBA implementation analysis proceed in parallel.

## First revision findings

- Aka Rev0 -> RevA: 46,167 raw differing bytes.
- Midori Rev0 -> RevA: 46,168 raw differing bytes.
- Their revision-change positions overlap almost completely: 99.10% Jaccard / 99.55% of the smaller set.
- Pikachu revisions show extensive movement/rebuild effects, so raw byte counts cannot be interpreted directly as gameplay changes.
- Kin Rev0 -> RevA: 10,841 raw differing bytes.
- Gin Rev0 -> RevA: 19,150 raw differing bytes.
- FireRed Rev0 -> Rev1: 7,016,197 raw differing bytes; this clearly requires structure-aware/relink-aware comparison rather than a flat binary diff.

## Analysis layers

1. Header/hash/revision identity.
2. Bank/chunk layout and relocation mapping.
3. Pokémon, move, item, trainer and encounter tables.
4. Map/metatile/layout conversion.
5. Script/event/NPC/warp correspondence.
6. Battle rules and runtime systems.
7. Graphics, text, audio and UI resources.
8. Save/RTC/state model.
9. Gen I -> FRLG official-remake correspondence.
10. Gen II -> RSE/FRLG GBA implementation requirements.
11. Latest verified Pokémon-system overlay for the seven remakes.

Machine-readable evidence:
- `manifests/japan-20-rom-census.csv`
- `manifests/japan-revision-summary.json`

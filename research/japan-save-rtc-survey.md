# JAPAN save / RTC survey — Generations I–III

This survey separates **legacy source saves** from the **native save format of the GBA remakes**.

No `.sav` or `.srm` files are currently present in the active runtime, so live checksum/block validation is pending. ROM hardware profiles and save-layout semantics are still sufficient to establish the conversion architecture.

## Japanese Generation I

Aka, Midori and Ao use 32 KiB battery-backed SRAM. Pikachu also uses 32 KiB SRAM; its MBC3 cartridge profile does **not** include the timer/RTC function.

Japanese Gen I differs materially from the international save layout:

- 8 PC boxes
- 30 Pokémon per box
- Japanese trainer/nickname string widths
- main save checksum plus box checksum handling

The corresponding international layout's 12 × 20 boxes must not be used as a JAPAN baseline.

## Japanese Generation II

Kin and Gin use 32 KiB battery-backed SRAM plus MBC3 RTC.
Japanese Crystal uses the larger 64 KiB SRAM / MBC30-compatible arrangement plus RTC.

Japanese Gen II storage uses:

- 9 PC boxes
- 30 Pokémon per box
- Japanese-length names
- primary and backup save data
- checksum validation
- persistent RTC-related state

Gold/Silver save logic stages the current day/hour/minute/second, writes primary and backup game data, stores checksums, backs up party mail/Mystery Gift state, and then saves RTC state.

Crystal extends that family with additional title-specific state, including Mobile/GS Ball-era data.

## Generation III

All six Japanese GBA references use 128 KiB Flash.

The common save architecture uses 32 × 4 KiB sectors. Each sector contains:

- 3968 bytes data
- 128-byte footer
- section ID
- checksum
- signature `0x08012025`
- save counter

Gameplay state alternates between two 14-sector save slots:

- slot A: sectors 0–13
- slot B: sectors 14–27

The active slot is selected by validated sector signatures/checksums and save counters, while sector positions rotate on writes.

Special sectors differ by title family:

- Ruby/Sapphire: Hall of Fame 28–29; 30–31 are e-Reader/Battle Tower-era special data.
- Emerald: Hall of Fame 28–29; Trainer Hill 30; Recorded Battle 31.
- FireRed/LeafGreen: Hall of Fame 28–29; Trainer Tower 30–31.

Ruby/Sapphire/Emerald have RTC hardware support. FireRed/LeafGreen do not.

In RSE, save state contains the local-time offset and the last berry-tree update timestamp; the actual clock source remains cartridge RTC hardware.

## Native remake save policy

RED/GREEN/BLUE/YELLOW/GOLD/SILVER/CRYSTAL will **not** keep the original GB/GBC binary save format as their runtime format.

They use a Generation-III-derived 128 KiB Flash save architecture so the modern Pokémon/entity/battle systems have one stable storage model.

Legacy saves are handled by an importer:

1. identify exact title/language/revision;
2. validate the legacy checksum(s);
3. decode Japanese-specific box/name/entity layout;
4. map story flags, party, boxes, inventory, Pokédex and time state;
5. write a **new GBA save** for the matching remake.

There is no in-place GB/GBC save expansion.

## Save identity

Each remake gets a distinct native save profile:

- RED — `JPN-RED-GBA`
- GREEN — `JPN-GREEN-GBA`
- BLUE — `JPN-BLUE-GBA`
- YELLOW — `JPN-YELLOW-GBA`
- GOLD — `JPN-GOLD-GBA`
- SILVER — `JPN-SILVER-GBA`
- CRYSTAL — `JPN-CRYSTAL-GBA`

This prevents saves from different ROM projects from being silently conflated.

## RTC policy

The common GBA engine may contain RTC support, but gameplay use is title-profiled:

- RED/GREEN/BLUE/YELLOW: no source RTC requirement.
- GOLD/SILVER/CRYSTAL: RTC required.
- RSE reference: RTC-capable.
- FRLG reference: no RTC hardware.

A physical GBA build of the Johto remakes therefore needs an RTC-capable target cartridge/flashcart, or equivalent emulator RTC support, if original time-of-day behavior is to be preserved.

## Pending live-save pass

When Japanese `.sav` files are supplied, the next validation pass should record:

- exact file hash/size;
- active save slot;
- checksum validity;
- current box/party/entity integrity;
- event flags/variables;
- RTC day/time state;
- title-specific special blocks;
- source-ROM ↔ save identity.

Machine-readable files:

- `manifests/japan-save-rtc-matrix.csv`
- `manifests/remake-save-policy.json`

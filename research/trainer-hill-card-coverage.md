# Pokémon Battle e Emerald coverage

Reference source: `pret/pokeemerald` at commit `5eff78649e7170a877b961ef0b3da13b81a16038`.

## What is already embedded

The localized Trainer Hill challenge data already contains 32 trainers originating from the 64-card Pokémon Battle e Emerald main set.

| Built-in mode | Card IDs | Count |
| --- | --- | ---: |
| Normal | 19-A017 .. 19-A024 | 8 |
| Variety | 19-A041 .. 19-A048 | 8 |
| Unique | 19-A049 .. 19-A056 | 8 |
| Expert | 19-A057 .. 19-A064 | 8 |
| **Total** | | **32** |

This was verified directly from `src/data/battle_frontier/trainer_hill.h` by matching `trainerNum1`, `trainerNum2`, and trainer names.

## What is still external

The following main-set cards are not represented by the localized built-in challenge tables:

- 19-A001 .. 19-A016
- 19-A025 .. 19-A040

That is 32 main-set cards.

The two promotional Emerald Trainer cards are also not embedded:

- 19-P001
- 19-P002

So the remaining payload target is **34 Trainer cards**.

## Why the special save sector matters

Emerald writes scanned Trainer Hill data to special save sector 30.

- Physical save offset: `30 * 0x1000 = 0x1E000`
- Sector begins with `SPECIAL_SECTOR_SENTINEL = 0x0000B39D`
- Challenge data begins four bytes after the sentinel.
- A challenge has up to eight trainers on four floors.
- The first scanned Trainer on each floor supplies that floor's map.
- The second Trainer supplies only its trainer data to the resulting challenge.

The decompilation defines the incoming card entry as:

- `struct EReaderTrainerHillTrainer`
- size `0x274`
- trainer number
- `TrainerHillTrainer`
- `TrainerHillFloorMap`
- byte-sum checksum

The scanned set is converted by `TryWriteTrainerHill` into a `TrainerHillChallenge` and stored in sector 30.

## Collection strategy

To recover a complete card entry from a scanned save, scan that card as the **first Trainer on a floor**. The saved challenge then retains both its trainer data and its reverse-side floor map.

Use:

`tools/trainer_hill_sector.py SAVE.sav --extract-first-cards output/`

The tool validates the special-sector sentinel and challenge checksum before exporting reconstructed `0x274` card entries.

Raw e-Reader dumps and ROM binaries are not committed to this repository. The card manifest stores only identity/hash/provenance information.

# Aegislash Stage 2 — BPEJ runtime hooks

Target: Pocket Monsters Emerald (Japan), BPEJ Rev.00.

Clean ROM SHA-256: `33f5610b9186b4add09fef68895deb00f552b997b3d133b5a961e5123506343c`

Stage 2 locally built ROM SHA-256: `5284b9d8aea2a204b6304aec25b0170bccc0204fdc00d131545a77ef12277f55`

No ROM binary is committed.

## Temporary compatibility IDs

- Species 252 / OLD_UNOWN_B -> ギルガルド
- Ability 76 / CACOPHONY -> バトルスイッチ
- Move 354 / PSYCHO_BOOST -> キングシールド

These are Stage-2 test IDs and are not the final expanded-table IDs.

## Injected runtime

Code is linked at ROM address `0x08917000`. There are no unresolved symbols or runtime relocations.

| BPEJ hook | Runtime entry | Purpose |
|---|---|---|
| 0x08045DAC | 0x08917001 | Stance Change after inability/PP/disobedience checks |
| 0x08045EF0 | 0x0891701B | King's Shield lets ordinary status moves through |
| 0x08045F34 | 0x08917051 | King's Shield blocked-contact Attack penalty |
| 0x0804F9B0 | 0x08917075 | Add King's Shield to Protect-family consecutive-use chain |

Each hook replaces eight verified vanilla bytes with an aligned absolute Thumb trampoline: `ldr r3,[pc,#0]; bx r3; .word target|1`.

## Stance Change behavior

- Persistent species remains Aegislash; battle-only state uses `gBattleMonForms[battler]`.
- Direct damaging move -> Blade Forme before the move continues.
- Direct King's Shield -> Shield Forme before protect success/failure is resolved.
- Ordinary status move -> no form change.
- Called moves are excluded by requiring `gCurrentMove == gChosenMove`, matching the tested Sleep Talk exception.
- Form stat recalculation uses the party Pokémon's level, IV, EV, and nature.
- HP, Speed, status and stat stages are not reset.

Gen VI stats:
- Shield: 60 / 50 / 150 / 60 / 50 / 150
- Blade: 60 / 150 / 50 / 60 / 150 / 50

The Stage-2 test save is Lv.50 Adamant, 31 IV, 0 EV:
- Shield: Atk 77 / Def 170 / SpA 63 / SpD 170
- Blade expected: Atk 187 / Def 70 / SpA 153 / SpD 70

## Graphics

The active 0x800-byte 64x64 4bpp frame is queued with Emerald's native `RequestSpriteCopy` at `0x08007204`; the matching 16-color form palette is loaded with `LoadPalette`.

Raw resources:
- 0x08918000 Shield front
- 0x08918800 Blade front
- 0x08919000 Shield back
- 0x08919800 Blade back
- 0x0891A000 Shield palette
- 0x0891A020 Blade palette

## King's Shield core

Move 354 still reuses vanilla `EFFECT_PROTECT` / `setprotectlike`.

Additional Stage-2 behavior:
- If protection came from King's Shield and the incoming move has power 0, protection is bypassed.
- A blocked damaging contact move lowers attacker Attack by two stages.
- Clear Body, Hyper Cutter, and White Smoke are excluded.
- King's Shield shares the vanilla Protect / Detect / Endure consecutive-use counter.

## Remaining mechanics

Stage 2 is a runtime core, not the final polished implementation:
- No dedicated stance-change message/transition animation yet; sprite/palette switches immediately.
- The Attack drop is currently a direct stage edit. Standard stat-change plumbing is still needed for Mist, Contrary, Defiant/Competitive, messages and stat animations.
- Shiny-specific Shield/Blade palettes are not yet split.
- Static binary validation passed. mGBA runtime execution was unavailable in the build container.

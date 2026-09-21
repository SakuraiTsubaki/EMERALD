# Arceus Stage-2 mGBA CPU/runtime verification

Target ROM: Pocket Monsters Emerald (Japan), BPEJ Rev.00.

Emulator: mGBA 0.10.5, AppImage artifact exported by the EMERALD repository and extracted locally.

Patched prototype ROM SHA-256:
\`bcd1a417adba623efb78e2bd9f9b6cd44d36dfea397be64b028c6bfc936d828b\`

## Boot smoke test

The patched ROM ran under mGBA through Xvfb for 12 seconds without emulator or ROM crash. The process was stopped by the external timeout, not by a fault.

Result: PASS.

## Direct ARM7TDMI execution method

mGBA was started with its GDB server. A minimal GDB Remote Serial Protocol client was used to:

1. pause the emulated ARM7TDMI;
2. write synthetic battle RAM;
3. enter the injected Thumb runtime through a real ARM \`bx\` instruction;
4. execute the Stage-2 function;
5. stop at an EWRAM Thumb \`bkpt\` sentinel;
6. inspect return registers and battle RAM.

This verifies the actual injected BPEJ machine code, not a host-language reimplementation.

## Core resolver tests

All passed:

- Gen IV Flame Plate -> Fire form 9.
- Gen IV Pixie Plate -> rejected / 0xFF.
- Gen VI Pixie Plate -> Fairy form 17.
- Gen VII Firium Z -> Fire form 9.
- Gen VI Firium Z -> rejected / 0xFF.
- Legend Plate vs Rock/Dark -> Fighting form 1.
- Legend Plate vs Water/Dragon -> Dragon form 15.
- Legend Plate vs Ghost/Dragon -> Dark form 16.

## Full move-preparation helper tests

These calls include the Stage-2 visual update path (RequestSpriteCopy + LoadPalette) as well as battle state writes.

### Gen VI — Pixie Plate + Judgment

Expected and observed:

- helper return: 1
- \`gBattleMonForms[0]\`: 17 / Fairy
- attacker battle types: 18 / 18
- \`dynamicMoveType\`: 0xD2 = Fairy | dynamic flags

Result: PASS.

### Gen VII — Firium Z + Judgment

Expected and observed:

- helper return: 1
- Arceus form: 9 / Fire
- attacker battle types: 10 / 10 / Fire
- \`dynamicMoveType\`: 0xC0 = Normal | dynamic flags

This is the critical Gen VII split: the type Z-Crystal changes Multitype form, but Judgment remains Normal because no Plate is held.

Result: PASS.

### Pokémon Legends: Arceus — Legend Plate vs Water/Dragon

Expected and observed:

- helper return: 2 / Legend transformation
- selected form: 15 / Dragon
- attacker battle types: 16 / 16 / Dragon
- \`dynamicMoveType\`: 0xD0 = Dragon | dynamic flags

Result: PASS.

## What this proves

The current BPEJ Stage-2 binary executes correctly on mGBA ARM7TDMI for:

- Plate form resolution;
- Pixie/Fairy form resolution;
- Gen VII Z-Crystal form-vs-Judgment separation;
- Legend Plate target-derived type selection;
- battle form/type writes;
- dynamic Judgment type writes;
- form visual-update calls.

## Still outside this verification

- battle-entry/switch-in form hook;
- forced-Special Judgment damage calculation in BPEJ;
- stock engine-wide Fairy integration;
- shiny palette selection;
- persistent PLA formState / field Plate use;
- shared Aegislash + Arceus dispatcher at 0x08045DAC;
- full player-input battle/UI presentation.

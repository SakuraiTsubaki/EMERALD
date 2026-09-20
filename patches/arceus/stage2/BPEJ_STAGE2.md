# Arceus Stage 2 — BPEJ runtime prototype

Target: Pocket Monsters Emerald (Japan), BPEJ Rev.00.

Clean ROM SHA-256:
\`33f5610b9186b4add09fef68895deb00f552b997b3d133b5a961e5123506343c\`

ROM binary is never committed.

## Purpose

This Stage-2 prototype executes the Arceus form resolver directly inside the retail Japanese Emerald battle core before the final expanded species/item/move tables exist.

Temporary test IDs:

- species 253 / OLD_UNOWN_C -> Arceus
- move 354 / Psycho Boost -> Judgment
- extension item IDs 377-413 -> Plates / Blank Plate / Legend Plate / type Z-Crystals

These are test IDs only. Final integration must use expanded tables.

## BPEJ addresses verified from the retail ROM

- gBattleMons: 0x02023D28
- gBattlerSpriteIds: 0x02023E88
- gCurrentMove: 0x02023E8E
- gChosenMove: 0x02023E90
- gBattlerAttacker: 0x02023EAF
- gBattlerTarget: 0x02023EB0
- gBattleStruct pointer: 0x02024140
- gBattleMonForms: 0x02024188
- gSprites: 0x02020630
- gTypeEffectiveness: 0x082EBB38
- Random: 0x0802BD8D
- GetBattlerSide: 0x080A62F9
- LoadPalette: 0x080A1201
- RequestSpriteCopy: 0x08007205

BattleStruct.dynamicMoveType is offset 0x13.

## Runtime / resources

Verified clean FF reservation:

- 0x0091B000-0x00930000

Stage-2 allocation:

- runtime: ROM 0x0091C000 / address 0x0891C000
- common front 4bpp: 0x0091D000
- common back 4bpp: 0x0091E000
- 18 normal palettes: 0x0091E800
- ruleset byte: 0x0091EA40

Ruleset byte:

- 0 = Gen IV
- 1 = Gen V
- 2 = Gen VI
- 3 = Gen VII
- 4 = BDSP
- 5 = Pokémon Legends: Arceus
- 6 = Gen IX

The same runtime binary is reused for every ruleset.

## Hook

Current prototype hook:

- BPEJ 0x08045DAC
- original bytes: 164a17490b781801
- trampoline: 004b184701c09108
- entry: 0x0891C001

The wrapper calls the Arceus helper, replays the four overwritten Thumb instructions, and resumes at 0x08045DB5.

Important: Aegislash Stage 2 uses the same 0x08045DAC hook. This Arceus ROM is intentionally an Arceus-only prototype. Final coexistence requires one shared dispatcher; do not merge two independent trampolines.

## Implemented in this prototype

- explicit 18-form Arceus form-to-type mapping
- Gen IV/V Plate forms
- Gen VI+ Pixie Plate / Fairy form
- Gen VII type Z-Crystals change Multitype form while Judgment remains Plate-only
- BDSP / Gen IX Plate resolver
- PLA ordinary/Blank Plate test behavior using held-item slots as a temporary proxy
- PLA Legend Plate target-derived form selection
- BPEJ type chart lookup plus Fairy interactions inside the Legend selector
- Judgment dynamic move type written through gBattleStruct
- battle-only form/type state written to gBattleMonForms and BattlePokemon types
- common front/back graphics plus palette-only 18-form visual switching
- no form index is used as a direct stock four-frame sprite-buffer offset

## Known Stage-2 limitations

This is not yet the final Arceus implementation.

- Form is currently resolved at move start, not at initial battle entry/switch-in.
- Judgment is not yet forced through a Special-category damage hook in the retail BPEJ damage routine.
- TYPE_FAIRY is not yet inserted into every stock Emerald core type table/loop; the Legend selector handles Fairy locally.
- Shiny form palette selection is not hooked yet.
- PLA persistent formState / out-of-battle Plate use is not yet wired into the retail save/UI path.
- PLA ordinary Plates are temporarily represented as held items for runtime testing.
- Aegislash and Arceus need a shared 0x08045DAC dispatcher.
- Full gameplay/UI validation still follows the CPU/core smoke tests.

## First locally built prototype

Clang/LLD ARMv4T Thumb build:

- runtime size: 1456 bytes
- runtime SHA-256: 6673cb7ef7c8522fe85687dc250a5d25897227de9463609437e8596fe663fc05
- unresolved runtime relocations: 0

Gen VI ruleset test ROM produced locally:

- output SHA-256: bcd1a417adba623efb78e2bd9f9b6cd44d36dfea397be64b028c6bfc936d828b

See \`analysis/roms/arceus-stage2-report.json\`.

## Reproduction

Build the runtime with the Stage-2 workflow or a compatible ARMv4T Clang/LLD toolchain, then run:

\`\`\`sh
python tools/patch_arceus_stage2_bpej.py \
  "Pocket Monsters - Emerald (Japan).gba" \
  "Pocket Monsters - Emerald (Japan) - Arceus Stage2.gba" \
  --runtime runtime.bin \
  --ruleset 2
\`\`\`

The patcher refuses the wrong ROM hash, wrong revision, unexpected hook bytes, non-FF reservation, incorrect resource sizes, or an oversized runtime.

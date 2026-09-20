# Morpeko Stage 2 — BPEJ runtime hooks

Target: Pocket Monsters Emerald (Japan), BPEJ Rev.00.

Clean ROM SHA-256: `33f5610b9186b4add09fef68895deb00f552b997b3d133b5a961e5123506343c`

Locally patched Stage-2 ROM SHA-256: `fc00b6c66b2078a534f0696d9d061ad2016eb75f8f355e5a6003cfc399e15a7f`

No ROM binary is committed.

## Temporary compatibility IDs

- Species 253 / OLD_UNOWN_C -> モルペコ
- Ability 76 / CACOPHONY -> はらぺこスイッチ

These are Stage-2 test IDs only. Ability 76 is also used by the Aegislash Stage-2 compatibility build for Stance Change; the two runtimes are separate clean-ROM experiments and the final expanded tables must assign dedicated IDs.

Aura Wheel is deliberately not claimed by this Stage-2 build. Its physical category, form-derived move type, failure rule, and Speed +1 are the next runtime stage rather than a partial approximation.

## Injected runtime

Runtime code is linked at ROM address `0x0891B000`.

Build verified:
- binary size: 520 bytes
- SHA-256: `f7fb7a1c6956aa3b90f5aa5cc1ca81979dbcf27517601e7aac24d8198b2acf5a`
- ELF relocations: 0

| BPEJ hook | Runtime entry | Purpose |
|---|---|---|
| `0x080406B8` | `0x0891B1C5` | Run vanilla end-turn Ability effects, then Hunger Switch if no vanilla effect ran |
| `0x0803E4B8` | `0x0891B1D7` | Reset a switched-out Morpeko to Full Belly before the battler slot is reused |

Both hooks use the same eight-byte aligned absolute Thumb trampoline style as the Aegislash runtime.

Verified retail bytes before patching:
- `0x080406B8`: `31 78 00 20 00 90 01 20`
- `0x0803E4B8`: `19 48 00 22 02 80 19 48`

## Japanese end-turn control-flow basis

The BPEJ address mapping was checked against `pret/pokeemerald-jp@6806c3e507da87a883b437f048969a45b38250c8`.

- `DoBattlerEndTurnEffects = 0x080405A8`
- case 1 / `ENDTURN_ABILITIES = 0x080406B8`
- retail `AbilityBattleEffects = 0x08042468`

The wrapper replays the original semantic operation by calling `AbilityBattleEffects(1, battler, 0, 0, 0)`. If vanilla returns a nonzero effect, that result is returned unchanged. Hunger Switch is only evaluated when vanilla returned zero, after which execution resumes at `0x080406C8`.

This avoids replacing or suppressing existing Emerald end-turn Abilities.

## Hunger Switch state

Battle-only state continues the Aegislash-compatible convention:

- `gBattleMonForms[battler] == 0`: Full Belly
- `gBattleMonForms[battler] == 1`: Hangry

The runtime toggles only when all of these are true:
- battle species is temporary Morpeko species 253;
- effective stored Ability is temporary Hunger Switch 76;
- HP is nonzero;
- `STATUS2_TRANSFORMED` is not set.

The transition does not recalculate stats because both Morpeko forms share the same personal parameters.

Switching out explicitly restores battle form 0.

## Stage-2 temporary SpeciesInfo

Species 253 is patched for this clean-ROM compatibility build to:

- HP 58
- Attack 95
- Defense 58
- Speed 97
- Special Attack 70
- Special Defense 58
- Electric / Dark
- Ability slot 1: 76
- Ability slot 2: 76

The remaining placeholder metadata is intentionally left unchanged in Stage 2; final species-table expansion will replace all temporary compatibility metadata.

## Initial and transitioned graphics

The Japanese retail GF ROM header exposes the native tables directly:

- front sprite table: `0x082DDA1C`
- back sprite table: `0x082D6148`
- normal palette table: `0x082D6F08`
- shiny palette table: `0x082D7CC8`
- SpeciesInfo table: `0x082F0D54`

Species 253's table pointers are redirected to Full Belly compressed resources, so Morpeko displays Full Belly immediately when first loaded rather than showing the OLD_UNOWN_C placeholder.

Raw transition resources used by the runtime:

- `0x0891C000`: Full Belly front, 0x800 bytes
- `0x0891C800`: Hangry front, 0x800 bytes
- `0x0891D000`: Full Belly back, 0x800 bytes
- `0x0891D800`: Hangry back, 0x800 bytes
- `0x0891E000`: Full Belly normal palette
- `0x0891E020`: Hangry normal palette
- `0x0891E040`: Full Belly shiny palette
- `0x0891E060`: Hangry shiny palette

Initial Full Belly table resources are separately GBA-LZ77-compressed at `0x0891F000` and above.

On a runtime form transition, the active 64x64 4bpp frame is queued with Emerald's native `RequestSpriteCopy`; the matching normal or shiny form palette is loaded with `LoadPalette`.

## Static validation

Passed on the clean BPEJ Rev.00 ROM:

- clean input SHA-256 matched;
- both hook preimages matched the Japanese retail bytes exactly;
- injection area was all `0xFF` before use;
- runtime ELF had no relocations;
- runtime and resource bytes were read back exactly;
- species 253 graphics table pointers resolved to the injected Full Belly resources;
- species 253 battle parameters read back as 58/95/58/97/70/58, Electric/Dark, Ability 76/76;
- generated IPS reapplied to the clean ROM byte-for-byte and reproduced Stage-2 SHA-256 `fc00b6c66b2078a534f0696d9d061ad2016eb75f8f355e5a6003cfc399e15a7f`.

## IPS artifact

`morpeko-bpej-stage2.ips` contains only the binary differences from the verified clean BPEJ ROM.

- size: 10,355 bytes
- SHA-256: `1aa079d9ba6f7286d615461690ba594b65a23247b93201a5b0eac5274cf37e05`
- records: 45

No copyrighted ROM image is stored in this repository.

## Runtime verification status

Static control-flow and binary validation are complete.

A local mGBA executable is not currently available in this execution environment, so this Morpeko Stage-2 build is **not yet labeled mGBA runtime-verified**. The existing Aegislash mGBA result must not be treated as Morpeko verification.

The next runtime gate is:
1. execute the injected end-turn entry against Morpeko Full Belly battle RAM and observe form 0 -> 1;
2. execute it again and observe 1 -> 0;
3. confirm non-Morpeko, fainted, wrong-Ability, and Transformed controls do not toggle;
4. execute the switch wrapper from Hangry and observe reset to Full Belly plus return to the original `HandleAction_Switch` path;
5. boot the complete patched BPEJ ROM and visually confirm initial Full Belly and both palette/sprite transitions.

After that, Stage 3 adds Aura Wheel.

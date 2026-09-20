# Morpeko Gen VIII integration plan for Emerald

Target baseline: `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`.
Japanese retail verification target: Pocket Monsters Emerald, BPEJ Rev.00, SHA-256 `33f5610b9186b4add09fef68895deb00f552b997b3d133b5a961e5123506343c`.

Target representation: **one persistent `SPECIES_MORPEKO`; Full Belly/Hangry are battle-only forms in `gBattleMonForms[]`.**

## 1. Battle-form state

`src/extensions/morpeko/morpeko.c` defines:
- form 0 = Full Belly
- form 1 = Hangry
- `Morpeko_TryHungerSwitch`
- `Morpeko_ResetBattleForm`
- Aura Wheel user/type helpers

Unlike Aegislash, Morpeko does not recalculate battle stats when its form changes. Both forms keep 58 / 95 / 58 / 97 / 70 / 58 and Electric / Dark.

## 2. Hunger Switch end-turn hook

Run one Morpeko form-change pass during the end-turn form phase after every active battler has acted.

For each living battler:
1. resolve its **effective** Ability after suppression/overwriting rules;
2. call `Morpeko_TryHungerSwitch(battler, effectiveAbility)`;
3. if TRUE, refresh the form-specific sprite and palette and run the normal form-change presentation;
4. do not alter HP, stat stages, status, PP, party data, or save data.

Do not toggle a battler whose battle state has `STATUS2_TRANSFORMED`; reference tests explicitly exclude transformed copies from Hunger Switch.

## 3. Reset adapters

Before a normal switch-out completes, on faint cleanup, and at battle end, call `Morpeko_ResetBattleForm`.

A newly sent-out Morpeko therefore starts in Full Belly Mode. The battle-only form never persists to the save.

## 4. Aura Wheel

Move data:
- Power 110
- Accuracy 100
- PP 10
- Physical
- Electric base type
- self Speed +1 after successful execution

Before type effectiveness/damage:
- reject the move if `Morpeko_CanUseAuraWheel(gBattlerAttacker)` is FALSE;
- resolve the effective move type with `Morpeko_GetAuraWheelType`;
- Full Belly -> Electric;
- Hangry -> Dark;
- Normalize -> Normal.

A transformed Pokémon whose current battle species is Morpeko is allowed to use Aura Wheel.

The Speed +1 must use Emerald's normal stat-change battle script/effect path. Do not directly increment `statStages[STAT_SPEED]`.

## 5. Graphics

Artifacts live under `artifacts/graphics/morpeko/`.

Runtime frame selection:
- Full Belly front/back = first 0x800-byte frame
- Hangry front/back = second 0x800-byte frame
- normal palettes switch with form
- shiny palettes switch with form when the battler is shiny

Because the two forms use different palette index layouts, changing only tile data is insufficient; reload the matching form palette on every actual transition.

## 6. Interaction with Aegislash

`gBattleMonForms[]` is now deliberately shared by multiple species:
- Aegislash: 0 Shield / 1 Blade
- Morpeko: 0 Full Belly / 1 Hangry

The byte has no global semantic meaning. Its meaning is always interpreted through the battler's species/form adapter. Do not write generic code that assumes 0/1 means Shield/Blade for every species.

## 7. Verification gate

Acceptance cases are in `tests/morpeko_behavior.md`.

The source/asset overlay can be validated immediately. Final BPEJ absolute hook addresses belong in a separate runtime-stage report only after the retail Japanese ROM control flow is mapped and executed under mGBA; they must not be guessed.

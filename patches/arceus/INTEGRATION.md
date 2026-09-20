# Arceus all-generation integration plan for Emerald

Target baseline: `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`.
Branch lineage: `feature/aegislash-gen6` -> `feature/arceus-all-gen`.

Target representation: **one persistent `SPECIES_ARCEUS`**. Form identity is explicit metadata; battle presentation uses `gBattleMonForms[]`.

## 1. Ruleset adapters

The Arceus extension separates mechanics that changed by generation:

- `ARCEUS_RULESET_GEN4`
- `ARCEUS_RULESET_GEN5`
- `ARCEUS_RULESET_GEN6`
- `ARCEUS_RULESET_GEN7`
- `ARCEUS_RULESET_GEN8_BDSP`
- `ARCEUS_RULESET_LEGENDS_ARCEUS`
- `ARCEUS_RULESET_GEN9`

Do not collapse these back into a single "modern" path. Gen VII Z-Crystals and Gen IX Terastallization make that inaccurate.

## 2. Species / ability / move data

Add:
- `SPECIES_ARCEUS`
- base stats 120 / 120 / 120 / 120 / 120 / 120
- base type Normal
- `ABILITY_MULTITYPE`
- `MOVE_JUDGMENT`: power 100, accuracy 100, PP 10 for mainline rulesets; PLA configuration may use PP 5
- modern category override: Judgment = Special

Do not encode forms as separate species.

## 3. Fairy engine type

Gen VI+ and PLA require Fairy.

Add `TYPE_FAIRY` after Dark and extend:
- `gTypeEffectiveness`;
- type names/messages;
- summary/menu type graphics;
- AI/type loops using `NUMBER_OF_MON_TYPES`;
- any fixed-size type arrays.

The exact non-neutral chart additions are in:
`manifests/fairy-type-chart-extension.csv`.

The Arceus module has a temporary `TYPE_FAIRY 18` fallback only to document the intended slot. A real engine constant/table entry is mandatory before build/runtime use.

## 4. Item allocation

Use `manifests/arceus-item-extensions.csv`.

Emerald stock ends at:
- 376 / 0x178 = `ITEM_OLD_SEA_MAP`

Allocated extension range:
- 377-392: sixteen Gen IV Plates in original Pt order;
- 393: Pixie Plate;
- 394: Blank Plate;
- 395: Legend Plate;
- 396-413: eighteen type-specific Z-Crystals in Gen VII order.

Do not reuse original later-generation numeric IDs inside Emerald.

Mainline rulesets use ordinary Plates as held items. Gen VII additionally lets type Z-Crystals drive Multitype form only. PLA exposes Plates through an out-of-battle use handler.

## 5. Persistent form state without changing save size

Stock `PokemonSubstruct0` ends with:

```c
u8 ppBonuses;
u8 friendship;
u16 filler;
```

Repurpose that existing 16-bit `filler` as `formState`; do not enlarge the substruct.

Suggested layout:
- bits 0-4: persistent form ID;
- bit 5: Legend Plate state;
- bits 6-15: reserved.

Add `MON_DATA_FORM_STATE` to the mon-data request enum and wire it into both `GetBoxMonData` and `SetBoxMonData`.

Getter:

```c
case MON_DATA_FORM_STATE:
    retVal = substruct0->formState;
    break;
```

Setter:

```c
case MON_DATA_FORM_STATE:
    substruct0->formState = *(const u16 *)data;
    break;
```

Use the normal `SetMonData` / `SetBoxMonData` path so the secure-data checksum is recalculated normally.

Compatibility property: untouched legacy saves have zero in this slot, which decodes as base form / no special trigger.

## 6. Held-item form resolution

Use `Arceus_GetHeldMultitypeForm(item, ruleset)`.

- Gen IV/V: sixteen Plates only.
- Gen VI: sixteen Plates + Pixie Plate.
- Gen VII: Plates **or** eighteen type-specific Z-Crystals.
- BDSP: Plates only.
- Gen IX: Plates only.

Judgment does **not** use this resolver. Judgment uses `Arceus_GetPlateForm` because Gen VII Z-Crystals change Arceus's form but do not change Judgment's type.

## 7. Item-manipulation rules

Call `Arceus_BlocksItemManipulation` from Trick / Switcheroo / Thief / Covet / Knock Off / Fling-style held-item mutation paths.

- Gen IV: block item manipulation on a Multitype Arceus regardless of current item.
- Gen V onward: block giving a Plate to Arceus or removing a Plate already held.
- Gen VII: Z-Crystals must also be protected; the Arceus adapter currently supplies this until a generic Z-Crystal item-lock layer exists.
- PLA: no held-item manipulation path.

## 8. Battle lifecycle

Call `Arceus_BeginBattle()` once when a new battle is initialized.

After a party Pokémon has been copied into `gBattleMons[battler]`, call:

```c
Arceus_ApplyBattleEntryForm(battler, gArceusRuleset);
```

This must occur after any path that calls `ClearTemporarySpeciesSpriteData`, because stock Emerald clears `gBattleMonForms[battler]` there.

Mainline:
- derive form from the current held-item ruleset.

PLA ordinary Plate:
- derive form from persistent `MON_DATA_FORM_STATE`.

PLA Legend Plate:
- first entry is Normal;
- later switch-out/switch-in in the same battle restores the side/party-slot battle form selected by the previous Judgment.

Do **not** blindly reset Legend Arceus to Normal on switch-out. Only `Arceus_EndBattle()` clears the temporary Legend battle state.

## 9. PLA field item use

Add an out-of-battle Plate use path that targets a party Arceus and calls:

```c
Arceus_UsePlate(mon, item, ARCEUS_RULESET_LEGENDS_ARCEUS);
```

Behavior:
- ordinary Plate -> store corresponding persistent form;
- Blank Plate -> store Normal;
- Legend Plate -> store Normal + Legend bit.

Refresh summary/menu sprite and displayed type from the resulting form.

## 10. Judgment hook

Call `Arceus_TryPrepareJudgment(gBattlerAttacker, gBattlerTarget, gArceusRuleset)` **after the attack-canceler has established that the move can execute** and before damage/type calculation.

Timing requirements:
- full paralysis / sleep / freeze / flinch prevent Legend transformation;
- a later accuracy miss does not undo the transformation;
- dynamic move type is set before damage, STAB and effectiveness calculation.

Mainline Plate:
- Judgment type comes from the user's Plate, including a non-Arceus user that obtained/copied Judgment.

Gen VII Z-Crystal:
- Multitype form follows the Z-Crystal;
- Judgment remains Normal because no Plate is held.

PLA:
- copied Judgment by non-Arceus -> Normal;
- ordinary Plate -> current persistent Arceus form;
- Legend Plate -> choose form from target matchup, then set Arceus and Judgment to that type.

The Legend selector uses:
1. best offensive multiplier;
2. best defense against target primary type;
3. best defense against target secondary type;
4. random among exact ties.

## 11. Gen IX Terastallization guard

When a future Tera subsystem is integrated:

- if `ruleset == ARCEUS_RULESET_GEN9` and attacker is Terastallized, **do not** let Multitype overwrite the battler's Tera type;
- still run the Plate-only Judgment resolver so Judgment keeps its Plate-derived move type;
- STAB must be evaluated from the Tera rules, not from a forced Plate form.

The current branch records this guard in the Arceus source comments but cannot execute it because EMERALD has no Tera state yet.

## 12. Judgment must remain Special

Stock Emerald's `CalculateBaseDamage` uses `IS_TYPE_PHYSICAL(type)` / `IS_TYPE_SPECIAL(type)`.

Include `src/extensions/battle_move_category/battle_move_category.c` and calculate:

```c
u8 category = GetBattleMoveCategory(move, type);
```

Use category, not dynamic type, for:
- Attack/Defense vs Sp. Atk/Sp. Def branch;
- burn physical-damage penalty;
- Reflect vs Light Screen;
- type-boosting held-item stat branch.

This keeps Judgment Special for Fighting/Rock/Ghost/etc. while retaining stock Gen III behavior for existing moves.

Do not add a field to `struct BattleMove` yet: the BPEJ Aegislash Stage-2 runtime currently relies on the 12-byte move-entry layout.

## 13. Plate 20% move boost

Ordinary Plates boost matching-type moves by 20% in the mainline rulesets.

Resolve Plate type from item identity with `Arceus_GetPlateForm` + `Arceus_FormToType`; do not allocate seventeen separate hold-effect opcodes unless another system needs them.

Apply the 20% modifier to the stat path selected by the move-category resolver.

Z-Crystals are **not** treated as ordinary 20% type-boosting items.

## 14. Graphics

Do not store 18 forms as 18 decompressed battler frames.

Stock `AllocateMonSpritesGfx` reserves only four `MON_PIC_SIZE` frames per battler.

Follow the Aegislash Stage-2 model:
- one compressed front asset per form;
- one compressed back asset per form;
- one normal and shiny 16-color palette per form;
- on form change, decompress/copy only the selected form into the battler's existing slot and reload its palette.

The current branch contains mechanics/API only; Arceus PNG/palette/4bpp assets are not yet present in the connected repositories.

## 15. Re-show / menu paths

Re-show battle:
- reconstruct graphics from current `gBattleMonForms[battler]`, not frame-offset arithmetic.

Summary / party / PC:
- mainline derives visible form from held-item rules;
- PLA derives from persistent formState;
- Legend state displays Normal outside the temporary battle transformation.

## 16. Transform rules

Keep Transform state separate from persistent Arceus metadata.

Generation IV:
- transformed Arceus may be re-resolved by the transformer's own Plate.

Generation V onward:
- transformed Pokémon keeps the target Arceus form regardless of its own held item.

Implement this in the transform/ruleset adapter; never write the copied form back into save data.

## 17. Acceptance gate

Use `tests/arceus_behavior.md`.

Minimum before merge:
- all 66 logic cases accounted for;
- Fairy type table verified;
- Gen VII Z-Crystal form / Judgment split verified;
- no out-of-bounds `gBattleMonForms` sprite-frame addressing;
- Judgment category verified with at least one Gen III-physical dynamic type;
- Legend switch-out/in preservation verified;
- battle-end reset verified;
- legacy save checksum/load verified;
- Gen IX Tera guard added when the Tera subsystem exists.

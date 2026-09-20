# Arceus all-generation integration plan for Emerald

Target baseline: `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`.
Branch lineage: `feature/aegislash-gen6` -> `feature/arceus-all-gen`.

Target representation: **one persistent `SPECIES_ARCEUS`**. Form identity is explicit metadata; battle presentation uses `gBattleMonForms[]`.

## 1. Species / ability / move data

Add:
- `SPECIES_ARCEUS`
- base stats 120 / 120 / 120 / 120 / 120 / 120
- base type Normal
- `ABILITY_MULTITYPE`
- `MOVE_JUDGMENT`: power 100, accuracy 100, PP 10 for mainline rulesets; PLA configuration may use PP 5
- modern category override: Judgment = Special

Do not encode forms as separate species.

## 2. Fairy engine type

Gen VI+ and PLA require Fairy.

Add `TYPE_FAIRY` after Dark and extend:
- type-effectiveness table;
- type names/messages;
- summary/menu type graphics;
- AI/type loops using `NUMBER_OF_MON_TYPES`;
- any fixed-size type arrays.

The Arceus module has a temporary `TYPE_FAIRY 18` fallback only to document the intended slot. A real engine constant/table entry is mandatory before build/runtime use.

## 3. Plate item allocation

Use `manifests/arceus-item-extensions.csv`.

Emerald stock ends at:
- 376 / 0x178 = `ITEM_OLD_SEA_MAP`

Arceus extension range:
- 377-392: the sixteen Gen IV Plates in original Pt order;
- 393: Pixie Plate;
- 394: Blank Plate;
- 395: Legend Plate.

Do not reuse Pt numeric IDs 298-313 inside Emerald.

Mainline rulesets use ordinary Plates as held items. PLA ruleset exposes them through an out-of-battle use handler. Blank/Legend are PLA-only active-use entries.

## 4. Persistent form state without changing save size

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

## 5. Battle lifecycle

Call `Arceus_BeginBattle()` once when a new battle is initialized.

After a party Pokémon has been copied into `gBattleMons[battler]`, call:

```c
Arceus_ApplyBattleEntryForm(battler, gArceusRuleset);
```

This must occur after any path that calls `ClearTemporarySpeciesSpriteData`, because stock Emerald clears `gBattleMonForms[battler]` there.

Mainline rulesets:
- derive form from current held Plate on each battle entry.

PLA ordinary Plate:
- derive form from persistent `MON_DATA_FORM_STATE`.

PLA Legend Plate:
- first entry is Normal;
- later switch-out/switch-in in the same battle restores the side/party-slot battle form selected by the previous Judgment.

Do **not** blindly reset Legend Arceus to Normal on switch-out. Only `Arceus_EndBattle()` clears the temporary Legend battle state.

## 6. PLA field item use

Add an out-of-battle Plate use path that targets a party Arceus and calls:

```c
Arceus_UsePlate(mon, item, ARCEUS_RULESET_LEGENDS_ARCEUS);
```

Behavior:
- ordinary Plate -> store corresponding persistent form;
- Blank Plate -> store Normal;
- Legend Plate -> store Normal + Legend bit.

Refresh summary/menu sprite and displayed type from the resulting form.

## 7. Judgment hook

Call `Arceus_TryPrepareJudgment(gBattlerAttacker, gBattlerTarget, gArceusRuleset)` **after the attack-canceler has established that the move can execute** and before damage/type calculation.

This timing is required because:
- full paralysis / sleep / freeze / flinch must prevent Legend transformation;
- a later accuracy miss must not undo the transformation;
- dynamic move type must be set before damage, STAB and effectiveness calculation.

Mainline:
- Judgment type comes from the user's held Plate;
- an Arceus with Multitype is synchronized to that form.

PLA:
- copied Judgment by non-Arceus -> Normal;
- ordinary Plate -> current persistent Arceus form;
- Legend Plate -> choose form from target matchup, then set Arceus and Judgment to that type.

The Legend selector implemented in `src/extensions/arceus/arceus.c` uses:
1. best offensive multiplier;
2. best defense against target primary type;
3. best defense against target secondary type;
4. random among exact ties.

## 8. Judgment must remain Special

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

## 9. Graphics

Do not store 18 forms as 18 decompressed battler frames.

Stock `AllocateMonSpritesGfx` reserves only four `MON_PIC_SIZE` frames per battler.

Follow the Aegislash Stage-2 model:
- one compressed front asset per form;
- one compressed back asset per form;
- one normal and shiny 16-color palette per form;
- on form change, decompress/copy only the selected form into the battler's existing slot and reload its palette.

The current branch contains mechanics/API only; Arceus PNG/palette/4bpp assets are not yet present in the connected repositories.

## 10. Re-show / Transform / menu paths

Re-show battle:
- reconstruct graphics from current `gBattleMonForms[battler]`, not frame-offset arithmetic.

Summary / party / PC:
- mainline ruleset derives visible form from held Plate;
- PLA derives from persistent formState;
- Legend state displays Normal outside the temporary battle transformation.

Transform:
- keep transformed species state separate from persistent Arceus form metadata.
- Gen IV Multitype-specific Transform/item-lock semantics should be handled in the ruleset adapter, not by writing a form into the copied Pokémon save data.

## 11. Acceptance gate

Use `tests/arceus_behavior.md`.

Minimum before merge:
- all 40 logic cases accounted for;
- Fairy type table verified;
- no out-of-bounds `gBattleMonForms` sprite-frame addressing;
- Judgment category verified with at least one Gen III-physical dynamic type;
- Legend switch-out/in preservation verified;
- battle-end reset verified;
- legacy save checksum/load verified.

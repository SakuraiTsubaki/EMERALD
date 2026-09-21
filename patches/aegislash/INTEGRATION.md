# Aegislash Gen VI integration plan for Emerald

Target baseline: `pret/pokeemerald@5eff78649e7170a877b961ef0b3da13b81a16038`.
Target representation: **one persistent `SPECIES_AEGISLASH`; Shield/Blade are battle-only forms in `gBattleMonForms[]`**.

## 1. Stance Change hook

Add `ABILITY_STANCE_CHANGE` and `MOVE_KINGS_SHIELD`, then include the Aegislash extension in the build.

Hook `Aegislash_TryStanceChange(gBattlerAttacker)` in `Cmd_attackcanceler()` after sleep/freeze/flinch/full-paralysis, PP and disobedience checks have succeeded, and before the move proceeds to protection/target handling. This prevents a failed action from changing form.

If it returns TRUE, run a form-change presentation script and resume the same battle-script cursor. Do not consume the move or PP in the form-change script.

The helper requires `gCurrentMove == gChosenMove`; this preserves the verified exception where Sleep Talk calls King's Shield but does not trigger Stance Change.

Reset to Shield on switch-out, faint and battle end. The party/save species remains Aegislash.

## 2. King's Shield, Gen VI behavior

Add `MOVE_KINGS_SHIELD`: Steel, power 0, accuracy 0, PP 10, priority +4, status, Protect-family success chain.

Reuse `EFFECT_PROTECT` / `setprotectlike`, but add a battle-only `kingsShielded` bit to `ProtectStruct`. On successful King's Shield, set both `protected` and `kingsShielded`. Include King's Shield in the same repeated-protect chain.

King's Shield blocks damaging Protect-affected moves, not ordinary status moves. A blocked contact move lowers the attacker's Attack by two stages (Gen VI rule).

The Stance Change hook runs before `setprotectlike`, so even a failed repeated King's Shield still changes Aegislash to Shield.

## 3. Graphics

Front combined 4bpp = 0x2000:
- 0x0000 Shield frame 0
- 0x0800 Shield frame 1
- 0x1000 Blade frame 0
- 0x1800 Blade frame 1

Back combined 4bpp = 0x1000:
- 0x0000 Shield
- 0x0800 Blade

`gBattleMonForms[battler]`: 0 Shield, 1 Blade. Front animation maps form 0 to frames 0/1 and form 1 to 2/3. Back selects 0/1.

Shield and Blade palette index ordering differs, so reload the matching 16-color palette on form transition.

## Stats

Shield: 60 / 50 / 150 / 60 / 50 / 150.
Blade: 60 / 150 / 50 / 60 / 150 / 50.

Atk/Def/SpA/SpD are recalculated from level, IV, EV and nature. HP, Speed and `statStages[]` remain unchanged.

## Build status

This is a source/asset overlay for the pinned baseline. The repository is currently a Japanese reconstruction scaffold, not a complete buildable BPEJ decompilation, so final link addresses and rebuilt-ROM verification must follow reconstruction. No ROM binary is committed.

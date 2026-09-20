# Aegislash battle behavior acceptance tests

1. Shield + damaging physical move -> form changes to Blade before move animation/damage.
2. Shield + damaging special move -> Blade.
3. Shield + status move (e.g. Growl) -> stays Shield.
4. Blade + damaging move -> stays Blade; no duplicate form-change event.
5. Blade + King's Shield -> Shield before King's Shield success/failure roll.
6. Repeated King's Shield can fail but still leaves Aegislash in Shield.
7. Sleep Talk calling King's Shield while Blade -> stays Blade.
8. Flinch/sleep/freeze/full paralysis prevents the move and prevents stance change.
9. Swords Dance Attack stage survives Shield <-> Blade changes unchanged.
10. Current HP and max HP do not change during stance change.
11. Speed does not change during stance change.
12. IV/EV/nature-derived Atk/Def/SpA/SpD equal a fresh calculation using the active form base stat.
13. Switching Blade Aegislash out resets battle form to Shield; party/save species remains `SPECIES_AEGISLASH`.
14. Battle end while Blade resets to Shield without persisting a Blade form to save data.
15. King's Shield blocks a damaging Protect-affected move.
16. King's Shield does not block an ordinary status move merely because Protect would.
17. Blocked contact move -> attacker Attack -2 (Gen VI rule).
18. Blocked non-contact move -> no Attack drop.
19. Form transition reloads the matching palette; no Shield/Blade palette-index corruption.
20. Front sprite selects Shield frames 0/1 or Blade frames 2/3; back selects Shield 0 or Blade 1.


## mGBA runtime verification

Verified on Pocket Monsters Emerald (Japan), BPEJ Rev.00, with mGBA headless development build `0.11-9139-3a5bc2462`.

The corrected Stage-2 King's Shield runtime was executed by the mGBA ARM7TDMI CPU against synthetic battle RAM states so the battle result is independent of level, HP, damage rolls, or UI timing.

- Test 17, blocked contact move: neutral Attack stage `6 -> 4` — **PASS**.
- Blocked non-contact damaging move: stage remains `6` — **PASS**.
- Ordinary status move while King's Shield is active: `ks_should_bypass() == 1` — **PASS**.
- Clear Body attacker: stage remains `6` — **PASS**.
- Protection inactive: stage remains `6` — **PASS**.
- Defender's last resulting move is not King's Shield: stage remains `6` — **PASS**.
- Attack stage floor: stage `1 -> 0`, not underflow — **PASS**.
- Corrected `ks_penalty_entry` wrapper: helper executes, returns to the original protected-hit path, and the original `MOVE_RESULT_MISSED` store executes — **PASS**.
- Move 354 / King's Shield enters the same repeated-Protect success-chain branch as Protect — **PASS**.
- Ordinary unrelated move does not enter that branch — **PASS**.

This is direct emulator CPU/runtime verification of the hook and mechanics. Full player-input battle presentation (messages/stat animation/stance transition polish) remains separate from this core-mechanics verification.

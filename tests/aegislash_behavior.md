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

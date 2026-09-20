# Morpeko battle behavior acceptance tests

Reference generation: Sword / Shield.

1. Send out Morpeko -> `gBattleMonForms[battler] == MORPEKO_FORM_FULL_BELLY`.
2. Full Belly + living + effective Hunger Switch at end of turn -> Hangry.
3. Hangry + living + effective Hunger Switch at next end of turn -> Full Belly.
4. Form change does not alter HP, max HP, base battle stats, status or stat stages.
5. Form change does not persist a second species/form into party or save data.
6. Hangry Morpeko switching out -> Full Belly before the battler slot is reused.
7. Hangry Morpeko fainting -> Full Belly cleanup.
8. Battle ending while Hangry -> Full Belly cleanup.
9. If Hunger Switch is not the effective Ability, end-turn form does not toggle.
10. A Pokémon transformed into Morpeko does not toggle from Hunger Switch.
11. A non-Morpeko attempting Aura Wheel -> move fails before damage/stat boost.
12. Morpeko in Full Belly using Aura Wheel -> Electric damage type.
13. Morpeko in Hangry using Aura Wheel -> Dark damage type.
14. Morpeko with Normalize using Aura Wheel -> Normal damage type in either form.
15. A Pokémon transformed into Morpeko can execute Aura Wheel.
16. Successful Aura Wheel -> user Speed +1 through standard stat-change plumbing.
17. Failed/blocked pre-execution Aura Wheel -> no Speed boost.
18. Aura Wheel parameters are Power 110 / Accuracy 100 / PP 10 / Physical.
19. Full Belly transition selects Full Belly front/back tiles and matching palette.
20. Hangry transition selects Hangry front/back tiles and matching palette.
21. Shiny battler selects form-matched shiny palette.
22. Graphics remain 64x64 indexed 4bpp with palette indices <= 15 and no interpolated colors.
23. Combined front raw resource is 0x1000 bytes: Full Belly 0x0000, Hangry 0x0800.
24. Combined back raw resource is 0x1000 bytes: Full Belly 0x0000, Hangry 0x0800.
25. LZ77 decode of each combined compressed resource exactly equals its raw 4bpp resource.

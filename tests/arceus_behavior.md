# Arceus behavior acceptance tests

Target branch: `feature/arceus-all-gen`.

## Persistent form storage

1. Existing Emerald Pokémon with zeroed `PokemonSubstruct0.filler` decode as form 0.
2. Writing `MON_DATA_FORM_STATE` changes no Pokémon struct size.
3. Checksum remains valid after `SetMonData(... MON_DATA_FORM_STATE ...)`.
4. Box -> party -> box round trip preserves formState.

## Gen IV ruleset

5. No Plate -> Normal form/type.
6. Each of the sixteen Gen IV Plates selects exactly its corresponding form/type.
7. Pixie Plate is rejected by the Gen IV form resolver.
8. No held item can select the unused ??? form.
9. Judgment with Flame Plate becomes Fire and remains Special.
10. Judgment with Fist Plate becomes Fighting but still uses Sp. Atk / Sp. Def.
11. Judgment copied by another Pokémon still derives its type from that user's held Plate.
12. Multitype Arceus entering battle derives form from held Plate without changing party species.

## Gen VI+ ruleset

13. Pixie Plate selects Fairy form/type.
14. Fairy Judgment is Special.
15. Normal plus 17 Plate forms are all addressable through explicit form -> type mapping.

## PLA ordinary Plates

16. Using an ordinary Plate on Arceus stores that persistent form without requiring a held item.
17. Using Blank Plate stores Normal.
18. Stored PLA form survives party/box movement and save/load.
19. Battle entry loads the stored ordinary Plate form.

## Legend Plate

20. Using Legend Plate stores Normal + Legend-state bit.
21. Legend-state Arceus enters battle as Normal.
22. Rock/Dark target -> Fighting wins on offensive effectiveness.
23. Water/Dragon target: when Dragon and Fairy are tied offensively, Dragon wins because it better resists the target's primary Water type.
24. Ghost/Dragon target: when Dark and Fairy are tied offensively, Dark wins because it better resists the target's primary Ghost type.
25. If offense and both defensive tie-breakers remain tied, selection is random only among the tied candidates.
26. Arceus changes form/type before Judgment damage/type calculation and therefore gets STAB.
27. Judgment miss still leaves Arceus in the newly selected type.
28. Sleep/freeze/flinch/full paralysis preventing the move also prevents the Legend type change.
29. A second Judgment may choose a different type and replaces the previous battle type.
30. Switching Legend-state Arceus out and back in preserves the latest battle-selected type.
31. Battle end clears the temporary Legend battle type and returns presentation to Normal.
32. Persistent formState remains Normal + Legend bit after battle.
33. A non-Arceus user of copied Judgment is Normal-type in PLA ruleset.

## Graphics

34. No form index is used as a direct offset beyond Emerald's four-frame battler buffer.
35. Each transition reloads the selected front/back graphics and 16-color palette.
36. Re-show battle screen restores the current form from battle state rather than forcing frame 0.

## Move category

37. Judgment remains Special for every dynamic type.
38. Burn does not halve Judgment merely because its dynamic type is a Gen III physical type.
39. Reflect does not reduce Judgment; Light Screen does.
40. Plate's 20% same-type boost applies to Judgment in mainline rulesets without converting it to physical damage.

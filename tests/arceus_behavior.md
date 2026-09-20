# Arceus behavior acceptance tests

Target branch: `feature/arceus-all-gen`.

## Persistent form storage

1. Existing Emerald Pokémon with zeroed `PokemonSubstruct0.filler` decode as form 0.
2. Writing `MON_DATA_FORM_STATE` changes no Pokémon struct size.
3. Checksum remains valid after `SetMonData(... MON_DATA_FORM_STATE ...)`.
4. Box -> party -> box round trip preserves formState.

## Generation IV

5. No Plate -> Normal form/type.
6. Each of the sixteen Gen IV Plates selects exactly its corresponding form/type.
7. Pixie Plate is rejected by the Gen IV form resolver.
8. No held item can select the unused ??? form.
9. Judgment with Flame Plate becomes Fire and remains Special.
10. Judgment with Fist Plate becomes Fighting but still uses Sp. Atk / Sp. Def.
11. Judgment copied by another Pokémon still derives its type from that user's held Plate.
12. Multitype Arceus entering battle derives form from held Plate without changing party species.
13. Gen IV item-manipulation helper blocks changes to a Multitype Arceus regardless of current item.

## Generation V

14. Sixteen Plates still select the same 17-form set.
15. Pixie Plate remains unavailable as a form trigger.
16. Plate removal from Arceus is blocked.
17. Giving a Plate to Arceus through item manipulation is blocked.
18. Non-Plate item manipulation is not blocked by the Arceus-specific Gen V rule.

## Generation VI

19. Pixie Plate selects Fairy form/type.
20. Fairy Judgment is Special.
21. Normal plus 17 Plate forms are all addressable through explicit form -> type mapping.
22. Fairy chart contains Dragon immunity and Poison/Steel weaknesses.

## Generation VII

23. Each type-specific Z-Crystal selects the matching Multitype form.
24. Normalium Z selects Normal form.
25. Firium Z makes Arceus Fire-type.
26. Fairium Z makes Arceus Fairy-type.
27. Judgment with Firium Z remains Normal-type.
28. Judgment with Fairium Z remains Normal-type.
29. Judgment with Flame Plate still becomes Fire-type.
30. Z-Crystal item manipulation is blocked by the Arceus adapter until a generic Z-item lock replaces it.

## Generation VIII — BDSP

31. Held Plates select all 18 playable forms.
32. Judgment follows held Plate.
33. Z-Crystal mapping is not active in the BDSP ruleset.

## PLA ordinary Plates

34. Using an ordinary Plate on Arceus stores that persistent form without requiring a held item.
35. Using Blank Plate stores Normal.
36. Stored PLA form survives party/box movement and save/load.
37. Battle entry loads the stored ordinary Plate form.

## Legend Plate

38. Using Legend Plate stores Normal + Legend-state bit.
39. Legend-state Arceus enters battle as Normal.
40. Rock/Dark target -> Fighting wins on offensive effectiveness.
41. Water/Dragon target: when Dragon and Fairy are tied offensively, Dragon wins because it better resists the target's primary Water type.
42. Ghost/Dragon target: when Dark and Fairy are tied offensively, Dark wins because it better resists the target's primary Ghost type.
43. If offense and both defensive tie-breakers remain tied, selection is random only among the tied candidates.
44. Arceus changes form/type before Judgment damage/type calculation and therefore gets STAB.
45. Judgment miss still leaves Arceus in the newly selected type.
46. Sleep/freeze/flinch/full paralysis preventing the move also prevents the Legend type change.
47. A second Judgment may choose a different type and replaces the previous battle type.
48. Switching Legend-state Arceus out and back in preserves the latest battle-selected type.
49. Battle end clears the temporary Legend battle type and returns presentation to Normal.
50. Persistent formState remains Normal + Legend bit after battle.
51. A non-Arceus user of copied Judgment is Normal-type in PLA ruleset.

## Generation IX

52. Held Plate resolves Multitype form exactly as in the modern Plate ruleset.
53. Judgment type is derived from the held Plate.
54. Future Tera integration: a Terastallized Arceus must not have its battle type overwritten by Multitype.
55. Future Tera integration: Judgment must still use the held Plate type while Arceus is Terastallized.
56. A mismatched Plate type and Tera type must not receive false STAB.

## Graphics

57. No form index is used as a direct offset beyond Emerald's four-frame battler buffer.
58. Each transition reloads the selected front/back graphics and 16-color palette.
59. Re-show battle screen restores the current form from battle state rather than forcing frame 0.

## Move category

60. Judgment remains Special for every dynamic type.
61. Burn does not halve Judgment merely because its dynamic type is a Gen III physical type.
62. Reflect does not reduce Judgment; Light Screen does.
63. Plate's 20% same-type boost applies to Judgment in mainline rulesets without converting it to physical damage.

## Save / compatibility

64. A vanilla Emerald save with untouched filler bytes opens without migration and reads base form.
65. FormState changes remain inside the existing encrypted/checksummed 80-byte BoxPokemon layout.
66. Aegislash battle-only use of `gBattleMonForms` remains independent of Arceus persistent formState.

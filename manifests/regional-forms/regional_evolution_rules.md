# Regional Evolution Rules and Boundary Cases

Reference: `rh-hideout/pokeemerald-expansion` commit `75b806a3ab57a81ff1eb6179288981f0b3cc3050`.

## Ordinary species that evolve into a regional form

- `SPECIES_PIKACHU` → `SPECIES_RAICHU_ALOLA` (Alola): `{EVO_ITEM, ITEM_THUNDER_STONE, SPECIES_RAICHU, CONDITIONS({IF_NOT_REGION, REGION_ALOLA})} #if P_ALOLAN_FORMS ,{EVO_ITEM, ITEM_THUNDER_STONE, SPECIES_RAICHU_ALOLA, CONDITIONS({IF_REGION, REGION_ALOLA})} #endif`
- `SPECIES_EXEGGCUTE` → `SPECIES_EXEGGUTOR_ALOLA` (Alola): `{EVO_ITEM, ITEM_LEAF_STONE, SPECIES_EXEGGUTOR, CONDITIONS({IF_NOT_REGION, REGION_ALOLA})} #if P_ALOLAN_FORMS ,{EVO_ITEM, ITEM_LEAF_STONE, SPECIES_EXEGGUTOR_ALOLA, CONDITIONS({IF_REGION, REGION_ALOLA})} #endif`
- `SPECIES_CUBONE` → `SPECIES_MAROWAK_ALOLA` (Alola): `{EVO_LEVEL, 28, SPECIES_MAROWAK, CONDITIONS({IF_NOT_REGION, REGION_ALOLA})} #if P_ALOLAN_FORMS ,{EVO_LEVEL, 28, SPECIES_MAROWAK_ALOLA, CONDITIONS({IF_REGION, REGION_ALOLA}, {IF_TIME, TIME_NIGHT})}, {EVO_NONE, 0, SPECIES_MAROWAK_ALOLA_TOTEM} #endif`
- `SPECIES_KOFFING` → `SPECIES_WEEZING_GALAR` (Galar): `{EVO_LEVEL, 35, SPECIES_WEEZING, CONDITIONS({IF_NOT_REGION, REGION_GALAR})} #if P_GALARIAN_FORMS ,{EVO_LEVEL, 35, SPECIES_WEEZING_GALAR, CONDITIONS({IF_REGION, REGION_GALAR})} #endif`
- `SPECIES_MIME_JR` → `SPECIES_MR_MIME_GALAR` (Galar): `{EVO_LEVEL, 0, SPECIES_MR_MIME, CONDITIONS({IF_KNOWS_MOVE, MOVE_MIMIC}, {IF_NOT_REGION, REGION_GALAR})} #if P_GALARIAN_FORMS ,{EVO_LEVEL, 0, SPECIES_MR_MIME_GALAR, CONDITIONS({IF_KNOWS_MOVE, MOVE_MIMIC}, {IF_REGION, REGION_GALAR})} #endif`
- `SPECIES_QUILAVA` → `SPECIES_TYPHLOSION_HISUI` (Hisui): `{EVO_LEVEL, 36, SPECIES_TYPHLOSION, CONDITIONS({IF_NOT_REGION, REGION_HISUI})} #if P_HISUIAN_FORMS ,{EVO_LEVEL, 36, SPECIES_TYPHLOSION_HISUI, CONDITIONS({IF_REGION, REGION_HISUI})} #endif`
- `SPECIES_DEWOTT` → `SPECIES_SAMUROTT_HISUI` (Hisui): `{EVO_LEVEL, 36, SPECIES_SAMUROTT, CONDITIONS({IF_NOT_REGION, REGION_HISUI})} #if P_HISUIAN_FORMS ,{EVO_LEVEL, 36, SPECIES_SAMUROTT_HISUI, CONDITIONS({IF_REGION, REGION_HISUI})} #endif`
- `SPECIES_PETILIL` → `SPECIES_LILLIGANT_HISUI` (Hisui): `{EVO_ITEM, ITEM_SUN_STONE, SPECIES_LILLIGANT, CONDITIONS({IF_NOT_REGION, REGION_HISUI})} #if P_HISUIAN_FORMS ,{EVO_ITEM, ITEM_SUN_STONE, SPECIES_LILLIGANT_HISUI, CONDITIONS({IF_REGION, REGION_HISUI})} #endif`
- `SPECIES_RUFFLET` → `SPECIES_BRAVIARY_HISUI` (Hisui): `{EVO_LEVEL, 54, SPECIES_BRAVIARY, CONDITIONS({IF_NOT_REGION, REGION_HISUI})} #if P_HISUIAN_FORMS ,{EVO_LEVEL, 54, SPECIES_BRAVIARY_HISUI, CONDITIONS({IF_REGION, REGION_HISUI})} #endif`
- `SPECIES_GOOMY` → `SPECIES_SLIGGOO_HISUI` (Hisui): `{EVO_LEVEL, 40, SPECIES_SLIGGOO, CONDITIONS({IF_NOT_REGION, REGION_HISUI})} #if P_HISUIAN_FORMS ,{EVO_LEVEL, 40, SPECIES_SLIGGOO_HISUI, CONDITIONS({IF_REGION, REGION_HISUI})} #endif`
- `SPECIES_BERGMITE` → `SPECIES_AVALUGG_HISUI` (Hisui): `{EVO_LEVEL, 37, SPECIES_AVALUGG, CONDITIONS({IF_NOT_REGION, REGION_HISUI})} #if P_HISUIAN_FORMS ,{EVO_LEVEL, 37, SPECIES_AVALUGG_HISUI, CONDITIONS({IF_REGION, REGION_HISUI})} #endif`
- `SPECIES_DARTRIX` → `SPECIES_DECIDUEYE_HISUI` (Hisui): `{EVO_LEVEL, 34, SPECIES_DECIDUEYE, CONDITIONS({IF_NOT_REGION, REGION_HISUI})} #if P_HISUIAN_FORMS ,{EVO_LEVEL, 36, SPECIES_DECIDUEYE_HISUI, CONDITIONS({IF_REGION, REGION_HISUI})} #endif`

## Regional forms with recorded evolutions

- `SPECIES_RATTATA_ALOLA`: `{EVO_LEVEL, 20, SPECIES_RATICATE_ALOLA, CONDITIONS({IF_TIME, TIME_NIGHT})}, {EVO_NONE, 0, SPECIES_RATICATE_ALOLA_TOTEM}`
- `SPECIES_SANDSHREW_ALOLA`: `{EVO_ITEM, ITEM_ICE_STONE, SPECIES_SANDSLASH_ALOLA}`
- `SPECIES_VULPIX_ALOLA`: `{EVO_ITEM, ITEM_ICE_STONE, SPECIES_NINETALES_ALOLA}`
- `SPECIES_DIGLETT_ALOLA`: `{EVO_LEVEL, 26, SPECIES_DUGTRIO_ALOLA}`
- `SPECIES_MEOWTH_ALOLA`: `{EVO_LEVEL, 0, SPECIES_PERSIAN_ALOLA, CONDITIONS({IF_MIN_FRIENDSHIP, FRIENDSHIP_EVO_THRESHOLD})}`
- `SPECIES_GEODUDE_ALOLA`: `{EVO_LEVEL, 25, SPECIES_GRAVELER_ALOLA}`
- `SPECIES_GRAVELER_ALOLA`: `{EVO_TRADE, 0, SPECIES_GOLEM_ALOLA}, {EVO_ITEM, ITEM_LINKING_CORD, SPECIES_GOLEM_ALOLA}`
- `SPECIES_GRIMER_ALOLA`: `{EVO_LEVEL, 38, SPECIES_MUK_ALOLA}`
- `SPECIES_MEOWTH_GALAR`: `{EVO_LEVEL, 28, SPECIES_PERRSERKER}`
- `SPECIES_PONYTA_GALAR`: `{EVO_LEVEL, 40, SPECIES_RAPIDASH_GALAR}`
- `SPECIES_SLOWPOKE_GALAR`: `{EVO_ITEM, ITEM_GALARICA_CUFF, SPECIES_SLOWBRO_GALAR} #if P_GEN_2_CROSS_EVOS ,{EVO_ITEM, ITEM_GALARICA_WREATH, SPECIES_SLOWKING_GALAR} #endif`
- `SPECIES_FARFETCHD_GALAR`: `{EVO_BATTLE_END, 0, SPECIES_SIRFETCHD, CONDITIONS({IF_CRITICAL_HITS_GE, 3})}`
- `SPECIES_MR_MIME_GALAR`: `{EVO_LEVEL, 42, SPECIES_MR_RIME}`
- `SPECIES_CORSOLA_GALAR`: `{EVO_LEVEL, 38, SPECIES_CURSOLA}`
- `SPECIES_ZIGZAGOON_GALAR`: `{EVO_LEVEL, 20, SPECIES_LINOONE_GALAR}`
- `SPECIES_LINOONE_GALAR`: `{EVO_LEVEL, 35, SPECIES_OBSTAGOON, CONDITIONS({IF_TIME, TIME_NIGHT})}`
- `SPECIES_DARUMAKA_GALAR`: `{EVO_ITEM, ITEM_ICE_STONE, SPECIES_DARMANITAN_GALAR_STANDARD}`
- `SPECIES_YAMASK_GALAR`: `{EVO_SCRIPT_TRIGGER, EVO_TRIGGER_TABLET_CURSE, SPECIES_RUNERIGUS, CONDITIONS({IF_CURRENT_DAMAGE_GE, 49})}`
- `SPECIES_GROWLITHE_HISUI`: `{EVO_ITEM, ITEM_FIRE_STONE, SPECIES_ARCANINE_HISUI}`
- `SPECIES_VOLTORB_HISUI`: `{EVO_ITEM, ITEM_LEAF_STONE, SPECIES_ELECTRODE_HISUI}`
- `SPECIES_QWILFISH_HISUI`: `{EVO_LEVEL, 0, SPECIES_OVERQWIL, CONDITIONS({IF_KNOWS_MOVE, MOVE_BARB_BARRAGE})}`
- `SPECIES_SNEASEL_HISUI`: `{EVO_LEVEL, 0, SPECIES_SNEASLER, CONDITIONS({IF_NOT_TIME, TIME_NIGHT}, {IF_HOLD_ITEM, ITEM_RAZOR_CLAW})}, {EVO_ITEM, ITEM_RAZOR_CLAW, SPECIES_SNEASLER, CONDITIONS({IF_NOT_TIME, TIME_NIGHT})}`
- `SPECIES_ZORUA_HISUI`: `{EVO_LEVEL, 30, SPECIES_ZOROARK_HISUI}`
- `SPECIES_SLIGGOO_HISUI`: `{EVO_LEVEL, 50, SPECIES_GOODRA_HISUI, CONDITIONS({IF_WEATHER, WEATHER_RAIN})}, {EVO_LEVEL, 50, SPECIES_GOODRA_HISUI, CONDITIONS({IF_WEATHER, WEATHER_FOG})}`
- `SPECIES_WOOPER_PALDEA`: `{EVO_LEVEL, 20, SPECIES_CLODSIRE}`
- `SPECIES_BASCULIN_WHITE_STRIPED`: `{EVO_LEVEL, 0, SPECIES_BASCULEGION_M, CONDITIONS({IF_RECOIL_DAMAGE_GE, 294}, {IF_GENDER, MON_MALE})}, {EVO_LEVEL, 0, SPECIES_BASCULEGION_F, CONDITIONS({IF_RECOIL_DAMAGE_GE, 294}, {IF_GENDER, MON_FEMALE})}`

## Nested form inside a regional form

- `SPECIES_DARMANITAN_GALAR_STANDARD` can become `SPECIES_DARMANITAN_GALAR_ZEN` through Zen Mode. Reference Zen parameters: ICE,FIRE, stats 105/160/55/30/55/135, BST 540. This is a battle/form-change layer, not another regional-form count.

## EMERALD modeling consequence

1. Persist regional identity as a species/form identity independent from National Dex number.
2. Keep regional-evolution species as independent National Dex species.
3. Keep region-sensitive evolution conditions separate from battle-only form changes.
4. White-Striped Basculin remains explicitly tagged as a special classification boundary case rather than silently merged into named Hisuian forms.

## Game-specific regional-evolution semantics

The reference implementation above is useful for EMERALD engineering, but it intentionally normalizes some later-game evolution mechanics. Preserve these title-specific rules separately when source-faithful behavior matters.

| Line | Title / ruleset | Evolution trigger |
| --- | --- | --- |
| Galarian Linoone → Obstagoon | Sword/Shield rule | Level 35 or higher at night. |
| Galarian Meowth → Perrserker | Sword/Shield rule | Level 28. |
| Galarian Corsola → Cursola | Sword/Shield rule | Level 38. |
| Galarian Farfetch'd → Sirfetch'd | Sword/Shield rule | Land at least 3 critical hits in one battle; evolution occurs after the battle. |
| Galarian Mr. Mime → Mr. Rime | Sword/Shield rule | Level 42. |
| Galarian Yamask → Runerigus | Sword/Shield | Take at least 49 HP of qualifying attack damage without fainting, then travel under the designated rock arch in Dusty Bowl. Healing does not erase the accumulated qualifying damage. |
| Galarian Yamask → Runerigus | Legends Z-A | The same 49-HP damage concept is retained, with the designated overworld trigger associated with the bridges above Coulant Waterway. |
| Hisuian Sneasel → Sneasler | Legends: Arceus | Expose it to a Razor Claw during the daytime. |
| Hisuian Sneasel → Sneasler | Scarlet/Violet | Level up while holding a Razor Claw during the daytime. |
| Hisuian Qwilfish → Overqwil | Legends: Arceus | Use Barb Barrage in Strong Style 20 times. |
| Hisuian Qwilfish → Overqwil | Scarlet/Violet 3.0.0+ | Level up while knowing Barb Barrage. |
| Hisuian Qwilfish → Overqwil | Legends Z-A | Land 20 hits with Barb Barrage; each target hit can increment the counter. |
| Paldean Wooper → Clodsire | Scarlet/Violet rule | Level 20. |
| White-Striped Basculin → Basculegion | Legends: Arceus | Cumulatively lose at least 294 HP to recoil without fainting; no additional level-up is required. Sex selects male/female Basculegion. |
| White-Striped Basculin → Basculegion | Scarlet/Violet-style rule | After cumulatively losing at least 294 HP to recoil without fainting, level up. Fainting resets progress; recovery does not. Sex selects male/female Basculegion. |

### Modeling requirement

Do not collapse the table above into a single global `EvolutionMethod`. EMERALD should retain a stable semantic condition set (level, time, held/used item, known move, battle critical-hit counter, qualifying damage counter, recoil counter, overworld/script trigger, gender) and let a per-ruleset policy select which conditions apply. This lets the same save/species representation reproduce Sword/Shield, Legends: Arceus, Scarlet/Violet, and Legends Z-A behavior without inventing separate Pokémon species for mechanic differences.

### External verification references

- https://bulbapedia.bulbagarden.net/wiki/Regional_form
- https://bulbapedia.bulbagarden.net/wiki/Overqwil_(Pok%C3%A9mon)
- https://bulbapedia.bulbagarden.net/wiki/Yamask_(Pok%C3%A9mon)
- https://bulbapedia.bulbagarden.net/wiki/Sneasel_(Pok%C3%A9mon)
- https://bulbapedia.bulbagarden.net/wiki/Basculin_(Pok%C3%A9mon)
- https://bulbapedia.bulbagarden.net/wiki/Critical_hit

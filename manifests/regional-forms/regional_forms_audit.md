# Regional Forms / Regional Evolutions — Parameter Survey Audit

Audit date: 2026-09-21

Reference implementation snapshot: `rh-hideout/pokeemerald-expansion` commit `75b806a3ab57a81ff1eb6179288981f0b3cc3050` (2026-09-20).

## Scope result

The current survey is internally complete for the regional-form and regional-evolution species set used by this project.

| Category | Count |
| --- | ---: |
| Named regional forms | 57 |
| White-Striped Basculin special regional-form boundary case | 1 |
| Strict regional-evolution species | 9 |
| Basculegion parameter forms (male/female) | 2 |
| Total master rows | 69 |

Named regional forms by region:

- Alola: 18
- Galar: 19
- Hisui: 16
- Paldea: 4

Including White-Striped Basculin gives 58 regional-form entries.

## Parameter integrity checks

- `regional_forms_master.csv`: 69 data rows.
- Base-stat total verification: 0 BST mismatches across all 69 rows.
- `regional_forms_levelup_reference.json`: 69 entries, 0 missing.
- `regional_forms_egg_moves_reference.json`: 69 entries, 0 missing.
- `regional_forms_graphics_reference.json`: 69 assets, 0 missing.
- Master CSV/JSON also retain type, base stats, abilities, gender ratio, height, weight, catch rate, EXP yield, egg cycles, friendship, growth rate, egg groups, cry mapping, regional flags, learnset symbols, graphics symbols and raw evolution semantics.

## Classification boundaries

### White-Striped Basculin

Keep `SPECIES_BASCULIN_WHITE_STRIPED` explicitly tagged as a special boundary case rather than silently merging it into the named `HISUI` form flag set.

The Japanese official Pokédex text for White-Striped Basculin states that, despite differences such as temperament, it has many Basculin characteristics and is defined as a regional form. The same modern Pokédex page also preserves Scarlet/Violet text noting that a separate-species hypothesis has become influential. This makes an explicit special classification useful for source-faithful research.

Official reference:
- https://zukan.pokemon.co.jp/detail/0550-2

### Ordinary species that evolve into regional forms

These must remain distinct from strict regional evolutions into a new National Dex species. Examples include Pikachu → Alolan Raichu and Quilava → Hisuian Typhlosion.

### Nested battle form

Galarian Darmanitan Zen Mode is a battle/form-change layer inside a regional form. It is not another regional-form count.

## Teachable-learnset status

The master rows already retain the `teachableLearnset` symbols, but the concrete generated move arrays are not frozen as a separate survey artifact yet.

The reference implementation generates `src/data/pokemon/teachable_learnsets.h` from:

1. `src/data/pokemon/all_learnables.json` (potential official-game learnables),
2. each species' teaching type,
3. TMs/HMs and tutors actually enabled in the build.

Therefore the final teachable set is build-policy dependent and should not be treated as a fixed species parameter without recording the build's TM/tutor configuration.

Reference documentation:
- https://github.com/rh-hideout/pokeemerald-expansion/blob/75b806a3ab57a81ff1eb6179288981f0b3cc3050/docs/tutorials/teachable_learnsets.md

The deterministic extractor and completeness gate are implemented in `tools/extract_regional_teachables.py` and documented in `manifests/regional-forms/regional_forms_teachable_extraction.md`. Before source integration is declared complete, run it against the generated header of the chosen EMERALD ruleset and commit:
- `manifests/regional-forms/regional_forms_teachable_reference.json`
- `manifests/regional-forms/regional_forms_teachable_reference.md`

## Official concept checks

Japanese official material defines regional forms as Pokémon adapted to a region-specific environment and explicitly distinguishes Galar-only evolutionary branches.

References:
- https://www.pokemon.co.jp/ex/usum/howtoplay/171027_01.html
- https://www.pokemon.co.jp/ex/sword_shield/story/190807_02.html
- https://zukan.pokemon.co.jp/detail/0052-2
- https://zukan.pokemon.co.jp/detail/0264-1

## Audit conclusion

The species/form roster, core battle parameters, evolution semantics, level-up moves, egg moves and graphics references are complete for the 69-row survey set. The only intentionally non-frozen parameter family is the generated teachable-move set, because it depends on the final EMERALD TM/HM/tutor policy.

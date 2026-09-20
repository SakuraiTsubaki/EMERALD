# Regional Forms / Regional Evolutions — Expanded EMERALD profile

The complete regional-form implementation uses **rh-hideout/pokeemerald-expansion** as the executable source base rather than rebuilding its modern Pokémon engine piecemeal on top of vanilla `pret/pokeemerald`.

Pinned upstream:

- repository: `rh-hideout/pokeemerald-expansion`
- commit: `75b806a3ab57a81ff1eb6179288981f0b3cc3050`
- profile: `expanded` in `manifests/engine-base.yml`

## Included scope

The project roster is frozen in `manifests/regional-forms/`:

- 57 named regional forms
- White-Striped Basculin as one explicit special boundary case
- 9 strict regional-evolution species
- male/female Basculegion parameter forms
- 69 master rows total
- Galarian Darmanitan Zen Mode tracked separately as a nested battle form

The upstream engine already provides the species constants, modern types, abilities, moves, evolution-condition machinery, learnsets, sprites, palettes, icons, cries, and save/Pokédex infrastructure needed by these entries.

## Why this is a separate build profile

The existing `classic` profile and `patches/pokeemerald/` remain tied to vanilla `pret/pokeemerald` for the external-event project.

The regional-form work requires modern dependencies that vanilla Emerald does not have: later-generation species IDs, Fairy type, later abilities/items/moves, region-aware evolution conditions, battle counters, and the corresponding graphics/audio resources. Reimplementing all of those independently would duplicate the expansion engine.

The `expanded` profile therefore pins the verified expansion source and applies only EMERALD-specific overlay patches.

## Required configuration

`tools/verify_regional_forms.py` makes the integration fail verification if regional forms, new regional evolutions, or cross-generation evolution support are disabled in the pinned source.

The pinned upstream already defaults to:

- `P_REGIONAL_FORMS TRUE`
- Alola / Galar / Hisui / Paldea aliases enabled
- `P_CROSS_GENERATION_EVOS TRUE`
- `P_NEW_EVOS_IN_REGIONAL_DEX TRUE`
- all generations of Pokémon enabled

## Verification

Run from this repository:

```sh
python tools/verify_regional_forms.py /path/to/pokeemerald-expansion
```

The verifier checks the pinned profile configuration and every master-row species/form symbol against the supplied source tree. It also checks the referenced level-up, teachable, egg-move and graphics symbols when present in the master data.

## Evolution policy

The source-faithful rule survey is retained in:

- `manifests/regional-forms/regional_evolution_rules.md`

Do not collapse title-specific mechanics into one universal rule. In particular, Qwilfish, Sneasel, Yamask and White-Striped Basculin have mechanics whose exact trigger differs by later title. The project keeps those distinctions as policy data instead of inventing extra species IDs.

# Morpeko / モルペコ — Generation VIII reference

Implementation target: Pokémon Sword / Shield debut behavior.

## Japanese-first identity

- モルペコ まんぷくもよう — Full Belly Mode
- モルペコ はらぺこもよう — Hangry Mode
- 特性: はらぺこスイッチ / Hunger Switch
- 専用技: オーラぐるま / Aura Wheel
- Type in both forms: Electric / Dark
- Base stats in both forms: 58 / 95 / 58 / 97 / 70 / 58
  - order: HP / Atk / Def / Spe / SpA / SpD

The Japanese Pokémon Sword / Shield official site states that Hunger Switch changes Morpeko's appearance every turn and that Aura Wheel is Electric in Full Belly Mode and Dark in Hangry Mode.

Official Japanese reference:
- https://www.pokemon.co.jp/ex/sword_shield/pokemon/190807_01.html
- https://zukan.pokemon.co.jp/detail/0877

## Battle transition model

Reference implementation inspected:
`rh-hideout/pokeemerald-expansion@c7d7ec67b0ca8134e5c290e624780a29440ee09c`.

Relevant paths:
- `src/data/pokemon/form_change_tables.h`
- `src/data/pokemon/species_info/gen_8_families.h`
- `src/data/moves_info.h`
- `src/battle_end_turn.c`
- `src/battle_main.c`
- `test/battle/ability/hunger_switch.c`
- `test/battle/move_effect/aura_wheel.c`

Verified transition table:
- end of turn: Full Belly -> Hangry
- end of turn: Hangry -> Full Belly
- switch out: -> Full Belly
- faint: -> Full Belly
- battle end: -> Full Belly
- a Pokémon merely transformed into Morpeko does not receive Hunger Switch's end-turn toggle

EMERALD representation:
- one persistent `SPECIES_MORPEKO`
- `gBattleMonForms[battler] = 0`: Full Belly
- `gBattleMonForms[battler] = 1`: Hangry
- party/save species remains Morpeko
- no base-stat or base-type recalculation is required during the form transition

## Aura Wheel

Debut-generation move parameters used by the port:
- Power: 110
- Accuracy: 100
- PP: 10
- Category: Physical
- Base type: Electric
- successful use raises the user's Speed by one stage
- Hangry Mode changes the move type to Dark
- Normalize overrides the form-derived type and makes the move Normal
- a non-Morpeko user cannot execute Aura Wheel
- a Pokémon transformed into Morpeko can execute Aura Wheel

The Speed boost must go through the normal battle stat-change plumbing rather than directly editing the stage byte so ordinary battle modifiers and messages remain coherent.

## Graphics

Source graphics are pinned to the same expansion reference above.

Target conversion rules:
- 64x64 indexed PNG
- palette index 0 reserved as transparency key
- no anti-aliasing
- no interpolation
- no invented colors
- maximum 16 palette indices
- GBA 4bpp tile order
- matching normal and shiny 16-entry GBA palettes
- combined front order: Full Belly, Hangry
- combined back order: Full Belly, Hangry

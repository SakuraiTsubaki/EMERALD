# Pokémon form census status

Status date: 2026-09-19

## Verdict

The form investigation is **not yet a complete census**.

The current EMERALD research is sufficient to identify the major engine/state models needed for a cross-generation form system, but it is not yet a row-by-row inventory of every official/internal form and every game/version-specific trigger and parameter.

## What is already covered

| Scope | Current evidence | Status |
| --- | --- | --- |
| Emerald retail ROM | `research/emerald-rom-form-audit.md` | Strong targeted audit of Castform, Unown, Deoxys, Spinda |
| Gen IV | `research/gen4-form-mechanics.md`, `manifests/gen4-form-mechanics.csv` | Core mechanics covered; not exhaustive row-by-row |
| Gen V | conversation/research notes only | **Missing dedicated repository census** |
| Gen VI | `research/gen6-form-mechanics.md`, manifest | Core mechanics covered; many grouped entries |
| Gen VII | `research/gen7-form-mechanics.md`, manifest | Core mechanics covered; regional/Totem/type-form families grouped |
| Gen VIII | `research/gen8-form-mechanics.md`, manifest | Core mechanics covered; G-Max and many identity families not enumerated individually |
| Gen IX | `research/gen9-form-mechanics.md`, manifest | Core mechanics covered; forms grouped and exact target ROM builds not pinned |
| Gen I-II | no dedicated census | **Not yet audited as a generation-wide form baseline** |

## Why this is not yet "전수조사 완료"

Examples of remaining gaps:

- every form must have one canonical row rather than grouped labels such as "9 trims", "20 patterns", "4 sizes", "18 Alolan forms", "63 combinations", "Type Form", "G-Max";
- every generation/version must be checked because the **same form can use different triggers or parameters in different games**;
- Gen V still needs a dedicated source/ROM-backed manifest;
- Gen I-II need their own baseline audit, especially Unown's historical form representation;
- Gen III needs Ruby/Sapphire/FireRed/LeafGreen and version-specific Deoxys handling in addition to the Emerald audit;
- all Mega Evolutions, Gigantamax forms, regional forms, Totem/internal forms, Vivillon patterns, Furfrou trims, Minior colors, Silvally/Arceus type forms, Alcremie combinations and similar families must be enumerated individually;
- unobtainable/data-only/scripted/boss-only forms need explicit rows instead of being mixed with player-usable forms;
- gender differences, costume forms, partner/special-individual forms and purely visual battle states need an explicit inclusion taxonomy;
- each row still needs complete parameters: species/form index, stats, types, abilities, learnset/move override, graphics/icon/palette/model identity, cry, height/weight/scale where relevant, trigger, reset condition, persistence, item/move/ability IDs, save-field representation, Pokédex behavior, transfer restrictions, and generation/version differences;
- exact Japanese target ROM/build identity is still unselected for many later-generation repositories, so ROM offsets and binary-table identities cannot yet be called verified target facts.

## Completion criterion

A true complete census will require a master manifest where **every distinct official/internal form state has an individual row**, linked to per-game/per-version evidence.

Recommended master outputs:

- `manifests/pokemon-form-census.csv`
- `manifests/pokemon-form-game-parameters.csv`
- `manifests/pokemon-form-triggers.csv`
- `research/pokemon-form-census.md`

The census should separate:
- persistent identity form;
- battle-only form;
- derived/item form;
- sub-identity / form argument;
- fusion;
- transformation system (Mega/Dynamax/Tera/etc.);
- data-only/unobtainable form;
- scripted/boss form;
- cosmetic/procedural appearance.

Only after all rows are reconciled against the relevant game/version sources should the project call the form survey complete.

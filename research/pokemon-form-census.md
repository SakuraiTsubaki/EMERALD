# Pokémon form census — normalized master inventory

Updated: 2026-09-19

## Census result

- Pokémon form/state rows: **799**
- non-Pokémon Pokéstar battle-actor rows moved out of census: **38**
- remaining unresolved numeric form-index rows: **0**
- Alcremie 63 cream/Sweet appearance combinations are expanded individually.
- Koraidon/Miraidon five presentation modes are explicitly represented.
- Ogerpon battle-only Embody Aspect forms are explicitly represented as form IDs 4-7.
- Gigantamax rows are no longer treated as missing persistent Form IDs; Gigantamax capability is a separate individual flag and G-Max is a battle transformation representation.

Rows by introduction generation:

- Gen 1: 58
- Gen 2: 44
- Gen 3: 34
- Gen 4: 55
- Gen 5: 47
- Gen 6: 168
- Gen 7: 100
- Gen 8: 200
- Gen 9: 93

## Evidence model

Enumeration and internal-form rules:
- PKHeX @ 8ad201e80244f630ab5a46922ab72fb79c5ad4f4

Current cross-generation personal parameters:
- Pokémon Showdown data/pokedex.ts @ 2ddfa0476f8207e12e204b1c69f7c7683b17633c

The census distinguishes **reference-order form indices** from **target-ROM-verified indices**. A Showdown formeOrder is useful for census ordering but is not promoted to a Japanese retail-ROM address/index claim.

## What "complete" means here

The **identity/state census** is now broad enough to enumerate normal alternate forms, cosmetic forms, battle-only forms, regional forms, Mega/G-Max forms, hidden/internal form values, compound FormArgument identities, scripted Lord/Lady forms and procedural Spinda appearance.

What is still a separate verification campaign is per-title/per-revision binary proof:
- exact Japanese retail/update build identity;
- exact personal-table form index and data-table offset;
- trigger/reset code address;
- graphics/model/cry table reference;
- historical parameter changes between generations.

That work belongs in a per-game parameter/ROM-evidence matrix, not by bloating the identity census.

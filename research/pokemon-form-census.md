# Pokémon form census — master inventory

Generated: 2026-09-19

## Scope

This is the first normalized **one-row-per-form/state** master inventory for EMERALD.

Primary enumeration baselines:
- Pokémon Showdown `data/pokedex.ts@2ddfa0476f8207e12e204b1c69f7c7683b17633c`
- PKHeX form/internal-form rules `@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

Japanese and Korean species names are pulled from the same pinned PKHeX revision. English technical form labels remain in the machine-readable form columns so source identifiers stay stable.

## Current census size

- normalized rows: **770**
- form families: **259**
- rows with unresolved exact numeric form index: **52**
- separate transformation-system rows: **9**

Rows by introduction generation:

- Gen 1: 123
- Gen 2: 56
- Gen 3: 58
- Gen 4: 60
- Gen 5: 91
- Gen 6: 124
- Gen 7: 82
- Gen 8: 89
- Gen 9: 87

## What is included

- base forms for every species family that has an alternate form;
- alternate personal-data forms;
- Mega / Mega X / Mega Y / Mega Z forms present in the current source baseline;
- Gigantamax forms represented as Pokémon form data;
- regional forms;
- battle-only forms represented as separate personal/form records;
- cosmetic forms referenced by the source data;
- Totem forms represented in the form data;
- Unown letters/punctuation;
- Vivillon patterns;
- Pikachu costume/cap forms;
- Alcremie cream forms (Sweet decoration remains a form argument/sub-identity, not a distinct numeric Form);
- data-only / unobtainable forms surfaced by the source data;
- manual internal additions: Mothim cloak values, Scatterbug/Spewpa hidden Vivillon-pattern values, Gen IV ??? Arceus, PLA Lord/Lady forms;
- Spinda procedural appearance as a non-discrete census row.

## Important distinction

Not every transformation is a stored form ID. `manifests/pokemon-form-transformation-systems.csv` separately tracks systems such as Dynamax and Terastallization where the entity's ordinary persistent Form is not replaced.

## What still blocks the word "fully verified"

The identity census is now mechanically broad, but 52 rows still lack a target-verified numeric form index. These are mostly records where the public parameter source names the form but does not expose the game's numeric form slot directly.

Also, later-generation user repositories still have exact Japanese build identity marked `unselected`. Until those exact retail/update builds are pinned, ROM offsets and binary table indices cannot honestly be called target-verified.

The next verification pass is therefore **numeric form-index and per-game trigger reconciliation**, not another representative-form survey.

# PKHeX localization reference

Pinned source: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

Project language priority is applied directly:

1. Japanese
2. Korean
3. English
4. other official languages later

The normalized table is:
- `manifests/pkhex/localized-names.csv`

Counts:
- species: 1026
- moves: 921
- abilities: 311
- forms: 1142
- items: 2685

## Index semantics

- species: resource index corresponds to species ID.
- moves: resource index corresponds to move ID.
- abilities: resource index corresponds to Ability ID.
- forms: this is a **form-label string index**, not the species' numeric Form value.
- items: global PKHeX item-text index; per-game item validity/mapping must still be checked against ItemStorage and game-specific tables.

This table is for names and identity alignment. Gameplay parameters remain in separate normalized manifests.

# Pokémon form census status

Updated: 2026-09-19

## Identity census

**Complete at the cross-generation reference level.**

- master Pokémon form/state rows: 799
- numeric-index gaps in the normalized reference census: 0
- non-Pokémon Pokéstar Studio battle actors: separated into their own manifest
- Alcremie 63 appearance combinations: expanded
- hidden/internal form values: included where identified by PKHeX rules
- Gigantamax: correctly classified as battle transformation/capability rather than a missing persistent Form ID

Primary file:
- `manifests/pokemon-form-census.csv`

## Game-parameter census

A normalized parameter table now exists:
- `manifests/pokemon-form-game-parameters.csv`

It contains per-form reference stats, types and Abilities plus form/sub-identity indices where the source model exposes them.

A trigger table also exists:
- `manifests/pokemon-form-trigger-matrix.csv`

## What is NOT yet target-ROM verified

"Cross-generation census complete" is not the same as "every retail binary fully reverse-engineered."

Still pending as a separate verification layer:
- exact Japanese retail/update build identity for repositories whose target is still unselected;
- exact ROM/personal-table offsets for each later title;
- exact historical per-title parameter overrides when a form was rebalanced;
- exact trigger/reset function addresses;
- graphics/model/icon/cry archive indices;
- transfer/Pokédex flags in every individual title/revision.

Those fields should be added as per-game evidence rows without changing the 799-row identity census.

# Generation 10 readiness

EMERALD is reserving engine capacity for Generation 10 before resuming additional form-change work.

This is capacity work, not speculative content work. No unreleased species, moves, items, abilities, forms, mechanics, IDs, or save fields are invented here.

## Current expansion baseline

Pinned executable base:

- rh-hideout/pokeemerald-expansion@75b806a3ab57a81ff1eb6179288981f0b3cc3050
- generation constants: include/config/general.h

The pinned source currently orders behavior generations as:

GEN_9 -> GEN_CHAMPIONS -> GEN_COUNT

GEN_CHAMPIONS is already a distinct post-Gen-9 behavior slot. It must not be renumbered just to make room for Generation 10.

EMERALD therefore reserves the next slot as:

GEN_9 -> GEN_CHAMPIONS -> GEN_10 -> GEN_COUNT

The overlay patch is:

patches/pokeemerald-expansion/0001-reserve-generation-10-slot.patch

It deliberately leaves GEN_LATEST = GEN_9 until Generation 10 behavior and data are actually known and verified.

## What changes now

1. The expanded engine gets a reserved GEN_10 configuration value after GEN_CHAMPIONS.
2. GEN_COUNT expands with it.
3. GEN_LATEST stays on Gen 9, so no current mechanics silently change.
4. PKHeX helper scripts read their source commit from manifests/pkhex-source-pin.yml instead of embedding the SHA in multiple scripts.
5. generation-specific TM/item display remaps are exported to a generic append-only table, while the existing Gen-9-specific output remains available for compatibility.
6. CI verifies that the reserved generation ordering stays intact.

## When Generation 10 source data becomes available

Do not renumber any existing EMERALD identifier.

Update in this order:

1. update authoritative Japanese-first source references;
2. advance pinned PKHeX / engine references only after review;
3. append new species, item, move, ability, evolution, learnset, encounter and save-format data;
4. add exact Generation 10 behavior rules;
5. verify save/entity width and serialization assumptions against the real formats;
6. only then switch GEN_LATEST to GEN_10.

Form-change implementation is intentionally outside this phase.

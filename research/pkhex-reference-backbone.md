# PKHeX as EMERALD reference backbone

Pinned reference: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4` (GPL-3.0).

## Decision

Use PKHeX as a **cross-generation reference oracle**, not as code to paste into the Emerald ROM project.

PKHeX.Core already centralizes:
- personal/species/form tables from Gen I through Gen IX/Z-A;
- PK1-PK9, PA8/PA9 Pokémon entity layouts;
- save formats and block structures across generations;
- encounter and legality constraints;
- evolution, learnset, tutor/TM and transfer rules;
- item availability/storage;
- Mystery Gift formats;
- ribbons/marks;
- localized strings;
- generation conversion behavior.

This gives EMERALD one consistent place to discover *what must be represented*. Exact Japanese ROM/decomp evidence remains authoritative for *how the target game actually implements it*.

## Snapshot size

The pinned repository contains **11664 files**.
`PKHeX.Core` contains **3549 files**.

Largest Core groups:
- Resources: 1731
- Legality: 642
- Saves: 617
- PKM: 183
- Editing: 160
- Items: 49
- PersonalInfo: 48
- Game: 41
- MysteryGifts: 21
- Ribbons: 20
- Moves: 16

## Why not copy it wholesale

PKHeX is GPLv3. More importantly, its C# implementation targets a desktop/save-editor domain, not a GBA ROM engine. Directly porting classes would couple EMERALD to unrelated UI/editor architecture and make source provenance harder to audit.

Instead:
1. pin PKHeX revision;
2. catalog every relevant source/resource path;
3. extract factual tables/rules into EMERALD-owned normalized manifests;
4. retain source path + commit provenance on every generated row;
5. compare against the exact game/version decomp or ROM;
6. implement the mechanic natively in Emerald C/ASM/data.

## Authority rule

When sources disagree:
1. exact Japanese target retail ROM / exact decomp revision;
2. exact game/version PKHeX table;
3. PKHeX conversion/legal model;
4. secondary references.

PKHeX is therefore the **coverage oracle**; the ROM is the **implementation oracle**.

## Import waves

### Wave A — schema backbone
Species/forms, personal data, moves, abilities, items, evolution and game IDs.

### Wave B — entity/save semantics
PK1-PK9/PA8/PA9 layouts, encryption/checksums, save blocks and form arguments.

### Wave C — gameplay relationships
Learnsets, TM/tutor compatibility, encounter/form legality, transfer conversion and item-driven form rules.

### Wave D — events
Mystery Gifts, event encounters, ribbons/marks and special distribution metadata.

### Wave E — regression oracle
Translate useful PKHeX test invariants into EMERALD-side validation without copying the application code.

## Asset rule

`PKHeX.Drawing.PokeSprite` and other artwork are cataloged only as references. Do not copy sprite/image assets into EMERALD as part of this pipeline. Actual game graphics must come from the appropriate game assets/extraction pipeline with their own provenance.

## Files

- `manifests/pkhex-source-pin.yml`
- `manifests/pkhex-domain-map.csv`
- `manifests/pkhex-repository-summary.csv`
- `manifests/pkhex-core-inventory.csv`
- `tools/pkhex_reference_extract.py`

The existing 809-row Pokémon form census is the first consumer of this backbone.

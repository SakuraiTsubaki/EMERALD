# PKHeX reference backbone

Pinned upstream:
- repository: `kwsch/PKHeX`
- commit: `8ad201e80244f630ab5a46922ab72fb79c5ad4f4`
- license: **GPLv3**

## Inventory

The pinned repository has been split into stable per-section manifests under `manifests/pkhex/`.

Total inventoried files: **11,643**

Core data/logic inventory:
- PKM: 183
- PersonalInfo: 48
- Items: 49
- Moves: 16
- Saves: 617
- Legality: 642
- Resources: 1,731
- MysteryGifts: 21
- Ribbons: 20
- Game metadata: 41
- Editing/reference algorithms: 160

Non-target layers:
- WinForms: 501
- Drawing: 3
- Drawing.Misc: 863
- Drawing.PokeSprite: 6,460
- Tests: 264
- .github: 15
- root files: 9

## Import rule

PKHeX is the **reference oracle**, not the Emerald runtime implementation.

We extract and normalize facts into EMERALD-owned CSV/JSON/YAML, then reconcile them against the actual game source/ROM before changing Emerald.

This is especially important because:
- PKHeX is GPLv3;
- current PKHeX abstractions can merge knowledge from many games and updates;
- an editor/legality rule is not automatically the same as a retail ROM routine;
- drawing/sprite projects contain additional third-party asset provenance.

Therefore:
- **data facts / IDs / layouts / relationships:** extract + verify;
- **algorithms:** use as reference, independently implement when needed;
- **WinForms/UI:** do not import;
- **sprite/drawing assets:** do not import without independent provenance review;
- **Tests:** use as verification reference.

## Language priority

For names/text:
1. Japanese
2. Korean
3. English
4. other official languages

## Target policy

Existing Emerald content remains canonical for existing Emerald entries:
- existing Emerald item IDs stay fixed;
- existing Emerald gameplay parameters stay fixed unless the project explicitly chooses a mechanic update;
- later-generation content is appended/extended rather than renumbering Emerald;
- source/reference data never overrides a verified Emerald ROM fact merely because it is newer.

## Extraction program

See:
- `manifests/pkhex-extraction-plan.csv`
- `manifests/pkhex-reference-index.csv`

The existing 809-row form census is the first completed normalized dataset from this backbone.

Next high-value extraction is **PersonalInfo by game**, because it gives one consistent backbone for species/form stats, typing, abilities, growth, gender and form-table identity across generations.

# PKHeX reference backbone for EMERALD

Pinned upstream reference:

- repository: `kwsch/PKHeX`
- commit: `8ad201e80244f630ab5a46922ab72fb79c5ad4f4`
- license: GPL-3.0
- selected scope: `PKHeX.Core`
- enumerated core files: **3,528**

## Why PKHeX.Core is the backbone

PKHeX already separates the cross-generation knowledge we need into reusable domains:

- Pokémon entity layouts: PK1-PK9, PA8/PA9
- per-game personal tables
- alternate-form and battle-form rules
- item validity/storage by game
- move metadata by generation
- save structures SAV1-SAV9
- encounter/evolution/learnset/RNG/transfer legality
- Mystery Gift formats
- ribbons/marks
- location/version metadata
- binary resources for personal/evolution/level-up/egg moves
- Japanese/Korean/English and other localized text resources

## Import rule

EMERALD will **not vendor/copy the PKHeX source tree**.

Instead, PKHeX is treated as a pinned reference oracle:

1. inspect a specific PKHeX commit;
2. extract factual mappings and tables;
3. normalize them into EMERALD CSV/JSON/YAML manifests;
4. record upstream path + commit provenance;
5. implement Emerald-side behavior independently.

This avoids coupling the ROM implementation to PKHeX's C# architecture while preserving traceability.

## Scope decision

Do not recursively inventory WinForms/Drawing on every pass. They are not required for the ROM/game-parameter backbone.

Primary working scope is `PKHeX.Core`:
- PKM
- PersonalInfo
- Items
- Moves
- Saves
- Legality
- MysteryGifts
- Ribbons
- Game
- Resources
- Editing helpers

WinForms/Drawing can be consulted only when a specific UI/sprite reference is needed.

## Next extraction order

1. species + form + personal tables
2. items
3. moves
4. abilities
5. evolutions
6. learnsets / egg moves / tutors
7. encounter tables
8. entity/save field layouts
9. conversion rules between generations
10. mystery gifts
11. ribbons/marks
12. Pokédex / transfer / legality restrictions

Japanese naming remains the primary language reference for this project, followed by Korean, then English.

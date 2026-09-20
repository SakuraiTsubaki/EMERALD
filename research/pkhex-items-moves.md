# PKHeX item / move ID-space reference

Pinned reference: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

`PKHeX.Core/Legality/Legal.cs` provides per-title maximum Species, Move and Item IDs.

The normalized table is:
- `manifests/pkhex/generation-limits.csv`

## Why this matters for EMERALD

Emerald's native ceilings are:
- Species: 386
- Move: 354
- Item: 376

Later-generation import must therefore use explicit extension spaces and crosswalks rather than replacing Emerald IDs.

## PKHeX coverage

### MoveInfo
PKHeX contains generation/context-specific:
- base PP tables;
- type tables in generations where PKHeX needs them;
- dummied-move bitsets for modern titles;
- maximum valid Move IDs;
- special classification helpers such as Dynamax/Torque moves.

It is **not a replacement for each game's full battle-engine move-effect table**. Power, accuracy, target logic and effect scripts still need source/ROM data when implementing them in Emerald.

### ItemStorage
PKHeX contains per-game:
- legal item IDs;
- inventory pocket/category membership;
- TM/HM/TR groupings;
- unreleased/invalid item filters;
- held-item legality sets.

It is **not a complete replacement for Emerald's gameplay item struct**. Existing Emerald item behavior remains canonical for shared items in this project, while later-generation ItemStorage is used for identity/availability/cross-generation validation.

This separation prevents the PKHeX legality model from accidentally overwriting Emerald gameplay parameters.

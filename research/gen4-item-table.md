# Generation IV item table crosswalk

This note aligns the public decompilation item tables for Diamond/Pearl, Platinum, and HeartGold/SoulSilver so EMERALD can use them as reference data without changing its own canonical item numbering.

## Source pins

- Diamond/Pearl: `pret/pokediamond` @ `5bc4b1a3d8f100f77a4c64e59a0d544a0e29b3ec`
  - `include/constants/items.h`
  - `include/itemtool.h`
- Platinum: `pret/pokeplatinum` @ `d18093e4fd79ed5260d98363a00f315441b6c656`
  - `generated/items.txt`
  - `include/item.h`
  - `docs/datafiles/items.md`
- HeartGold/SoulSilver: `pret/pokeheartgold` @ `e97c7fc975a7447f288c42acc2e155f5a673e30f`
  - `include/constants/items.h`
  - `include/item.h`

## ID evolution

The Gen IV games largely preserve item IDs rather than renumbering the table between releases.

- Diamond/Pearl names normal items through ID **464** (`ITEM_SECRETPOTION`).
- Diamond/Pearl leaves IDs **112-134** unnamed in its current constants. Platinum uses ID **112** for `ITEM_GRISEOUS_ORB` and labels **113-134** as unused placeholders.
- Platinum keeps the established IDs and appends:
  - **465** `ITEM_VS_RECORDER`
  - **466** `ITEM_GRACIDEA`
  - **467** `ITEM_SECRET_KEY`
- HeartGold/SoulSilver preserves the Platinum range through **467**, then appends IDs **468-536**.
- HGSS's final named item is **536** `ITEM_ENIGMA_STONE`; its constants define `ITEMS_COUNT 537`.

Notable HGSS additions include Apricorn/key items, Apricorn Balls, Sport Ball, Park Ball, GB Sounds, Tidal Bell, RageCandyBar, 27 Data Cards, Jade Orb, Lock Capsule, Red Orb, Blue Orb, and Enigma Stone.

The complete ID-by-ID crosswalk is in `manifests/gen4-item-id-crosswalk.csv`.

## Item parameter layout

The three games use the same basic Gen IV item-parameter model.

Diamond/Pearl's current decompilation still names several bytes generically:

- `unk4`
- `unk5`
- `unk6`
- `unk8_B`
- `unkA`
- `unkB`

Platinum identifies the corresponding semantics as:

- `pluckEffect`
- `flingEffect`
- `flingPower`
- `battlePocket`
- `fieldUseFunc`
- `battleUseFunc`

HGSS exposes the same concepts directly as `pluckEffect`, `flingEffect`, `flingPower`, `battlePocket`, `fieldUseFunc`, and `battleUseFunc`.

Common parameters include price, held-item effect and parameter, Natural Gift power/type, toss/register flags, field pocket, battle pocket, field/battle use function, party-use flag, and the party-use effect block (healing, EV changes, stat stages, friendship changes, etc.).

HGSS also documents its item NARC mapping explicitly:

- 0: parameter data
- 1: icon character graphics (NCGR)
- 2: icon palette (NCLR)
- 3: Gen III / AGB item-code mapping

That fourth mapping is particularly useful for EMERALD because HGSS has an explicit `UpConvertItemId_Gen3to4` path.

## EMERALD policy

**EMERALD remains the target/canonical item table.** Gen IV IDs are reference/source IDs, not replacement IDs.

When importing or comparing later-generation items:

1. Preserve the original Emerald item IDs and Emerald behavior for items already present.
2. Match by semantic item identity, not by assuming a Gen IV numeric ID equals an Emerald numeric ID.
3. Use Platinum/HGSS parameter names to interpret Diamond/Pearl's currently unnamed fields.
4. Treat Platinum's use of ID 112 as a reserved-slot reuse, not as evidence that the whole table shifted.
5. For HGSS-only items, record the source ID and parameters separately before assigning any EMERALD-side extension ID.
6. Keep display text/localization separate from the numeric/parameter crosswalk; project language priority remains Japanese first, then Korean, English, then other official languages.

## Immediate consequence

For a full EMERALD item-parameter normalization, the safe source hierarchy is:

- Emerald: authoritative target behavior and target ID
- Platinum/HGSS: best-understood Gen IV parameter semantics
- Diamond/Pearl: origin/version comparison
- HGSS Gen III AGB mapping: conversion evidence for items shared with Gen III

No EMERALD item should be renumbered merely to match DP/Pt/HGSS.

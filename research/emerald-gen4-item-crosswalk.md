# Emerald ↔ Generation IV item crosswalk

This file makes **Pokémon Emerald the canonical target item table** and aligns it with the official Gen III/AGB migration mapping embedded in HeartGold/SoulSilver.

## Pinned sources

- Emerald: `pret/pokeemerald` @ `5eff78649e7170a877b961ef0b3da13b81a16038`
  - `include/constants/items.h`
  - `src/data/items.h`
- Diamond/Pearl: `pret/pokediamond` @ `5bc4b1a3d8f100f77a4c64e59a0d544a0e29b3ec`
  - `include/constants/items.h`
- Platinum: `pret/pokeplatinum` @ `d18093e4fd79ed5260d98363a00f315441b6c656`
  - `generated/items.txt`
- HeartGold/SoulSilver: `pret/pokeheartgold` @ `e97c7fc975a7447f288c42acc2e155f5a673e30f`
  - `include/agb/constants/items.h`
  - `include/constants/items.h`
  - `src/item.c`

## Why HGSS is the authoritative bridge

HGSS stores four values for every Gen IV item in `sItemNarcIds`. The fourth value is an `AGB_ITEM_*` code representing the corresponding Ruby/Sapphire/Emerald/FireRed/LeafGreen item ID used for migration.

`UpConvertItemId_Gen3to4()` searches that mapping to convert a Gen III AGB item code into a Gen IV item ID.

This gives us a game-authored bridge rather than a name-based guess.

## Current coverage

- Emerald/AGB slots: **377** (IDs 0-376)
- Unique nonzero Emerald items with a direct HGSS AGB mapping: **262**
- Emerald items without a direct HGSS AGB mapping: **114**
- `ITEM_NONE` is handled separately as ID 0.

Items without a migration mapping include unused Gen III slots and items that are not transferable through the Gen III → Gen IV migration path. They are **not automatically matched by name**, because identical names can refer to different key items in different games.

## Event-ticket status

- ITEM_EON_TICKET (Emerald 275): no_official_agb_mapping
- ITEM_RED_ORB (Emerald 276): official_hgss_agb → HGSS 534 ITEM_RED_ORB
- ITEM_BLUE_ORB (Emerald 277): official_hgss_agb → HGSS 535 ITEM_BLUE_ORB
- ITEM_MYSTIC_TICKET (Emerald 370): no_official_agb_mapping
- ITEM_AURORA_TICKET (Emerald 371): no_official_agb_mapping
- ITEM_OLD_SEA_MAP (Emerald 376): no_official_agb_mapping

The four Emerald event-delivery items remain Emerald-native content. Their lack of a Gen IV migration mapping does not affect the Littleroot ticket NPC work.

## Emerald parameter policy

`manifests/emerald-item-parameters.csv` records the Emerald source values for all 377 item slots.

These fields are the canonical target baseline:

- price
- held effect
- held-effect parameter
- importance
- registrability
- pocket
- field-use type/function
- battle-use mode/function
- secondary ID

Fields omitted by a designated initializer are recorded as their C zero-initialized defaults.

When later-generation items are added to EMERALD, they should receive new EMERALD-side extension IDs and be translated into this Emerald parameter model. Existing Emerald IDs and behavior should not be renumbered to imitate Gen IV.

## Files

- `manifests/emerald-item-parameters.csv`: canonical Emerald item parameter table
- `manifests/emerald-gen4-item-crosswalk.csv`: Emerald-centered official AGB/Gen IV mapping
- `manifests/gen4-item-id-crosswalk.csv`: DP/Pt/HGSS Gen IV ID comparison

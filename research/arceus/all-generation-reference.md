# Arceus / アルセウス — multi-generation form reference

Implementation target: one persistent `SPECIES_ARCEUS` with explicit form-to-type mapping. Do not encode 18 species and do not assume form ID equals engine type ID.

## Generation IV

Arceus debuts with Multitype and sixteen held Plates.

Playable forms:
- Normal
- Fighting, Flying, Poison, Ground, Rock, Bug, Ghost, Steel
- Fire, Water, Grass, Electric, Psychic, Ice, Dragon, Dark

That is 17 playable forms total.

Generation IV also contains an unused internal ???-type Arceus representation. There is no legitimate ??? Plate, and Multitype resolves an Arceus without a matching Plate to Normal. Keep this as research/internal compatibility only; never expose it as a selectable Plate form.

Platinum Plate IDs 298-313 are Flame through Iron Plate. The EMERALD project must not reuse those numeric IDs because Emerald already uses the same numeric slots for unrelated items. The extension allocation is tracked in `manifests/arceus-item-extensions.csv`.

Judgment is Special, 100 power, and changes type from the user's held Plate. Multitype changes Arceus's type/form from the Plate.

## Generation VI+

Generation VI introduces Fairy and Pixie Plate. Arceus therefore has 18 playable type forms: Normal plus all 17 non-Normal types.

This is the point where a generalized implementation must stop treating the historical Gen IV type-number coincidence as a permanent rule. Use an explicit form -> type table.

## Pokémon Legends: Arceus

Held items do not exist in PLA. Plates are used directly on Arceus.

- Ordinary Plate: persistently selects that form/type.
- Blank Plate: persistently selects Normal.
- Legend Plate: stores a special Legend state and presents Arceus as Normal outside the battle-derived Judgment state.

Legend Plate battle behavior:
1. At battle entry, Legend-state Arceus starts Normal.
2. When Judgment is successfully allowed to execute, choose an attacking type against the selected target.
3. Maximize offensive effectiveness first; a 4x weakness outranks a 2x weakness.
4. If tied, choose the candidate type that best resists the target's primary type, with immunity better than resistance.
5. If still tied, apply the same rule to the target's secondary type.
6. If still tied, choose randomly among the remaining candidates.
7. Change Arceus's type/form before Judgment resolves, so Judgment receives STAB.
8. The changed type remains battle state until another Judgment changes it or the battle ends.
9. At battle end, Legend-state Arceus returns to its Normal persistent presentation.

PLA copied Judgment is Normal when used by a non-Arceus user.

## EMERALD representation

Persistent per-Pokémon state uses the existing encrypted/checksummed 16-bit `PokemonSubstruct0.filler` slot as `formState`; this preserves the 12-byte substruct size and therefore the Gen III save layout.

Suggested bit layout:
- bits 0-4: persistent form ID (0-31)
- bit 5: Legend Plate state
- bits 6-15: reserved for generalized future form metadata

Existing saves naturally decode as zero => base/Normal form.

Battle-only state remains `gBattleMonForms[battler]`. Legend Plate additionally needs a side/party-slot battle sidecar so switch-out/switch-in does not accidentally erase the type selected by the previous Judgment.

## Graphics constraint

Stock Emerald allocates four decompressed 64x64 frames per battler. Arceus must not address forms 0-17 as preloaded sprite frames.

Use the Aegislash Stage-2 strategy:
- keep each form's compressed front/back graphics and palette in ROM;
- load only the active form into the battler's existing decompressed/VRAM slot;
- reload the matching palette on every form change.

## Judgment and the Gen III physical/special split

Changing only `dynamicMoveType` is insufficient. Emerald chooses Attack/Defense versus Sp. Atk/Sp. Def from the move's type. Judgment must remain Special even when its dynamic type is Fighting, Rock, Ghost, etc.

The branch therefore adds a non-invasive `GetBattleMoveCategory(move, effectiveType)` resolver rather than changing the 12-byte `struct BattleMove` layout.

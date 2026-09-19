# Generation VI form mechanics

Gen VI reference scope: X/Y and Omega Ruby/Alpha Sapphire.

The user's X/Y/ORAS repositories are currently foundation workspaces with exact build identity still unselected, so this document records cross-game mechanics and data-model findings only. It does not claim target-specific ROM addresses.

## Storage model

PK6 continues to store a persistent 5-bit form value. In PKHeX's PK6 model:

- Form is stored in the high five bits of byte 0x1D.
- Gen VI also exposes form-argument bookkeeping:
  - FormArgument (32-bit field beginning at 0x3C)
  - FormArgumentRemain at 0xED
  - FormArgumentElapsed at 0xEE

The timed-form fields are particularly relevant to Furfrou (five-day trims) and Hoopa (three-day Unbound duration).

## Mega Evolution

State model: battle-only transformation.

Normal requirements:
- Trainer has an enabled Key Stone/Mega Ring-equivalent.
- Pokémon holds its species/form-specific Mega Stone.
- One Mega Evolution activation per Trainer per battle.

Exception:
- Rayquaza uses Dragon Ascent instead of a Mega Stone in ORAS.

On Mega Evolution:
- form/personal data switches for the battle;
- base stats (except HP), types and Ability may change;
- it remains Mega through switching;
- it reverts at battle end;
- Mega form is not a valid stored out-of-battle form.

Generation VI timing detail:
- turn order on the transformation turn was already decided using the pre-Mega Speed/priority state;
- the Mega stats/types themselves are used for damage and other calculations after transformation.

## Primal Reversion (ORAS)

State model: automatic battle-only transformation keyed by held item.

Kyogre + Blue Orb:
- 100 / 150 / 90 / 90 / 180 / 160 (HP/Atk/Def/Spe/SpA/SpD)
- Water
- Primordial Sea

Groudon + Red Orb:
- 100 / 180 / 160 / 90 / 150 / 90
- Ground / Fire
- Desolate Land

Behavior:
- automatic on entering battle;
- no Key Stone;
- no manual selection;
- does not consume the Trainer's Mega Evolution allowance;
- no one-per-battle limit;
- held Orb cannot normally be removed from the correct holder in battle.

## Aegislash

State model: battle-only Ability-driven form.

Shield Forme:
- 60 / 50 / 150 / 60 / 50 / 150
- Steel / Ghost
- Stance Change

Blade Forme:
- 60 / 150 / 50 / 60 / 150 / 50
- Steel / Ghost
- Stance Change

Trigger:
- damaging move: Shield -> Blade before the move;
- King's Shield: Blade -> Shield before the move;
- switching out returns it to Shield.

These are the original Generation VI 150/150 defensive/offensive values, not the later 140/140 values.

## Furfrou

State model: persistent cosmetic form + time argument.

Forms:
- Natural
- Heart
- Star
- Diamond
- Debutante
- Matron
- Dandy
- La Reine
- Kabuki
- Pharaoh

All use the same battle parameters:
- 75 / 80 / 60 / 102 / 65 / 90
- Normal
- Fur Coat

A trim lasts five days, then reverts to Natural. Gen VI also does not preserve a trimmed Furfrou as a normal boxed form. This is why a plain form ID is insufficient: the timer is part of the form state.

## Vivillon

State model: immutable generated identity.

There are 20 patterns in Gen VI. The ordinary geographic pattern is determined when Scatterbug/Spewpa is generated from the Nintendo 3DS region/location settings and is carried through evolution. It cannot normally be changed.

This is a form-ID case with no form-change trigger.

## Flabébé / Floette / Florges

State model: immutable inherited identity.

Five flower colors:
- Red
- Yellow
- Orange
- Blue
- White

The color is retained through evolution and cannot normally be changed.

### Eternal Flower Floette

A sixth Floette form exists in Gen VI game data but was unobtainable in those games.

Parameters:
- 74 / 65 / 67 / 92 / 125 / 128
- Fairy
- Flower Veil
- distinct cry
- associated with Light of Ruin

This is important for ROM/data auditing even though it was not normally obtainable.

## Pumpkaboo / Gourgeist

State model: persistent generated size form.

Four sizes:
- Small
- Average
- Large
- Super

Pumpkaboo:
- Small: 44 / 66 / 70 / 56 / 44 / 55
- Average: 49 / 66 / 70 / 51 / 44 / 55
- Large: 54 / 66 / 70 / 46 / 44 / 55
- Super: 59 / 66 / 70 / 41 / 44 / 55

Gourgeist:
- Small: 55 / 85 / 122 / 99 / 58 / 75
- Average: 65 / 90 / 122 / 84 / 58 / 75
- Large: 75 / 95 / 122 / 69 / 58 / 75
- Super: 85 / 100 / 122 / 54 / 58 / 75

Order is HP/Atk/Def/Spe/SpA/SpD.

Unlike purely cosmetic forms, size is part of personal parameters and affects stats.

## Xerneas

State model: automatic visual battle state.

- Neutral Mode outside battle.
- Active Mode in battle/Contest.
- no battle-parameter difference.

This should be implemented as appearance state, not a separate stat/personality table.

## Hoopa (ORAS)

State model: persistent timed form.

Confined:
- 80 / 110 / 60 / 70 / 150 / 130
- Psychic / Ghost
- Magician

Unbound:
- 80 / 160 / 60 / 80 / 170 / 130
- Psychic / Dark
- Magician

Prison Bottle:
- Gen VI item ID 765 (0x02FD)
- changes Confined -> Unbound
- duration: up to three days
- in Gen VI, storage/PC handling reverts it to Confined

Hoopa therefore requires both Form and a timer/form-argument state.

## Cosplay Pikachu (ORAS)

State model: persistent costume form + move synchronization.

Forms:
- no costume
- Rock Star -> Meteor Mash
- Belle -> Icicle Crash
- Pop Star -> Draining Kiss
- Ph.D. -> Electric Terrain
- Libre -> Flying Press

Changing/removing costume at a Contest Hall also updates the costume-exclusive move. It has the same basic Pikachu battle parameters but is a distinct special individual that cannot evolve or breed.

## Arceus update

Generation VI adds Fairy and the Pixie Plate.

- Pixie Plate = Gen VI item ID 644 (0x0284)
- boosts Fairy moves by 20%
- makes Multitype Arceus Fairy-type
- makes Judgment Fairy-type

From Gen VI onward there is a real Plate for all 17 non-Normal types, producing 18 playable Arceus type forms including Normal.

## Existing form systems carried forward

Gen IV/V mechanisms still matter:
- Giratina / Griseous Orb
- Shaymin / Gracidea
- Rotom appliances
- Deoxys form switching
- Arceus Plates
- Forces of Nature / Reveal Glass
- Kyurem fusion / DNA Splicers
- Keldeo / Secret Sword
- Meloetta / Relic Song
- Genesect / Drives

One notable behavioral evolution is that Gen VI no longer has the Gen V seasonal world system, so Deerling/Sawsbuck are retained form identities rather than a live monthly season mechanic.

## EMERALD engine implication

A cross-generation form engine now needs at least these state models:

1. persistent form ID;
2. battle-only derived form;
3. immutable generated identity;
4. procedural appearance;
5. timed persistent form (Furfrou, Hoopa);
6. held-item transformation;
7. actively used item transformation;
8. move-known / move-used transformation;
9. Ability/battle-condition transformation;
10. fusion partner state;
11. Mega/Primal battle transformation with Trainer-level activation limits and special timing.

The form descriptor should not assume that a form ID is equivalent to a type ID. Gen VI's Fairy/Arceus changes make a generation-neutral explicit mapping safer.

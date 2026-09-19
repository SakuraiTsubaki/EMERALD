# Generation VIII form mechanics

Scope: Pokémon Sword / Shield, Brilliant Diamond / Shining Pearl, and Pokémon Legends: Arceus.

The user's Generation VIII decompilation repositories currently have `identity_status: unselected`, so this document records cross-game mechanics and portable data-model findings only. It does not claim target-specific ROM addresses.

## Gen VIII entity-state model

Generation VIII separates several concepts that earlier games often overloaded into form state.

From the PK8-compatible data model:

- persistent `Form`: full byte at 0x24
- `CanGigantamax`: separate individual flag
- `DynamaxLevel`: separate byte
- `FormArgument`: separate 32-bit auxiliary state
- party/battle transformation state is separate again

This is important for EMERALD: **Gigantamax capability is not a form ID**.

Pokémon Legends: Arceus uses its own PA8-compatible layout but still preserves a form field and form-argument state. It also has separate individual flags for:
- Alpha
- Noble

PLA does not use Dynamax/Gigantamax in gameplay; these compatibility fields must therefore not be interpreted as active PLA mechanics.

---

## Sword / Shield: Dynamax

State model: battle-only transformation.

Normal behavior:
- player activates Dynamax in an allowed battle;
- lasts up to 3 turns;
- switching out ends Dynamax;
- usable once per battle under normal rules;
- ordinary moves become Max Moves.

Dynamax does not replace the Pokémon's persistent Form.

### Dynamax Level

Dynamax Level is an individual parameter independent of Form.

Max-HP multiplier:
- Dynamax Level 0: 1.50x max HP
- each level adds 0.05x
- Dynamax Level 10: 2.00x max HP

When entering/leaving Dynamax, current HP is adjusted with the changed maximum HP. Other ordinary battle stats do not receive the same blanket multiplier.

---

## Gigantamax

State model: battle-only Dynamax variant + persistent eligibility flag.

A species that supports Gigantamax only uses its Gigantamax appearance/G-Max Move when the individual has the **Gigantamax Factor**.

Therefore two Pokémon with identical:
- species
- normal form
- stats

may still differ in whether they can Gigantamax.

The Isle of Armor's Max Soup can toggle this factor for eligible species, subject to species-specific restrictions.

EMERALD should represent this as an individual capability flag, not as a stored normal form.

---

## Morpeko

Forms:
- Full Belly
- Hangry

Stats:
- 58 / 95 / 58 / 97 / 70 / 58
- Electric / Dark
- Hunger Switch

Order: HP / Atk / Def / Spe / SpA / SpD.

At the end of every turn, Hunger Switch toggles Full Belly <-> Hangry.

The battle parameters remain the same, but **Aura Wheel changes type**:
- Full Belly -> Electric
- Hangry -> Dark

Outside battle Morpeko uses Full Belly Form.

State model: battle-only Ability-driven toggle + move-parameter override.

---

## Cramorant

Forms:
- normal
- Gulping
- Gorging

Stats:
- 70 / 85 / 55 / 85 / 85 / 95
- Flying / Water
- Gulp Missile

Using Surf or Dive:
- HP > 50% -> Gulping Form with Arrokuda
- HP <= 50% -> Gorging Form with Pikachu

When hit while carrying prey, Gulp Missile spits the prey at the attacker and returns Cramorant to normal.

State model: battle-only **move-used + HP threshold + retaliation payload**.

This is more than a form toggle: battle state must remember which payload/prey is currently stored.

---

## Eiscue

Forms:
- Ice Face
- Noice Face

Ice Face:
- 75 / 80 / 110 / 50 / 65 / 90

Noice Face:
- 75 / 80 / 70 / 130 / 65 / 50

Type: Ice.

Ice Face negates a physical hit and changes to Noice Face.

In Generation VIII Sword/Shield, hail can restore Ice Face.

State model: battle-only Ability/one-hit shield state + weather reset + form-specific personal stats.

---

## Galarian Darmanitan

This is a nested-form example:

1. persistent regional identity = Galarian Darmanitan
2. battle form = Standard / Zen

Galarian Standard:
- 105 / 140 / 55 / 95 / 30 / 55
- Ice

Galarian Zen:
- 105 / 160 / 55 / 135 / 30 / 55
- Ice / Fire

With Zen Mode, low HP switches the regional form into Zen Mode during battle.

State model: regional persistent form + battle-only HP/Ability form.

---

## Toxtricity

Persistent forms:
- Amped
- Low Key

Both:
- 75 / 98 / 70 / 75 / 114 / 70
- Electric / Poison

The form is chosen when Toxel evolves at level 30 according to its original Nature grouping.

The forms are not normally switchable afterward.

Ability sets differ:
- Amped: Punk Rock / Plus / Technician
- Low Key: Punk Rock / Minus / Technician

Gigantamax is another layer: both base forms converge on the same Gigantamax Toxtricity when the individual has the Gigantamax Factor.

State model: evolution-selected persistent identity + separate G-Max eligibility.

---

## Sinistea / Polteageist

Persistent authenticity identity:
- Phony
- Antique

Battle parameters are the same, but evolution-item compatibility differs:
- Phony Sinistea -> Cracked Pot
- Antique Sinistea -> Chipped Pot

The authenticity state survives evolution.

State model: immutable hidden identity that affects item/evolution rules.

---

## Alcremie

Alcremie combines two persistent cosmetic parameters:

### Cream
1. Vanilla Cream
2. Ruby Cream
3. Matcha Cream
4. Mint Cream
5. Lemon Cream
6. Salted Cream
7. Ruby Swirl
8. Caramel Swirl
9. Rainbow Swirl

### Sweet
1. Strawberry
2. Berry
3. Love
4. Star
5. Clover
6. Flower
7. Ribbon

9 x 7 = **63 ordinary appearance combinations**.

Base battle parameters are shared:
- 65 / 60 / 75 / 64 / 110 / 121
- Fairy
- Sweet Veil / Aroma Veil

Milcery evolution uses:
- held Sweet
- spin direction
- spin duration
- time/environment conditions

Gigantamax Factor again exists separately from the cream/sweet appearance identity.

State model: persistent **multi-parameter appearance identity**, not merely one semantic form enum.

---

## Zacian / Zamazenta

### Zacian

Hero of Many Battles:
- 92 / 130 / 115 / 138 / 80 / 115
- Fairy

Crowned Sword:
- 92 / 170 / 115 / 148 / 80 / 115
- Fairy / Steel
- triggered in Sword/Shield battle by Rusted Sword
- Iron Head becomes Behemoth Blade

### Zamazenta

Hero of Many Battles:
- 92 / 130 / 115 / 138 / 80 / 115
- Fighting

Crowned Shield:
- 92 / 130 / 145 / 128 / 80 / 145
- Fighting / Steel
- triggered by Rusted Shield
- Iron Head becomes Behemoth Bash

These are the **Generation VIII Sword/Shield values**, before later-generation balance changes.

State model: held-item-derived battle form + move substitution.

---

## Eternatus / Eternamax

Eternatus:
- 140 / 85 / 95 / 130 / 145 / 95

Eternamax:
- 255 / 115 / 250 / 130 / 125 / 250
- BST 1125

Type remains Poison / Dragon.

Eternamax is a special scripted/boss state rather than a normal player-storable transformation.

State model: scripted battle-only boss form.

This should not be represented as an ordinary obtainable persistent form in EMERALD.

---

## Urshifu

Persistent forms:
- Single Strike Style
- Rapid Strike Style

Both:
- 100 / 130 / 100 / 97 / 63 / 60
- Ability: Unseen Fist

Single Strike:
- Fighting / Dark
- evolution selected by Tower of Darkness

Rapid Strike:
- Fighting / Water
- evolution selected by Tower of Waters

The styles are not normally interchangeable after evolution.

Each style has its own Gigantamax appearance/G-Max Move; Gigantamax eligibility is still a separate individual flag.

---

## Calyrex fusion

Base Calyrex:
- 100 / 80 / 80 / 80 / 80 / 80

Reins of Unity fuses Calyrex with one partner.

### Ice Rider
Calyrex + Glastrier:
- 100 / 165 / 150 / 50 / 85 / 130
- Psychic / Ice
- As One (Unnerve + Chilling Neigh)
- Glacial Lance

### Shadow Rider
Calyrex + Spectrier:
- 100 / 85 / 80 / 150 / 165 / 100
- Psychic / Ghost
- As One (Unnerve + Grim Neigh)
- Astral Barrage

Using Reins of Unity again separates the pair.

The partner Pokémon's individual state must be preserved for restoration.

State model: persistent fusion partner + form-specific personal data + move synchronization.

Conceptually this extends the Kyurem/Necrozma fusion model.

---

## Brilliant Diamond / Shining Pearl

BDSP is a Generation VIII title but does **not** add the Sword/Shield Dynamax/Gigantamax system.

Its relevant form behaviors are primarily modern implementations of Sinnoh-era systems such as:
- Deoxys form data
- Burmy/Wormadam
- Rotom appliances
- Giratina
- Shaymin
- Arceus

For the EMERALD form engine, BDSP is most useful as a modern Gen IV compatibility/reference implementation rather than as the source of a new general transformation category.

---

# Pokémon Legends: Arceus

PLA changes the mechanics again because:
- held items are not used in normal battle mechanics;
- Abilities are not active as the standard battle system;
- form-changing key items are actively used from the satchel;
- Alpha/Noble are separate individual flags rather than ordinary forms.

## Alpha / Noble

PA8-compatible entity data has separate:
- IsAlpha
- IsNoble

flags.

These must not be encoded into the Pokémon form number.

This gives us a general rule for EMERALD:
**special size/boss status belongs in auxiliary individual flags, not in form identity.**

---

## Dialga Origin Forme

Use **Adamant Crystal** on Dialga to toggle forms.

Normal:
- 100 / 120 / 120 / 90 / 150 / 100

Origin:
- 100 / 100 / 120 / 90 / 150 / 120

Both Steel / Dragon.

State model: actively used key-item persistent form.

---

## Palkia Origin Forme

Use **Lustrous Globe** to toggle.

Normal:
- 90 / 120 / 100 / 100 / 150 / 120

Origin:
- 90 / 100 / 100 / 120 / 150 / 120

Both Water / Dragon.

State model: actively used key-item persistent form.

---

## Giratina in PLA

Use **Griseous Core** to toggle Altered / Origin.

This is mechanically different from the older held Griseous Orb model because PLA does not use held items in the same way.

So the same species/form relationship has **different trigger adapters by game generation**:

- Gen IV-VIII conventional titles: held Griseous Orb
- PLA: actively use Griseous Core

This is a strong reason to keep trigger logic separate from form/personal data.

---

## Enamorus

Forms:
- Incarnate
- Therian

Incarnate:
- 74 / 115 / 70 / 106 / 135 / 80

Therian:
- 74 / 115 / 110 / 46 / 135 / 100

Both Fairy / Flying.

Use Reveal Glass to toggle forms.

PLA does not execute ordinary Ability mechanics, but the forms retain their ability identities for cross-game data:
- Incarnate: Cute Charm / Contrary
- Therian: Overcoat

State model: active-use item persistent form.

---

## Basculegion

Male and female are effectively gender-selected personal forms because they have different battle parameters.

Male:
- 120 / 112 / 65 / 78 / 80 / 75

Female:
- 120 / 92 / 65 / 78 / 100 / 75

Both Water / Ghost.

State model: immutable gender-derived form/personal-data selection.

---

## Rotom in PLA

Rotom changes appliance forms through mechanical appliances installed in the player's quarters.

This retains the established persistent Rotom form model while changing the field interaction implementation.

---

## Arceus and the Legend Plate

Normal Plates in PLA are key items used directly on Arceus rather than held items.

The **Legend Plate** adds a new battle-derived form/type behavior.

After using the Legend Plate:
- Arceus is Normal outside the relevant attack state;
- when Judgment is selected, the game chooses an advantageous type against the target;
- Arceus changes its type/form before attacking;
- Judgment uses that selected type;
- battle end restores the ordinary state.

This is effectively **move-target-derived dynamic type/form selection**.

It cannot be represented correctly by a simple persistent Plate form.

---

## EMERALD implementation requirements after Gen VIII

A generation-neutral form/transform system now needs distinct fields/concepts for:

1. base species
2. persistent form
3. battle-only form
4. form argument / auxiliary state
5. fusion partner
6. immutable sub-identity (authenticity, cream/sweet, core color, size, etc.)
7. held-item / used-item / move / Ability / HP / weather / terrain triggers
8. trainer-level transformation allowance
9. Dynamax turn counter
10. Dynamax Level
11. Gigantamax eligibility flag
12. special individual flags such as Alpha / Noble
13. form-specific move substitution
14. scripted boss-only forms
15. generation-specific trigger adapters for the same form

The key design rule is:

**Form identity, transformation capability, temporary battle state, and special individual attributes must be separate.**

That rule handles everything from Emerald Castform through Gen VIII Gigantamax, Calyrex fusion, and PLA Origin forms without abusing one numeric form field.

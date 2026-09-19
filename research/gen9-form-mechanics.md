# Generation IX form and transformation mechanics

Scope: Pokémon Scarlet / Violet + The Hidden Treasure of Area Zero, and Pokémon Legends: Z-A / Mega Dimension as the later Generation IX branch.

The user's Scarlet/Violet/Z-A repositories currently have `identity_status: unselected`. This document therefore records cross-game mechanics and portable data-model facts, but does not claim target-specific ROM addresses.

Current external reference date: 2026-09-19.

## PK9 storage model

Generation IX keeps persistent form identity and Terastal state as separate concepts.

From the PK9-compatible data model:

- persistent `Form`: byte 0x24
- `TeraTypeOriginal`: byte 0x94
- `TeraTypeOverride`: byte 0x95
- `FormArgument`: 32-bit value at 0xD0
- individual scale: separate value

Therefore:

**Terastallization is not a normal persistent form change.**

A Pokémon can have:
- one persistent species/form identity;
- one stored Tera Type;
- another battle-only Terastallized state.

This is a decisive architectural difference for EMERALD.

---

# Scarlet / Violet

## Terastallization

State model: battle transformation independent of normal Form.

General behavior:
- a Pokémon has a stored Tera Type;
- the Trainer activates Terastallization during battle;
- type/STAB calculations use Terastal rules;
- appearance gains the crystal/Tera-jewel presentation;
- normal persistent Form is not replaced.

The PK9 layout directly supports this separation by storing Form and Tera Type independently.

### Stellar Type

The Indigo Disk adds Stellar as a Terastal type/state.

For most Pokémon this is still a Terastal battle layer, not a new persistent species form.

Terapagos is the major exception because its Terastal states are represented by distinct personal/form data.

---

## Paldean Tauros

Regional identity with three Paldean breeds:
- Combat: Fighting
- Blaze: Fighting / Fire
- Aqua: Fighting / Water

The breed is persistent and not normally switchable.

Raging Bull changes type according to breed.

State model: fixed regional sub-form with move-type coupling.

---

## Palafin

Forms:
- Zero
- Hero

Zero:
- 100 / 70 / 72 / 100 / 53 / 62

Hero:
- 100 / 160 / 97 / 100 / 106 / 87

Order: HP / Atk / Def / Spe / SpA / SpD.

Ability: Zero to Hero.

Trigger:
- starts battle in Zero Form;
- switch it out without fainting;
- when it returns, it becomes Hero;
- remains Hero until battle ends.

Outside battle it is always Zero Form.

State model: battle-only switch-triggered personal-data replacement.

---

## Dudunsparce

Persistent generated identity:
- Two-Segment
- Three-Segment

The forms are not interchangeable.

Three-Segment is approximately a 1% outcome from the underlying evolution/form-generation condition.

Battle parameters are otherwise the same.

State model: immutable generated appearance form.

---

## Maushold

Persistent generated identity:
- Family of Four
- Family of Three

Not interchangeable.

Family of Three is approximately a 1% outcome.

State model: immutable generated appearance form.

---

## Tatsugiri

Persistent forms:
- Curly
- Droopy
- Stretchy

The standard personal stats/type are shared, but the form has a battle-mechanical consequence when Tatsugiri is commanding Dondozo.

Order Up bonus:
- Curly -> Dondozo Attack +1
- Droopy -> Dondozo Defense +1
- Stretchy -> Dondozo Speed +1

State model: immutable form identity + partner-move effect parameter.

---

## Squawkabilly

Persistent plumage forms:
- Green
- Blue
- Yellow
- White

The forms are not normally changeable.

Some ability-slot data differs between plumages, so this is not purely a sprite selector.

State model: immutable form with personal-data differences.

---

## Gimmighoul

Forms:
- Chest
- Roaming

Chest:
- 45 / 30 / 70 / 10 / 75 / 70

Roaming:
- 45 / 30 / 25 / 80 / 75 / 45

Order: HP / Atk / Def / Spe / SpA / SpD.

The forms do not normally transform into each other.

Both evolve into Gholdengo.

State model: fixed encounter/form identity with different personal stats.

---

## Bloodmoon Ursaluna

Bloodmoon is a fixed special form, not a transformation available to ordinary Ursaluna.

Bloodmoon:
- 113 / 70 / 120 / 52 / 135 / 65
- Ground / Normal
- Mind's Eye

It has different stats, move access and Ability from ordinary Ursaluna and cannot be reached by evolving Ursaring into that form.

State model: special persistent identity.

---

## Poltchageist / Sinistcha

Poltchageist:
- Counterfeit
- Artisan

Sinistcha:
- Unremarkable
- Masterpiece

The form is permanent and inherited through evolution:

Counterfeit + Unremarkable Teacup -> Unremarkable Sinistcha  
Artisan + Masterpiece Teacup -> Masterpiece Sinistcha

This is an authenticity-state mechanic similar to Sinistea/Polteageist.

State model: hidden persistent identity + evolution-item compatibility rule.

---

# Ogerpon

Ogerpon combines held-item persistent form selection with a second Terastal battle layer.

Base stats for all forms:
- 80 / 120 / 84 / 110 / 60 / 96
- order: HP / Atk / Def / Spe / SpA / SpD

Forms:

### Teal Mask
- Grass
- Defiant
- Tera Type locked to Grass
- Terastallized Embody Aspect: Speed +1

### Wellspring Mask
- Grass / Water
- Water Absorb
- Tera Type locked to Water
- Terastallized Embody Aspect: Sp. Def +1

### Hearthflame Mask
- Grass / Fire
- Mold Breaker
- Tera Type locked to Fire
- Terastallized Embody Aspect: Attack +1

### Cornerstone Mask
- Grass / Rock
- Sturdy
- Tera Type locked to Rock
- Terastallized Embody Aspect: Defense +1

The held Mask determines:
- persistent Ogerpon form;
- ordinary typing;
- ordinary Ability;
- Ivy Cudgel type;
- fixed Tera Type;
- which Embody Aspect stat boost is applied after Terastallizing.

This is a key Generation IX example where:

**held item -> persistent form -> locked transformation type -> battle-only transformed Ability/effect**

all stack together.

---

# Terapagos

Forms:
1. Normal
2. Terastal
3. Stellar

Normal:
- 90 / 65 / 85 / 60 / 65 / 85
- Normal
- Tera Shift

Terastal:
- 95 / 95 / 110 / 85 / 105 / 110
- Normal
- Tera Shell

Stellar:
- 160 / 105 / 110 / 85 / 130 / 110
- Stellar Terastal state
- Teraform Zero

Order: HP / Atk / Def / Spe / SpA / SpD.

Trigger chain:

Normal
-> enters battle
-> Tera Shift
-> Terastal Form

Terastal Form
-> Terastallizes
-> Stellar Form

Terapagos is therefore a **nested battle transformation** where the first form change is automatic Ability-driven and the second is Trainer-triggered Terastallization.

The form changes also alter:
- base stats;
- Ability;
- presentation;
- Terastal behavior.

This is one of the strongest arguments for separating:
- persistent form;
- automatic battle form;
- transformation layer.

---

# Existing forms with changed Gen IX trigger rules

## Hoopa

Prison Bottle still switches Confined / Unbound, but Scarlet/Violet no longer uses the old three-day automatic reversion.

Move synchronization also follows the form:
- Confined -> Hyperspace Hole
- Unbound -> Hyperspace Fury

The form timer used by older games is therefore a **generation-specific trigger rule**, not a permanent property of Hoopa's form definition.

## Dialga / Palkia / Giratina

Scarlet/Violet changes the Legends: Arceus active-use items back into held-item form triggers:

- Dialga + Adamant Crystal -> Origin
- Palkia + Lustrous Globe -> Origin
- Giratina + Griseous Core -> Origin

Important Giratina change:
- Griseous Orb no longer selects Origin Form in Scarlet/Violet;
- Griseous Core selects Origin;
- Griseous Orb remains a held boost item for Altered Giratina.

Again: the form definition must be separate from generation-specific trigger adapters.

## Shaymin

Gracidea changes Land / Sky.

Scarlet/Violet retains restrictions involving freeze/night for activation, but Sky no longer simply depends on the exact old Gen IV storage rules.

## Deoxys

The Meteorite is now an actively used key item that presents/selects:
- Normal
- Attack
- Defense
- Speed

instead of requiring a specific map meteorite.

---

# Other state changes

## Deerling / Sawsbuck

Scarlet/Violet no longer uses the original Gen V monthly season system.

The four seasonal forms are associated with Paldea regions. Party members can update their form to match location when the game is started.

This is now a location/session trigger rather than an RTC-month trigger.

## Vivillon

Scarlet/Violet defaults to Fancy Pattern.

Pokémon GO postcards can temporarily change which regional Vivillon pattern is generated in the world for a limited period.

That changes **encounter-generation form selection**, not an already-owned Vivillon's stored form.

---

# Things that are NOT alternate forms

For EMERALD taxonomy these should remain separate species, not forms:

- Paradox Pokémon
- Wiglett / Wugtrio versus Diglett / Dugtrio
- Toedscool / Toedscruel versus Tentacool / Tentacruel
- convergent species generally

Visual or conceptual resemblance is not sufficient to merge species IDs.

---

# Pokémon Legends: Z-A

Pokémon Legends: Z-A is part of Generation IX and is now released.

It brings Mega Evolution back as a major battle-transformation system.

The user's Z-A repository still has no exact build identity selected, so no ROM addresses are claimed here.

## Mega Evolution in Z-A

The persistent concept is still:
- compatible species/form;
- Mega Stone;
- Trainer Key Stone / Mega Ring.

But Z-A changes the **battle runtime**.

Mega Evolution requires a Mega Gauge / Mega Power resource. In real-time combat:
- attacks and Mega Power pickups fill/provide Mega Power;
- Mega Evolution consumes that resource;
- the Mega state can end when the resource drains;
- Mega Power can be replenished to extend/use transformation.

This differs from the old Gen VI/VII 'activate and remain Mega until battle end' implementation.

So even the same Mega personal data now needs a new **generation-specific battle transformation controller**.

## Rogue Mega Evolution

Wild Pokémon can be forced into Mega Evolution by high Mega Power concentrations.

This is a scripted/wild transformation state and does not require the normal owned-Pokémon Key Stone workflow.

State model: scripted wild/boss Mega state.

## New Mega forms

Legends: Z-A introduced many new Mega Evolutions, including examples such as:
- Mega Meganium (Grass/Fairy)
- Mega Feraligatr (Water/Dragon)
- Mega Emboar
- Mega Chesnaught
- Mega Delphox
- Mega Greninja

The Mega Dimension DLC adds further Mega forms including:
- Mega Raichu X
- Mega Raichu Y
- Mega Chimecho
- Mega Baxcalibur
- Mega Zeraora
- Mega Lucario Z
- Mega Garchomp Z

Current public form inventories list **48 new Mega-Evolved forms introduced across Z-A and its version 2.0.0 Mega Dimension content**.

These are additional personal/form records, but they reuse the Mega transformation family rather than requiring a completely new persistent-form storage category.

## Z Mega Evolution

Mega Dimension adds a Z Mega Evolution subtype.

Example:
- Mega Lucario Z

Official behavior:
- moves have effectively no/less command wind-up than ordinary Mega equivalents;
- Z Mega forms consume Mega Power much faster.

This adds a new transformation parameter:

`mega_variant = normal | Z`

plus a different Mega-resource drain/timing profile.

This is not the same thing as a Z-Move.

---

# EMERALD implementation implications after Gen IX

A fully generation-neutral form/transform engine now needs:

## Persistent entity state
- species
- persistent form
- FormArgument / subtype data
- immutable identity flags
- fusion partner
- size/scale
- stored Tera Type
- form-dependent item/evolution identity

## Battle state
- derived battle form
- transformed type
- temporary Ability override
- temporary personal/stat table
- one-hit/shield state
- partner payload
- transformation turn/resource state
- Terastallization state
- Mega state
- Mega variant
- Mega resource/gauge
- fusion-layer battle transformation

## Trigger layer
- held item
- used item
- Ability
- HP threshold
- move selected
- move used
- switch-out/switch-in
- KO event
- partner Pokémon
- evolution condition
- map/region/session
- encounter generation
- trainer command
- scripted boss event

The important design rule becomes:

**Species identity, persistent form identity, stored elemental transformation type, transformation capability, and current battle transformation must all be independent fields.**

That architecture covers Emerald Castform through Terapagos and Z-A's gauge-driven Mega Evolution without forcing unrelated mechanics into one numeric form value.

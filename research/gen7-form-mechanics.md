# Generation VII form mechanics

Scope: Pokémon Sun / Moon, Ultra Sun / Ultra Moon, with a short Generation VII Let's Go note.

The user's Generation VII decompilation repositories are currently foundation workspaces with `identity_status: unselected`; therefore this document records verified cross-game mechanics and data-model facts, but does not claim game-specific ROM addresses yet.

## PK7 storage model

Generation VII keeps the Generation VI-style persistent form field.

PK7:
- byte 0x1D:
  - bit 0: fateful encounter
  - bits 1-2: gender
  - bits 3-7: **5-bit form ID**
- 0x3C: 32-bit FormArgument
  - low byte: FormArgumentRemain
  - next byte: FormArgumentElapsed
  - next byte: FormArgumentMaximum

This means Gen VII continues to support persistent form IDs plus auxiliary form state.

## Alolan regional forms

Generation VII introduces 18 Alolan forms, all for Generation I species.

These are best modeled as **fixed regional personal-data forms**, not player-triggered transformations.

Depending on the species, regional identity is selected by:
- encounter origin,
- evolutionary location/region,
- time of day,
- evolution item.

Examples:
- Cubone -> Alolan Marowak at level 28 at night in Alola.
- Exeggcute evolves to Alolan Exeggutor in Alola.
- Pikachu evolves to Alolan Raichu in Alola.

USUM allows original-form evolutions in Ultra Space for some lines.

## Oricorio

Forms:
- Baile: Fire/Flying
- Pom-Pom: Electric/Flying
- Pa'u: Psychic/Flying
- Sensu: Ghost/Flying

Stats are identical:
- 75 / 70 / 70 / 93 / 98 / 70 (HP/Atk/Def/Spe/SpA/SpD)
- Ability: Dancer

Trigger: actively use a Nectar.

Gen VII item IDs:
- 853 Red Nectar -> Baile
- 854 Yellow Nectar -> Pom-Pom
- 855 Pink Nectar -> Pa'u
- 856 Purple Nectar -> Sensu

State model: persistent item-used form.

## Lycanroc

Forms:
- Midday
- Midnight
- Dusk (USUM)

Midday:
- 75 / 115 / 65 / 112 / 55 / 65

Midnight:
- 85 / 115 / 75 / 82 / 55 / 75

Dusk:
- 75 / 117 / 65 / 110 / 55 / 65
- Ability: Tough Claws

Dusk Form requires an Own Tempo Rockruff and, in USUM, evolution from level 25 during the special evening window (17:00-17:59 in-game).

State model: evolution-selected permanent identity, not a later switchable form.

## Wishiwashi

Forms:
- Solo
- School

Solo:
- 45 / 20 / 20 / 40 / 25 / 25
- Water
- Schooling

School:
- 45 / 140 / 130 / 30 / 140 / 135
- Water
- Schooling

At the end of a turn:
- level < 20 or HP <= 25% -> Solo
- level >= 20 and HP > 25% -> School

Switching out School Form reverts the battle state to Solo.

State model: battle-only Ability/HP/level-derived form.

## Minior

State has two layers.

Layer 1: immutable core color
- Red
- Orange
- Yellow
- Green
- Blue
- Indigo
- Violet

Layer 2: battle state
- Meteor
- Core exposed

Meteor:
- 60 / 60 / 100 / 60 / 60 / 100
- Rock/Flying
- Shields Down

Core:
- 60 / 100 / 60 / 120 / 100 / 60
- Rock/Flying
- Shields Down

The seven core colors are cosmetic identities and are not normally changeable. Shields Down changes Meteor/Core state according to HP during battle.

State model: **persistent color identity + battle-only shell state**.

## Mimikyu

Forms:
- Disguised
- Busted

Stats/type do not change:
- 55 / 90 / 80 / 96 / 50 / 105
- Ghost/Fairy
- Disguise

Generation VII behavior:
- starts battle Disguised;
- first damaging hit handled by Disguise deals **zero damage**;
- then changes to Busted;
- remains Busted for the rest of the battle.

The later Generation VIII 1/8-max-HP Disguise penalty does **not** apply in Gen VII.

State model: battle-only Ability/one-hit state.

## Ash-Greninja

Special Battle Bond Greninja.

Normal Greninja:
- 72 / 95 / 67 / 122 / 103 / 71

Ash-Greninja:
- 72 / 145 / 67 / 132 / 153 / 71
- Water/Dark remains unchanged

Generation VII trigger:
- Battle Bond Greninja directly causes an opponent to faint with a damaging move;
- if battle continues, it changes into Ash-Greninja;
- battle end returns it to normal;
- if Ash-Greninja faints, that Greninja cannot transform again that battle.

Gen VII Water Shuriken while transformed:
- power 20
- exactly 3 hits

State model: battle-only Ability/KO-triggered form.

## Zygarde

Persistent base identities:
- 10%
- 50%

Battle form:
- Complete

10%:
- 54 / 100 / 71 / 115 / 61 / 85

50%:
- 108 / 100 / 121 / 95 / 81 / 95

Complete:
- 216 / 100 / 121 / 85 / 91 / 95

All Dragon/Ground.

Power Construct:
- at end of turn, if 10% or 50% Zygarde is at <= 50% HP -> Complete;
- Complete has higher max HP;
- current HP is adjusted by preserving damage already taken;
- battle end returns to the starting 10%/50% identity.

Outside battle, Zygarde Cube / Reassembly Unit controls 10% and 50% forms and Ability configuration.

Gen VII item ID:
- 847 Zygarde Cube

Important internal detail:
- 10% Aura Break and 10% Power Construct are separate internal forms;
- 50% Aura Break and 50% Power Construct are also separate internal forms.

So **visual form + Ability state** can be encoded as separate personal-form indices.

## Silvally

Forms:
- Normal plus one for every other type = 18 type forms.

Stats do not change:
- 95 / 95 / 95 / 95 / 95 / 95

Ability:
- RKS System

Trigger:
- held Memory determines Silvally's type/form;
- the same Memory determines Multi-Attack's type.

Generation VII Multi-Attack power: **90**.

Memory item IDs:
- 904 Fighting
- 905 Flying
- 906 Poison
- 907 Ground
- 908 Rock
- 909 Bug
- 910 Ghost
- 911 Steel
- 912 Fire
- 913 Water
- 914 Grass
- 915 Electric
- 916 Psychic
- 917 Ice
- 918 Dragon
- 919 Dark
- 920 Fairy

No Memory -> Normal.

State model: held-item-derived persistent/derived type form, conceptually parallel to Arceus Plates.

## Necrozma (USUM)

This is the most complex Gen VII case.

Base Necrozma:
- 97 / 107 / 101 / 79 / 127 / 89
- Psychic
- Prism Armor

Dusk Mane:
- 97 / 157 / 127 / 77 / 113 / 109
- Psychic/Steel
- Prism Armor
- fusion with Solgaleo

Dawn Wings:
- 97 / 113 / 109 / 77 / 157 / 127
- Psychic/Ghost
- Prism Armor
- fusion with Lunala

Ultra Necrozma:
- 97 / 167 / 97 / 129 / 167 / 97
- Psychic/Dragon
- Neuroforce

### Fusion

N-Solarizer:
- fuse Necrozma + Solgaleo -> Dusk Mane
- use again -> split
- only one such fusion can exist at a time
- Solgaleo's individual properties must be retained for later separation

N-Lunarizer:
- same model with Lunala -> Dawn Wings

Gen VII item-table state pairs:
- 943 / 945 N-Solarizer
- 944 / 946 N-Lunarizer

The duplicate item IDs represent stateful key-item handling before/after fusion.

### Ultra Burst

Requirements:
- Dusk Mane or Dawn Wings
- holding Ultranecrozium Z

Battle command -> Ultra Necrozma.

Rules:
- battle-only;
- once per battle;
- faints -> returns to prior fusion form and cannot Ultra Burst again that battle;
- battle end -> prior fusion form;
- after Ultra Burst, on a later turn, Photon Geyser can still be upgraded to Light That Burns the Sky.

Ultranecrozium Z has Gen VII table entries 923/929.

State model: **persistent fusion partner + battle-only transformation layered on top**.

This is more complex than Kyurem because the fused form itself can transform again in battle.

## Magearna Original Color

Original Color Magearna already exists as a separate form in SM/USUM data, but was not legitimately obtainable until Pokémon HOME in Generation VIII.

Battle parameters are the same as regular Magearna. The difference is appearance.

State model: data-only / immutable cosmetic identity in Gen VII.

## Totem-sized forms (USUM)

USUM exposes obtainable Totem-sized Pokémon.

With the exception of Wishiwashi, these larger variants are internally programmed as unique forms even though the Pokédex does not list them as ordinary alternate forms.

Differences can include:
- height
- weight
- Ability for the distributed Totem-like individual

Their size affects weight-dependent mechanics.

This means Gen VII needs another category: **hidden/internal form not represented as a normal Pokédex form**.

## Existing systems

Generation VII also retains earlier systems:
- Mega Evolution
- Primal Reversion
- Aegislash Stance Change
- Giratina / Griseous Orb
- Shaymin / Gracidea
- Rotom appliances
- Deoxys
- Arceus Plates
- Kyurem fusion
- Keldeo
- Meloetta
- Genesect
- Furfrou
- Hoopa

## Let's Go Pikachu / Eevee

LGPE is also Generation VII but uses a different Switch-era engine and removes Abilities and held items.

Relevant differences:
- Alolan forms remain as fixed forms and are obtained mainly through trades / GO transfer.
- Mega Evolution remains available.
- Partner Pikachu / Partner Eevee are special partner individuals with unique moves and stat systems rather than ordinary alternate-form switching.

For EMERALD's generic form engine, SM/USUM are the more important Gen VII behavioral reference.

## EMERALD engine implications

By Gen VII, a cross-generation form descriptor needs to model more than a single form ID:

- persistent form ID
- battle form ID
- immutable sub-identity (Minior core color)
- Ability-state variant encoded as form (Zygarde)
- hidden/internal form (Totem size)
- held-item derived form
- active-use item form
- evolution-selected regional/time form
- HP/level threshold form
- one-hit state form
- KO-triggered battle form
- fusion partner state
- nested battle transformation over a fused form
- form-specific stat/type/Ability/move overrides
- item state that itself changes while fused

A practical EMERALD representation should therefore separate **base identity**, **persistent form**, **battle form**, and **form argument / auxiliary state** rather than overloading one numeric form field.

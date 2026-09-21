# JAPAN script semantics survey — Generation I–III

This layer begins from **6,479 valid map-script roots recovered directly from the twenty Japanese ROMs**. No root in the extracted active-map set is invalid.

The direct-ROM roots establish coverage and revision/build identity. Semantic interpretation is then attached through the corresponding disassembly/decompilation command model; raw pointer equality is never used as semantic equality.

## Three script engines

### Generation I

Generation I map logic is primarily LR35902 machine code, with helper systems for text, trainers, gifts, static battles and event flags. It is therefore not correct to feed Red/Green/Blue/Yellow through a Generation-II-style event-bytecode decoder.

The remake importer needs a machine-code/source-correspondence adapter that emits higher-level actions such as:

- check/set/reset event;
- give Pokémon;
- initiate static battle;
- hide/show object;
- select next map-script state;
- display text / movement / audio actions.

Shared Kanto static battle semantics include Articuno Lv50, Zapdos Lv50, Moltres Lv50, Mewtwo Lv70 and the two Snorlax Lv30 encounters.

Shared gift semantics include the Mt. Moon Magikarp Lv5 purchase, Eevee Lv25, Lapras Lv15 and the Fighting Dojo Hitmon choice at Lv30.

Yellow adds separate Bulbasaur, Charmander and Squirtle Lv10 gift routes. These are title semantics, not revision changes.

## Generation II

Generation II uses event-command bytecode. Key commands include:

- `givepoke` 0x2D
- `giveegg` 0x2E
- `loadwildmon` 0x5D
- `loadtrainer` 0x5E
- `startbattle` 0x5F
- `swarm` 0xA0

Script coverage must include scene scripts, callbacks, coord events, bg events and object scripts in addition to each map's root.

Shared Gold/Silver semantics include the three Lv5 starters, Togepi Egg, Eevee Lv20, Tyrogue Lv10, Kenya Spearow Lv10, Sudowoodo Lv20, Friday Lapras Lv20 and the forced-shiny Gyarados Lv30.

Gold/Silver version logic gives:
- Gold: Ho-Oh Lv40 / Lugia Lv70
- Silver: Ho-Oh Lv70 / Lugia Lv40

Crystal is a distinct script profile:
- Dragon Shrine Dratini Lv15 gift;
- Suicune Lv40 fixed battle;
- GS Ball Celebi Lv30 fixed battle;
- Ho-Oh Lv60;
- Lugia Lv60;
- changed Goldenrod/Celadon Game Corner prize profiles.

## Generation III

Generation III uses the GBA script-command VM. Important opcodes verified from the command table include:

- `special` 0x25
- `specialvar` 0x26
- `trainerbattle` 0x5C
- `dotrainerbattle` 0x5D
- `givemon` 0x79
- `giveegg` 0x7A
- `setwildbattle` 0xB6
- `dowildbattle` 0xB7

Ruby/Sapphire examples include fossil revival at Lv20, Castform Lv25 holding Mystic Water, Beldum Lv5, Wynaut Egg, the three Regis Lv40, Rayquaza Lv70, version legendary Lv45, Kecleon Lv30 and New Mauville Voltorb Lv25.

Emerald keeps the same script VM but changes content substantially. Important examples are the postgame Johto starter choice at Lv5, Groudon/Kyogre Lv70 in Terra/Marine Cave, Rayquaza Lv70, Kecleon Lv30 and Aqua Hideout Electrode Lv30.

FireRed/LeafGreen use the same broad GBA command model but their semantic census is treated as a Kanto-remake profile: starter choice, Dojo gifts, Game Corner prizes, fossils, Lapras, Kanto static legends/Snorlax and Sevii-specific gifts/static encounters.

## Remake architecture consequence

Do not copy original script binaries into the GBA remakes.

Normalize source behavior into a common intermediate event representation, for example:

```
condition / flag / variable
→ action
→ battle or gift payload
→ object-state transition
→ continuation
```

Then compile that representation into the Generation-III-derived runtime.

This preserves the original Japanese title's progression logic while allowing the seven remake repositories to share one modern GBA execution layer.

Machine-readable summary:
- `manifests/japan-script-semantic-summary.json`
- `manifests/japan-script-root-extraction.json`

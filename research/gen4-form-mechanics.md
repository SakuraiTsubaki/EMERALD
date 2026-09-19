# Generation IV form-change mechanics and game parameters

Primary reference: pret/pokeplatinum @ d18093e4fd79ed5260d98363a00f315441b6c656
HGSS comparison: pret/pokeheartgold @ e97c7fc975a7447f288c42acc2e155f5a673e30f
Emerald target: pret/pokeemerald @ 5eff78649e7170a877b961ef0b3da13b81a16038

## Storage model

Generation IV stores a persistent 5-bit form value in PokemonDataBlockB at offset 0x18 together with fatefulEncounter and gender. Code reads/writes it as MON_DATA_FORM.

Stock Emerald has no generic persistent form field. Its encrypted Pokemon substructures special-case Castform, Unown, Deoxys and Spinda instead. Therefore importing Gen IV forms requires state storage plus form-aware parameters, not only sprites.

## Giratina

- form 0: Altered; 150/100/120/90/100/120; Ghost/Dragon; Pressure
- form 1: Origin; 150/120/100/90/120/100; Ghost/Dragon; Levitate
- BoxPokemon_SetGiratinaForm checks held item.
- Griseous Orb held -> Origin; otherwise -> Altered.
- After change: MON_DATA_FORM write, ability recalc, stat recalc.
- Platinum can force Origin in Distortion World; outside it, Origin without the Orb returns to Altered.
- Griseous Orb = Pt ID 112, price 10000, HOLD_EFFECT_GIRATINA_BOOST, effectParam 20, Fling 60, Items pocket, no field-use function.

## Shaymin

- form 0: Land; 100/100/100/100/100/100; Grass; Natural Cure
- form 1: Sky; 100/103/75/127/120/75; Grass/Flying; Serene Grace
- Gracidea is actively used from party menu.
- Pokemon_CanShayminSkyForm requires Land form, HP > 0, fateful encounter, not frozen, and RTC 04:00-19:59.
- Sky has its own learnset, including Air Slash and Leaf Storm.
- RTC reset logic returns Sky to Land outside the allowed time window; freeze handling also returns it to Land.
- Gracidea = Pt ID 466, price 0, Key Items, preventToss true, canRegister true, ITEM_USE_FUNC_GRACIDEA.

## Rotom

- forms: 0 Base, 1 Heat, 2 Wash, 3 Frost, 4 Fan, 5 Mow
- Base: 50/50/77/91/95/77
- appliance forms: 50/65/107/86/105/107
- all Gen IV Rotom forms remain Electric/Ghost with Levitate.
- Platinum Secret Key gates the appliance room; the key is not used directly on Rotom.
- Pokemon_SetRotomForm removes the old appliance move, adds the new one, writes MON_DATA_FORM, recalculates ability and stats.
- moves: Heat Overheat; Wash Hydro Pump; Frost Blizzard; Fan Air Slash; Mow Leaf Storm.
- Secret Key = Pt ID 467, price 0, Key Items, preventToss true, hold effect none, no normal field-use function.
- HGSS retains appliance-form switching in the Silph Co. room without Platinum's Secret Key distribution route.

## Arceus

- base stats: 120/120/120/120/120/120
- ability: Multitype
- held Plate holdEffect is converted to type and written to MON_DATA_FORM.
- no matching Plate -> Normal.
- Pt IDs 298-313 are the sixteen Plates.
- all Plates: price 1000, effectParam 20, Fling power 90, Items pocket, no field-use function.
- each Plate has a unique HOLD_EFFECT_ARCEUS_* value; the same effect both boosts matching-type moves and selects Arceus type/form.
- valid Plate types: Fire, Water, Electric, Grass, Ice, Fighting, Poison, Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel.
- the Gen IV form index follows type numbering and includes the reserved Mystery-type gap.

## Deoxys

- 0 Normal: 50/150/50/150/150/50
- 1 Attack: 50/180/20/150/180/20
- 2 Defense: 50/70/160/90/70/160
- 3 Speed: 50/95/90/180/95/90
- all Psychic with Pressure.
- Veilstone meteorite scripts call ChangeDeoxysForm.
- the script loops all party Deoxys, writes MON_DATA_FORM, recalculates stats and updates Pokédex form data.
- Gen III migration initializes Deoxys by origin game: R/S Normal, FR Attack, LG Defense, Emerald Speed.

## Burmy / Wormadam

- Burmy form changes persist after eligible battles and are selected from battle terrain.
- Plant: grass terrain.
- Sandy: plain, sand, mountain, cave, Distortion/Giratina terrain.
- Trash: buildings, bridges, Elite Four/facility terrain.
- skipped in Link, Frontier, Safari and Pal Park battles.
- Burmy: 40/29/45/36/29/45; Bug; Shed Skin.
- Wormadam Plant: 60/59/85/36/79/105; Bug/Grass; Anticipation.
- Wormadam Sandy: 60/79/105/36/59/85; Bug/Ground; Anticipation.
- Wormadam Trash: 60/69/95/36/69/95; Bug/Steel; Anticipation.

## Castform / Cherrim

Castform is battle-only: Forecast + sun/rain/hail changes battle form/type to Fire/Water/Ice, otherwise Normal. Base stats are 70 all.

Cherrim is battle-only: sun changes Overcast to Sunshine; rain/hail/weather suppression returns Overcast. Base stats are 70/60/70/85/87/78, Grass, Flower Gift. Sunshine does not use a separate stat table.

## Fixed identity forms

Unown, Shellos and Gastrodon need form-aware graphics/data but are not normal player-switchable forms. Spinda is procedural personality-based appearance rather than a discrete form ID.

## EMERALD implementation requirement

Do not implement this as a single 'change sprite' routine. A complete port needs persistent and battle-only form state, form-specific personal data, stat/type/ability recalculation, form graphics/icon/palette selection, form learnset hooks, item/script/weather/terrain/RTC triggers, and form-aware save/Pokedex handling.

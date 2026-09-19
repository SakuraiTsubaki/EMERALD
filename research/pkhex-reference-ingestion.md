# PKHeX reference ingestion plan

Pinned upstream reference:
- `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`
- license: GNU GPLv3

## Policy

PKHeX is used as a **reference oracle / extraction source**, not copied wholesale into the EMERALD runtime.

We extract and normalize factual/game-parameter data into project-owned CSV/JSON/YAML manifests, then implement the Emerald-side engine independently.

Reasons:
- PKHeX already normalizes cross-generation game structures extremely well.
- Its GPLv3 code should not be casually embedded into a differently licensed runtime without deliberate license handling.
- Our target is a GBA Emerald engine, so direct C# code reuse would not be useful anyway.
- Keeping source provenance lets every extracted field be verified against the pinned upstream revision.

## Scope to ingest

### 1. Personal / species parameters
Source:
- `PKHeX.Core/PersonalInfo/`
- `PersonalTable`

Game tables covered by PKHeX include:
- RB / Y
- GS / C
- RS / E / FR / LG
- DP / Pt / HGSS
- BW / B2W2
- XY / ORAS
- SM / USUM / LGPE
- SWSH / BDSP / PLA
- SV / Z-A

Extract:
- species/form count and indexes
- base stats
- typing
- gender ratio
- growth
- catch rate
- base friendship
- EV yields
- abilities
- held items
- hatch cycles
- egg groups
- height / weight
- form table metadata
- tutor/TM compatibility where represented

### 2. Forms
Source:
- `FormConverter`
- `FormInfo`
- personal tables

Extract:
- form IDs
- form names
- battle-only status
- Mega / Primal / Z Mega status
- fused-form status
- out-of-battle reversion form
- Totem / Lord / hidden forms
- form-argument semantics
- generation-specific form availability

### 3. Items
Extract:
- item IDs by generation
- names/localization
- pockets
- held effects
- field-use / battle-use semantics where exposed
- form-changing item relations
- conversion mappings
- key-item/event-item identity

### 4. Moves
Extract:
- move IDs
- type / category
- power / accuracy / PP
- priority
- target
- effect ID
- flags
- generation-specific parameter changes
- form-specific move conversions

### 5. Abilities
Extract:
- ability IDs/names
- generation availability
- species/form slot mappings
- form-trigger abilities and battle-state dependencies

### 6. Evolutions
Extract:
- source species/form
- target species/form
- level/item/move/time/location/gender/party conditions
- generation/version differences
- regional-form evolution rules

### 7. Encounters
Extract:
- game/version
- area/location
- encounter species/form
- level range
- slot/method
- weather/time/season/special conditions
- static/gift/trade/event encounters

### 8. Save structures
Extract/document:
- PK1/2/3/4/5/6/7/8/9 entity layouts
- generation save block structures
- form fields and form arguments
- ribbons/marks
- Dynamax/Gigantamax/Tera fields
- Alpha/Noble/scale
- transfer-only fields
- checksum/encryption/shuffle behavior

This data is reference material; Emerald's save format remains its own target format unless explicitly extended.

### 9. Legality / validation rules
Use as **behavioral verification data**, not as runtime copy.

Extract:
- impossible form combinations
- battle-only form restrictions
- fused/trade restrictions
- event-only forms
- generation-transfer normalization
- form reset rules
- item/move/ability compatibility constraints

### 10. Conversion rules
Extract:
- Gen III -> IV item mappings
- entity generation conversion rules
- form preservation/reset behavior
- move/ability normalization
- transfer restrictions

### 11. Mystery Gifts / event data
Extract:
- supported gift formats
- event species/forms/items
- fateful encounter flags
- event-only moves
- distribution-specific metadata

### 12. Ribbons / Marks
Extract:
- IDs
- generation/game origin
- legality/persistence
- transfer mapping

### 13. Locations
Extract:
- location IDs per generation
- met/egg location semantics
- transfer remapping

### 14. Localization
Project language priority remains:
1. Japanese
2. Korean
3. English
4. other official languages

PKHeX localized resources can be used for cross-checking names, but Japanese game/source terminology remains the primary semantic reference.

## Output architecture

Do not create one giant opaque dump.

Recommended normalized outputs:

- `manifests/pkhex/species-forms.csv`
- `manifests/pkhex/personal-parameters.csv`
- `manifests/pkhex/items.csv`
- `manifests/pkhex/moves.csv`
- `manifests/pkhex/abilities.csv`
- `manifests/pkhex/evolutions.csv`
- `manifests/pkhex/encounters.csv`
- `manifests/pkhex/ribbons-marks.csv`
- `manifests/pkhex/locations.csv`
- `manifests/pkhex/conversions.csv`
- `manifests/pkhex/form-rules.csv`
- `manifests/pkhex/save-fields.csv`
- `manifests/pkhex/mystery-gifts.csv`

Every row should include:
- `source_repo`
- `source_commit`
- `source_path`
- `game/context`
- `generation`
- verification status

## Emerald integration rule

PKHeX answers:
> What does each game/version believe this Pokémon/item/move/form/save field means?

EMERALD then answers:
> How do we reproduce or extend that behavior while preserving Emerald IDs and target-engine rules?

PKHeX data must therefore never automatically renumber native Emerald IDs or overwrite verified Emerald behavior.

The existing Emerald item/form manifests remain the target-side authority.

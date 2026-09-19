# Generations I-III form baseline

## Generation I

The original Generation I games do not have a general alternate-form system comparable to later generations.

Visual differences caused by palette/context are not treated as persistent form IDs.

## Generation II

### Unown
- 26 forms: A-Z.
- Form is derived from individual-value data rather than a generic stored form field.
- ! and ? do not exist until Generation III.

Generation II gender/shiny visual differences are not separate form IDs.

## Generation III

### Unown
- expands to 28 forms: A-Z, !, ?.
- form derives from personality data.

### Castform
- Normal / Sunny / Rainy / Snowy.
- weather-driven battle-only form/type switching.
- stock Emerald ROM stores the four graphics frames together and uses battle state rather than a generic persistent form field.

### Deoxys
- Normal / Attack / Defense / Speed personal/form data exists across the Gen III family.
- Gen III selects the effective local form by game version:
  - Ruby/Sapphire: Normal
  - FireRed: Attack
  - LeafGreen: Defense
  - Emerald: Speed
- Emerald contains a dedicated runtime Speed-form stat vector and special graphics handling.

### Spinda
- personality-derived spot pattern.
- procedural appearance, not a finite discrete form ID.

## Exclusions

- shiny coloration: palette/status variant, not form;
- ordinary gender sprite differences: not form unless a later game explicitly stores them as form values;
- contest condition, status, animation frame, shiny and party icon differences are not independently counted as forms.

## EMERALD consequence

Generation III demonstrates why the target engine must support both:
- discrete form IDs; and
- derived/procedural appearance and battle-state forms.

# JAPAN battle logic survey and remake policy

The original twenty-ROM survey and the GBA remake architecture require two separate concepts:

1. **historical battle behavior**, used to understand and verify each Japanese source title;
2. **remake battle behavior**, used by RED/GREEN/BLUE/YELLOW/GOLD/SILVER/CRYSTAL on the Generation-III-derived runtime.

They must not be conflated.

## Original-generation boundary

### Generation I

The original battle engine has a single Special stat, no Abilities, no held-item system and no native doubles. Physical/special damage category is determined by move type rather than by individual move.

Critical hits use the Generation-I base-Speed-driven model rather than the later staged system. Generation I also carries type/status/damage quirks that should remain documented for regression tests, not silently leak into the modern remake profile.

### Generation II

Generation II splits Special into Sp. Atk and Sp. Def, adds held items, friendship-dependent battle data and weather-era mechanics, but still has no Abilities and still assigns physical/special category by type.

Gold/Silver/Crystal therefore need their original battle semantics preserved as a reference profile even though the remake default is modern.

### Generation III

Generation III introduces the GBA runtime model we actually want to build on: Abilities, Natures, IV/EV-era Pokémon data, double battles and the Gen III weather/battle architecture.

However, Gen III still uses type-based physical/special classification and lacks later type/move/status/experience rules. It is the implementation base, not the final rule target.

## Remake default: modern-latest

The expanded engine is pinned to:

`rh-hideout/pokeemerald-expansion@75b806a3ab57a81ff1eb6179288981f0b3cc3050`

At that exact ref, the battle configuration already exposes the modernization switches required by this project. The remake default keeps the relevant settings at `GEN_LATEST`, including:

- critical-hit chance and multiplier;
- paralysis speed;
- confusion self-hit chance;
- catch EXP;
- trainer EXP multiplier;
- EXP distribution and scaling;
- badge stat boosts;
- stat recalculation;
- burn damage;
- updated type matchups;
- sleep duration;
- updated move data/types/flags;
- physical/special split;
- updated Ability data.

The Pokémon configuration likewise keeps updated types, stats, Abilities, EV yields, EXP yields and level-up learnsets at `GEN_LATEST`.

## What remains original

Modern battle rules do **not** mean rewriting the source games' identities.

The remake still preserves:

- which trainer or static Pokémon appears at a story point;
- original map/event progression;
- version-specific encounter meaning;
- original gift/static encounter identity;
- title-specific trainer/event identity.

Those source facts are converted into the modern engine.

Example: the original Route 12 Snorlax remains the Route 12 Snorlax event, but the battle itself runs through the modern move/type/status/critical/ability/item rule layer.

## Battle gimmicks

The pinned engine capability set enables Mega Evolution, Primal Reversion, Ultra Burst, Gigantamax and Tera-related forms/features alongside regional forms and cross-generation evolutions.

**Capability is not the same thing as availability.**

The common engine may support them, while each remake title controls whether they are obtainable, when they unlock, and whether a given story/battle permits them. This avoids flattening RED through CRYSTAL into one identical campaign.

## Verification strategy

Every battle-sensitive migration should support two comparisons:

- source/reference result: what the original Japanese title does;
- remake result: what the modern battle profile intentionally does.

Intentional differences are recorded as modernization, not treated as conversion bugs.

Raw ROM revision diff size is not enough to claim battle-code equality. Revision-specific battle changes, if any, require instruction-level or source-correspondence evidence.

Machine-readable files:

- `manifests/japan-battle-generation-matrix.csv`
- `manifests/japan-battle-runtime-policy.json`

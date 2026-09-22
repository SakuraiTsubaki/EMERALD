# Generation Superset Merge

## Decision

Generation I, II and III are merged as **three independent supersets** before any later cross-generation world integration.

This is a union, not a destructive overwrite.

- Generation I = 赤 + 緑 + 青 + ピカチュウ + every verified Japanese revision.
- Generation II = 金 + 銀 + クリスタル + every verified Japanese revision.
- Generation III = ルビー + サファイア + エメラルド + ファイアレッド + リーフグリーン + every verified Japanese revision.

The Japanese ROM set is the primary binary evidence. ROM binaries are never committed.

## Core rule

Every source fact is imported into a canonical representation with provenance:

`source game -> source revision -> source address/id -> canonical entity -> runtime representation`

If two sources are identical after canonicalization, they may share one canonical payload while retaining multiple provenance records.

If two sources differ, neither is silently deleted. The difference becomes a variant keyed by source profile, revision, event state, version mode, or another explicit discriminator.

## Generation I

Canonical world: **Kanto**.

RED, GREEN, BLUE and YELLOW are source profiles of one Generation I superset. YELLOW-specific events, graphics, encounter behavior, scripts and SGB behavior remain available instead of replacing the earlier profiles.

Runtime can expose:

- a union mode containing every compatible Generation I feature;
- RED/GREEN/BLUE/YELLOW reproduction profiles;
- revision-specific reproduction when a revision difference is materially observable.

## Generation II

Canonical worlds: **Johto + Kanto**.

GOLD, SILVER and CRYSTAL are source profiles of one Generation II superset. Crystal additions are not treated as a reason to erase Gold/Silver behavior; Gold/Silver-only data remains variant data.

RTC/time events, animations, map/event differences and Crystal-specific systems are canonicalized separately.

## Generation III

Canonical worlds: **Hoenn + Kanto + Sevii Islands**.

RSE and FRLG are different source families but feed one Generation III canonical model.

- Ruby/Sapphire/Emerald supply Hoenn, RSE events and RSE-specific engine behavior.
- FireRed/LeafGreen supply Generation III Kanto, Sevii Islands and FRLG-specific behavior.
- Hoenn is not discarded.
- Kanto/Sevii are not forced into raw RSE layouts.
- Both families are converted into a common GBA map/metatile/event representation before runtime integration.

## Save rule

Source saves remain isolated by source game/revision. Saves are **not byte-merged**.

Import pipeline:

`source SAV -> source parser -> canonical persistent state -> target GBA save schema`

This preserves original save evidence while allowing the merged runtime to maintain one expanded target save format.

## Conflict handling

Never resolve a conflict by “newer automatically wins.”

Use this order:

1. preserve the Japanese original value and provenance;
2. determine whether values are truly equivalent after canonicalization;
3. if equivalent, deduplicate payload only;
4. if behavior differs, store explicit variants;
5. select behavior through runtime profile/configuration;
6. modern battle/data-system changes remain a separate modern-core layer and must not rewrite historical source evidence.

## Implementation order

1. Freeze ROM identity and revision provenance in `manifests/generation-supersets.json`.
2. Build per-source adapters.
3. Define canonical IDs for maps, warps, objects, scripts, encounters, trainers, text, graphics and audio.
4. Produce field-level/version-level difference manifests.
5. Import Generation I into one Kanto canonical dataset.
6. Import Generation II into one Johto+Kanto canonical dataset.
7. Import Generation III RSE + FRLG into one Hoenn+Kanto+Sevii canonical dataset.
8. Add runtime profile flags for original-version reproduction.
9. Add union-mode regression tests proving no source-exclusive content was lost.
10. Only after the three supersets are stable, compose the larger cross-generation world/runtime.

## Verification rule

A merged dataset is incomplete if any verified source-only asset, map, event, encounter, trainer, script, text, mechanic, revision fix or observable behavior has no provenance record and no canonical destination.

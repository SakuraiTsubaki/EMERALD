# Generation 10 readiness

EMERALD is reserving engine and storage capacity for Generation 10 before resuming additional form-change work.

This is capacity work, not speculative content work. No unreleased species, moves, items, abilities, forms, mechanics, IDs, or save fields are invented here.

## Retail binary evidence

The project baseline is the six supplied retail Emerald ROM/save pairs:

- Japanese BPEJ is the primary reference.
- English BPEE is the first comparison reference.
- German BPED, French BPEF, Italian BPEI, and Spanish BPES are verified separately.
- All six ROMs are revision 0 and 16 MiB.
- All six saves are 128 KiB Flash saves.
- Exact hashes and per-save active-slot observations are recorded in `manifests/emerald-binary-baseline.csv`.
- The reproducible read-only analyzer is `tools/analyze_emerald_binary_set.py`.

The Japanese ROM has a materially different occupied layout from the five international ROMs. EMERALD therefore does not use one hard-coded trailing free-space address as a cross-region expansion contract.

See `research/rom-save-expansion-baseline.md` for the binary survey.

## Current expansion baseline

Pinned executable base:

- `rh-hideout/pokeemerald-expansion@75b806a3ab57a81ff1eb6179288981f0b3cc3050`
- generation constants: `include/config/general.h`

The pinned source originally orders behavior generations as:

`GEN_9 -> GEN_CHAMPIONS -> GEN_COUNT`

`GEN_CHAMPIONS` is already a distinct post-Gen-9 behavior slot. It must not be renumbered just to make room for Generation 10.

EMERALD reserves the next slot as:

`GEN_9 -> GEN_CHAMPIONS -> GEN_10 -> GEN_COUNT`

The generation-capacity overlay is:

`patches/pokeemerald-expansion/0001-reserve-generation-10-slot.patch`

It deliberately leaves `GEN_LATEST = GEN_9` until Generation 10 behavior and data are actually known and verified.

## ROM capacity strategy

The supplied retail ROMs are 16 MiB, but the pinned modern expansion linker exposes the full 32 MiB GBA ROM address space.

New source-built data should therefore grow through the linker into that 32 MiB space. Region-specific trailing `0xFF` holes remain useful evidence for retail analysis, but they are not treated as a shared allocation map across BPEJ/BPEE/BPED/BPEF/BPEI/BPES.

ROM binaries are never committed to this repository. Only hashes, structural observations, source overlays, patches, and verification artifacts are tracked.

## Save compatibility strategy

Retail Emerald uses 128 KiB Flash divided into 32 sectors of 4096 bytes.

The gameplay save contract remains:

- two alternating save slots;
- 14 gameplay sectors per slot;
- Hall of Fame sectors 28-29;
- Trainer Hill sector 30;
- Recorded Battle sector 31;
- sector signature `0x08012025`;
- footer metadata starting at offset `0xFF4`.

Vanilla Emerald uses 3968 bytes of logical data in a full sector and leaves bytes `0xF80..0xFF3` unused before the 12-byte footer metadata. The pinned expansion reuses exactly those 116 bytes per gameplay sector as `SaveBlock3`:

`14 x 116 = 1624 bytes per save slot`

All six supplied checksum-valid active save slots have zero bytes in this footer-extension area. This directly confirms that the expansion mechanism does not collide with observed retail Emerald save data.

The six saves also expose 2172 bytes of vanilla logical slack per active slot. That space is recorded as evidence only. It is not an automatic capacity pool because current expanded structure sizes must be audited before any portion is claimed.

Special sectors 28-31 remain reserved even when a supplied save happens not to contain special-sector data. They are not expansion space.

## Entity storage bottlenecks

At the pinned expansion revision, BoxPokemon storage uses:

- species: 11 bits, maximum 2047;
- moves: 11 bits, maximum 2047;
- held item: originally 10 bits, maximum 1023, followed by six unused bits in the same original Emerald 16-bit held-item word.

EMERALD applies:

`patches/pokeemerald-expansion/0002-widen-held-item-save-field.patch`

That patch widens `heldItem` to the full 16-bit word without changing the serialized byte position or increasing the BoxPokemon structure size.

Species and move fields remain 11 bits in this phase. They are not widened speculatively. If verified Generation 10 data exceeds either 2047 ceiling, the serialization design must be reviewed with real data before changing it.

## What changes now

1. Reserve `GEN_10` after `GEN_CHAMPIONS` without renumbering existing behavior generations.
2. Keep `GEN_LATEST` at Gen 9 so current mechanics do not silently change.
3. Build expanded ROMs against the pinned 32 MiB linker instead of relying on one retail-region free-space offset.
4. Preserve the original 128 KiB Flash layout and use the verified 1624-byte `SaveBlock3` extension mechanism.
5. Preserve special sectors 28-31.
6. Widen the held-item save field to 16 bits in place while leaving species and move widths unchanged.
7. Keep PKHeX source provenance centralized in `manifests/pkhex-source-pin.yml`.
8. Keep generation-specific conversion data append-only.
9. Verify all of these invariants in CI with `tools/verify_future_generation_readiness.py`.

## When Generation 10 source data becomes available

Do not renumber existing EMERALD identifiers.

Update in this order:

1. update authoritative Japanese-first source references;
2. advance pinned PKHeX / engine references only after review;
3. append verified species, item, move, ability, evolution, learnset, encounter and save-format data;
4. compare real new ID maxima against the existing serialized field widths;
5. add exact Generation 10 behavior rules;
6. verify old retail saves, expanded saves, and serialization migrations against real formats;
7. only then switch `GEN_LATEST` to `GEN_10`.

Additional form-change implementation remains outside this capacity phase.

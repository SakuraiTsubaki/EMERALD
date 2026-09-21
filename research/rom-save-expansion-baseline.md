# Emerald ROM/save expansion baseline

This baseline is derived from the six original Emerald ROM/save pairs supplied for the project. The binaries themselves are not committed. Only hashes and structural observations are stored in EMERALD.

## ROM set

All six ROMs are 16 MiB, revision 0, with valid GBA header checksums.

| Language | Game code | Last non-FF byte | Trailing FF |
| --- | --- | ---: | ---: |
| Japanese | BPEJ | 0xF3F7C7 | 788,536 bytes |
| English | BPEE | 0xE3CF63 | 1,847,452 bytes |
| German | BPED | 0xE3CF63 | 1,847,452 bytes |
| French | BPEF | 0xE3CF63 | 1,847,452 bytes |
| Italian | BPEI | 0xE3CF63 | 1,847,452 bytes |
| Spanish | BPES | 0xE3CF63 | 1,847,452 bytes |

The Japanese ROM has a materially different occupied layout from the five international ROMs. EMERALD must therefore not treat one hard-coded free-space address as a cross-region expansion contract.

The pinned modern linker already declares:

- ROM origin: 0x08000000
- ROM length: 32 MiB

Generation-10 capacity work should therefore grow from source builds into the 32 MiB ROM address space instead of consuming region-specific trailing holes by absolute address.

## Save set

All six saves are 128 KiB Flash saves with the Emerald 32-sector layout.

For every checksum-valid active save slot:

- 14 gameplay sectors are present.
- sector signature is 0x08012025.
- all section checksums validate.
- vanilla logical payload slack is 2,172 bytes per slot.
- the unused footer area from 0xF80 through 0xFF3 is 116 bytes per sector.
- 14 x 116 = 1,624 footer-extension bytes per save slot.
- every byte in both observed slack classes is zero in all six active saves.

The 1,624-byte footer-extension area is the exact space used by pokeemerald-expansion SaveBlock3. The supplied original saves therefore confirm that this extension mechanism does not collide with original Emerald data.

The additional 2,172 bytes of vanilla logical slack are recorded as evidence but are not automatically allocated. Current expanded structs must be audited before any of that space is claimed.

## Immediate identifier bottleneck

At the pinned pokeemerald-expansion revision:

- species stored in BoxPokemon: 11 bits, maximum 2047.
- moves stored in BoxPokemon: 11 bits, maximum 2047.
- held item stored in BoxPokemon: 10 bits, maximum 1023.
- the held-item field is followed by six unused bits in the same original 16-bit Emerald save field.

The held-item ceiling is therefore the first avoidable save-format bottleneck.

EMERALD patch 0002 widens heldItem from 10 bits to 16 bits and removes the adjacent six-bit unused field. This does not change the size or byte position of the original Emerald held-item field, and existing expanded saves with zero high bits remain representable.

Species and move widening are intentionally not performed in this phase. Their current 11-bit ceilings are tracked by CI and will be redesigned only if real Generation-10 data requires it, so tera type and evolution-tracker data are not displaced speculatively.

## Files

- manifests/emerald-binary-baseline.csv
- tools/analyze_emerald_binary_set.py
- patches/pokeemerald-expansion/0002-widen-held-item-save-field.patch
- tools/verify_future_generation_readiness.py

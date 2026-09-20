# PKHeX entity and save format extraction

Pinned reference: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

## Entity format milestones

- Gen I-II have no generic stored form field.
- Gen III still has no generic form field; appearance/forms are derived or title/runtime-specific.
- Gen IV-V introduce a 5-bit persistent form at byte 0x40 bits 3-7.
- Gen VI-VII move the 5-bit form field to byte 0x1D bits 3-7 and add FormArgument state.
- Gen VIII/IX use a dedicated form byte at 0x24.
- Gen VIII separates Gigantamax capability and Dynamax Level from Form.
- Gen IX stores Tera Type independently from Form.

This directly supports EMERALD's proposed separation of persistent form, auxiliary form argument, individual flags and battle transformation state.

## Save extraction

`manifests/pkhex/save-formats.csv` enumerates the top-level PKHeX save classes. The next pass drills into each generation's substructures to extract:

- party and box locations;
- item/bag structures;
- Pokédex;
- event flags and variables;
- Mystery Gift state;
- RTC/time fields;
- checksums/encryption;
- generation-specific special blocks.

These schemas are reference data. EMERALD implementations remain independently written.

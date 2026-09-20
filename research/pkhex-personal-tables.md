# PKHeX Personal table extraction

Pinned reference: `kwsch/PKHeX@8ad201e80244f630ab5a46922ab72fb79c5ad4f4`

The Personal resources are fixed-size record arrays. Entry counts can therefore be validated directly as:

`resource bytes / PersonalInfo*.SIZE`

## Key results

- Emerald: 10,836 bytes / 28 = **387 entries**
- DP: 22,044 / 44 = **501**
- Pt/HGSS: 22,352 / 44 = **508**
- BW: 40,080 / 60 = **668**
- B2W2: 53,884 / 76 = **709**
- XY: 51,136 / 64 = **799**
- ORAS: 66,080 / 80 = **826**
- SM: 80,724 / 84 = **961**
- USUM: 81,984 / 84 = **976**
- SWSH: 209,792 / 176 = **1192**
- PLA: 224,576 / 176 = **1276**
- SV: 113,920 / 80 = **1424**
- Z-A: 115,600 / 80 = **1445**

## Stable leading fields

Across the inspected PersonalInfo layouts, the first bytes remain highly regular:
- 0x00 HP
- 0x01 Attack
- 0x02 Defense
- 0x03 Speed
- 0x04 Special Attack
- 0x05 Special Defense
- 0x06 Type 1
- 0x07 Type 2

Later fields evolve by generation.

## Form table evolution

- Gen I-III: no generic FormCount/FormStatsIndex in the Personal record.
- Gen IV: FormCount @0x29, FormStatsIndex @0x2A.
- Gen V-VII: FormStatsIndex @0x1C, FormCount @0x20.
- Gen VIII: FormStatsIndex @0x1E, FormCount @0x20.
- Gen IX: FormStatsIndex @0x18, FormCount @0x1A.

## Ability evolution

- Gen I-II: no modern Ability slots.
- Gen III-IV: two Ability slots.
- Gen V onward: two normal + one hidden Ability.
- Gen VIII onward: Ability IDs are stored as 16-bit values in Personal data.

The next extraction step can decode each Personal record into a common EMERALD schema once binary resource access is available. The record counts and parser layouts are already verified here.

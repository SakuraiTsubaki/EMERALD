# Generation V form mechanics — census baseline

Reference census baselines:
- PKHeX @ 8ad201e80244f630ab5a46922ab72fb79c5ad4f4
- Pokémon Showdown data/pokedex.ts @ 2ddfa0476f8207e12e204b1c69f7c7683b17633c

## New / materially changed Generation V form families

### Basculin
- Red-Striped / Blue-Striped are persistent encounter identities.
- Same species, form value selects appearance and Ability-slot differences.

### Darmanitan
- Standard / Zen.
- Zen Mode is battle-only and Ability/HP-driven.
- Unovan Zen changes Fire -> Fire/Psychic and swaps the offensive/defensive stat profile.

### Deerling / Sawsbuck
- Spring / Summer / Autumn / Winter.
- In Gen V the world season is RTC-month driven and party forms update to the current season.
- Stats/types remain shared; appearance is form-dependent.

### Tornadus / Thundurus / Landorus
- Incarnate / Therian.
- B2W2 introduces Therian formes.
- Reveal Glass is the active-use form-change item.
- Personal data changes: stats and Ability differ by forme.

### Kyurem
- Kyurem / White Kyurem / Black Kyurem.
- DNA Splicers implement fusion with Reshiram or Zekrom.
- Fusion must retain partner identity for later separation.
- Fused forms have separate stats/Ability and move conversion rules.

### Keldeo
- Ordinary / Resolute.
- Resolute is derived from knowing Secret Sword in B2W2.
- Battle parameters are otherwise shared.

### Meloetta
- Aria / Pirouette.
- Relic Song triggers battle-only form switching.
- Form changes stats and Normal/Psychic <-> Normal/Fighting typing.
- Returns to Aria outside battle.

### Genesect
- Normal + Douse / Shock / Burn / Chill Drive forms.
- Held Drive selects the form/cassette identity and Techno Blast type.
- Base stats/type/Ability remain shared.

## Carry-over mechanics

Generation V also continues earlier form families such as Unown, Castform, Deoxys, Burmy/Wormadam, Cherrim, Shellos/Gastrodon, Rotom, Giratina, Shaymin and Arceus.

## Engine implications

Generation V adds three important trigger families to the cross-generation model:
1. fusion partner state (Kyurem);
2. move-known persistent form derivation (Keldeo);
3. move-used battle form switching (Meloetta).

These remain separate from ordinary persistent form ID storage.

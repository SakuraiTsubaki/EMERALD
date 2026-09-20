typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define SPECIES_MORPEKO 253
#define ABILITY_HUNGER_SWITCH 76
#define FORM_FULL_BELLY 0
#define FORM_HANGRY 1
#define STATUS2_TRANSFORMED (1u << 21)

#define G_ACTIVE_BATTLER (*(volatile u8 *)0x02023D08)
#define G_BATTLE_MONS ((volatile u8 *)0x02023D28)
#define G_BATTLER_PARTY_INDEXES ((volatile u16 *)0x02023D12)
#define G_BATTLER_SPRITE_IDS ((volatile u8 *)0x02023E88)
#define G_BATTLE_MON_FORMS ((volatile u8 *)0x02024188)
#define G_PLAYER_PARTY ((volatile u8 *)0x02024190)
#define G_ENEMY_PARTY ((volatile u8 *)0x020243E8)
#define G_BATTLER_SPRITES ((volatile u8 *)0x02020630)

#define PLAYER_PARTY_MON_SIZE 0x64
#define BATTLE_MON_SIZE 0x58
#define SPRITE_SIZE_BYTES 0x44

#define FULL_FRONT    ((const u8 *)0x0891C000)
#define HANGRY_FRONT  ((const u8 *)0x0891C800)
#define FULL_BACK     ((const u8 *)0x0891D000)
#define HANGRY_BACK   ((const u8 *)0x0891D800)
#define FULL_PAL      ((const u16 *)0x0891E000)
#define HANGRY_PAL    ((const u16 *)0x0891E020)
#define FULL_SHINY    ((const u16 *)0x0891E040)
#define HANGRY_SHINY  ((const u16 *)0x0891E060)

static volatile u8 *battle_mon(u8 battler)
{
    return G_BATTLE_MONS + ((u32)battler * BATTLE_MON_SIZE);
}

static u16 read16(volatile u8 *p)
{
    return (u16)(p[0] | ((u16)p[1] << 8));
}

static u32 read32(volatile u8 *p)
{
    return (u32)p[0] | ((u32)p[1] << 8) | ((u32)p[2] << 16) | ((u32)p[3] << 24);
}

static u8 call_GetBattlerSide(u8 battler)
{
    typedef u8 (*Fn)(u8);
    return ((Fn)0x080A62F9)(battler);
}

static u8 call_IsMonShiny(void *mon)
{
    typedef u8 (*Fn)(void *);
    return ((Fn)0x0806E631)(mon);
}

static void call_LoadPalette(const void *src, u16 offset, u16 size)
{
    typedef void (*Fn)(const void *, u16, u16);
    ((Fn)0x080A1201)(src, offset, size);
}

static void call_RequestSpriteCopy(const u8 *src, u8 *dest, u16 size)
{
    typedef void (*Fn)(const u8 *, u8 *, u16);
    ((Fn)0x08007205)(src, dest, size);
}

static u8 call_AbilityBattleEffects(u8 caseId, u8 battler, u8 ability, u8 special, u16 move)
{
    typedef u8 (*Fn)(u8, u8, u8, u8, u16);
    return ((Fn)0x08042469)(caseId, battler, ability, special, move);
}

static void *party_mon(u8 battler)
{
    u16 partyIndex = G_BATTLER_PARTY_INDEXES[battler];
    volatile u8 *party = call_GetBattlerSide(battler) == 0 ? G_PLAYER_PARTY : G_ENEMY_PARTY;
    return (void *)(party + ((u32)partyIndex * PLAYER_PARTY_MON_SIZE));
}

static void copy_form_gfx(u8 battler, u8 form)
{
    u8 spriteId = G_BATTLER_SPRITE_IDS[battler];
    volatile u8 *sprite = G_BATTLER_SPRITES + ((u32)spriteId * SPRITE_SIZE_BYTES);
    u16 tileNum = read16(sprite + 4) & 0x03FF;
    u8 *dst = (u8 *)(0x06010000 + ((u32)tileNum << 5));
    const u8 *src;
    const u16 *pal;
    u8 shiny = call_IsMonShiny(party_mon(battler));

    if (call_GetBattlerSide(battler) == 0)
        src = form == FORM_HANGRY ? HANGRY_BACK : FULL_BACK;
    else
        src = form == FORM_HANGRY ? HANGRY_FRONT : FULL_FRONT;

    if (shiny)
        pal = form == FORM_HANGRY ? HANGRY_SHINY : FULL_SHINY;
    else
        pal = form == FORM_HANGRY ? HANGRY_PAL : FULL_PAL;

    call_RequestSpriteCopy(src, dst, 0x800);
    call_LoadPalette(pal, (u16)(0x100 + ((u16)battler << 4)), 32);
}

static u8 morpeko_toggle(u8 battler)
{
    volatile u8 *bm = battle_mon(battler);
    u8 form;

    if (read16(bm) != SPECIES_MORPEKO)
        return 0;
    if (bm[0x20] != ABILITY_HUNGER_SWITCH)
        return 0;
    if (read16(bm + 0x28) == 0)
        return 0;
    if (read32(bm + 0x50) & STATUS2_TRANSFORMED)
        return 0;

    form = G_BATTLE_MON_FORMS[battler] == FORM_HANGRY ? FORM_FULL_BELLY : FORM_HANGRY;
    G_BATTLE_MON_FORMS[battler] = form;
    copy_form_gfx(battler, form);
    return 1;
}

__attribute__((used,noinline))
u32 morpeko_endturn_bridge(void)
{
    u8 battler = G_ACTIVE_BATTLER;
    u8 effect = call_AbilityBattleEffects(1, battler, 0, 0, 0);

    if (effect != 0)
        return effect;

    return morpeko_toggle(battler);
}

__attribute__((used,noinline))
void morpeko_reset_switch(u8 battler)
{
    volatile u8 *bm = battle_mon(battler);

    if (read16(bm) != SPECIES_MORPEKO)
        return;

    if (G_BATTLE_MON_FORMS[battler] != FORM_FULL_BELLY)
    {
        G_BATTLE_MON_FORMS[battler] = FORM_FULL_BELLY;
        copy_form_gfx(battler, FORM_FULL_BELLY);
    }
}

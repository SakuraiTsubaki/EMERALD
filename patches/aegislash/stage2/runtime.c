typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed int s32;

#define SPECIES_AEGISLASH 252
#define ABILITY_STANCE_CHANGE 76
#define MOVE_KINGS_SHIELD 354
#define FORM_SHIELD 0
#define FORM_BLADE 1

#define G_BATTLE_MONS ((volatile u8 *)0x02023D28)
#define G_BATTLER_PARTY_INDEXES ((volatile u16 *)0x02023D12)
#define G_BATTLER_SPRITE_IDS ((volatile u8 *)0x02023E88)
#define G_CURRENT_MOVE (*(volatile u16 *)0x02023E8E)
#define G_CHOSEN_MOVE (*(volatile u16 *)0x02023E90)
#define G_BATTLER_ATTACKER (*(volatile u8 *)0x02023EAF)
#define G_BATTLER_TARGET (*(volatile u8 *)0x02023EB0)
#define G_LAST_RESULTING_MOVES ((volatile u16 *)0x02023F04)
#define G_PROTECT_STRUCTS ((volatile u8 *)0x02023FE0)
#define G_BATTLE_MON_FORMS ((volatile u8 *)0x02024188)
#define G_PLAYER_PARTY ((volatile u8 *)0x02024190)
#define G_ENEMY_PARTY ((volatile u8 *)0x020243E8)
#define G_BATTLER_SPRITES ((volatile u8 *)0x02020630)
#define G_BATTLE_MOVES ((volatile u8 *)0x082ED220)

#define PLAYER_PARTY_MON_SIZE 0x64
#define BATTLE_MON_SIZE 0x58
#define SPRITE_SIZE_BYTES 0x44
#define BATTLE_MOVE_SIZE 12

#define SHIELD_FRONT ((const u32 *)0x08918000)
#define BLADE_FRONT  ((const u32 *)0x08918800)
#define SHIELD_BACK  ((const u32 *)0x08919000)
#define BLADE_BACK   ((const u32 *)0x08919800)
#define SHIELD_PAL   ((const u16 *)0x0891A000)
#define BLADE_PAL    ((const u16 *)0x0891A020)

#define MON_DATA_ATK_EV 27
#define MON_DATA_DEF_EV 28
#define MON_DATA_SPATK_EV 30
#define MON_DATA_SPDEF_EV 31
#define MON_DATA_ATK_IV 40
#define MON_DATA_DEF_IV 41
#define MON_DATA_SPATK_IV 43
#define MON_DATA_SPDEF_IV 44

#define STAT_ATK 1
#define STAT_DEF 2
#define STAT_SPATK 4
#define STAT_SPDEF 5

#define ABILITY_CLEAR_BODY 29
#define ABILITY_HYPER_CUTTER 52
#define ABILITY_WHITE_SMOKE 73

static u32 call_GetMonData(void *mon, s32 field)
{
    typedef u32 (*Fn)(void *, s32, void *);
    return ((Fn)0x0806A059)(mon, field, (void *)0);
}
static u8 call_GetNature(void *mon)
{
    typedef u8 (*Fn)(void *);
    return ((Fn)0x0806CB35)(mon);
}
static u16 call_ModifyStatByNature(u8 nature, u16 stat, u8 statIndex)
{
    typedef u16 (*Fn)(u8, u16, u8);
    return ((Fn)0x0806D36D)(nature, stat, statIndex);
}
static u8 call_GetBattlerSide(u8 battler)
{
    typedef u8 (*Fn)(u8);
    return ((Fn)0x080A62F9)(battler);
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

__attribute__((noinline,optnone))
static u32 div100(u32 x)
{
    u32 q = 0;
    while (x >= 100) { x -= 100; q++; }
    return q;
}

static u16 calc_stat(u8 base, u8 iv, u8 ev, u8 level, u8 nature, u8 statIndex)
{
    u32 n = (2u * base + iv + (ev >> 2)) * level;
    n = div100(n) + 5;
    return call_ModifyStatByNature(nature, (u16)n, statIndex);
}
static volatile u8 *battle_mon(u8 battler)
{
    return G_BATTLE_MONS + ((u32)battler * BATTLE_MON_SIZE);
}
static void *party_mon(u8 battler)
{
    u16 partyIndex = G_BATTLER_PARTY_INDEXES[battler];
    volatile u8 *party = call_GetBattlerSide(battler) == 0 ? G_PLAYER_PARTY : G_ENEMY_PARTY;
    return (void *)(party + ((u32)partyIndex * PLAYER_PARTY_MON_SIZE));
}
static u16 read16(volatile u8 *p) { return (u16)(p[0] | ((u16)p[1] << 8)); }
static void write16(volatile u8 *p, u16 v) { p[0]=(u8)v; p[1]=(u8)(v>>8); }

static void apply_form_stats(u8 battler, u8 form)
{
    volatile u8 *bm = battle_mon(battler);
    void *mon = party_mon(battler);
    u8 level = bm[0x2A];
    u8 nature = call_GetNature(mon);
    u8 atkBase = form == FORM_BLADE ? 150 : 50;
    u8 defBase = form == FORM_BLADE ? 50 : 150;
    u8 spaBase = form == FORM_BLADE ? 150 : 50;
    u8 spdBase = form == FORM_BLADE ? 50 : 150;

    write16(bm+0x02, calc_stat(atkBase,(u8)call_GetMonData(mon,MON_DATA_ATK_IV),(u8)call_GetMonData(mon,MON_DATA_ATK_EV),level,nature,STAT_ATK));
    write16(bm+0x04, calc_stat(defBase,(u8)call_GetMonData(mon,MON_DATA_DEF_IV),(u8)call_GetMonData(mon,MON_DATA_DEF_EV),level,nature,STAT_DEF));
    write16(bm+0x08, calc_stat(spaBase,(u8)call_GetMonData(mon,MON_DATA_SPATK_IV),(u8)call_GetMonData(mon,MON_DATA_SPATK_EV),level,nature,STAT_SPATK));
    write16(bm+0x0A, calc_stat(spdBase,(u8)call_GetMonData(mon,MON_DATA_SPDEF_IV),(u8)call_GetMonData(mon,MON_DATA_SPDEF_EV),level,nature,STAT_SPDEF));
}

static void copy_form_gfx(u8 battler, u8 form)
{
    u8 spriteId = G_BATTLER_SPRITE_IDS[battler];
    volatile u8 *sprite = G_BATTLER_SPRITES + ((u32)spriteId * SPRITE_SIZE_BYTES);
    u16 tileNum = read16(sprite + 4) & 0x03FF;
    u8 *dst = (u8 *)(0x06010000 + ((u32)tileNum << 5));
    const u8 *src;
    const u16 *pal;

    if (call_GetBattlerSide(battler) == 0)
        src = (const u8 *)(form == FORM_BLADE ? BLADE_BACK : SHIELD_BACK);
    else
        src = (const u8 *)(form == FORM_BLADE ? BLADE_FRONT : SHIELD_FRONT);
    pal = form == FORM_BLADE ? BLADE_PAL : SHIELD_PAL;

    call_RequestSpriteCopy(src, dst, 0x800);
    call_LoadPalette(pal, (u16)(0x100 + ((u16)battler << 4)), 32);
}
static void set_form(u8 battler, u8 form)
{
    G_BATTLE_MON_FORMS[battler] = form;
    apply_form_stats(battler, form);
    copy_form_gfx(battler, form);
}

__attribute__((used,noinline))
u32 stance_helper(void)
{
    u8 battler = G_BATTLER_ATTACKER;
    volatile u8 *bm = battle_mon(battler);
    u16 species = read16(bm);
    u16 move = G_CURRENT_MOVE;
    u8 targetForm;

    if (species != SPECIES_AEGISLASH || bm[0x20] != ABILITY_STANCE_CHANGE || read16(bm+0x28) == 0)
        return 0;
    if (move != G_CHOSEN_MOVE)
        return 0;
    if (move == MOVE_KINGS_SHIELD)
        targetForm = FORM_SHIELD;
    else if (G_BATTLE_MOVES[(u32)move * BATTLE_MOVE_SIZE + 1] != 0)
        targetForm = FORM_BLADE;
    else
        return 0;
    if (G_BATTLE_MON_FORMS[battler] == targetForm)
        return 0;
    set_form(battler,targetForm);
    return 1;
}

__attribute__((used,noinline))
u32 ks_should_bypass(void)
{
    u8 target = G_BATTLER_TARGET;
    u16 move = G_CURRENT_MOVE;
    volatile u8 *protect = G_PROTECT_STRUCTS + ((u32)target << 4);
    if (!(protect[0] & 1)) return 0;
    if (G_LAST_RESULTING_MOVES[target] != MOVE_KINGS_SHIELD) return 0;
    return G_BATTLE_MOVES[(u32)move * BATTLE_MOVE_SIZE + 1] == 0;
}

__attribute__((used,noinline))
void ks_contact_penalty(void)
{
    u8 target=G_BATTLER_TARGET, attacker=G_BATTLER_ATTACKER;
    u16 move=G_CURRENT_MOVE;
    volatile u8 *protect=G_PROTECT_STRUCTS+((u32)target<<4);
    volatile u8 *atkMon=battle_mon(attacker);
    u8 ability;
    u8 *stage;

    if (!(protect[0]&1)) return;
    if (G_LAST_RESULTING_MOVES[target] != MOVE_KINGS_SHIELD) return;
    if (G_BATTLE_MOVES[(u32)move*BATTLE_MOVE_SIZE+1] == 0) return;
    if (!(G_BATTLE_MOVES[(u32)move*BATTLE_MOVE_SIZE+8]&1)) return;

    ability=atkMon[0x20];
    if (ability==ABILITY_CLEAR_BODY || ability==ABILITY_HYPER_CUTTER || ability==ABILITY_WHITE_SMOKE) return;

    stage=(u8 *)(atkMon+0x19);
    if (*stage>1) *stage-=2; else *stage=0;
}

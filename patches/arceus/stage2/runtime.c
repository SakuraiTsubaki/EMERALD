typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define SPECIES_ARCEUS_TEST 253
#define MOVE_JUDGMENT_TEST 354

#define RULESET_GEN4 0
#define RULESET_GEN5 1
#define RULESET_GEN6 2
#define RULESET_GEN7 3
#define RULESET_GEN8_BDSP 4
#define RULESET_PLA 5
#define RULESET_GEN9 6
#define ARCEUS_RULESET (*(const volatile u8 *)0x0891EA40)

#define TYPE_NORMAL 0
#define TYPE_FIGHTING 1
#define TYPE_FLYING 2
#define TYPE_POISON 3
#define TYPE_GROUND 4
#define TYPE_ROCK 5
#define TYPE_BUG 6
#define TYPE_GHOST 7
#define TYPE_STEEL 8
#define TYPE_MYSTERY 9
#define TYPE_FIRE 10
#define TYPE_WATER 11
#define TYPE_GRASS 12
#define TYPE_ELECTRIC 13
#define TYPE_PSYCHIC 14
#define TYPE_ICE 15
#define TYPE_DRAGON 16
#define TYPE_DARK 17
#define TYPE_FAIRY 18

#define FORM_NORMAL 0
#define FORM_FIGHTING 1
#define FORM_FLYING 2
#define FORM_POISON 3
#define FORM_GROUND 4
#define FORM_ROCK 5
#define FORM_BUG 6
#define FORM_GHOST 7
#define FORM_STEEL 8
#define FORM_FIRE 9
#define FORM_WATER 10
#define FORM_GRASS 11
#define FORM_ELECTRIC 12
#define FORM_PSYCHIC 13
#define FORM_ICE 14
#define FORM_DRAGON 15
#define FORM_DARK 16
#define FORM_FAIRY 17
#define FORM_INVALID 0xFF

#define ITEM_FLAME_PLATE 377
#define ITEM_SPLASH_PLATE 378
#define ITEM_ZAP_PLATE 379
#define ITEM_MEADOW_PLATE 380
#define ITEM_ICICLE_PLATE 381
#define ITEM_FIST_PLATE 382
#define ITEM_TOXIC_PLATE 383
#define ITEM_EARTH_PLATE 384
#define ITEM_SKY_PLATE 385
#define ITEM_MIND_PLATE 386
#define ITEM_INSECT_PLATE 387
#define ITEM_STONE_PLATE 388
#define ITEM_SPOOKY_PLATE 389
#define ITEM_DRACO_PLATE 390
#define ITEM_DREAD_PLATE 391
#define ITEM_IRON_PLATE 392
#define ITEM_PIXIE_PLATE 393
#define ITEM_BLANK_PLATE 394
#define ITEM_LEGEND_PLATE 395
#define ITEM_NORMALIUM_Z 396
#define ITEM_FIRIUM_Z 397
#define ITEM_WATERIUM_Z 398
#define ITEM_ELECTRIUM_Z 399
#define ITEM_GRASSIUM_Z 400
#define ITEM_ICIUM_Z 401
#define ITEM_FIGHTINIUM_Z 402
#define ITEM_POISONIUM_Z 403
#define ITEM_GROUNDIUM_Z 404
#define ITEM_FLYINIUM_Z 405
#define ITEM_PSYCHIUM_Z 406
#define ITEM_BUGINIUM_Z 407
#define ITEM_ROCKIUM_Z 408
#define ITEM_GHOSTIUM_Z 409
#define ITEM_DRAGONIUM_Z 410
#define ITEM_DARKINIUM_Z 411
#define ITEM_STEELIUM_Z 412
#define ITEM_FAIRIUM_Z 413

#define G_BATTLE_MONS ((volatile u8 *)0x02023D28)
#define G_BATTLER_SPRITE_IDS ((volatile u8 *)0x02023E88)
#define G_CURRENT_MOVE (*(volatile u16 *)0x02023E8E)
#define G_CHOSEN_MOVE (*(volatile u16 *)0x02023E90)
#define G_BATTLER_ATTACKER (*(volatile u8 *)0x02023EAF)
#define G_BATTLER_TARGET (*(volatile u8 *)0x02023EB0)
#define G_BATTLE_MON_FORMS ((volatile u8 *)0x02024188)
#define G_BATTLER_SPRITES ((volatile u8 *)0x02020630)
#define G_BATTLE_STRUCT_PTR (*(volatile u8 **)0x02024140)
#define G_TYPE_EFFECTIVENESS ((const u8 *)0x082EBB38)

#define BATTLE_MON_SIZE 0x58
#define SPRITE_SIZE_BYTES 0x44
#define ARCEUS_FRONT ((const u8 *)0x0891D000)
#define ARCEUS_BACK ((const u8 *)0x0891E000)
#define ARCEUS_PALETTES ((const u16 *)0x0891E800)

static u16 read16(volatile u8 *p) { return (u16)(p[0] | ((u16)p[1] << 8)); }
static volatile u8 *battle_mon(u8 battler) { return G_BATTLE_MONS + ((u32)battler * BATTLE_MON_SIZE); }

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
static u16 call_Random(void)
{
    typedef u16 (*Fn)(void);
    return ((Fn)0x0802BD8D)();
}

__attribute__((used,noinline))
u8 arceus_form_to_type(u8 form)
{
    static const u8 types[18] = {
        TYPE_NORMAL, TYPE_FIGHTING, TYPE_FLYING, TYPE_POISON, TYPE_GROUND,
        TYPE_ROCK, TYPE_BUG, TYPE_GHOST, TYPE_STEEL, TYPE_FIRE, TYPE_WATER,
        TYPE_GRASS, TYPE_ELECTRIC, TYPE_PSYCHIC, TYPE_ICE, TYPE_DRAGON,
        TYPE_DARK, TYPE_FAIRY
    };
    if (form >= 18) return TYPE_NORMAL;
    return types[form];
}

__attribute__((used,noinline))
u8 arceus_plate_form(u16 item, u8 ruleset)
{
    switch (item) {
    case ITEM_FLAME_PLATE: return FORM_FIRE;
    case ITEM_SPLASH_PLATE: return FORM_WATER;
    case ITEM_ZAP_PLATE: return FORM_ELECTRIC;
    case ITEM_MEADOW_PLATE: return FORM_GRASS;
    case ITEM_ICICLE_PLATE: return FORM_ICE;
    case ITEM_FIST_PLATE: return FORM_FIGHTING;
    case ITEM_TOXIC_PLATE: return FORM_POISON;
    case ITEM_EARTH_PLATE: return FORM_GROUND;
    case ITEM_SKY_PLATE: return FORM_FLYING;
    case ITEM_MIND_PLATE: return FORM_PSYCHIC;
    case ITEM_INSECT_PLATE: return FORM_BUG;
    case ITEM_STONE_PLATE: return FORM_ROCK;
    case ITEM_SPOOKY_PLATE: return FORM_GHOST;
    case ITEM_DRACO_PLATE: return FORM_DRAGON;
    case ITEM_DREAD_PLATE: return FORM_DARK;
    case ITEM_IRON_PLATE: return FORM_STEEL;
    case ITEM_PIXIE_PLATE:
        return ruleset >= RULESET_GEN6 ? FORM_FAIRY : FORM_INVALID;
    case ITEM_BLANK_PLATE:
        return ruleset == RULESET_PLA ? FORM_NORMAL : FORM_INVALID;
    default: return FORM_INVALID;
    }
}

static u8 arceus_z_form(u16 item)
{
    switch (item) {
    case ITEM_NORMALIUM_Z: return FORM_NORMAL;
    case ITEM_FIRIUM_Z: return FORM_FIRE;
    case ITEM_WATERIUM_Z: return FORM_WATER;
    case ITEM_ELECTRIUM_Z: return FORM_ELECTRIC;
    case ITEM_GRASSIUM_Z: return FORM_GRASS;
    case ITEM_ICIUM_Z: return FORM_ICE;
    case ITEM_FIGHTINIUM_Z: return FORM_FIGHTING;
    case ITEM_POISONIUM_Z: return FORM_POISON;
    case ITEM_GROUNDIUM_Z: return FORM_GROUND;
    case ITEM_FLYINIUM_Z: return FORM_FLYING;
    case ITEM_PSYCHIUM_Z: return FORM_PSYCHIC;
    case ITEM_BUGINIUM_Z: return FORM_BUG;
    case ITEM_ROCKIUM_Z: return FORM_ROCK;
    case ITEM_GHOSTIUM_Z: return FORM_GHOST;
    case ITEM_DRAGONIUM_Z: return FORM_DRAGON;
    case ITEM_DARKINIUM_Z: return FORM_DARK;
    case ITEM_STEELIUM_Z: return FORM_STEEL;
    case ITEM_FAIRIUM_Z: return FORM_FAIRY;
    default: return FORM_INVALID;
    }
}

__attribute__((used,noinline))
u8 arceus_held_form(u16 item, u8 ruleset)
{
    u8 form = arceus_plate_form(item, ruleset);
    if (form != FORM_INVALID) return form;
    if (ruleset == RULESET_GEN7) return arceus_z_form(item);
    return FORM_INVALID;
}

static u8 type_multiplier(u8 atk, u8 def)
{
    u32 i;
    if (atk == TYPE_FAIRY) {
        if (def == TYPE_FIGHTING || def == TYPE_DRAGON || def == TYPE_DARK) return 20;
        if (def == TYPE_FIRE || def == TYPE_POISON || def == TYPE_STEEL) return 5;
        return 10;
    }
    if (def == TYPE_FAIRY) {
        if (atk == TYPE_DRAGON) return 0;
        if (atk == TYPE_POISON || atk == TYPE_STEEL) return 20;
        if (atk == TYPE_FIGHTING || atk == TYPE_BUG || atk == TYPE_DARK) return 5;
        return 10;
    }
    for (i = 0; i < 336; i += 3) {
        u8 a = G_TYPE_EFFECTIVENESS[i];
        u8 d = G_TYPE_EFFECTIVENESS[i + 1];
        u8 m = G_TYPE_EFFECTIVENESS[i + 2];
        if (a >= 0xFE) continue;
        if (a == atk && d == def) return m;
    }
    return 10;
}

static u16 offensive_multiplier(u8 atk, u8 d1, u8 d2)
{
    u16 v = type_multiplier(atk, d1);
    if (d2 != d1) v = (u16)((v * type_multiplier(atk, d2)) / 10);
    return v;
}

static u8 better_tuple(u16 off, u8 d1, u8 d2, u16 bestOff, u8 bestD1, u8 bestD2)
{
    if (off != bestOff) return off > bestOff;
    if (d1 != bestD1) return d1 < bestD1;
    return d2 < bestD2;
}

static u8 equal_tuple(u16 off, u8 d1, u8 d2, u16 bestOff, u8 bestD1, u8 bestD2)
{
    return off == bestOff && d1 == bestD1 && d2 == bestD2;
}

__attribute__((used,noinline))
u8 arceus_choose_legend_form(u8 target)
{
    volatile u8 *bm = battle_mon(target);
    u8 target1 = bm[0x21], target2 = bm[0x22];
    u16 bestOff = 0;
    u8 bestD1 = 0xFF, bestD2 = 0xFF;
    u8 form, count = 0, pick;

    for (form = 0; form < 18; form++) {
        u8 type = arceus_form_to_type(form);
        u16 off = offensive_multiplier(type, target1, target2);
        u8 d1 = type_multiplier(target1, type);
        u8 d2 = target2 == target1 ? 10 : type_multiplier(target2, type);
        if (better_tuple(off,d1,d2,bestOff,bestD1,bestD2)) {
            bestOff = off; bestD1 = d1; bestD2 = d2;
        }
    }
    for (form = 0; form < 18; form++) {
        u8 type = arceus_form_to_type(form);
        u16 off = offensive_multiplier(type, target1, target2);
        u8 d1 = type_multiplier(target1, type);
        u8 d2 = target2 == target1 ? 10 : type_multiplier(target2, type);
        if (equal_tuple(off,d1,d2,bestOff,bestD1,bestD2)) count++;
    }
    if (count <= 1) pick = 0;
    else {
        u16 r = call_Random();
        while (r >= count) r -= count;
        pick = (u8)r;
    }
    for (form = 0; form < 18; form++) {
        u8 type = arceus_form_to_type(form);
        u16 off = offensive_multiplier(type, target1, target2);
        u8 d1 = type_multiplier(target1, type);
        u8 d2 = target2 == target1 ? 10 : type_multiplier(target2, type);
        if (equal_tuple(off,d1,d2,bestOff,bestD1,bestD2)) {
            if (pick == 0) return form;
            pick--;
        }
    }
    return FORM_NORMAL;
}

static void set_dynamic_move_type(u8 type)
{
    volatile u8 *bs = G_BATTLE_STRUCT_PTR;
    if (bs != (volatile u8 *)0)
        bs[0x13] = (u8)(type | 0xC0);
}

static void load_arceus_visual(u8 battler, u8 form)
{
    u8 spriteId = G_BATTLER_SPRITE_IDS[battler];
    volatile u8 *sprite = G_BATTLER_SPRITES + ((u32)spriteId * SPRITE_SIZE_BYTES);
    u16 tileNum = read16(sprite + 4) & 0x03FF;
    u8 *dst = (u8 *)(0x06010000 + ((u32)tileNum << 5));
    const u8 *gfx = call_GetBattlerSide(battler) == 0 ? ARCEUS_BACK : ARCEUS_FRONT;
    const u16 *pal = ARCEUS_PALETTES + ((u32)form * 16);
    call_RequestSpriteCopy(gfx, dst, 0x800);
    call_LoadPalette(pal, (u16)(0x100 + ((u16)battler << 4)), 32);
}

__attribute__((used,noinline))
void arceus_set_form(u8 battler, u8 form)
{
    volatile u8 *bm = battle_mon(battler);
    u8 type;
    if (form >= 18) form = FORM_NORMAL;
    type = arceus_form_to_type(form);
    G_BATTLE_MON_FORMS[battler] = form;
    bm[0x21] = type;
    bm[0x22] = type;
    load_arceus_visual(battler, form);
}

__attribute__((used,noinline))
u32 arceus_move_prepare_helper(void)
{
    const u8 ruleset = ARCEUS_RULESET;
    u8 attacker = G_BATTLER_ATTACKER;
    volatile u8 *bm = battle_mon(attacker);
    u16 species = read16(bm);
    u16 item = read16(bm + 0x2E);
    u16 move = G_CURRENT_MOVE;
    u8 form;

    if (species != SPECIES_ARCEUS_TEST)
        return 0;

    if (ruleset == RULESET_PLA) {
        if (item == ITEM_LEGEND_PLATE && move == MOVE_JUDGMENT_TEST && move == G_CHOSEN_MOVE) {
            form = arceus_choose_legend_form(G_BATTLER_TARGET);
            arceus_set_form(attacker, form);
            set_dynamic_move_type(arceus_form_to_type(form));
            return 2;
        }
        form = arceus_plate_form(item, ruleset);
        if (form == FORM_INVALID) form = FORM_NORMAL;
        arceus_set_form(attacker, form);
        if (move == MOVE_JUDGMENT_TEST)
            set_dynamic_move_type(arceus_form_to_type(form));
        return 1;
    }

    form = arceus_held_form(item, ruleset);
    if (form == FORM_INVALID) form = FORM_NORMAL;
    arceus_set_form(attacker, form);

    if (move == MOVE_JUDGMENT_TEST) {
        u8 jform = arceus_plate_form(item, ruleset);
        if (jform == FORM_INVALID) jform = FORM_NORMAL;
        set_dynamic_move_type(arceus_form_to_type(jform));
    }
    return 1;
}

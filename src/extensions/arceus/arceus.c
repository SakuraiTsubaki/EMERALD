#include "global.h"
#include "battle.h"
#include "battle_main.h"
#include "item.h"
#include "pokemon.h"
#include "random.h"
#include "arceus.h"
#include "constants/abilities.h"
#include "constants/items.h"
#include "constants/moves.h"
#include "constants/pokemon.h"

#ifndef TYPE_FAIRY
// Integration must add Fairy to the engine type table. Keeping this fallback
// here documents the intended post-Dark slot without changing stock headers.
#define TYPE_FAIRY 18
#endif

struct ArceusPlateMap
{
    u16 item;
    u8 form;
    u8 minimumRuleset;
};

static const struct ArceusPlateMap sArceusPlateMap[] =
{
    { ITEM_FIST_PLATE,   ARCEUS_FORM_FIGHTING, ARCEUS_RULESET_GEN4 },
    { ITEM_SKY_PLATE,    ARCEUS_FORM_FLYING,   ARCEUS_RULESET_GEN4 },
    { ITEM_TOXIC_PLATE,  ARCEUS_FORM_POISON,   ARCEUS_RULESET_GEN4 },
    { ITEM_EARTH_PLATE,  ARCEUS_FORM_GROUND,   ARCEUS_RULESET_GEN4 },
    { ITEM_STONE_PLATE,  ARCEUS_FORM_ROCK,     ARCEUS_RULESET_GEN4 },
    { ITEM_INSECT_PLATE, ARCEUS_FORM_BUG,      ARCEUS_RULESET_GEN4 },
    { ITEM_SPOOKY_PLATE, ARCEUS_FORM_GHOST,    ARCEUS_RULESET_GEN4 },
    { ITEM_IRON_PLATE,   ARCEUS_FORM_STEEL,    ARCEUS_RULESET_GEN4 },
    { ITEM_FLAME_PLATE,  ARCEUS_FORM_FIRE,     ARCEUS_RULESET_GEN4 },
    { ITEM_SPLASH_PLATE, ARCEUS_FORM_WATER,    ARCEUS_RULESET_GEN4 },
    { ITEM_MEADOW_PLATE, ARCEUS_FORM_GRASS,    ARCEUS_RULESET_GEN4 },
    { ITEM_ZAP_PLATE,    ARCEUS_FORM_ELECTRIC, ARCEUS_RULESET_GEN4 },
    { ITEM_MIND_PLATE,   ARCEUS_FORM_PSYCHIC,  ARCEUS_RULESET_GEN4 },
    { ITEM_ICICLE_PLATE, ARCEUS_FORM_ICE,      ARCEUS_RULESET_GEN4 },
    { ITEM_DRACO_PLATE,  ARCEUS_FORM_DRAGON,   ARCEUS_RULESET_GEN4 },
    { ITEM_DREAD_PLATE,  ARCEUS_FORM_DARK,     ARCEUS_RULESET_GEN4 },
    { ITEM_PIXIE_PLATE,  ARCEUS_FORM_FAIRY,    ARCEUS_RULESET_GEN6_PLUS },
};

static const u8 sArceusFormTypes[ARCEUS_FORM_COUNT] =
{
    [ARCEUS_FORM_NORMAL]   = TYPE_NORMAL,
    [ARCEUS_FORM_FIGHTING] = TYPE_FIGHTING,
    [ARCEUS_FORM_FLYING]   = TYPE_FLYING,
    [ARCEUS_FORM_POISON]   = TYPE_POISON,
    [ARCEUS_FORM_GROUND]   = TYPE_GROUND,
    [ARCEUS_FORM_ROCK]     = TYPE_ROCK,
    [ARCEUS_FORM_BUG]      = TYPE_BUG,
    [ARCEUS_FORM_GHOST]    = TYPE_GHOST,
    [ARCEUS_FORM_STEEL]    = TYPE_STEEL,
    [ARCEUS_FORM_FIRE]     = TYPE_FIRE,
    [ARCEUS_FORM_WATER]    = TYPE_WATER,
    [ARCEUS_FORM_GRASS]    = TYPE_GRASS,
    [ARCEUS_FORM_ELECTRIC] = TYPE_ELECTRIC,
    [ARCEUS_FORM_PSYCHIC]  = TYPE_PSYCHIC,
    [ARCEUS_FORM_ICE]      = TYPE_ICE,
    [ARCEUS_FORM_DRAGON]   = TYPE_DRAGON,
    [ARCEUS_FORM_DARK]     = TYPE_DARK,
    [ARCEUS_FORM_FAIRY]    = TYPE_FAIRY,
};

// Legend Plate battle transformations are battle state, not persistent form
// state. Keep them by side/party slot so switching out and back in preserves
// the most recent Judgment-selected type until the battle ends.
static u8 sLegendBattleForms[2][PARTY_SIZE];

static struct Pokemon *GetBattlerPartyMonForArceus(u8 battler)
{
    if (GetBattlerSide(battler) == B_SIDE_PLAYER)
        return &gPlayerParty[gBattlerPartyIndexes[battler]];
    return &gEnemyParty[gBattlerPartyIndexes[battler]];
}

static u8 GetLegendBattleForm(u8 battler)
{
    return sLegendBattleForms[GetBattlerSide(battler)][gBattlerPartyIndexes[battler]];
}

static void SetLegendBattleForm(u8 battler, u8 form)
{
    sLegendBattleForms[GetBattlerSide(battler)][gBattlerPartyIndexes[battler]] = form;
}

void Arceus_BeginBattle(void)
{
    u8 side;
    u8 i;

    for (side = 0; side < ARRAY_COUNT(sLegendBattleForms); side++)
        for (i = 0; i < PARTY_SIZE; i++)
            sLegendBattleForms[side][i] = ARCEUS_FORM_INVALID;
}

void Arceus_EndBattle(void)
{
    u8 battler;

    for (battler = 0; battler < gBattlersCount; battler++)
    {
        if (gBattleMons[battler].species == SPECIES_ARCEUS)
        {
            gBattleMonForms[battler] = ARCEUS_FORM_NORMAL;
            SET_BATTLER_TYPE(battler, TYPE_NORMAL);
        }
    }

    Arceus_BeginBattle();
}

u8 Arceus_FormToType(u8 form)
{
    if (form == ARCEUS_FORM_MYSTERY_GEN4_INTERNAL)
        return TYPE_MYSTERY;
    if (form >= ARCEUS_FORM_COUNT)
        return TYPE_NORMAL;
    return sArceusFormTypes[form];
}

u8 Arceus_GetPlateForm(u16 item, enum ArceusRuleset ruleset)
{
    u32 i;

    if (ruleset == ARCEUS_RULESET_LEGENDS_ARCEUS && item == ITEM_BLANK_PLATE)
        return ARCEUS_FORM_NORMAL;

    for (i = 0; i < ARRAY_COUNT(sArceusPlateMap); i++)
    {
        if (sArceusPlateMap[i].item == item)
        {
            if (ruleset == ARCEUS_RULESET_GEN4
             && sArceusPlateMap[i].minimumRuleset > ARCEUS_RULESET_GEN4)
                return ARCEUS_FORM_INVALID;
            return sArceusPlateMap[i].form;
        }
    }

    return ARCEUS_FORM_INVALID;
}

u16 Arceus_MakeFormState(u8 form, bool8 legendPlate)
{
    u16 state = form & ARCEUS_FORM_STATE_FORM_MASK;

    if (legendPlate)
        state |= ARCEUS_FORM_STATE_LEGEND_PLATE;
    return state;
}

u8 Arceus_GetPersistentForm(struct Pokemon *mon)
{
    u16 state = GetMonData(mon, MON_DATA_FORM_STATE);
    u8 form = state & ARCEUS_FORM_STATE_FORM_MASK;

    if (form >= ARCEUS_FORM_COUNT)
        return ARCEUS_FORM_NORMAL;
    return form;
}

bool8 Arceus_HasLegendPlateState(struct Pokemon *mon)
{
    return (GetMonData(mon, MON_DATA_FORM_STATE) & ARCEUS_FORM_STATE_LEGEND_PLATE) != 0;
}

bool8 Arceus_UsePlate(struct Pokemon *mon, u16 item, enum ArceusRuleset ruleset)
{
    u8 form;
    u16 state;

    if (ruleset != ARCEUS_RULESET_LEGENDS_ARCEUS
     || GetMonData(mon, MON_DATA_SPECIES) != SPECIES_ARCEUS)
        return FALSE;

    if (item == ITEM_LEGEND_PLATE)
    {
        state = Arceus_MakeFormState(ARCEUS_FORM_NORMAL, TRUE);
        SetMonData(mon, MON_DATA_FORM_STATE, &state);
        return TRUE;
    }

    form = Arceus_GetPlateForm(item, ruleset);
    if (form == ARCEUS_FORM_INVALID)
        return FALSE;

    state = Arceus_MakeFormState(form, FALSE);
    SetMonData(mon, MON_DATA_FORM_STATE, &state);
    return TRUE;
}

static void SetArceusBattleForm(u8 battler, u8 form, bool8 rememberLegendForm)
{
    u8 type;

    if (form >= ARCEUS_FORM_COUNT)
        form = ARCEUS_FORM_NORMAL;

    type = Arceus_FormToType(form);
    gBattleMonForms[battler] = form;
    SET_BATTLER_TYPE(battler, type);

    if (rememberLegendForm)
        SetLegendBattleForm(battler, form);

    // The integration layer reloads the form-specific sprite/palette here.
    // Do not address form N as frame N: stock Emerald only allocates four
    // decompressed frames per battler.
}

void Arceus_ApplyBattleEntryForm(u8 battler, enum ArceusRuleset ruleset)
{
    struct Pokemon *mon;
    u8 form;

    if (gBattleMons[battler].species != SPECIES_ARCEUS)
        return;

    mon = GetBattlerPartyMonForArceus(battler);

    if (ruleset == ARCEUS_RULESET_LEGENDS_ARCEUS)
    {
        if (Arceus_HasLegendPlateState(mon))
        {
            form = GetLegendBattleForm(battler);
            if (form == ARCEUS_FORM_INVALID)
                form = ARCEUS_FORM_NORMAL;
            SetArceusBattleForm(battler, form, TRUE);
        }
        else
        {
            SetArceusBattleForm(battler, Arceus_GetPersistentForm(mon), FALSE);
        }
        return;
    }

    if (gBattleMons[battler].ability != ABILITY_MULTITYPE)
    {
        SetArceusBattleForm(battler, ARCEUS_FORM_NORMAL, FALSE);
        return;
    }

    form = Arceus_GetPlateForm(gBattleMons[battler].item, ruleset);
    if (form == ARCEUS_FORM_INVALID)
        form = ARCEUS_FORM_NORMAL;
    SetArceusBattleForm(battler, form, FALSE);
}

static u8 GetTypeMultiplierSingle(u8 attackingType, u8 defendingType)
{
    s32 i = 0;

    while (TYPE_EFFECT_ATK_TYPE(i) != TYPE_ENDTABLE)
    {
        if (TYPE_EFFECT_ATK_TYPE(i) == attackingType
         && TYPE_EFFECT_DEF_TYPE(i) == defendingType)
            return TYPE_EFFECT_MULTIPLIER(i);
        i += 3;
    }

    return TYPE_MUL_NORMAL;
}

static u16 GetOffensiveMultiplier(u8 attackingType, u8 targetType1, u8 targetType2)
{
    u16 value = GetTypeMultiplierSingle(attackingType, targetType1);

    if (targetType2 != targetType1)
        value = value * GetTypeMultiplierSingle(attackingType, targetType2) / TYPE_MUL_NORMAL;
    return value;
}

static u8 ChooseLegendPlateForm(u8 target)
{
    u8 candidates[ARCEUS_FORM_COUNT];
    u8 candidateCount = 0;
    u8 targetType1 = gBattleMons[target].types[0];
    u8 targetType2 = gBattleMons[target].types[1];
    u16 bestOffense = 0;
    u8 bestPrimaryDefense = 0xFF;
    u8 bestSecondaryDefense = 0xFF;
    u8 form;

    for (form = 0; form < ARCEUS_FORM_COUNT; form++)
    {
        u8 candidateType = Arceus_FormToType(form);
        u16 offense = GetOffensiveMultiplier(candidateType, targetType1, targetType2);
        u8 primaryDefense = GetTypeMultiplierSingle(targetType1, candidateType);
        u8 secondaryDefense = targetType2 == targetType1
                            ? TYPE_MUL_NORMAL
                            : GetTypeMultiplierSingle(targetType2, candidateType);

        if (offense > bestOffense
         || (offense == bestOffense && primaryDefense < bestPrimaryDefense)
         || (offense == bestOffense && primaryDefense == bestPrimaryDefense
          && secondaryDefense < bestSecondaryDefense))
        {
            bestOffense = offense;
            bestPrimaryDefense = primaryDefense;
            bestSecondaryDefense = secondaryDefense;
            candidateCount = 0;
            candidates[candidateCount++] = form;
        }
        else if (offense == bestOffense
              && primaryDefense == bestPrimaryDefense
              && secondaryDefense == bestSecondaryDefense)
        {
            candidates[candidateCount++] = form;
        }
    }

    if (candidateCount == 0)
        return ARCEUS_FORM_NORMAL;
    return candidates[Random() % candidateCount];
}

bool8 Arceus_TryPrepareJudgment(u8 attacker, u8 target, enum ArceusRuleset ruleset)
{
    struct Pokemon *mon;
    u8 form;
    u8 type;

    if (gCurrentMove != MOVE_JUDGMENT)
        return FALSE;

    // Main-series Judgment changes type from the user's Plate even if the user
    // is not Arceus. Legends: Arceus instead derives Judgment from Arceus's
    // active form; a copied Judgment is Normal.
    if (ruleset != ARCEUS_RULESET_LEGENDS_ARCEUS)
    {
        form = Arceus_GetPlateForm(gBattleMons[attacker].item, ruleset);
        if (form == ARCEUS_FORM_INVALID)
            form = ARCEUS_FORM_NORMAL;

        type = Arceus_FormToType(form);
        gBattleStruct->dynamicMoveType =
            type | F_DYNAMIC_TYPE_SET | F_DYNAMIC_TYPE_IGNORE_PHYSICALITY;

        if (gBattleMons[attacker].species == SPECIES_ARCEUS
         && gBattleMons[attacker].ability == ABILITY_MULTITYPE)
            SetArceusBattleForm(attacker, form, FALSE);
        return TRUE;
    }

    if (gBattleMons[attacker].species != SPECIES_ARCEUS)
    {
        gBattleStruct->dynamicMoveType =
            TYPE_NORMAL | F_DYNAMIC_TYPE_SET | F_DYNAMIC_TYPE_IGNORE_PHYSICALITY;
        return TRUE;
    }

    mon = GetBattlerPartyMonForArceus(attacker);
    if (Arceus_HasLegendPlateState(mon))
    {
        form = ChooseLegendPlateForm(target);
        SetArceusBattleForm(attacker, form, TRUE);
    }
    else
    {
        form = gBattleMonForms[attacker];
        if (form >= ARCEUS_FORM_COUNT)
            form = Arceus_GetPersistentForm(mon);
    }

    type = Arceus_FormToType(form);
    gBattleStruct->dynamicMoveType =
        type | F_DYNAMIC_TYPE_SET | F_DYNAMIC_TYPE_IGNORE_PHYSICALITY;
    return TRUE;
}

void Arceus_ResetBattleForm(u8 battler)
{
    if (gBattleMons[battler].species == SPECIES_ARCEUS)
    {
        gBattleMonForms[battler] = ARCEUS_FORM_NORMAL;
        SET_BATTLER_TYPE(battler, TYPE_NORMAL);
    }
}

#include "global.h"
#include "battle.h"
#include "pokemon.h"
#include "aegislash.h"
#include "constants/abilities.h"
#include "constants/moves.h"
#include "constants/pokemon.h"

struct AegislashFormStats
{
    u8 attack;
    u8 defense;
    u8 spAttack;
    u8 spDefense;
};

static const struct AegislashFormStats sAegislashFormStats[] =
{
    [AEGISLASH_FORM_SHIELD] = { 50, 150,  50, 150 },
    [AEGISLASH_FORM_BLADE]  = {150,  50, 150,  50 },
};

static struct Pokemon *GetBattlerPartyMonForAegislash(u8 battler)
{
    if (GetBattlerSide(battler) == B_SIDE_PLAYER)
        return &gPlayerParty[gBattlerPartyIndexes[battler]];
    else
        return &gEnemyParty[gBattlerPartyIndexes[battler]];
}

static u16 CalcAegislashBattleStat(u8 baseStat, u8 iv, u8 ev, u8 level, u8 nature, u8 statIndex)
{
    u16 stat = (((2 * baseStat + iv + ev / 4) * level) / 100) + 5;
    return ModifyStatByNature(nature, stat, statIndex);
}

static void ApplyAegislashFormStats(u8 battler, u8 form)
{
    struct Pokemon *mon = GetBattlerPartyMonForAegislash(battler);
    const struct AegislashFormStats *formStats = &sAegislashFormStats[form];
    u8 nature = GetNature(mon);
    u8 level = gBattleMons[battler].level;

    gBattleMons[battler].attack = CalcAegislashBattleStat(
        formStats->attack,
        gBattleMons[battler].attackIV,
        GetMonData(mon, MON_DATA_ATK_EV),
        level,
        nature,
        STAT_ATK);

    gBattleMons[battler].defense = CalcAegislashBattleStat(
        formStats->defense,
        gBattleMons[battler].defenseIV,
        GetMonData(mon, MON_DATA_DEF_EV),
        level,
        nature,
        STAT_DEF);

    gBattleMons[battler].spAttack = CalcAegislashBattleStat(
        formStats->spAttack,
        gBattleMons[battler].spAttackIV,
        GetMonData(mon, MON_DATA_SPATK_EV),
        level,
        nature,
        STAT_SPATK);

    gBattleMons[battler].spDefense = CalcAegislashBattleStat(
        formStats->spDefense,
        gBattleMons[battler].spDefenseIV,
        GetMonData(mon, MON_DATA_SPDEF_EV),
        level,
        nature,
        STAT_SPDEF);
}

static bool8 IsDirectlySelectedMove(void)
{
    // Called-move paths such as Sleep Talk must not trigger Stance Change.
    return gCurrentMove == gChosenMove;
}

static bool8 IsDamagingMove(u16 move)
{
    // Emerald gives fixed-damage/counter-style moves power 1; status moves use 0.
    return gBattleMoves[move].power != 0;
}

void Aegislash_SetBattleForm(u8 battler, u8 form)
{
    if (form > AEGISLASH_FORM_BLADE)
        return;

    if (gBattleMonForms[battler] == form)
        return;

    gBattleMonForms[battler] = form;
    ApplyAegislashFormStats(battler, form);

    // Presentation refresh belongs to the integration hook:
    // Shield front = frames 0/1, Blade front = frames 2/3;
    // back = 0/1. Reload the form-specific palette as well.
}

void Aegislash_ResetBattleForm(u8 battler)
{
    if (gBattleMons[battler].species == SPECIES_AEGISLASH)
        Aegislash_SetBattleForm(battler, AEGISLASH_FORM_SHIELD);
}

bool8 Aegislash_TryStanceChange(u8 battler)
{
    u8 targetForm;

    if (gBattleMons[battler].species != SPECIES_AEGISLASH
     || gBattleMons[battler].ability != ABILITY_STANCE_CHANGE
     || gBattleMons[battler].hp == 0
     || !IsDirectlySelectedMove())
        return FALSE;

    if (gCurrentMove == MOVE_KINGS_SHIELD)
        targetForm = AEGISLASH_FORM_SHIELD;
    else if (IsDamagingMove(gCurrentMove))
        targetForm = AEGISLASH_FORM_BLADE;
    else
        return FALSE;

    if (gBattleMonForms[battler] == targetForm)
        return FALSE;

    Aegislash_SetBattleForm(battler, targetForm);
    return TRUE;
}

bool8 Aegislash_KingsShieldContactPenaltyApplies(u8 attacker, u8 defender, u16 move)
{
    (void)attacker;

    return gProtectStructs[defender].kingsShielded
        && (gBattleMoves[move].flags & FLAG_MAKES_CONTACT)
        && (gBattleMoves[move].flags & FLAG_PROTECT_AFFECTED)
        && gBattleMoves[move].power != 0;
}

#ifndef GUARD_ARCEUS_H
#define GUARD_ARCEUS_H

#include "global.h"

struct Pokemon;

enum ArceusRuleset
{
    ARCEUS_RULESET_GEN4 = 0,
    ARCEUS_RULESET_GEN6_PLUS,
    ARCEUS_RULESET_LEGENDS_ARCEUS,
};

enum ArceusForm
{
    ARCEUS_FORM_NORMAL = 0,
    ARCEUS_FORM_FIGHTING,
    ARCEUS_FORM_FLYING,
    ARCEUS_FORM_POISON,
    ARCEUS_FORM_GROUND,
    ARCEUS_FORM_ROCK,
    ARCEUS_FORM_BUG,
    ARCEUS_FORM_GHOST,
    ARCEUS_FORM_STEEL,
    ARCEUS_FORM_FIRE,
    ARCEUS_FORM_WATER,
    ARCEUS_FORM_GRASS,
    ARCEUS_FORM_ELECTRIC,
    ARCEUS_FORM_PSYCHIC,
    ARCEUS_FORM_ICE,
    ARCEUS_FORM_DRAGON,
    ARCEUS_FORM_DARK,
    ARCEUS_FORM_FAIRY,

    ARCEUS_FORM_COUNT,
    ARCEUS_FORM_MYSTERY_GEN4_INTERNAL = ARCEUS_FORM_COUNT,
    ARCEUS_FORM_INVALID = 0xFF,
};

#define ARCEUS_FORM_STATE_FORM_MASK       0x001F
#define ARCEUS_FORM_STATE_LEGEND_PLATE    0x0020

void Arceus_BeginBattle(void);
void Arceus_EndBattle(void);

u8 Arceus_FormToType(u8 form);
u8 Arceus_GetPlateForm(u16 item, enum ArceusRuleset ruleset);

u16 Arceus_MakeFormState(u8 form, bool8 legendPlate);
u8 Arceus_GetPersistentForm(struct Pokemon *mon);
bool8 Arceus_HasLegendPlateState(struct Pokemon *mon);
bool8 Arceus_UsePlate(struct Pokemon *mon, u16 item, enum ArceusRuleset ruleset);

void Arceus_ApplyBattleEntryForm(u8 battler, enum ArceusRuleset ruleset);
bool8 Arceus_TryPrepareJudgment(u8 attacker, u8 target, enum ArceusRuleset ruleset);
void Arceus_ResetBattleForm(u8 battler);

#endif // GUARD_ARCEUS_H

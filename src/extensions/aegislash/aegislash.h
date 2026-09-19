#ifndef GUARD_AEGISLASH_H
#define GUARD_AEGISLASH_H

#include "global.h"

enum AegislashBattleForm
{
    AEGISLASH_FORM_SHIELD = 0,
    AEGISLASH_FORM_BLADE = 1,
};

bool8 Aegislash_TryStanceChange(u8 battler);
void Aegislash_SetBattleForm(u8 battler, u8 form);
void Aegislash_ResetBattleForm(u8 battler);
bool8 Aegislash_KingsShieldContactPenaltyApplies(u8 attacker, u8 defender, u16 move);

#endif // GUARD_AEGISLASH_H

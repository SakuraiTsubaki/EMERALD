#ifndef GUARD_MORPEKO_H
#define GUARD_MORPEKO_H

#include "global.h"

enum MorpekoBattleForm
{
    MORPEKO_FORM_FULL_BELLY = 0,
    MORPEKO_FORM_HANGRY = 1,
};

bool8 Morpeko_TryHungerSwitch(u8 battler, u8 effectiveAbility);
void Morpeko_SetBattleForm(u8 battler, u8 form);
void Morpeko_ResetBattleForm(u8 battler);
bool8 Morpeko_CanUseAuraWheel(u8 battler);
u8 Morpeko_GetAuraWheelType(u8 battler, u8 effectiveAbility);

#endif // GUARD_MORPEKO_H

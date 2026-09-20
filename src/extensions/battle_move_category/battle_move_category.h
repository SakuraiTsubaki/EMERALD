#ifndef GUARD_BATTLE_MOVE_CATEGORY_H
#define GUARD_BATTLE_MOVE_CATEGORY_H

#include "global.h"

enum BattleMoveCategory
{
    BATTLE_MOVE_CATEGORY_PHYSICAL = 0,
    BATTLE_MOVE_CATEGORY_SPECIAL,
    BATTLE_MOVE_CATEGORY_STATUS,
};

u8 GetBattleMoveCategory(u16 move, u8 effectiveType);

#endif // GUARD_BATTLE_MOVE_CATEGORY_H

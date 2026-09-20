#include "global.h"
#include "battle.h"
#include "battle_move_category.h"
#include "constants/moves.h"

u8 GetBattleMoveCategory(u16 move, u8 effectiveType)
{
    // Modern moves can override Emerald's type-based physical/special split
    // without changing the 12-byte struct BattleMove layout used by the
    // BPEJ runtime work.
    if (move == MOVE_JUDGMENT)
        return BATTLE_MOVE_CATEGORY_SPECIAL;

    if (gBattleMoves[move].power == 0)
        return BATTLE_MOVE_CATEGORY_STATUS;

    if (IS_TYPE_PHYSICAL(effectiveType))
        return BATTLE_MOVE_CATEGORY_PHYSICAL;

    return BATTLE_MOVE_CATEGORY_SPECIAL;
}

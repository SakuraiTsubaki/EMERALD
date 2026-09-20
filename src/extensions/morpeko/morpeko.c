#include "global.h"
#include "battle.h"
#include "morpeko.h"
#include "constants/abilities.h"
#include "constants/battle.h"
#include "constants/pokemon.h"
#include "constants/types.h"

static bool8 IsMorpekoBattleSpecies(u8 battler)
{
    // A transformed Pokémon copies the target species in battle and is therefore
    // allowed to use Aura Wheel, but Hunger Switch itself must not toggle it.
    return gBattleMons[battler].species == SPECIES_MORPEKO;
}

void Morpeko_SetBattleForm(u8 battler, u8 form)
{
    if (!IsMorpekoBattleSpecies(battler))
        return;

    if (form > MORPEKO_FORM_HANGRY)
        return;

    if (gBattleMonForms[battler] == form)
        return;

    gBattleMonForms[battler] = form;

    // Morpeko's base stats and Electric/Dark typing do not change between forms.
    // The integration layer only needs to refresh the active sprite/palette.
}

void Morpeko_ResetBattleForm(u8 battler)
{
    if (IsMorpekoBattleSpecies(battler))
        Morpeko_SetBattleForm(battler, MORPEKO_FORM_FULL_BELLY);
}

bool8 Morpeko_TryHungerSwitch(u8 battler, u8 effectiveAbility)
{
    u8 targetForm;

    if (!IsMorpekoBattleSpecies(battler)
     || effectiveAbility != ABILITY_HUNGER_SWITCH
     || gBattleMons[battler].hp == 0
     || (gBattleMons[battler].status2 & STATUS2_TRANSFORMED))
        return FALSE;

    if (gBattleMonForms[battler] == MORPEKO_FORM_HANGRY)
        targetForm = MORPEKO_FORM_FULL_BELLY;
    else
        targetForm = MORPEKO_FORM_HANGRY;

    Morpeko_SetBattleForm(battler, targetForm);
    return TRUE;
}

bool8 Morpeko_CanUseAuraWheel(u8 battler)
{
    // This intentionally accepts a Pokémon transformed into Morpeko.
    return IsMorpekoBattleSpecies(battler);
}

u8 Morpeko_GetAuraWheelType(u8 battler, u8 effectiveAbility)
{
    // Normalize overrides Aura Wheel's form-derived Electric/Dark typing.
    if (effectiveAbility == ABILITY_NORMALIZE)
        return TYPE_NORMAL;

    if (IsMorpekoBattleSpecies(battler)
     && gBattleMonForms[battler] == MORPEKO_FORM_HANGRY)
        return TYPE_DARK;

    return TYPE_ELECTRIC;
}

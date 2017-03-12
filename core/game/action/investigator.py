from core.game.action.common import ApplyEffectAction
from core.game.common import Step
from core.game.effects.common import CantPlayActionEffect
from core.game.effects.investigator import RoundUpEffect, InvestigationEffect


class RoundUp(ApplyEffectAction):
    mana_cost = None
    cooldown = 2
    turn_step = Step.DAY_ACTIVE_STEP

    effects = [
        ApplyEffectAction.effect(CantPlayActionEffect, {}, 'executor', {'turns': 1}),
        ApplyEffectAction.effect(RoundUpEffect)]

    name = 'round_up'


class Investigation(ApplyEffectAction):
    mana_cost = None
    cooldown = 1
    turn_step = Step.DAY_ACTIVE_STEP

    effects = [
        ApplyEffectAction.effect(CantPlayActionEffect, {}, 'executor', {'turns': 1}),
        ApplyEffectAction.effect(InvestigationEffect, {'investigator': 'executor'})]

    name = 'investigation'

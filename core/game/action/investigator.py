from core.game.action.arguments import CharacterArgument
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
    arguments = [CharacterArgument]
    description = """
        This night target will be damaged by 2 points during a round-up.
        You can't do your basic attack this night.
    """


class Investigation(ApplyEffectAction):
    mana_cost = None
    cooldown = 1
    turn_step = Step.DAY_ACTIVE_STEP


    effects = [
        ApplyEffectAction.effect(CantPlayActionEffect, {}, 'executor', {'turns': 1}),
        ApplyEffectAction.effect(InvestigationEffect, {'investigator': 'executor'})]

    name = 'investigation'
    arguments = [CharacterArgument]
    description = """
        You will find out the target's role by the next morning.
        You can't do your basic attack this night.
    """
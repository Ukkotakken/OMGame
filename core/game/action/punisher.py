from core.game.action.common import Action, ApplyEffectAction
from core.game.common import Step, GuiltyDegree
from core.game.effects.common import CantPlayActionEffect
from core.game.effects.punisher import BloodhoundEffect, PunishmentEffect
from core.game.events.common import VoteEvent


class PunisherVote(Action):
    turn_step = Step.DAY_VOTE_STEP
    can_cancel = False

    name = 'vote'

    def __init__(self, caller, executor, target, victim=None):
        super().__init__(caller, executor, target)
        if victim:
            guilty_degree = executor.find_guilty_degree(target, victim)
        else:
            guilty_degree = executor.guilty_degrees.get(target)
        self.strength = self.executor.vote_strength
        if guilty_degree is GuiltyDegree.DAMAGED:
            self.strength += 1
        if guilty_degree is GuiltyDegree.KILLED:
            self.strength += 2


    def play(self, game):
        self.target.add_votes(self.strength)
        game.log(VoteEvent(self))


class Punishment(ApplyEffectAction):
    turn_step = Step.DAY_ACTIVE_STEP
    mana_cost = 1

    name = 'Punishment'

    effects = [ApplyEffectAction.effect(PunishmentEffect, {'punisher': 'executor'})]


class Bloodhound(ApplyEffectAction):
    mana_cost = 1
    turn_step = Step.DAY_ACTIVE_STEP

    effects = [
        ApplyEffectAction.effect(CantPlayActionEffect, {}, 'executor', {'turns': 1}),
        ApplyEffectAction.effect(BloodhoundEffect, {'punisher': 'executor'})]

    name = 'bloodhound'

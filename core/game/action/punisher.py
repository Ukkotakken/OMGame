from core.game.action.arguments import CharacterArgument
from core.game.action.common import Action, ApplyEffectAction
from core.game.common import Step, GuiltyDegree
from core.game.effects.common import CantPlayActionEffect
from core.game.effects.punisher import BloodhoundEffect, PunishmentEffect
from core.game.events.common import VoteEvent


class PunisherVote(Action):
    turn_step = Step.DAY_VOTE_STEP
    can_cancel = False

    name = 'vote'
    arguments = [
        CharacterArgument('target_player_id', 'target'), CharacterArgument('victim_player_id', 'victim')]
    description = """
        Your vote is special. When you vote against someone who damaged/killed someone, you get + 1/2 to your vote strength.
        You should specify the victim, though, but by default info of your bloodhound plays is used.
    """

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

    name = 'punishment'
    arguments = [
        CharacterArgument('target_player_id'), CharacterArgument('victim_player_id')]
    description = """
        If target character killed victim you will damage him directly (ignoring any additional protection) by 1 point.
        During magic power turn, you will damage her by 2 points if she killed victim, and by 1 point if she damaged him.
        If target is innocent, you will be banished from class and would never be able to use your abilities again.
    """


    effects = [ApplyEffectAction.effect(PunishmentEffect, {'punisher': 'executor'})]


class Bloodhound(ApplyEffectAction):
    mana_cost = 1
    turn_step = Step.DAY_ACTIVE_STEP
    arguments = [CharacterArgument()]
    description = """
        You will find everybody who attacked or damaged the target during the night.
        If target is killed and it is magic turn, you will know the roles of the killers.
    """

    effects = [
        ApplyEffectAction.effect(CantPlayActionEffect, {}, 'executor', {'turns': 1}),
        ApplyEffectAction.effect(BloodhoundEffect, {'punisher': 'executor'})]

    name = 'bloodhound'

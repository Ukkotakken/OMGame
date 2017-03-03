from abc import ABCMeta, abstractmethod

from core.game.common import Step
from core.game.events.common import VoteEvent


class Action:
    __metaclass__ = ABCMeta

    mana_cost = None
    cooldown = 0
    can_cancel = True

    def __init__(self, caller, executor, target):
        self.caller = caller
        self.executor = executor
        self.target = target

    @abstractmethod
    def play(self, game):
        pass

    def play_user_visible_effect(self, character):
        pass

    __hash__ = None

    def __eq__(self, other):
        if hasattr(other, '__dict__'):
            return self.__dict__ == other.__dict__
        return False


class Vote(Action):
    turn_step = Step.DAY_VOTE_STEP
    can_cancel = False

    name = 'vote'

    def play(self, game):
        self.target.add_votes(self.executor.vote_strength)
        game.log(VoteEvent(self))


class BaseAttack(Action):
    turn_step = Step.NIGHT_ACTIVE_STEP

    name = 'base_attack'

    def play(self, game):
        self.target.receive_damage(
            strength=self.executor.attack_strength,
            type=self.executor.attack_type,
            action=self)

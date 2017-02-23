from abc import ABCMeta, abstractmethod

from core.game.common import Step
from core.game.events.common import VoteEvent


class Action:
    __metaclass__ = ABCMeta

    mana_cost = 0
    cooldown = 0
    can_cancel = True

    def __init__(self, caller, executor, target):
        self.caller = caller
        self.executor = executor
        self.target = target

    def play(self, game):
        if self.executor.can_play(self):
            self._play(game)
            self.executor.set_action_played(self, game)
        else:
            # TODO(ukkotakken): Do failover event (to which player?).
            pass

    @abstractmethod
    def _play(self, game):
        pass

    def play_user_visible_effect(self, character):
        pass


class Vote(Action):
    turn_step = Step.DAY_VOTE_STEP
    can_cancel = False

    def _play(self, game):
        self.target.add_votes(self.executor.vote_strength)
        game.log(VoteEvent(self))


class BaseAttack(Action):
    turn_step = Step.NIGHT_ACTIVE_STEP

    def _play(self, game):
        self.target.receive_damage(
            strength=self.executor.attack_strength,
            type=self.executor.attack_type,
            action=self)

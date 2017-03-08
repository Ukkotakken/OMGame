import inspect
from abc import ABCMeta, abstractmethod

from core.game.common import Step
from core.game.events.common import VoteEvent


class ActionBase:
    def __init__(self, caller, executor, target):
        self.caller = caller
        self.executor = executor
        self.target = target

    __hash__ = None

    def __eq__(self, other):
        return other.__class__ is self.__class__ and self.__dict__ == other.__dict__


class Action(ActionBase):
    __metaclass__ = ABCMeta

    mana_cost = None
    cooldown = 0
    can_cancel = True

    @property
    def turn_step(self):
        raise NotImplementedError("Action subclasses should have turn step setted!")

    @abstractmethod
    def play(self, game):
        pass

    def play_user_visible_effect(self, character):
        pass

    def can_play_check(self, character):
        return True


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


class ApplyEffectAction(Action):
    # Effects in format (class, kw_mapping, target, defaults)
    @property
    def effects(self):
        raise NotImplementedError("ApplyEffectAction subclasses should have effect setted!")

    @staticmethod
    def effect(effect, kw_mapping=None, target='target', defaults=None):
        return effect, kw_mapping or {}, target, defaults or {}

    def __init__(self, caller, executor, target, **kwargs):
        super().__init__(caller, executor, target)
        kwargs['self'] = self
        kwargs['caller'] = caller
        kwargs['executor'] = executor
        kwargs['target'] = target
        self.kwargs = kwargs # TODO(ukkotakken): Save it only in test enviroment
        self.effect_target_and_args = []
        for effect, kw_mapping, effect_target, defaults in self.effects:
            effect_signature = inspect.signature(effect)
            kw = {k: v for k, v in kwargs.items() if k in effect_signature.parameters}
            kw_update = {k: kwargs[v] for k, v in kw_mapping.items()
                         if v in kwargs and k in effect_signature.parameters}
            for k in kw_mapping:
                if k in kw:
                    del kw[k]
            kw.update(kw_update)
            for k in defaults:
                if k not in kw:
                    kw[k] = defaults[k]
            bind = effect_signature.bind(**kw)
            self.effect_target_and_args.append((kwargs.get(effect_target), effect, bind.args, bind.kwargs))
        del self.kwargs['self']

    def play(self, game):
        for target, effect, args, kwargs in self.effect_target_and_args:
            target.add_effect(effect(*args, **kwargs))

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return False
        if other.effects != self.effects:
            return False
        return self.kwargs == other.kwargs

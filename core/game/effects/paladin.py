from core.game.action.common import ActionBase
from core.game.common import DamageType, TurnType
from core.game.effects.common import CharacterEffect, TimedCharacterEffect
from core.game.effects.priorities import EffectPriority
from core.game.events.common import DamageEvent
from core.game.events.investigator import InvestigationEvent, AwarenessEvent
from core.game.turn import DayTurn, NightTurn


class RetributionDamageAction(ActionBase):
    pass


class RetributionEffect(CharacterEffect):
    priority = EffectPriority.RECEIVE_DAMAGE_AFTER_DAMAGE_PRIORITY

    def receive_damage(self, character, strength, type, action):
        result = character.receive_damage(strength, type, action)
        if action.executor is not None:
            action.executor.receive_damage(1, DamageType.PHISICAL, RetributionDamageAction)
        return result


class DivineShieldEffect(TimedCharacterEffect):
    priority = EffectPriority.RECEIVE_DAMAGE_ABSORB_PRIORITY

    def __init__(self):
        self.strength = None
        super().__init__(1)

    def __init_strength(self, turn_type):
        if turn_type is TurnType.DIVINE_POWER:
            self.strength = 10
        else:
            self.strength = 2

    def receive_damage(self, character, strength, type, action):
        if self.strength is None:
            self.__init_strength(character.game.turn.turn_type)
        if strength > self.strength:
            strength -= self.strength
            self.strength = 0
            return character.receive_damage(strength, type, action)
        else:
            self.strength -= strength


class BodyguardEffect(TimedCharacterEffect):
    priority = EffectPriority.RECEIVE_DAMAGE_CHANGE_TARGET_PRIORITY

    def __init__(self, bodyguard):
        self.bodyguard = bodyguard
        super().__init__(1)

    def receive_damage(self, character, strength, type, action):
        return self.bodyguard.receive_damage(strength, type, action)


class SoulSaveEffect(TimedCharacterEffect):
    priority = EffectPriority.IMPRISON_CANCEL_PRIORITY

    def imprison(self, character):
        if not (character.caused_damage or character.killed):
            return
        character.imprison()
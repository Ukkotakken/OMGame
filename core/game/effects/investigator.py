from core.game.action.common import ActionBase
from core.game.common import DamageType
from core.game.effects.common import CharacterEffect, TimedCharacterEffect
from core.game.effects.priorities import EffectPriority
from core.game.events.investigator import InvestigationEvent, AwarenessEvent
from core.game.turn import DayTurn


class AwarenessEffect(CharacterEffect):
    priority = EffectPriority.TURN_START_INFO_PRIORITY

    def on_turn_start(self, character, turn):
        if turn.__class__ is DayTurn:
            character.game.log(AwarenessEvent(character))
        character.on_turn_start(turn)


class RoundUpDamageAction(ActionBase):
    pass


class RoundUpEffect(TimedCharacterEffect):
    priority = EffectPriority.TURN_END_DAMAGE_PRIORITY

    def __init__(self, caller):
        super().__init__(1)
        self.caller = caller

    def on_turn_end(self, character, turn):
        character.receive_damage(character, 2, DamageType.PHISICAL, RoundUpDamageAction(self.caller, None, character))


class InvestigationEffect(TimedCharacterEffect):
    priority = EffectPriority.TURN_START_INFO_PRIORITY

    def __init__(self, target):
        super().__init__(2)
        self.target = target

    def on_turn_start(self, character, turn):
        if turn.__class__ is DayTurn:
            character.game.log(InvestigationEvent(character, self.target))

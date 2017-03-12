from core.game.action.common import ActionBase
from core.game.common import DamageType
from core.game.effects.common import CharacterEffect, TimedCharacterEffect
from core.game.effects.priorities import EffectPriority
from core.game.events.common import DamageEvent
from core.game.events.investigator import InvestigationEvent, AwarenessEvent
from core.game.turn import DayTurn, NightTurn


class AwarenessEffect(CharacterEffect):
    priority = EffectPriority.TURN_START_INFO_PRIORITY

    def on_turn_start(self, character, turn):
        if turn.__class__ is DayTurn:
            damage_effects = [e for e in character.game.new_events
                              if e.__class__ is DamageEvent]
            character.game.log(AwarenessEvent(character, damage_effects))
        character.on_turn_start(turn)


class RoundUpDamageAction(ActionBase):
    pass


class RoundUpEffect(TimedCharacterEffect):
    priority = EffectPriority.TURN_END_DAMAGE_PRIORITY

    def __init__(self, caller):
        super().__init__(1)
        self.caller = caller

    def on_turn_end(self, character, turn):
        if turn.__class__ is NightTurn:
            character.receive_damage(2, DamageType.PHISICAL, RoundUpDamageAction(self.caller, None, character))


class InvestigationEffect(TimedCharacterEffect):
    priority = EffectPriority.TURN_START_INFO_PRIORITY

    def __init__(self, investigator):
        super().__init__(2)
        self.investigator = investigator

    def on_turn_start(self, character, turn):
        if turn.__class__ is DayTurn:
            character.game.log(InvestigationEvent(self.investigator, character))
        character.on_turn_start(turn)

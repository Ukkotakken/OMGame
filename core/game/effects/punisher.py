from core.game.effects.common import CharacterEffect, pipe_argument
from core.game.effects.priorities import EffectPriority
from core.game.events.common import DamageEvent
from core.game.events.punisher import PenanceEvent
from core.game.turn import DayTurn


class Penance(CharacterEffect):
    priority = EffectPriority.TURN_END_INFO_PRIORITY

    def on_kill(self, character, killed_character):
        character.game.log(PenanceEvent(character, killed_character))
        character.on_kill(killed_character)
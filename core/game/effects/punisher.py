from core.game.effects.common import CharacterEffect, pipe_argument
from core.game.events.common import DamageEvent
from core.game.turn import DayTurn


class Penance(CharacterEffect):
    priority = None

    def after__turn_end(self, character, _, turn):
        if not isinstance(turn, DayTurn):
            return pipe_argument(turn)
        attack_targets = [
            e.action.target for e in character.game.new_events
            if isinstance(e, DamageEvent)
               and e.action.target is not None
               and e.action.executor is character]
        for c in attack_targets:
            if c.dies(): character.game.log(PenanceEvent(c))



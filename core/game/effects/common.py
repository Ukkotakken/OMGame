from core.game.effects.priorities import EffectPriority
from core.game.turn import DayTurn


def pipe_argument(*args, **kwargs):
    return None, (args, kwargs)


def pipe_value(value):
    return value, None


class CharacterEffect:
    @property
    def priority(self):
        raise NotImplementedError("Subclasses should implement this!")

    def __lt__(self, other):
        return self.priority < other.priority

    def passed(self):
        return False


class ReceiveManaEffect(CharacterEffect):
    priority = EffectPriority.RECEIVE_MANA_PRIORITY

    def __init__(self, mana_table):
        """mana_table is a dict turn_type -> mana_amount"""
        self.mana_table = mana_table

    def turn_start(self, character, turn):
        if turn.__class__ is DayTurn:
            character.mana += self.mana_table[turn.turn_type]
        character.turn_start(turn)

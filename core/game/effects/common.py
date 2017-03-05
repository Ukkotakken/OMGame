from core.game.effects.priorities import EffectPriority
from core.game.turn import DayTurn


def pipe_argument(*args, **kwargs):
    return None, (args, kwargs)


def pipe_value(value):
    return value, None


class CharacterEffect:
    @property
    def priority(self):
        raise NotImplementedError("CharacterEffect subclasses should have priority setted!")

    def __lt__(self, other):
        return self.priority < other.priority

    def passed(self):
        return False


class TimedCharacterEffect(CharacterEffect):
    def __init__(self, turns=None):
        self.turns = turns

    def on_turn_start(self, character, turn):
        if self.turns is not None:
            self.turns -= 1
        character.on_turn_start(turn)

    def passed(self):
        return self.turns is not None and self.turns <= -1


class ReceiveManaEffect(CharacterEffect):
    priority = EffectPriority.RECEIVE_MANA_PRIORITY

    def __init__(self, mana_table):
        """mana_table is a dict turn_type -> mana_amount"""
        self.mana_table = mana_table

    def on_turn_start(self, character, turn):
        if turn.__class__ is DayTurn:
            character.mana += self.mana_table[turn.turn_type]
        character.on_turn_start(turn)


class CantPlayActionEffect(TimedCharacterEffect):
    priority = EffectPriority.CAN_PLAY_CANCELING_PRIORITY

    def can_play(self, character, action):
        return False
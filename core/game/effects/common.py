from core.game.turn import DayTurn


def pipe_argument(*args, **kwargs):
    return None, args, kwargs


def pipe_value(value):
    return value, None


class CharacterEffect:
    pass


class ReceiveManaEffect(CharacterEffect):
    def __init__(self, mana_table):
        """mana_table is a dict turn_type -> mana_amount"""
        self.mana_table = mana_table

    def before__turn_starts(self, character, turn):
        if turn.__class__ is DayTurn:
            character.mana += self.mana_table[turn.turn_type]
        return pipe_argument(turn=turn)

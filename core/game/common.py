from enum import Enum, unique


@unique
class DamageType(Enum):
    PHISICAL = 1
    BURNING = 2
    INTERNAL = 3
    BLOODY_MESS = 4


@unique
class State(Enum):
    ALIVE = 1
    DEAD = 2
    IMPRISONED = 3


@unique
class Sides(Enum):
    SIDE_123 = 1
    SIDE_236 = 2
    SIDE_369 = 3
    SIDE_689 = 4
    SIDE_789 = 5
    SIDE_478 = 6
    SIDE_147 = 7
    SIDE_124 = 8
    # Chosen one sides
    SIDE_456_AGENT = 9
    SIDE_258_TEURG = 10
    # Judge side
    SIDE_159_JUDGE = 11
    SIDE_10_PSYCHO = 12


@unique
class TurnType(Enum):
    MAGIC_POWER = 1
    DIVINE_POWER = 2


@unique
class Step(Enum):
    DAY_PASSIVE_STEP = "DAY_PASSIVE_STEP"
    DAY_ACTIVE_STEP = "DAY_ACTIVE_STEP"
    DAY_VOTE_STEP = "DAY_VOTE_STEP"
    NIGHT_PASSIVE_STEP = "NIGHT_PASSIVE_STEP"
    NIGHT_ACTIVE_STEP = "NIGHT_ACTIVE_STEP"


class GuiltyDegree(Enum):
    NO_GUILTY = 0
    DAMAGED = 1
    KILLED = 2
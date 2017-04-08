class DamageType:
    PHISICAL = 'PHISICAL'
    BURNING = 'BURNING'
    INTERNAL = 'INTERNAL'
    BLOODY_MESS = 'BLOODY_MESS'


class State:
    ALIVE = 'ALIVE'
    DEAD = 'DEAD'
    IMPRISONED = 'IMPRISONED'


class TimeOfDay:
    DAY = "Day"
    NIGHT = "Night"


class Sides:
    SIDE_123 = '123'
    SIDE_236 = '236'
    SIDE_369 = '369'
    SIDE_689 = '689'
    SIDE_789 = '789'
    SIDE_478 = '478'
    SIDE_147 = '147'
    SIDE_124 = '124'
    # Chosen one sides
    SIDE_456_AGENT = '456'
    SIDE_258_TEURG = '258'
    # Judge side
    SIDE_159_JUDGE = '159'
    SIDE_10_PSYCHO = '0'


class TurnType:
    MAGIC_POWER = "MAGIC"
    DIVINE_POWER = "DIVINE"


class Step:
    DAY_PASSIVE_STEP = "DAY_PASSIVE_STEP"
    DAY_ACTIVE_STEP = "DAY_ACTIVE_STEP"
    DAY_VOTE_STEP = "DAY_VOTE_STEP"
    NIGHT_PASSIVE_STEP = "NIGHT_PASSIVE_STEP"
    NIGHT_ACTIVE_STEP = "NIGHT_ACTIVE_STEP"


class GuiltyDegree:
    NO_GUILTY = "NO_GUILTY"
    DAMAGED = "DAMAGED"
    KILLED = "KILLED"

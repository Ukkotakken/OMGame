from core.game.characters.common import Character
from core.game.common import TurnType, DamageType
from core.game.effects.common import ReceiveManaEffect


class Punisher(Character):
    start_health = 3
    start_max_health = 3
    start_mana = 1
    role_base_attack = 1
    role_vote_strength = 1
    role_attack_type = DamageType.PHISICAL
    role_abilities_list = [
    ]
    role_effects_list = [
        ReceiveManaEffect({TurnType.MAGIC_POWER: 1, TurnType.DIVINE_POWER: 0})]
    role_sides = set()
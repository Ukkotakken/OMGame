from core.game.characters.common import Character
from core.game.common import DamageType


class Archmage(Character):
    start_health = 1
    start_max_health = 1
    start_mana = 2
    role_base_attack = 0
    role_vote_strength = 1
    role_attack_type = DamageType.PHISICAL
    role_abilities_list = []
    role_effects_list = []
    role_sides = set()

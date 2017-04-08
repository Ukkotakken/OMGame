from core.game.action.investigator import Investigation, RoundUp
from core.game.characters.common import Character
from core.game.common import DamageType, Sides
from core.game.effects.investigator import AwarenessEffect


class Investigator(Character):
    start_health = 3
    start_max_health = 3
    start_mana = 0
    base_attack = 1
    vote_strength = 2
    attack_type = DamageType.PHISICAL
    role_abilities_list = [
        RoundUp,
        Investigation]
    role_effects_list = [
        AwarenessEffect()]
    role_sides = {Sides.SIDE_124, Sides.SIDE_147, Sides.SIDE_478}

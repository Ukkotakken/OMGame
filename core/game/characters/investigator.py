from core.game.action.investigator import Investigation, RoundUp
from core.game.characters.common import Character
from core.game.common import DamageType, Sides
from core.game.effects.investigator import AwarenessEffect


class Investigator(Character):
    start_health = 3
    start_max_health = 3
    start_mana = 0
    role_base_attack = 1
    role_vote_strength = 2
    role_attack_type = DamageType.PHISICAL
    role_abilities_list = [
        RoundUp,
        Investigation]
    role_effects_list = [
        AwarenessEffect()]
    role_sides = {Sides.SIDE_123, Sides.SIDE_124, Sides.SIDE_236}

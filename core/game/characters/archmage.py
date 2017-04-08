from core.game.action.archmage import ManaStorm, Fireball, ChainLightning, ElementalProtection, \
    ElementalProtectionEffect
from core.game.characters.common import Character
from core.game.common import DamageType, TurnType, Sides
from core.game.effects.archmage import TurnTypeKnowledge, ManaShieldEffect
from core.game.effects.common import ReceiveManaEffect


class Archmage(Character):
    start_health = 1
    start_max_health = 1
    start_mana = 2
    base_attack = 0
    vote_strength = 1
    attack_type = DamageType.PHISICAL
    role_abilities_list = [
        Fireball,
        ManaStorm,
        ChainLightning,
        ElementalProtection
    ]
    role_effects_list = [
        TurnTypeKnowledge(),
        ManaShieldEffect(),
        ElementalProtectionEffect(),
        ReceiveManaEffect({TurnType.MAGIC_POWER: 2, TurnType.DIVINE_POWER: 1})]
    role_sides = {Sides.SIDE_123, Sides.SIDE_124, Sides.SIDE_236}

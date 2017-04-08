from core.game.action.paladin import LayOnHands, DivineShield, Bodyguard, SoulSave
from core.game.characters.common import Character
from core.game.common import DamageType, Sides, TurnType
from core.game.effects.common import ReceiveManaEffect
from core.game.effects.paladin import RetributionEffect


class Paladin(Character):
    start_health = 4
    start_max_health = 4
    start_mana = 1
    base_attack = 1
    vote_strength = 1
    attack_type = DamageType.PHISICAL
    role_abilities_list = [
        LayOnHands,
        DivineShield,
        Bodyguard,
        SoulSave]
    role_effects_list = [
        RetributionEffect(),
        ReceiveManaEffect({TurnType.MAGIC_POWER: 0, TurnType.DIVINE_POWER: 1})]
    role_sides = {Sides.SIDE_147, Sides.SIDE_478, Sides.SIDE_789}

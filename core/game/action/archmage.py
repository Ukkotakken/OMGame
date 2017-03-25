from core.game.action.arguments import CharacterArgument
from core.game.action.common import Action, ApplyEffectAction
from core.game.common import Step, DamageType, TurnType
from core.game.effects.archmage import ElementalProtectionEffect, ChainLightningEffect


class Fireball(Action):
    mana_cost = 3
    cooldown = -1

    turn_step = Step.NIGHT_ACTIVE_STEP

    name = 'fireball'
    arguments = [CharacterArgument()]
    description = """
        Burns target by 1 point of damage (2 during magic turn).
    """

    def play(self, game):
        strength = 4 if game.turn.turn_type is TurnType.MAGIC_POWER else 2
        self.target.receive_damage(strength, DamageType.BURNING, self)


class ManaStorm(Action):
    mana_cost = 3
    cooldown = -1

    name = 'mana_storm'
    arguments = []
    description = """
        Burns everybody in the city by 1 point of damage (2 during magic turn).
    """

    turn_step = Step.NIGHT_ACTIVE_STEP

    def play(self, game):
        base_damage = 2 if game.turn.turn_type is TurnType.MAGIC_POWER else 1
        for c in game.characters:
            c.receive_damage(base_damage, DamageType.BURNING, self)


class ChainLightning(ApplyEffectAction):
    mana_cost = 2
    cooldown = -1

    name = 'chain_lightning'
    arguments = [CharacterArgument()]
    description = """
        Strikes a lighting into the target.
        At the end of the night target and all whom she attacked/attacked her receive 1 (2) points of burning damage.
        During the magic power turns it will also damage the characters who attacked those who communicated with target by 1 point.
    """

    turn_step = Step.NIGHT_PASSIVE_STEP

    effects = [ApplyEffectAction.effect(ChainLightningEffect, {'action': 'self'})]

    def play(self, game):
        self.target.add_effect(ChainLightningEffect(self))


class ElementalProtection(ApplyEffectAction):
    mana_cost = 0
    cooldown = -1

    name = 'elemental_protection'
    arguments = [CharacterArgument()]
    description = """
        Target will not be receive damage from your spells during the following night.
    """

    turn_step = Step.DAY_ACTIVE_STEP

    effects = [ApplyEffectAction.effect(ElementalProtectionEffect, defaults={'turns': 1})]
from core.game import effects
from core.game.action.common import Action, ApplyEffectAction
from core.game.common import Step, DamageType, TurnType
from core.game.effects.archmage import ElementalProtectionEffect, ChainLightningEffect
from core.game.effects.common import CharacterEffect, TimedCharacterEffect
from core.game.effects.priorities import EffectPriority
from core.game.events.common import DamageEvent


class Fireball(Action):
    mana_cost = 3
    cooldown = -1

    name = 'fireball'

    turn_step = Step.NIGHT_ACTIVE_STEP

    def play(self, game):
        strength = 4 if game.turn.turn_type is TurnType.MAGIC_POWER else 2
        self.target.receive_damage(strength, DamageType.BURNING, self)


class ManaStorm(Action):
    mana_cost = 3
    cooldown = -1

    name = 'mana_storm'

    turn_step = Step.NIGHT_ACTIVE_STEP

    def play(self, game):
        base_damage = 2 if game.turn.turn_type is TurnType.MAGIC_POWER else 1
        for c in game.characters:
            c.receive_damage(base_damage, DamageType.BURNING, self)


class ChainLightning(ApplyEffectAction):
    mana_cost = 2
    cooldown = -1

    name = 'chain_lightning'

    turn_step = Step.NIGHT_PASSIVE_STEP

    effects = [ApplyEffectAction.effect(ChainLightningEffect, {'action': 'self'})]

    def play(self, game):
        self.target.add_effect(ChainLightningEffect(self))

class ElementalProtection(ApplyEffectAction):
    mana_cost = 0
    cooldown = -1

    name = 'elemental_protection'

    turn_step = Step.DAY_ACTIVE_STEP

    effects = [ApplyEffectAction.effect(ElementalProtectionEffect, defaults={'turns': 1})]
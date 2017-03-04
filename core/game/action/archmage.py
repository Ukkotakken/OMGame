from core.game import effects
from core.game.action.common import Action
from core.game.common import Step, DamageType, TurnType
from core.game.effects.common import CharacterEffect
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


class ChainLightning(Action):
    mana_cost = 2
    cooldown = -1

    name = 'chain_lightning'

    turn_step = Step.NIGHT_PASSIVE_STEP

    def play(self, game):
        self.target.add_effect(ChainLightningEffect(self))


class ChainLightningEffect(CharacterEffect):
    priority = EffectPriority.CHAIN_LIGHTNING_PRIORITY

    def __init__(self, action):
        self.action = action

    def turn_end(self, character, turn):
        battles = {(e.character, e.action.executor)
               for e in character.game.new_events
               if isinstance(e, DamageEvent) and e.action.target is not None}
        battles |= {(b, a) for a, b in battles}

        first_order_targets = {t for t, e in battles if e is character}
        first_order_targets -= {character}

        second_order_targets =  {t for t, e in battles if e in first_order_targets}
        second_order_targets -= first_order_targets
        second_order_targets -= {character}

        strength = 2 if turn.turn_type is TurnType.MAGIC_POWER else 1
        damage_action = ChainLightningDamage(self.action.caller, None, None)
        character.receive_damage(strength, DamageType.BURNING, damage_action)
        for c in first_order_targets:
            c.receive_damage(strength, DamageType.BURNING, damage_action)

        if strength > 1:
            for c in second_order_targets:
                c.receive_damage(strength - 1, DamageType.BURNING, damage_action)

        character.turn_end(turn)

    def passed(self):
        return True

class ChainLightningDamage(Action):
    turn_step = Step.NIGHT_ACTIVE_STEP


class ElementalProtection(Action):
    mana_cost = 0
    cooldown = -1

    name = 'elemental_protection'

    turn_step = Step.DAY_ACTIVE_STEP

    def play(self, game):
        self.target.add_effect(ElementalProtectionEffect(2))


class ElementalProtectionEffect(CharacterEffect):
    priority = EffectPriority.ELEMENTAL_PROTECTION_PRIORITY

    def __init__(self, duration_turn=None):
        self.duration_turn = duration_turn # Default option is 2 for day + night

    def receive_damage(self, character, strength, type, action):
        if action.__class__ in {ChainLightningDamage, ManaStorm, Fireball}:
            return
        character.receive_damage(strength=strength, type=type, action=action)

    def turn_end(self, character, *args, **kwargs):
        if self.duration_turn is not None:
            self.duration_turn -= 1
        return character.turn_end(*args, **kwargs)

    def passed(self):
        return self.duration_turn is not None and self.duration_turn <= 0

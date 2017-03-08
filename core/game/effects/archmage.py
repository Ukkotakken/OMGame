from core.game import characters
from core.game.action.common import ActionBase
from core.game.common import TurnType, DamageType
from core.game.effects.common import CharacterEffect, TimedCharacterEffect
from core.game.effects.priorities import EffectPriority
from core.game.events.archmage import SendTurnTypeEvent
from core.game.events.common import DamageEvent
from core.game.turn import DayTurn


class TurnTypeKnowledge(CharacterEffect):
    priority = EffectPriority.TURN_START_INFO_PRIORITY

    def on_turn_start(self, character, turn):
        if isinstance(turn, DayTurn):
            character.game.log(SendTurnTypeEvent(character, turn.turn_type))
        character.on_turn_start(turn)


class ManaShieldEffect(CharacterEffect):
    priority = EffectPriority.MANA_SHIELD_PRIORITY

    def receive_damage(self, character, strength, type, action):
        damage_amount = min(strength, character.mana)
        character.game.log(DamageEvent(character, damage_amount, type, action))
        character.mana -= damage_amount
        strength -= damage_amount
        character.receive_damage(strength=strength, type=type, action=action)


class ElementalProtectionEffect(TimedCharacterEffect):
    priority = EffectPriority.RECEIVE_DAMAGE_CANCELING_PRIORITY

    def receive_damage(self, character, strength, type, action):
        if action.__class__ in {ChainLightningDamage} or action.__class__ in characters.archmage.Archmage.role_abilities_list:
            return
        character.receive_damage(strength=strength, type=type, action=action)

class ChainLightningDamage(ActionBase):
    pass

class ChainLightningEffect(CharacterEffect):
    priority = EffectPriority.TURN_END_DAMAGE_PRIORITY

    def __init__(self, action):
        self.action = action

    def on_turn_end(self, character, turn):
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

        character.on_turn_end(turn)

    def passed(self):
        return True

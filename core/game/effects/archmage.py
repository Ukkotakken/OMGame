from core.game.action.archmage import ChainLightningDamage, ManaStorm, Fireball
from core.game.common import TurnType, DamageType
from core.game.effects.common import CharacterEffect, pipe_argument
from core.game.effects.priorities import EffectPriority
from core.game.events.archmage import SendTurnTypeEvent
from core.game.events.common import DamageEvent
from core.game.turn import DayTurn


class TurnTypeKnowledge(CharacterEffect):
    priority = EffectPriority.TURN_TYPE_KNOWLEDGE_PRIORITY

    def before__turn_start(self, character, turn):
        if isinstance(turn, DayTurn):
            character.game.log(SendTurnTypeEvent(character, turn.turn_type))
        return pipe_argument(turn=turn)


class ManaShieldEffect(CharacterEffect):
    priority = EffectPriority.MANA_SHIELD_PRIORITY

    def before__receive_damage(self, character, strength, type, action):
        damage_amount = min(strength, character.mana)
        character.game.log(DamageEvent(character, damage_amount, type, action))
        character.mana -= damage_amount
        strength -= damage_amount
        return pipe_argument(strength=strength, type=type, action=action)

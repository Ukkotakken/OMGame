from core.game.effects.common import CharacterEffect
from core.game.effects.priorities import EffectPriority
from core.game.events.archmage import SendTurnTypeEvent
from core.game.events.common import DamageEvent
from core.game.turn import DayTurn


class TurnTypeKnowledge(CharacterEffect):
    priority = EffectPriority.TURN_TYPE_KNOWLEDGE_PRIORITY

    def turn_start(self, character, turn):
        if isinstance(turn, DayTurn):
            character.game.log(SendTurnTypeEvent(character, turn.turn_type))
        character.turn_start(turn)


class ManaShieldEffect(CharacterEffect):
    priority = EffectPriority.MANA_SHIELD_PRIORITY

    def receive_damage(self, character, strength, type, action):
        damage_amount = min(strength, character.mana)
        character.game.log(DamageEvent(character, damage_amount, type, action))
        character.mana -= damage_amount
        strength -= damage_amount
        character.receive_damage(strength=strength, type=type, action=action)

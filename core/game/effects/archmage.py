from core.game.effects.common import CharacterEffect, pipe_argument
from core.game.events.archmage import SendTurnTypeEvent


class TurnTypeKnowledge(CharacterEffect):
    def before__turn_start(self, character, turn):
        character.game.log(SendTurnTypeEvent(character, turn.turn_type))
        return pipe_argument(turn=turn)


class ManaShieldEffect(CharacterEffect):
    def before__receive_damage(self, character, strength, type, action):
        damage_amount = min(strength, character.mana)
        character.mana -= damage_amount
        strength -= damage_amount
        pipe_argument(character=character, strength=strength, type=type, action=action)

from core.game.action.arguments import CharacterArgument
from core.game.action.common import ApplyEffectAction, Action
from core.game.common import Step, TurnType
from core.game.effects.common import CantPlayActionEffect
from core.game.effects.paladin import DivineShieldEffect, BodyguardEffect, SoulSaveEffect


class SoulSave(ApplyEffectAction):
    name = "soulsave"
    arguments = [CharacterArgument]
    description = """
        If target never attacked nor killed anybody, you will save it from prison.
    """

    mana_cost = None
    cooldown = 1
    turn_step = Step.DAY_ACTIVE_STEP

    effects = [
        ApplyEffectAction.effect(SoulSaveEffect, defaults={'turns': 1})]

    def can_play_check(self, character):
        # Can't be played on self
        return character is not self.target


class Bodyguard(ApplyEffectAction):
    name = "bodyguard"
    arguments = [CharacterArgument]
    description = """
        If anybody will try to attack the target (by targeted attack) you will receive the damage instead of the target
        (and do the retribution, of course).
    """

    mana_cost = None
    cooldown = 0
    turn_step = Step.DAY_ACTIVE_STEP

    effects = [
        ApplyEffectAction.effect(BodyguardEffect, {'bodyguard': 'executor'}),
        ApplyEffectAction.effect(CantPlayActionEffect, {}, 'executor', {'turns': 1}),]

    def can_play_check(self, character):
        # Can't be played on self
        return character is not self.target


class DivineShield(ApplyEffectAction):
    name = "divine_shield"
    arguments = [CharacterArgument]
    description = """
        You will absorb 2 points of damage this night. If it's a divine turn - you will absorb 10 points of damage.
    """

    mana_cost = 1
    cooldown = -1
    turn_step = Step.DAY_ACTIVE_STEP

    effects = [ApplyEffectAction.effect(DivineShieldEffect, target='executor')]


class LayOnHands(Action):
    name = "lay_on_hands"
    arguments = [CharacterArgument]
    description = """
        You heal 1 health point of the target (2 during divine turn). You can't heal yourself.
    """

    mana_cost = 1
    cooldown = -1
    turn_step = Step.DAY_ACTIVE_STEP

    def play(self, game):
        strength = 2 if game.turn.turn_type is TurnType.DIVINE_POWER else 1
        self.target.receive_heal(strength, self)

    def can_play_check(self, character):
        # Can't be played on self
        return character is not self.target
from core.game.action.common import ApplyEffectAction, Action
from core.game.common import Step, TurnType
from core.game.effects.common import CantPlayActionEffect
from core.game.effects.paladin import DivineShieldEffect, BodyguardEffect, SoulSaveEffect


class SoulSave(ApplyEffectAction):
    mana_cost = None
    cooldown = 1
    turn_step = Step.DAY_ACTIVE_STEP

    effects = [
        ApplyEffectAction.effect(SoulSaveEffect, defaults={'turns': 1})]


class Bodyguard(ApplyEffectAction):
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
    mana_cost = 1
    cooldown = -1
    turn_step = Step.DAY_ACTIVE_STEP

    effects = [ApplyEffectAction.effect(DivineShieldEffect, target='executor')]


class LayOnHands(Action):
    mana_cost = 1
    cooldown = -1
    turn_step = Step.DAY_ACTIVE_STEP

    def play(self, game):
        strenght = 2 if game.turn.turn_type is TurnType.DIVINE_POWER else 1
        self.target.receive_heal(strenght, self)

    def can_play_check(self, character):
        # Can't be played on self
        return character is not self.target
from core.game.action.common import Action
from core.game.characters.common import Character
from core.game.common import GuiltyDegree, TurnType, DamageType
from core.game.effects.common import CharacterEffect, pipe_argument, TimedCharacterEffect
from core.game.effects.priorities import EffectPriority
from core.game.events.common import DamageEvent
from core.game.events.punisher import PenanceEvent, BloodhoundEvent, PunishmentBanishEvent
from core.game.exceptions import BanishedFromClassException
from core.game.turn import DayTurn, NightTurn


class Penance(CharacterEffect):
    priority = EffectPriority.TURN_END_INFO_PRIORITY

    def on_kill(self, character, killed_character):
        character.game.log(PenanceEvent(character, killed_character))
        character.on_kill(killed_character)


class BloodhoundEffect(TimedCharacterEffect):
    priority = EffectPriority.TURN_END_INFO_PRIORITY

    def __init__(self, punisher):
        self.punisher = punisher
        super().__init__(1)

    def on_turn_end(self, character, turn):
        if isinstance(turn, NightTurn):
            character.game.log(BloodhoundEvent(self.punisher, character, turn.turn_type is TurnType.MAGIC_POWER))
            dies = character.dies()
            for c in character.damaged_by_characters:
                if self.punisher.guilty_degrees.get(c) is not GuiltyDegree.KILLED:
                    self.punisher.guilty_degrees[c] = GuiltyDegree.KILLED if dies else GuiltyDegree.DAMAGED


class ClassBanishEffect(CharacterEffect):
    priority = EffectPriority.PLAY_CANCELING_PRIORITY

    def play(self, character, ability, target=None, **kwargs):
        if ability in character.role_abilities_list:
            raise BanishedFromClassException()
        return character.play(ability, target, **kwargs)

    def vote(self, _character, character):
        return Character.vote(_character, character)

    def attack(self, _character, character):
        return Character.attack(_character, character)

class PunishmentEffect(TimedCharacterEffect):
    priority = EffectPriority.PUNISHMENT_PRIORITY

    def __init__(self, victim, punisher):
        self.victim = victim
        self.punisher = punisher
        super().__init__(turns=1)

    def receive_damage(self, character, strength, type, action):
        guilty_degree = self.punisher.find_guilty_degree(character, self.victim)
        if action.executor is self.punisher:
            if guilty_degree is not GuiltyDegree.NO_GUILTY:
                base_damage = 1 if character.game.turn.turn_type is TurnType.MAGIC_POWER else 0
                if guilty_degree is GuiltyDegree.KILLED:
                    base_damage += 1
                character.health -= base_damage
                character.game.log(DamageEvent(character, base_damage, DamageType.PHISICAL, action))
            else:
                self.punisher.add_effect(ClassBanishEffect())
                character.game.log(PunishmentBanishEvent(self.punisher))

        character.receive_damage(strength, type, action)

from core.game.action.common import Action, Vote
from core.game.characters.punisher import find_guilty_degree, GuiltyDegree
from core.game.common import Step, TurnType, DamageType
from core.game.effects.common import CharacterEffect, TimedCharacterEffect, CantPlayActionEffect
from core.game.effects.priorities import EffectPriority
from core.game.events.common import VoteEvent, DamageEvent
from core.game.events.punisher import BloodhoundEvent
from core.game.exceptions import BanishedFromClassException
from core.game.turn import NightTurn


class PunisherVote(Action):
    turn_step = Step.DAY_VOTE_STEP
    can_cancel = False

    name = 'vote'

    def __init__(self, caller, executor, target, victim=None):
        super().__init__(caller, executor, target)
        if victim:
            self.guilty_degree = executor.find_guilty_degree(target, victim)
        else:
            self.guilty_degree = executor.guilty_degrees.get(target)

    def play(self, game):
        additional_strength = 0
        if self.guilty_degree:
            if self.guilty_degree is GuiltyDegree.DAMAGED:
                additional_strength += 1
            if self.guilty_degree is GuiltyDegree.KILLED:
                additional_strength += 2
        self.target.add_votes(self.executor.vote_strength + additional_strength)
        game.log(VoteEvent(self))


class Vengeance(Action):
    turn_step = Step.DAY_ACTIVE_STEP
    mana_cost = 1

    name = 'vengeance'

    def __init__(self, caller, executor, target, victim):
        super().__init__(caller, executor, target)
        self.victim = victim

    def play(self, game):
        self.target.add_effect(VengeanceEffect(self.victim, self.executor))


class VengeanceEffect(TimedCharacterEffect):
    priority = EffectPriority.VENGEANCE_PRIORITY

    def __init__(self, victim, punisher):
        self.victim = victim
        self.punisher = punisher
        super().__init__(turns=1)

    def receive_damage(self, character, strength, damage_type, action):
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

        character.receive_damage(strength, damage_type, action)


class ClassBanishEffect(CharacterEffect):
    priority = EffectPriority.PLAY_CANCELING_AND_ALTERING_PRIORITY

    def play(self, character, ability, target=None, **kwargs):
        if ability in character.role_abilities_list:
            if isinstance(ability, PunisherVote):
                ability = Vote
            else:
                raise BanishedFromClassException()
        character.play(ability, target, **kwargs)


class Bloodhound(Action):
    mana_cost = 1
    turn_step = Step.DAY_ACTIVE_STEP

    def play(self, game):
        self.executor.add_effect(CantPlayActionEffect(turns=1))
        self.target.add_effect(BloodhoundEffect(self.executor))


class BloodhoundEffect(TimedCharacterEffect):
    priority = EffectPriority.TURN_END_INFO_PRIORITY

    def __init__(self, punisher):
        self.punisher = punisher
        super().__init__(1)

    def on_turn_end(self, character, turn):
        if isinstance(turn, NightTurn):
            character.game.log(BloodhoundEvent(self.punisher, character, turn.turn_type is TurnType.MAGIC_POWER))

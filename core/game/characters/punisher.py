from enum import Enum

from core.game.action.punisher import PunisherVote
from core.game.characters.common import Character, check_effects
from core.game.common import TurnType, DamageType
from core.game.effects.common import ReceiveManaEffect
from core.game.events.common import VoteInstantEvent, DamageEvent, TurnEndEvent, DeathEvent


class Punisher(Character):
    start_health = 3
    start_max_health = 3
    start_mana = 1
    role_base_attack = 1
    role_vote_strength = 1
    role_attack_type = DamageType.PHISICAL
    role_abilities_list = [
    ]
    role_effects_list = [
        ReceiveManaEffect({TurnType.MAGIC_POWER: 1, TurnType.DIVINE_POWER: 0})]
    role_sides = set()

    def __init__(self, *args, **kwargs):
        self.guilty_degrees = {}
        super().__init__(*args, **kwargs)

    @check_effects
    def vote(self, character):
        self.game.log(VoteInstantEvent(self.play(PunisherVote, caller=self, target=character)))

    @check_effects
    def find_guilty_degree(self, character, target):
        if target in character.killed:
            return GuiltyDegree.KILLED
        if target in character.caused_damage:
            return GuiltyDegree.DAMAGED
        return GuiltyDegree.NO_GUILTY


class GuiltyDegree(Enum):
    NO_GUILTY = 0
    DAMAGED = 1
    KILLED = 2

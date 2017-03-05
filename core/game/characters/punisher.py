from core.game.action.punisher import PunisherVote, Bloodhound, Vengeance
from core.game.characters.common import Character, check_effects
from core.game.common import TurnType, DamageType, GuiltyDegree, Sides
from core.game.effects.common import ReceiveManaEffect
from core.game.effects.punisher import Penance
from core.game.events.common import VoteInstantEvent


class Punisher(Character):
    start_health = 3
    start_max_health = 3
    start_mana = 1
    role_base_attack = 1
    role_vote_strength = 1
    role_attack_type = DamageType.PHISICAL
    role_abilities_list = [
        PunisherVote,
        Vengeance,
        Bloodhound
    ]
    role_effects_list = [
        ReceiveManaEffect({TurnType.MAGIC_POWER: 1, TurnType.DIVINE_POWER: 0}),
        Penance()
    ]
    role_sides = {Sides.SIDE_123, Sides.SIDE_124, Sides.SIDE_147}

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

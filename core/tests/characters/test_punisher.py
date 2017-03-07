from unittest.mock import MagicMock

from nose_parameterized import parameterized

from core.game.action.common import Vote
from core.game.action.punisher import Punishment, Bloodhound, PunisherVote
from core.game.characters.common import Character
from core.game.characters.punisher import Punisher
from core.game.common import TurnType, DamageType, GuiltyDegree
from core.game.effects.archmage import ManaShieldEffect
from core.game.events.common import ActionPlayedEvent, DamageEvent, DeathEvent, VictoryEvent
from core.game.events.punisher import PenanceEvent, PunishmentBanishEvent, BloodhoundEvent
from core.game.exceptions import BanishedFromClassException
from core.tests.test_game import GameTestBase


class PunisherTest(GameTestBase):
    def setUp(self):
        self.chars = [
            Punisher(MagicMock()),
            Character(MagicMock()),
            Character(MagicMock())
        ]
        self.punisher = self.chars[0]
        self.alice = self.chars[1]
        self.bob = self.chars[2]
        self.alice.sides = self.bob.sides = {-1}
        super().setUp()

    def testPeanance(self):
        self.next_turn_skip_events()
        self.punisher.attack(self.alice)
        self.game.play_turn()
        self.game.pop_new_events()
        self.game.start_new_turn()
        self.assertEventsEqual(self.game.pop_new_events(), [])

        self.next_turn_skip_events()
        self.alice.health = 1
        self.punisher.attack(self.alice)
        self.game.play_turn()
        self.game.pop_new_events()
        self.game.start_new_turn()
        self.assertEventsEqual(
            self.game.pop_new_events(), [DeathEvent(self.alice), PenanceEvent(self.punisher, self.alice)])

    def doAliceAttacksBob(self, additional_events=None, kills=False):
        additional_events = additional_events or []
        self.alice.attack(self.bob)
        alice_attack = self.alice.action_queue[0]

        if kills:
            self.bob.health = 1
            additional_events.append(DeathEvent(self.bob))

        self.game.play_and_start_new_turn()

        self.assertEventsEqual(
            self.game.pop_new_events(),
            [
                ActionPlayedEvent(alice_attack),
                DamageEvent(self.bob, 1, DamageType.PHISICAL, alice_attack)] + additional_events)
        if kills:
            self.assertIn(self.bob, self.alice.killed)

    @parameterized.expand([
        (GuiltyDegree.KILLED,),
        (GuiltyDegree.DAMAGED,)])
    def testPunishment(self, guilty_degree):
        kills = guilty_degree is GuiltyDegree.KILLED
        self.next_turn_skip_events()
        self.doAliceAttacksBob(kills=kills)

        punishment = self.punisher.play(Punishment, self.alice, victim=self.bob, caller=self.punisher)
        self.game.play_turn()
        self.assertEventsEqual(self.game.pop_new_events(), [ActionPlayedEvent(punishment)])

        self.game.start_new_turn()
        self.alice.health = 4
        self.game.turn.turn_type = TurnType.MAGIC_POWER
        punisher_attack = self.punisher.attack(self.alice)
        self.game.play_and_start_new_turn()
        damage_amount = 2 if kills else 1
        self.assertEventsEqual(
            self.game.pop_new_events(),
            [ActionPlayedEvent(punisher_attack),
             DamageEvent(self.alice, 1, DamageType.PHISICAL, punisher_attack),
             DamageEvent(self.alice, damage_amount, DamageType.PHISICAL, punisher_attack)]
        )

    def testPunishment_ignoresManashield(self):
        self.next_turn_skip_events()
        self.alice.add_effect(ManaShieldEffect())
        self.doAliceAttacksBob(kills=True)

        self.punisher.mana = 1
        self.punisher.play(Punishment, self.alice, victim=self.bob, caller=self.punisher)
        punishment = self.punisher.action_queue[0]
        self.game.play_turn()
        self.assertEventsEqual(self.game.pop_new_events(), [ActionPlayedEvent(punishment)])

        self.game.start_new_turn()
        self.alice.health = 3
        self.alice.mana = 1
        self.game.turn.turn_type = TurnType.MAGIC_POWER
        self.punisher.attack(self.alice)
        punisher_attack = self.punisher.action_queue[0]
        self.game.play_and_start_new_turn()
        self.assertEventsEqual(
            self.game.pop_new_events(),
            [ActionPlayedEvent(punisher_attack),
             DamageEvent(self.alice, 1, DamageType.PHISICAL, punisher_attack),
             DamageEvent(self.alice, 2, DamageType.PHISICAL, punisher_attack)])
        self.assertEqual(self.alice.health, 1)
        self.assertEqual(self.alice.mana, 0)

    def testPunishment_innocent(self):
        punishment = self.punisher.play(Punishment, self.alice, victim=self.bob, caller=self.punisher)
        self.game.play_turn()
        self.assertEventsEqual(self.game.pop_new_events(), [ActionPlayedEvent(punishment)])

        self.game.start_new_turn()
        punisher_attack = self.punisher.attack(self.alice)
        self.game.play_and_start_new_turn()
        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(punisher_attack),
                DamageEvent(self.alice, 1, DamageType.PHISICAL, punisher_attack),
                PunishmentBanishEvent(self.punisher)])

        self.punisher.vote(self.alice)
        self.assertEqual(self.punisher.action_queue[0].__class__, Vote)
        with self.assertRaises(BanishedFromClassException):
            self.punisher.play(Punishment, self.alice, victim=self.bob, caller=self.punisher)
        with self.assertRaises(BanishedFromClassException):
            self.punisher.play(Bloodhound, self.alice, caller=self.punisher)

    @parameterized.expand([
        (GuiltyDegree.KILLED,),
        (GuiltyDegree.DAMAGED,)])
    def testBloodhound(self, guilty_degree):
        bloodhound_action = self.punisher.play(Bloodhound, self.bob, caller=self.punisher)
        self.game.play_and_start_new_turn()
        self.assertEventsEqual(self.game.pop_new_events(), [ActionPlayedEvent(bloodhound_action)])

        kill = guilty_degree is GuiltyDegree.KILLED
        self.game.turn.turn_type = TurnType.MAGIC_POWER
        self.punisher.attack(self.alice) # Attack should be ignored
        self.doAliceAttacksBob(kills=kill, additional_events=[BloodhoundEvent(self.punisher, self.bob, True)])

        punisher_vote = self.punisher.play(PunisherVote, self.alice, caller=self.punisher)
        self.assertEqual(punisher_vote.strength, 3 if kill else 2)
        self.alice.vote(self.punisher)


    @parameterized.expand([
        (GuiltyDegree.KILLED,),
        (GuiltyDegree.DAMAGED,)])
    def testPunisherVote(self, guilty_degree):
        kill = guilty_degree is GuiltyDegree.KILLED
        self.next_turn_skip_events()
        self.doAliceAttacksBob(kills=kill)

        punisher_vote = self.punisher.play(PunisherVote, self.alice, victim=self.bob, caller=self.punisher)
        self.assertEqual(punisher_vote.strength, 3 if kill else 2)
        self.alice.vote(self.punisher)

        self.game.play_turn()
        self.assertEqual(self.alice.votes_number, 3 if kill else 2)
        self.assertEqual(self.punisher.votes_number, 1)
        self.game.start_new_turn()


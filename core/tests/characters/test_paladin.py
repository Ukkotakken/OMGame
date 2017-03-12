from unittest.mock import MagicMock

from nose_parameterized.parameterized import parameterized

from core.game.action.paladin import SoulSave, Bodyguard, DivineShield, LayOnHands
from core.game.characters.common import Character
from core.game.characters.paladin import Paladin
from core.game.common import GuiltyDegree, TurnType, DamageType
from core.game.effects.paladin import RetributionDamageAction
from core.game.events.common import ActionPlayedEvent, DamageEvent, ImprisonEvent, VoteEvent
from core.tests.test_game import GameTestBase


class PaladinTest(GameTestBase):
    def setUp(self):
        self.chars = [
            Paladin(MagicMock()),
            Character(MagicMock()),
            Character(MagicMock()),
            Character(MagicMock())]
        self.paladin = self.chars[0]
        self.alice = self.chars[1]
        self.bob = self.chars[2]
        self.carol = self.chars[3]
        for i in range(1, len(self.chars)):
            self.chars[i].sides = {-i}
        super().setUp()

    def testRetribution(self):
        self.next_turn_no_events()
        alice_attack = self.alice.attack(self.paladin)
        self.next_turn_expect_events([
            ActionPlayedEvent(alice_attack),
            DamageEvent(self.paladin, 1, DamageType.PHISICAL, alice_attack),
            DamageEvent(self.alice, 1, DamageType.PHISICAL, RetributionDamageAction(None, None, None))])

    @parameterized.expand([
        (GuiltyDegree.NO_GUILTY,),
        (GuiltyDegree.KILLED,),
        (GuiltyDegree.DAMAGED,)])
    def testSoulSave(self, guilty_degree):
        self.next_turn_no_events()
        if guilty_degree is not GuiltyDegree.NO_GUILTY:
            self.alice.attack(self.bob)
            if guilty_degree is GuiltyDegree.KILLED:
                self.bob.health = 1
        self.next_turn_skip_events()

        vote_action = self.carol.vote(self.alice)
        soul_save_action = self.paladin.play(SoulSave, self.alice, caller=self.paladin)
        expected_events = [
            VoteEvent(vote_action),
            ActionPlayedEvent(vote_action),
            ActionPlayedEvent(soul_save_action)]
        if guilty_degree is not GuiltyDegree.NO_GUILTY:
            expected_events.append(ImprisonEvent(self.alice))
        self.next_turn_expect_events(expected_events)

    def testBodyguard(self):
        self.paladin.play(Bodyguard, self.paladin, caller=self.paladin)
        self.next_turn_no_events()
        self.next_turn_no_events()

        self.paladin.play(Bodyguard, self.bob, caller=self.paladin)
        self.next_turn_skip_events()

        alice_attack = self.alice.attack(self.bob)
        self.next_turn_expect_events([
            ActionPlayedEvent(alice_attack),
            DamageEvent(self.paladin, 1, DamageType.PHISICAL, alice_attack),
            DamageEvent(self.alice, 1, DamageType.PHISICAL, RetributionDamageAction(None, None, None))])
        self.assertEqual(self.bob.health, 3)
        self.assertEqual(self.paladin.health, 3)

    @parameterized.expand([
        (TurnType.DIVINE_POWER,),
        (TurnType.MAGIC_POWER,)])
    def testDivineShield(self, turn_type):
        self.game.turn.turn_type = turn_type
        divine_shield_action = self.paladin.play(DivineShield, caller=self.paladin)
        self.next_turn_expect_events([ActionPlayedEvent(divine_shield_action)])

        self.game.turn.turn_type = turn_type
        self.alice.base_attack = 3
        alice_attack = self.alice.attack(self.paladin)
        expected_events = [
            ActionPlayedEvent(alice_attack),
            DamageEvent(self.alice, 1, DamageType.PHISICAL, RetributionDamageAction(None, None, None))]
        if turn_type is TurnType.MAGIC_POWER:
            expected_events.append(DamageEvent(self.paladin, 1, DamageType.PHISICAL, alice_attack))
        self.next_turn_expect_events(expected_events)

    @parameterized.expand([
        (TurnType.DIVINE_POWER,),
        (TurnType.MAGIC_POWER,)])
    def testLayOnHands(self, turn_type):
        self.bob.health = 1
        self.game.turn.turn_type = turn_type
        lay_on_hands_action = self.paladin.play(LayOnHands, self.bob, caller=self.paladin)
        self.next_turn_expect_events([ActionPlayedEvent(lay_on_hands_action)])
        self.assertEqual(self.bob.health, 3 if turn_type is TurnType.DIVINE_POWER else 2)

    def testLayOnHands_overheal(self):
        lay_on_hands_action = self.paladin.play(LayOnHands, self.bob, caller=self.paladin)
        self.next_turn_expect_events([ActionPlayedEvent(lay_on_hands_action)])
        self.assertEqual(self.bob.health, 3)


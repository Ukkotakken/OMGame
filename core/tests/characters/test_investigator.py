from unittest.mock import MagicMock

from core.game.action.investigator import RoundUp, Investigation
from core.game.characters.common import Character
from core.game.characters.investigator import Investigator
from core.game.common import DamageType
from core.game.effects.investigator import RoundUpDamageAction
from core.game.events.common import ActionPlayedEvent, DamageEvent
from core.game.events.investigator import AwarenessEvent, InvestigationEvent
from core.tests.test_game import GameTestBase


class InvestigatorTest(GameTestBase):
    def setUp(self):
        self.chars = [
            Investigator(MagicMock()),
            Character(MagicMock()),
            Character(MagicMock())
        ]
        self.investigator = self.chars[0]
        self.alice = self.chars[1]
        self.bob = self.chars[2]
        self.alice.sides = self.bob.sides = {-1}
        super().setUp()

    def testAwareness(self):
        self.next_turn_skip_events()
        self.game.play_and_start_new_turn()
        self.assertEventsEqual(self.game.pop_new_events(), [AwarenessEvent(self.investigator, [])])

        self.next_turn_no_events()
        alice_attack = self.alice.attack(self.bob)
        alice_damage_event = DamageEvent(self.bob, 1, DamageType.PHISICAL, alice_attack)
        self.game.play_and_start_new_turn()
        self.assertEventsEqual(self.game.pop_new_events(), [
            ActionPlayedEvent(alice_attack),
            alice_damage_event,
            AwarenessEvent(self.investigator, [alice_damage_event])])

    def testRoundUp(self):
        self.game.pop_new_events()
        self.investigator.play(RoundUp, target=self.alice, caller=self.investigator)
        self.next_turn_no_events() # As investigator can't play roundup yet
        investigator_attack = self.investigator.attack(self.bob)
        damage_event = DamageEvent(self.bob, 1, DamageType.PHISICAL, investigator_attack)
        self.next_turn_expect_events([
            AwarenessEvent(self.investigator, [damage_event]),
            damage_event,
            ActionPlayedEvent(investigator_attack)])

        self.investigator.play(RoundUp, target=self.alice, caller=self.investigator)
        self.next_turn_no_events() # As investigator can't play roundup yet
        investigator_attack = self.investigator.attack(self.bob)
        damage_event = DamageEvent(self.bob, 1, DamageType.PHISICAL, investigator_attack)
        self.next_turn_expect_events([
            AwarenessEvent(self.investigator, [damage_event]),
            damage_event,
            ActionPlayedEvent(investigator_attack)])

        roundup_action = self.investigator.play(RoundUp, target=self.alice, caller=self.investigator)
        self.next_turn_expect_events([ActionPlayedEvent(roundup_action)]) # As cooldown is ok now
        self.investigator.attack(self.bob)

        alice_damage = DamageEvent(
            self.alice,
            2,
            DamageType.PHISICAL,
            RoundUpDamageAction(self.investigator, None, self.alice))
        self.next_turn_expect_events([AwarenessEvent(self.investigator, [alice_damage]), alice_damage])

    def testInvestigation(self):
        self.game.pop_new_events()
        self.investigator.play(Investigation, target=self.alice, caller=self.investigator)
        self.next_turn_no_events() # As investigator can't play investigation yet
        self.next_turn_expect_events([AwarenessEvent(self.investigator, [])])

        investigation_action = self.investigator.play(Investigation, target=self.alice, caller=self.investigator)
        self.next_turn_expect_events([ActionPlayedEvent(investigation_action)])
        self.investigator.attack(self.bob)
        self.next_turn_expect_events([
            AwarenessEvent(self.investigator, []), InvestigationEvent(self.investigator, self.alice)])

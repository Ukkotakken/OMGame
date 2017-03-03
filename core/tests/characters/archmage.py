from unittest.mock import MagicMock

from core.game.action.archmage import Fireball
from core.game.action.common import BaseAttack
from core.game.characters.archmage import Archmage
from core.game.characters.common import Character
from core.game.common import TurnType, DamageType
from core.game.events.archmage import SendTurnTypeEvent
from core.game.events.common import ActionPlayedEvent, DamageEvent, DeathEvent
from core.tests.game import GameTestBase


class ArchmageTest(GameTestBase):
    def setUp(self):
        self.chars = [
            Archmage(MagicMock()),
            Character(MagicMock()),
            Character(MagicMock())
        ]
        self.archmage = self.chars[0]
        self.alice = self.chars[1]
        self.bob = self.chars[2]
        super().setUp()

    def testTurnTypeKnowledge(self):
        events = self.game.pop_new_events()
        self.assertEventsEqual(events, [SendTurnTypeEvent(self.archmage, self.game.turn.turn_type)])

    def testManaShield(self):
        self.next_turn_skip_events()
        archmage_mana = self.archmage.mana
        archmage_health = self.archmage.health
        self.alice.attack(self.archmage)
        self.game.play_turn()
        self.assertEqual(self.archmage.health, archmage_health)
        self.assertEqual(self.archmage.mana, archmage_mana - 1)

        new_events = self.game.pop_new_events()
        attack_action = BaseAttack(caller=self.alice, executor=self.alice, target=self.archmage)
        expected_events = [
            ActionPlayedEvent(attack_action),
            DamageEvent(
                character=self.archmage,
                strength=1,
                type=DamageType.PHISICAL,
                action=attack_action)]
        self.assertEventsEqual(new_events, expected_events)

    def testFireball_DamageNightType(self):
        self.next_turn_skip_events()
        self.game.turn.turn_type = TurnType.DIVINE_POWER

        self.archmage.mana = 6
        self.alice.health = 3
        self.bob.health = 3
        self.archmage.play(Fireball, caller=self.archmage, target=self.alice)
        self.archmage.play(Fireball, caller=self.archmage, target=self.bob)
        self.game.play_turn()

        alice_ball = Fireball(self.archmage, self.archmage, self.alice)
        bob_ball = Fireball(self.archmage, self.archmage, self.bob)

        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(alice_ball),
                ActionPlayedEvent(bob_ball),
                DamageEvent(self.alice, 2, DamageType.BURNING, alice_ball),
                DamageEvent(self.bob, 2, DamageType.BURNING, bob_ball)])

        self.game.start_new_turn()

        self.assertEqual(self.alice.health, 1)
        self.assertEqual(self.bob.health, 1)

        self.next_turn_skip_events()
        self.game.turn.turn_type = TurnType.MAGIC_POWER
        self.archmage.mana = 5
        self.archmage.play(Fireball, caller=self.archmage, target=self.alice)
        self.game.play_turn()

        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(alice_ball),
                DamageEvent(self.alice, 4, DamageType.BURNING, alice_ball)])

        self.game.start_new_turn()

        self.assertEventsEqual(
            self.game.pop_new_events(), [
                DeathEvent(self.alice),
                SendTurnTypeEvent(self.archmage, self.game.turn.turn_type)])

    def testFireball_NoMana(self):
        self.next_turn_skip_events()
        self.game.turn.turn_type = TurnType.DIVINE_POWER

        self.archmage.mana = 4
        self.archmage.play(Fireball, caller=self.archmage, target=self.alice)
        self.archmage.play(Fireball, caller=self.archmage, target=self.bob)
        self.game.play_turn()

        alice_ball = Fireball(self.archmage, self.archmage, self.alice)
        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(alice_ball),
                DamageEvent(self.alice, 2, DamageType.BURNING, alice_ball)])

    def testManaStorm(self):
        # TODO(ukkotakken): Add a test.
        pass

    def testChainLightning(self):
        # TODO(ukkotakken): Add a test.
        pass

    def testElementalProtection(self):
        # TODO(ukkotakken): Add a test.
        pass



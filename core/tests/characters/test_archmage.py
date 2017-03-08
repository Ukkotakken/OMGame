from unittest.mock import MagicMock

from core.game.action.archmage import Fireball, ManaStorm, ChainLightning, ElementalProtection
from core.game.action.common import BaseAttack
from core.game.characters.archmage import Archmage
from core.game.characters.common import Character
from core.game.common import TurnType, DamageType
from core.game.effects.archmage import ChainLightningDamage
from core.game.events.archmage import SendTurnTypeEvent
from core.game.events.common import ActionPlayedEvent, DamageEvent, DeathEvent, VictoryEvent
from core.tests.test_game import GameTestBase


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
        self.alice.sides = self.bob.sides = {-1}
        super().setUp()

    def testTurnTypeKnowledge(self):
        events = self.game.pop_new_events()
        self.assertEventsEqual(events, [SendTurnTypeEvent(self.archmage, self.game.turn.turn_type)])

    def testManaShield(self):
        self.next_turn_skip_events()
        archmage_mana = self.archmage.mana
        archmage_health = self.archmage.health
        attack_action = self.alice.attack(self.archmage)
        self.game.play_turn()
        self.assertEqual(self.archmage.health, archmage_health)
        self.assertEqual(self.archmage.mana, archmage_mana - 1)

        new_events = self.game.pop_new_events()
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
        alice_ball = self.archmage.play(Fireball, caller=self.archmage, target=self.alice)
        bob_ball = self.archmage.play(Fireball, caller=self.archmage, target=self.bob)
        self.game.play_turn()

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
        alice_ball = self.archmage.play(Fireball, caller=self.archmage, target=self.alice)
        self.archmage.play(Fireball, caller=self.archmage, target=self.bob)
        self.game.play_turn()

        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(alice_ball),
                DamageEvent(self.alice, 2, DamageType.BURNING, alice_ball)])

    def testManaStorm(self):
        self.next_turn_skip_events()
        self.game.turn.turn_type = TurnType.DIVINE_POWER

        self.archmage.mana = 3
        mana_storm = self.archmage.play(ManaStorm, caller=self.archmage)
        self.game.play_turn()
        self.assertEqual(self.alice.health, 2)
        self.assertEqual(self.bob.health, 2)
        self.assertEqual(self.archmage.health, 1)
        self.assertEqual(self.archmage.mana, 0)

        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(mana_storm),
                DamageEvent(self.alice, 1, DamageType.BURNING, mana_storm),
                DamageEvent(self.bob, 1, DamageType.BURNING, mana_storm)])

    def testManaStorm_Spamming(self):
        self.next_turn_skip_events()
        self.game.turn.turn_type = TurnType.DIVINE_POWER

        self.archmage.mana = 8
        mana_storm = self.archmage.play(ManaStorm, caller=self.archmage)
        self.archmage.play(ManaStorm, caller=self.archmage)
        self.game.play_turn()
        self.assertEqual(self.alice.health, 1)
        self.assertEqual(self.bob.health, 1)
        self.assertEqual(self.archmage.health, 1)
        self.assertEqual(self.archmage.mana, 2)

        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(mana_storm),
                ActionPlayedEvent(mana_storm),
                DamageEvent(self.alice, 1, DamageType.BURNING, mana_storm),
                DamageEvent(self.bob, 1, DamageType.BURNING, mana_storm),
                DamageEvent(self.alice, 1, DamageType.BURNING, mana_storm),
                DamageEvent(self.bob, 1, DamageType.BURNING, mana_storm)])


    def testChainLightning(self):
        self.next_turn_skip_events()
        self.game.turn.turn_type = TurnType.DIVINE_POWER

        self.archmage.mana = 5
        chain_lightning_action = self.archmage.play(ChainLightning, caller=self.archmage, target=self.alice)
        alice_attack = self.alice.attack(self.bob)
        self.game.play_turn()
        self.assertEqual(self.alice.health, 2)
        self.assertEqual(self.bob.health, 1)
        self.assertEqual(self.archmage.health, 1)
        self.assertEqual(self.archmage.mana, 3)

        chain_lightning_damage = ChainLightningDamage(self.archmage, None, None)
        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(chain_lightning_action),
                ActionPlayedEvent(alice_attack),
                DamageEvent(self.alice, 1, DamageType.BURNING, chain_lightning_damage),
                DamageEvent(self.bob, 1, DamageType.BURNING, chain_lightning_damage),
                DamageEvent(self.bob, 1, DamageType.PHISICAL, alice_attack)])

    def testElementalProtection(self):
        elemental_protection_action = ElementalProtection(self.archmage, self.archmage, self.alice)
        expected_daily_events =  [
            ActionPlayedEvent(elemental_protection_action),
            SendTurnTypeEvent(self.archmage, self.game.turn.turn_type)]

        # Day 1 - EP + CL
        self.game.turn.turn_type = TurnType.DIVINE_POWER

        self.archmage.play(ElementalProtection, caller=self.archmage, target=self.alice)

        self.game.play_turn()
        self.assertEventsEqual(self.game.pop_new_events(), expected_daily_events)

        # Night 1 (CL)
        self.game.start_new_turn()

        self.archmage.mana = 3
        chain_lightning_action = self.archmage.play(ChainLightning, caller=self.archmage, target=self.alice)
        alice_attack = self.alice.attack(self.bob)
        self.game.play_turn()
        self.assertEqual(self.alice.health, 3)
        self.assertEqual(self.bob.health, 1)
        self.assertEqual(self.archmage.health, 1)
        self.assertEqual(self.archmage.mana, 1)

        chain_lightning_damage = ChainLightningDamage(self.archmage, None, None)

        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(chain_lightning_action),
                ActionPlayedEvent(alice_attack),
                DamageEvent(self.bob, 1, DamageType.BURNING, chain_lightning_damage),
                DamageEvent(self.bob, 1, DamageType.PHISICAL, alice_attack)])

        self.bob.health = 3

        # Day 2 - EP + FB
        self.game.start_new_turn()

        self.game.turn.turn_type = TurnType.DIVINE_POWER

        self.archmage.play(ElementalProtection, caller=self.archmage, target=self.alice)

        self.game.play_turn()
        self.assertEventsEqual(self.game.pop_new_events(), expected_daily_events)

        # Night 2 (FB)
        self.game.start_new_turn()

        self.archmage.mana = 3
        self.archmage.play(Fireball, caller=self.archmage, target=self.alice)
        self.game.play_turn()
        self.assertEqual(self.alice.health, 3)
        self.assertEqual(self.archmage.health, 1)
        self.assertEqual(self.archmage.mana, 0)

        fireball_action = Fireball(self.archmage, self.archmage, self.alice)
        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(fireball_action)])

        # Day 3 - EP + MS
        self.game.start_new_turn()

        self.game.turn.turn_type = TurnType.DIVINE_POWER

        self.archmage.play(ElementalProtection, caller=self.archmage, target=self.alice)

        self.game.play_turn()
        self.assertEventsEqual(self.game.pop_new_events(), expected_daily_events)

        # Night 3 (MS)
        self.game.start_new_turn()

        self.archmage.mana = 3
        self.archmage.play(ManaStorm, caller=self.archmage)
        self.game.play_turn()
        self.assertEqual(self.alice.health, 3)
        self.assertEqual(self.bob.health, 2)
        self.assertEqual(self.archmage.health, 1)
        self.assertEqual(self.archmage.mana, 0)

        mana_storm = ManaStorm(self.archmage, self.archmage, None)
        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(mana_storm),
                DamageEvent(self.bob, 1, DamageType.BURNING, mana_storm)])

        # Day 3 - EP + MS
        self.game.start_new_turn()
        self.game.play_turn()
        self.next_turn_skip_events()


        # Night 4 (MS)
        self.game.turn.turn_type = TurnType.MAGIC_POWER
        self.archmage.mana = 3
        self.archmage.play(Fireball, caller=self.archmage, target=self.alice)
        self.game.play_turn()
        self.assertEqual(self.alice.health, -1)
        self.assertEqual(self.bob.health, 2)
        self.assertEqual(self.archmage.health, 1)
        self.assertEqual(self.archmage.mana, 0)

        self.assertEventsEqual(
            self.game.pop_new_events(), [
                ActionPlayedEvent(fireball_action),
                DamageEvent(self.alice, 4, DamageType.BURNING, fireball_action)])

import unittest
from collections import defaultdict
from unittest.mock import MagicMock

from core.game.action.common import Vote, BaseAttack
from core.game.characters.common import Character
from core.game.common import State, DamageType
from core.game.events.common import TurnStartEvent, TurnEndEvent, VoteEvent, ImprisonEvent, DamageEvent, DeathEvent, \
    ActionPlayedEvent
from core.game.exceptions import WrongTurnException
from core.game.game import Game
from core.game.turn import DayTurn, NightTurn


class GameBasicsTest(unittest.TestCase):
    def setUp(self):
        self.chars = [
            Character(MagicMock()),
            Character(MagicMock())]
        self.alice = self.chars[0]
        self.bob = self.chars[1]
        self.game = Game(self.chars, MagicMock())

    def testAttack_failDay(self):
        try:
            self.alice.attack(self.bob)
        except WrongTurnException as e:
            self.assertEquals(e.ability, BaseAttack)
            self.assertTrue(isinstance(e.turn, DayTurn))

    def testAttack_failCooldown(self):
        self.next_turn_skip_events()
        self.assertEqual(self.bob.health, 3)
        self.alice.attack(self.bob)
        self.alice.attack(self.bob)
        self.game.end_turn()
        self.assertEqual(self.bob.health, 2)

        new_events = self.game.pop_new_events()
        attack_action = BaseAttack(caller=self.alice, executor=self.alice, target=self.bob)
        expected_events = [
            ActionPlayedEvent(attack_action),
            DamageEvent(
                character=self.bob,
                strength=1,
                type=DamageType.PHISICAL,
                action=attack_action)]
        self.assertEventsEqual(new_events, expected_events)


    def testVote_failNight(self):
        self.next_turn_skip_events()
        try:
            self.alice.vote(self.bob)
        except WrongTurnException as e:
            self.assertEquals(e.ability, Vote)
            self.assertTrue(isinstance(e.turn, NightTurn))

    def testAttack(self):
        self.assertEquals(self.bob.health, 3)
        self.next_turn_skip_events()
        self.alice.attack(self.bob)
        self.game.end_turn()
        self.assertEquals(self.bob.health, 2)

        new_events = self.game.pop_new_events()
        attack_action = BaseAttack(caller=self.alice, executor=self.alice, target=self.bob)
        expected_events = [
            ActionPlayedEvent(attack_action),
            DamageEvent(
                character=self.bob,
                strength=1,
                type=DamageType.PHISICAL,
                action=attack_action)]
        self.assertEventsEqual(new_events, expected_events)


    def testAttack_kill(self):
        self.bob.health = 1
        self.next_turn_skip_events()
        self.alice.attack(self.bob)
        self.game.end_turn()
        self.assertEquals(self.bob.health, 0)
        self.assertEquals(self.bob.state, State.DEAD)

        new_events = self.game.pop_new_events()
        attack_action = BaseAttack(caller=self.alice, executor=self.alice, target=self.bob)
        expected_events = [
            DeathEvent(self.bob),
            ActionPlayedEvent(attack_action),
            DamageEvent(
                character=self.bob,
                strength=1,
                type=DamageType.PHISICAL,
                action=attack_action)]
        self.assertEventsEqual(new_events, expected_events)

    def testAttack_killWin(self):
        # Set sides
        self.alice.sides = {0}
        self.bob.sides = {1}
        # Kill one of the characters
        self.bob.health = 1
        self.next_turn_skip_events()
        self.alice.attack(self.bob)
        self.game.end_turn()
        self.assertEquals(self.bob.health, 0)
        self.assertEquals(self.bob.state, State.DEAD)

        new_events = self.game.pop_new_events()
        expected_damage_event = DamageEvent(
            character=self.bob,
            strength=1,
            type=DamageType.PHISICAL,
            action=BaseAttack(caller=self.alice, executor=self.alice, target=self.bob))
        self.assertEquals(
            filter_by_class(new_events, DamageEvent),
            [expected_damage_event])
        self.assertEquals(
            filter_by_class(new_events, DeathEvent),
            [DeathEvent(self.bob)])
        # self.assertEquals(
        #    filter_by_class(new_events, VictoryEvent),
        #    [VictoryEvent(0, [self.alice])])

    def testVote_imprison(self):
        self.assertEquals(self.bob.state, State.ALIVE)
        self.alice.vote(self.bob)
        self.game.end_turn()
        self.assertEqual(self.bob.state, State.IMPRISONED)

        vote_action = Vote(caller=self.alice, executor=self.alice, target=self.bob)
        expected_events = [
            VoteEvent(vote_action),
            ActionPlayedEvent(vote_action),
            ImprisonEvent(self.bob)]
        self.assertEventsEqual(self.game.pop_new_events(), expected_events)

    def testVote_dead(self):
        self.alice.state = State.DEAD
        self.alice.vote(self.bob)
        self.game.end_turn()
        self.assertEqual(self.bob.state, State.ALIVE)

        new_events = self.game.pop_new_events()
        self.assertEventsEqual(new_events, [])

    def testVote_tie(self):
        self.game.pop_new_events()
        self.assertEquals(self.alice.state, State.ALIVE)
        self.assertEquals(self.bob.state, State.ALIVE)
        self.alice.vote(self.bob)
        self.bob.vote(self.alice)
        self.game.end_turn()
        self.assertEquals(self.alice.state, State.ALIVE)
        self.assertEquals(self.bob.state, State.ALIVE)

        new_events = self.game.pop_new_events()
        vote_actions = [
            Vote(caller=self.bob, executor=self.bob, target=self.alice),
            Vote(caller=self.alice, executor=self.alice, target=self.bob)]
        expected_events = sum([
                                  [VoteEvent(v), ActionPlayedEvent(v)] for v in vote_actions], [])
        self.assertEventsEqual(new_events, expected_events)

    def next_turn_skip_events(self):
        self.game.end_turn()
        self.game.pop_new_events()

    def assertEventsEqual(self, events, expected_events, ignore_classes={TurnStartEvent, TurnEndEvent}):
        grouped_events = defaultdict(list)
        for e in events:
            if e.__class__ not in ignore_classes:
                grouped_events[e.__class__].append(e)
        grouped_expected_events = defaultdict(list)
        for e in expected_events:
            if e.__class__ not in ignore_classes:
                grouped_expected_events[e.__class__].append(e)
        self.assertEqual(set(grouped_events.keys()), set(grouped_expected_events.keys()))
        for k in grouped_events.keys():
            self.assertCountEqual(grouped_events[k], grouped_expected_events[k])


def filter_by_class(events, event_class):
    return [e for e in events if e.__class__ is event_class]


if __name__ == '__main__':
    unittest.main()

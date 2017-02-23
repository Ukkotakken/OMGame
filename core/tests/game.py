import unittest

from core.game.action.common import Vote, BaseAttack
from core.game.characters.common import Character
from core.game.common import State
from core.game.exceptions import WrongTurnException
from core.game.game import Game
from core.game.turn import DayTurn, NightTurn


class MockPlayer:
    def __init__(self, user_id):
        self.user_id = user_id
        self.character = None

    def set_character(self, character):
        self.character = character


class MockGameHandler:
    def send_message(self, text, user_id=None):
        pass

    def over(self):
        pass


class GameBasicsTest(unittest.TestCase):
    def setUp(self):
        self.chars = [
            Character(MockPlayer(1)),
            Character(MockPlayer(2))]
        self.game = Game(self.chars, MockGameHandler())

    def testAttack_failDay(self):
        try:
            self.chars[0].attack(self.chars[1])
        except WrongTurnException as e:
            self.assertEquals(e.ability, BaseAttack)
            self.assertTrue(isinstance(e.turn, DayTurn))

    def testVote_failNight(self):
        self.game.end_turn()
        try:
            self.chars[0].vote(self.chars[1])
        except WrongTurnException as e:
            self.assertEquals(e.ability, Vote)
            self.assertTrue(isinstance(e.turn, NightTurn))

    def testAttack(self):
        self.assertEquals(self.chars[1].health, 3)
        self.game.end_turn()
        self.chars[0].attack(self.chars[1])
        self.game.end_turn()
        self.assertEquals(self.chars[1].health, 2)

    def testAttack_kill(self):
        self.chars[1].health = 1
        self.game.end_turn()
        self.chars[0].attack(self.chars[1])
        self.game.end_turn()
        self.assertEquals(self.chars[1].health, 0)
        self.assertEquals(self.chars[1].state, State.DEAD)

    def testAttack_killWin(self):
        # Set sides
        self.chars[0].sides = {0}
        self.chars[1].sides = {1}
        # Wait a day
        self.game.end_turn()
        self.game.end_turn()
        # Kill one of the characters
        self.chars[1].health = 1
        self.game.end_turn()
        self.chars[0].attack(self.chars[1])
        self.game.end_turn()
        self.assertEquals(self.chars[1].health, 0)
        self.assertEquals(self.chars[1].state, State.DEAD)

    def testVote_imprison(self):
        self.assertEquals(self.chars[1].state, State.ALIVE)
        self.chars[0].vote(self.chars[1])
        self.game.end_turn()
        self.assertEqual(self.chars[1].state, State.IMPRISONED)

    def testVote_dead(self):
        self.chars[0].state = State.DEAD
        self.chars[0].vote(self.chars[1])
        self.game.end_turn()
        self.assertEqual(self.chars[1].state, State.ALIVE)

    def testVote_tie(self):
        self.assertEquals(self.chars[0].state, State.ALIVE)
        self.assertEquals(self.chars[1].state, State.ALIVE)
        self.chars[0].vote(self.chars[1])
        self.chars[1].vote(self.chars[0])
        self.game.end_turn()
        self.assertEquals(self.chars[0].state, State.ALIVE)
        self.assertEquals(self.chars[1].state, State.ALIVE)


if __name__ == '__main__':
    unittest.main()

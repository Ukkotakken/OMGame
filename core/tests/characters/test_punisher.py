from unittest.mock import MagicMock

from core.game.action.archmage import Fireball, ManaStorm, ChainLightning, ChainLightningEffect, ChainLightningDamage, \
    ElementalProtection
from core.game.action.common import BaseAttack
from core.game.characters.archmage import Archmage
from core.game.characters.common import Character
from core.game.characters.punisher import Punisher
from core.game.common import TurnType, DamageType
from core.game.events.archmage import SendTurnTypeEvent
from core.game.events.common import ActionPlayedEvent, DamageEvent, DeathEvent
from core.tests.test_game import GameTestBase


class PunisherTest(GameTestBase):
    def setUp(self):
        self.chars = [
            Punisher(MagicMock()),
            Archmage(MagicMock()),
            Character(MagicMock()),
            Character(MagicMock())
        ]
        self.punisher = self.chars[0]
        self.archmage = self.chars[1]
        self.alice = self.chars[2]
        self.bob = self.chars[3]
        self.alice.sides = self.bob.sides = {-1}
        super().setUp()

    def testPeanance(self):
        pass

    def testVengeance(self):
        pass

    def testVengeance_innocent(self):
        pass

    def testBloodhound(self):
        pass

    def testPunisherVote(self):
        pass
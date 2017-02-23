from core.game.common import TurnType
from core.game.events.common import Event


class SendTurnTypeEvent(Event):
    def __init__(self, character, turn_type):
        self.character = character
        self.turn_type = turn_type

    def play(self, game_handler):
        if self.turn_type is TurnType.DIVINE_POWER:
            self.character.player.send_message("You feel presence of divine powers!")
        elif self.turn_type is TurnType.MAGIC_POWER:
            self.character.player.send_message("You feel presence of magic powers!")

from mongoengine.fields import StringField, ReferenceField

from core.game.common import TurnType
from core.game.events.common import Event
from core.mongo.documents import CharacterDocument


class SendTurnTypeEvent(Event):
    character = ReferenceField(CharacterDocument)
    turn_type = StringField()

    def play(self, game_handler):
        if self.turn_type is TurnType.DIVINE_POWER:
            self.character.player.send_message("You feel presence of divine powers!")
        elif self.turn_type is TurnType.MAGIC_POWER:
            self.character.player.send_message("You feel presence of magic powers!")

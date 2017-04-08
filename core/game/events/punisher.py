from mongoengine.fields import ReferenceField, BooleanField

from core.game.events.common import Event
from core.mongo.documents import CharacterDocument


class PenanceEvent(Event):
    character = ReferenceField(CharacterDocument)
    penance_character = ReferenceField(CharacterDocument)

    def play(self, game_handler):
        # If character dies - send punisher his role
        pass


class BloodhoundEvent(Event):
    punisher = ReferenceField(CharacterDocument)
    character = ReferenceField(CharacterDocument)
    send_roles = BooleanField(default=False)

    def play(self, game_handler):
        # Self character.damaged_by_characters + roles if needed.
        pass


class PunishmentBanishEvent(Event):
    punisher = ReferenceField(CharacterDocument)

    def play(self, game_handler):
        # Send a message that punisher was banished from the class
        pass

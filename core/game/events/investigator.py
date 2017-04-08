from mongoengine.fields import ReferenceField, EmbeddedDocumentListField

from core.game.events.common import Event, DamageEvent
from core.mongo.documents import CharacterDocument


class AwarenessEvent(Event):
    character = ReferenceField(CharacterDocument)
    damage_events = EmbeddedDocumentListField(DamageEvent)

    def play(self, game_handler):
        pass


class InvestigationEvent(Event):
    character = ReferenceField(CharacterDocument)
    target = ReferenceField(CharacterDocument)

    def play(self, game_handler):
        pass
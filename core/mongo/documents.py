from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import ReferenceField, ListField, MapField


class EffectDocument(EmbeddedDocument):
    meta = {'allow_inheritance': True}


class EventDocument(EmbeddedDocument):
    meta = {'allow_inheritance': True}


class CharacterDocument(Document):
    meta = {'allow_inheritance': True}


class ActionDocument(Document):
    caller = ReferenceField(CharacterDocument)
    executor = ReferenceField(CharacterDocument)
    target = ReferenceField(CharacterDocument)

    meta = {'allow_inheritance': True}

class TurnDocument(Document):
    meta = {'allow_inheritance': True}

    actions = MapField(ListField(ActionDocument))


class PlayerDocument(Document):
    meta = {'allow_inheritance': True}


class GameHandlerDocument(Document):
    meta = {'allow_inheritance': True}

class GameDocument(Document):
    meta = {'allow_inheritance': True}

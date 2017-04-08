from mongoengine.fields import ReferenceField, FloatField, StringField, ListField

from core.mongo.documents import EventDocument, CharacterDocument, ActionDocument, TurnDocument


class Event(EventDocument):
    def play(self, game_handler):
        pass

    __hash__ = None

    def __eq__(self, other):
        return other.__class__ is self.__class__ and self.__dict__ == other.__dict__


class DeathEvent(Event):
    character = ReferenceField(CharacterDocument)

    def play(self, game_handler):
        game_handler.send_message("%s is dead!" % self.character.name)
        self.character.player.send_message("You are dead!")


class ImprisonEvent(Event):
    character = ReferenceField(CharacterDocument)

    def play(self, game_handler):
        game_handler.send_message("%s is sent to prison!" % self.character.name)
        self.character.player.send_message("You've got a prison sentence!")


class DamageEvent(Event):
    character = ReferenceField(CharacterDocument)
    strength = FloatField()
    type = StringField()
    action = ReferenceField(ActionDocument)


class ActionPlayedEvent(Event):
    action = ReferenceField(ActionDocument)


class VictoryEvent(Event):
    side = StringField()
    characters = ListField(ReferenceField(CharacterDocument))

    def play(self, game_handler):
        coalition = ', '.join(c.name for c in self.characters)
        game_handler.send_message("Coalition %s wins!" % coalition)
        for c in self.characters:
            c.player.send_message("You win!")


class TurnStartEvent(Event):
    turn = ReferenceField(TurnDocument)

    def play(self, game_handler):
        game_handler.send_message("%s starts!" % self.turn.NAME)
        for character in game_handler.game.characters:
            if character.in_play():
                character.player.send_status()


class TurnEndEvent(Event):
    turn = ReferenceField(TurnDocument)

    def play(self, game_handler):
        game_handler.send_message("%s is ended!" % self.turn.NAME)


class VoteEvent(Event):
    vote_action = ReferenceField(ActionDocument)

class InstantEvent(Event):
    pass


class VoteInstantEvent(InstantEvent):
    vote_action = ReferenceField(ActionDocument)

    def play(self, game_handler):
        game_handler.send_message(
            "%s votes for %s!" % (
                self.vote_action.executor, self.vote_action.target))

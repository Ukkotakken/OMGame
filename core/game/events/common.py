class Event:
    def play(self, game_handler):
        pass


class DeathEvent(Event):
    def __init__(self, character):
        self.character = character

    def play(self, game_handler):
        game_handler.send_message("%s is dead!" % self.character.name)
        self.character.player.send_message("You are dead!")


class ImprisonEvent(Event):
    def __init__(self, character):
        self.character = character

    def play(self, game_handler):
        game_handler.send_message("%s is sent to prison!" % self.character.name)
        self.character.player.send_message("You've got a prison sentence!")


class DamageEvent(Event):
    def __init__(self, character, strength, type, action):
        self.character = character
        self.strength = strength
        self.type = type
        self.action = action


class ActionPlayedEvent(Event):
    def __init__(self, action):
        self.action = action


class VictoryEvent(Event):
    def __init__(self, side, characters):
        self.side = side
        self.characters = characters

    def play(self, game_handler):
        coalition = ', '.join(c.name for c in self.characters)
        game_handler.send_message("Coalition %s wins!" % coalition)
        for c in self.characters:
            c.player.send_message("You win!")


class TurnStartEvent(Event):
    def __init__(self, turn):
        self.turn = turn

    def play(self, game_handler):
        game_handler.send_message("%s starts!" % self.turn.NAME)


class TurnEndEvent(Event):
    def __init__(self, turn):
        self.turn = turn

    def play(self, game_handler):
        game_handler.send_message("%s is ended!" % self.turn.NAME)


class VoteEvent(Event):
    def __init__(self, vote_action):
        self.vote_action = vote_action


class InstantEvent(Event):
    pass


class VoteInstantEvent(InstantEvent):
    def __init__(self, vote_action):
        self.vote_action = vote_action

    def play(self, game_handler):
        game_handler.send_message(
            "%s votes for %s!" % (
                self.vote_action.executor, self.vote_action.target))

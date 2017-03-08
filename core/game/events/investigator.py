from core.game.events.common import Event


class AwarenessEvent(Event):
    def __init__(self, character):
        self.character = character

    def play(self, game_handler):
        pass


class InvestigationEvent(Event):
    def __init__(self, character, target):
        self.character = character
        self.target = target

    def play(self, game_handler):
        pass
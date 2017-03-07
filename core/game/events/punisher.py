from core.game.events.common import Event


class PenanceEvent(Event):
    def __init__(self, character, peanance_character):
        self.character = character
        self.peanance_character = peanance_character

    def play(self, game_handler):
        # If character dies - send punisher his role
        pass


class BloodhoundEvent(Event):
    def __init__(self, punisher, character, send_roles=False):
        self.punisher = punisher
        self.character = character
        self.send_roles = send_roles

    def play(self, game_handler):
        # Self character.damaged_by_characters + roles if needed.
        pass


class PunishmentBanishEvent(Event):
    def __init__(self, punisher):
        self.punisher = punisher

    def play(self, game_handler):
        # Send a message that punisher was banished from the class
        pass

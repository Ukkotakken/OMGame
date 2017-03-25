class Argument:
    # name
    # argname

    def list_options(self, game):
        return []

    def transform_argument(self, value, game_handler):
        return None


class CharacterArgument(Argument):
    name = "target_player_id"
    argname = "target"

    def __init__(self, name="target_player_id", argname="target"):
        self.name = name
        self.argname = argname

    def list_options(self, game_handler):
        return [(str(p.user_id), str(p.user_id)) for p in game_handler.players.values()]

    def transform(self, value, game_handler):
        user_id = int(value)
        return game_handler.players[user_id].character
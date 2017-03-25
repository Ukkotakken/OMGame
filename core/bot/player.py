class Player:
    def __init__(self, user_id, chat_id, bot=None):
        self.chat_id = chat_id
        self.user_id = user_id
        self.game_handler = None
        self.bot = bot

    def send_message(self, text):
        self.bot.sendMessage(chat_id=self.chat_id, text=text)

    def join_game(self, game_handler):
        if self.game_handler is not None:
            self.send_message("You already participate in a game")
        elif game_handler is None:
            self.send_message("Game doesn't exist")
        else:
            self.game_handler = game_handler
            game_handler.add_player(self)
            self.send_message("You joined game %s" % game_handler.chat_id)

    def set_character(self, character):
        self.character = character

    def status(self):
        if self.game_handler is None:
            self.send_message("You are not participating in any game yet.")
        else:
            self.send_message("You are in a game %s" % self.game_handler.chat_id)
            if self.character is None:
                self.send_message("Game is not yet started")
            else:
                self.send_message(self.send_status_message(self.character.status()))

    def send_status_message(self, status):
        status_msg = "Your character status is following:\n"
        status_msg += "\tHealth: %s/%s\n" % (status.get("health", 0), status.get("max_health", 0))
        if status.get("mana") is not None:
            status_msg += "\tMana: %s\n" % status.get("mana")
        if status.get("base_attack"):
            status_msg += "\tBase attack: %s (type /attack player_id during night to attack)\n" % status.get("base_attack")
        status_msg += "\tVote strength: %s (type /vote player_id during day to vote)\n" % status.get("vote_strength")
        if status.get("abilities"):
            status_msg += "\tYou have following abilities:\n"
            for (ability, action) in status.get("abilities").items():
                status_msg += "\t\t%s\n" % ability
        self.send_message(status_msg)

    def desc(self, ability_name):
        if self.character is None:
            self.send_message("You should be in a game to use this command")
            return
        if ability_name not in self.character.abilities:
            self.send_message("You don't posess such an ability")
            return
        ability = self.character.abilities[ability_name]
        self.send_message(ability.description)

class Player:
    def __init__(self, user_id, chat_id, bot=None):
        self.chat_id = chat_id
        self.user_id = user_id
        self.game_handler = None
        self.character = None
        self.bot = bot

    def send_message(self, text):
        self.game_handler.send_message(text, user_id=self.user_id)

    def send_status(self):
        self.game_handler.send_status(user_id=self.user_id)

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
            return "You are not participating in any game yet."
        else:
            message_start = "You are in a game %s\n" % self.game_handler.chat_id
            if self.character is None:
                return message_start + "Game is not yet started"
            else:
                return message_start + self.make_status_message(self.character.status())

    def make_status_message(self, status):
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
        return status_msg

    def menu(self, query_line=""):
        query = query_line.strip().split()
        menus = {
            "play": self.play_menu,
            "vote": self.vote_menu,
            "attack": self.attack_menu
        }
        if query and query[0] != "menu":
            action = query[0]
            message, buttons = menus.get(action, self.error_menu)(query)
            buttons.append(("<- Back", ' '.join(query[:-1]) or 'menu'))
        else:
            message, buttons = self.default_menu()
        return message, buttons

    def default_menu(self, query=None):
        text = self.status()
        if not self.character:
            return text, []
        actions = [("Play", "play")]
        if self.character.vote_action.turn_step in self.character.game.turn.STEP_ORDER:
            actions.append(("Vote", "vote"))
        elif self.character.attack_action.turn_step in self.character.game.turn.STEP_ORDER:
            actions.append(("Attack", "attack"))
        return text, actions

    def error_menu(self, query, message=""):
        text = "Error encountered while processing query %s. %s" % (' '.join(query), message)
        return text, [("Main menu", "")]

    def vote_menu(self, query):
        return self.action_argument_menu(query, self.character.vote_action, query[1:])

    def attack_menu(self, query):
        return self.action_argument_menu(query, self.character.attack_action, query[1:])

    def status_menu(self, query):
        # TODO(ukkotakken): Add action query and cancel action button here.
        return self.status(), []

    def play_menu(self, query):
        query_base = ' '.join(query) + ' '
        if not self.character:
            return self.error_menu(query, message="You don't have a character to play an action.")
        if len(query) == 1:
            buttons = [(a.name, query_base + a.name) for a in self.character.abilities]
            return "Select ability:", buttons
        if query[1] not in self.character.abilities:
            return self.error_menu(query, message="You don't have such ability.")
        action = self.character.abilities[query[1]]
        return self.action_argument_menu(query_base, action, query[2:])

    def action_argument_menu(self, query, action, arguments):
        turn = self.character.game.turn
        if action.turn_step not in turn.STEP_ORDER:
            if len(arguments) >= len(action.arguments):
                return "Action %s can't be played during %s." % (action.name, turn.NAME), []
        if len(action.arguments) < len(arguments):
            # All arguments are filled. We should apply the action.
            kwargs = {"caller": self.character}
            for arg, value in zip(action.arguments, arguments):
                kwargs[arg.argname] = arg.transform(value, self.game_handler)
            self.character.play(action, **kwargs)
            return "You will try to play application %s" % query, [("Menu", "menu")]
        if len(action.arguments) == len(arguments):
            query.append("+")
            return "Approve %s call?" % query, [("Yes", ' '.join(query))]
        argument = action.arguments[len(arguments)]
        description = action.compose_description()
        if action.turn_step in turn.STEP_ORDER:
            description += '\n\nSelect %s:' % argument.name
            query_base = ' '.join(query) + ' '
            buttons = [(name, query_base + opt) for name, opt in  argument.list_options(self.game_handler)]
            return description, buttons
        else:
            description += "\n\nAction %s can't be played during %s." % (action.name, turn.NAME)
            return description, []

from telegram.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inlinekeyboardmarkup import InlineKeyboardMarkup

from core.game.characters.common import Character
from core.game.game import Game


class GameHandler:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.players = {}
        self.game = None

    def send_message(self, text, user_id=None):
        if user_id is None:
            self.bot.sendMessage(chat_id=self.chat_id, text=text)
        elif user_id in self.players:
            self.bot.sendMessage(chat_id=self.players[user_id].chat_id, text=text)
        else:
            # TODO(ukkotakken): Add no such user error
            pass

    def send_status(self, user_id):
        if user_id in self.players:
            player = self.players[user_id]
            text, buttons = player.menu()
            keyboard = [[InlineKeyboardButton(b_text, callback_data=b_callback)] for b_text, b_callback in buttons]
            reply_markup = InlineKeyboardMarkup(keyboard)
            self.bot.sendMessage(chat_id=player.chat_id, reply_markup=reply_markup, text=text)
        else:
            # TODO(ukkotakken): Add no such user error
            pass

    def add_player(self, player):
        self.players[player.user_id] = player
        self.send_message("Player %s joined the game!" % player.user_id)

    def end_turn(self, player):
        self.game.play_and_start_new_turn(player.character)
        self.resolve_events()

    def resolve_events(self):
        for event in self.game.pop_new_events():
            event.play(self)

    def start_game(self, bot):
        self.game = Game([Character(player) for player in self.players.values()], self)
        self.send_message(bot, """Game started!""")

    def end_game(self):
        # TODO(ukkotakken): implement end_game
        pass

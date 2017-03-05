import logging

from telegram.chat import Chat
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater

from core.game.characters.common import Character
from core.game.game import Game


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

    def set_character(self, character):
        self.character = character


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
            self.players[user_id].message(text)
        else:
            # TODO(ukkotakken): Add no such user error
            pass

    def add_player(self, player):
        self.players[player.user_id] = player

    def start_game(self, bot):
        self.game = Game([Character(player) for player in self.players.values()], self)
        self.send_message(bot, """Game started!""")

    def end_game(self):
        # TODO(ukkotakken): implement end_game
        pass


def extract_player_and_arguments(method):
    def extractor(self, bot, update):
        user_id = update.message.from_user.id
        player = self.players.get(user_id)
        args = update.message.text.split()[1:]
        return method(player, *args)

    return extractor


class Handler:
    def __init__(self):
        self.active_games = {}
        self.players = {}

    def setup_game(self, bot, update):
        game_chat_id = update.message.chat_id
        if game_chat_id not in self.active_games:
            game_handler = GameHandler(bot, game_chat_id)
            self.active_games[game_chat_id] = game_handler
            update.message.reply_text("""
                Game created.
                Send /join_game %s to this bot to join it.
                Send /start_game to this chat to start it.""" % (game_chat_id))
        else:
            game_handler = self.active_games[game_chat_id]
            if game_handler.game is None:
                update.message.reply_text("""
                    Game is already created.
                    Send /join_game %s to this bot to join it.
                    Send /start_game to this chat to start it.""" % (game_chat_id))
            else:
                update.message.reply_text("Game %s is in progress." % (game_chat_id))

    def join_game(self, bot, update):
        if update.message.chat.type is not Chat.PRIVATE:
            update.message.reply_text("You should send it to a private chat!")
            return

        user_id = update.message.from_user.id
        chat_id = update.message.chat_id
        player = self.players.setdefault(user_id, Player(user_id, chat_id, bot))

        parts = update.message.text.split()[1:]
        if len(parts) == 1:
            player.join_game(self.active_games.get(int(parts[0])))
        else:
            update.message.reply_text("Usage: /join_game game_id")

    def start_game(self, bot, update):
        game_handler = self.active_games.get(update.message.chat_id)
        if game_handler is None:
            update.message.reply_text("Start with: /setup_game")
        elif game_handler.game is None:
            game_handler.start_game()
        else:
            update.message.reply_text("Game is in progress!")

    @extract_player_and_arguments
    def play(self, player, ability_name, *args):
        pass

    @extract_player_and_arguments
    def vote(self, player, user_id):
        target_player = player.game_handler.players.get(user_id)
        if target_player is None:
            player.message("No such player in your game!")
        player.character.vote(target_player.character, caller=player.character)

    @extract_player_and_arguments
    def attack(self, player, user_id):
        target_player = player.game_handler.players.get(user_id)
        if target_player is None:
            player.message("No such player in your game!")
        player.character.attack(target_player.character, caller=player.character)

    @extract_player_and_arguments
    def end_turn(self, player):
        player.game_handler.game.play_and_start_new_turn(player.character)

    @extract_player_and_arguments
    def stats(self, player):
        player.message(player.stats())

    def help(self, bot, update):
        pass


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
with open('token') as t:
    token = t.read()
updater = Updater(token=token)
dispatcher = updater.dispatcher

h = Handler()
dispatcher.add_handler(CommandHandler("start_game", h.start_game))
dispatcher.add_handler(CommandHandler("vote", h.vote))
dispatcher.add_handler(CommandHandler('attack', h.attack))
dispatcher.add_handler(CommandHandler('play_and_start_new_turn', h.end_turn))
dispatcher.add_handler(CommandHandler('stats', h.stats))
dispatcher.add_handler(MessageHandler(Filters.command, h.help))

updater.start_polling()

import logging

from telegram.chat import Chat
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater

from core.bot.game_handler import GameHandler
from core.bot.player import Player


def extract_player_and_arguments(method):
    def extractor(self, bot, update):
        user_id = int(update.message.from_user.id)
        player = self.players.get(user_id)
        args = update.message.text.split()[1:]
        return method(self, player, *args)

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
        if update.message.chat.type != Chat.PRIVATE:
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
            game_handler.start_game(bot)
            update.message.reply_text("Game started! Players in game: %s" %
                                      ', '.join(map(str, game_handler.players.keys())))
            game_handler.resolve_events()
        else:
            update.message.reply_text("Game is in progress!")

    @extract_player_and_arguments
    def play(self, player, ability_name, *args):
        pass

    @extract_player_and_arguments
    def desc(self, player, ability_name):
        player.desc(ability_name)

    @extract_player_and_arguments
    def vote(self, player, user_id):
        target_player = player.game_handler.players.get(int(user_id))
        if target_player is None:
            player.send_message("No such player in your game!")
        player.character.vote(target_player.character)

    @extract_player_and_arguments
    def attack(self, player, user_id):
        target_player = player.game_handler.players.get(int(user_id))
        if target_player is None:
            player.send_message("No such player in your game!")
        player.character.attack(target_player.character)

    @extract_player_and_arguments
    def end_turn(self, player):
        player.game_handler.end_turn(player)

    @extract_player_and_arguments
    def status(self, player):
        player.status()

    def help(self, bot, update):
        pass


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
with open('token') as t:
    token = t.read()
updater = Updater(token=token)
dispatcher = updater.dispatcher

print("bot created")
h = Handler()
dispatcher.add_handler(CommandHandler("setup_game", h.setup_game))
dispatcher.add_handler(CommandHandler("join_game", h.join_game))
dispatcher.add_handler(CommandHandler("start_game", h.start_game))
dispatcher.add_handler(CommandHandler("vote", h.vote))
dispatcher.add_handler(CommandHandler('attack', h.attack))
dispatcher.add_handler(CommandHandler('end_turn', h.end_turn))
dispatcher.add_handler(CommandHandler('status', h.status))
dispatcher.add_handler(MessageHandler(Filters.command, h.help))
print("handler setted up")

updater.start_polling()
print("started_polling")
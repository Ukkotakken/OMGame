import logging

from telegram.chat import Chat
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inlinekeyboardmarkup import InlineKeyboardMarkup

from core.bot.game_handler import GameHandler
from core.bot.player import Player


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

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

    def end_turn(self, bot, update):
        player = self.players.get(int(update.message.from_user.id))
        player.game_handler.end_turn(player)

    def menu(self, bot, update):
        player = self.players.get(int(update.message.from_user.id))
        text, buttons = player.menu()
        keyboard = [[InlineKeyboardButton(b_text, callback_data=b_callback)] for b_text, b_callback in buttons]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text, reply_markup=reply_markup)

    def menu_button(self, bot, update):
        query = update.callback_query.data
        player = self.players.get(int(update.callback_query.from_user.id))
        text, buttons = player.menu(query_line=query)
        keyboard = [[InlineKeyboardButton(b_text, callback_data=b_callback)] for b_text, b_callback in buttons]
        if keyboard:
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reply_markup = None

        bot.editMessageText(text=text,
                            reply_markup=reply_markup,
                            chat_id=update.callback_query.message.chat_id,
                            message_id=update.callback_query.message.message_id)

    def help(self, bot, update):
        pass

    def error(self, bot, update, error):
        print(error)

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
dispatcher.add_handler(CommandHandler('end_turn', h.end_turn))
dispatcher.add_handler(CommandHandler('menu', h.menu))
dispatcher.add_handler(MessageHandler(Filters.command, h.help))
dispatcher.add_error_handler(h.error)
updater.dispatcher.add_handler(CallbackQueryHandler(h.menu_button))

print("handler setted up")

updater.start_polling()
print("started_polling")
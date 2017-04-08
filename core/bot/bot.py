import json
import logging

from telegram.chat import Chat
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inlinekeyboardmarkup import InlineKeyboardMarkup

from core.bot.game_handler import GameHandler
from core.bot.player import Player


class Handler:
    def __init__(self, bot_name):
        self.active_games = {}
        self.players = {}
        self.bot_name = bot_name

    def setup_game(self, bot, update):
        game_chat_id = update.message.chat_id
        join_game_url = "https://telegram.me/%s?start=%s" % (self.bot_name, game_chat_id)
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Join game!", url=join_game_url)]])
        if game_chat_id not in self.active_games:
            game_handler = GameHandler(chat_id=game_chat_id)
            self.active_games[game_chat_id] = game_handler
            update.message.reply_text("Game created.", reply_markup=reply_markup)
        else:
            game_handler = self.active_games[game_chat_id]
            if game_handler.game is None:
                update.message.reply_text("Game is already created.", reply_markup=reply_markup)
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
            game_handler = self.active_games.get(int(parts[0]))
            if player.game_handler is not None:
                player.send_message("You already participate in a game")
            elif game_handler is None:
                player.send_message("Game doesn't exist")
            else:
                player.game_handler = game_handler
                game_handler.add_player(player)
                text, reply_markup = self._prepare_menu(player)
                bot.sendMessage(text=text, chat_id=player.chat_id, reply_markup=reply_markup)
        else:
            update.message.reply_text("Usage: /start game_id")

    def end_turn(self, bot, update):
        player = self.players.get(int(update.message.from_user.id))
        player.game_handler.end_turn(player)

    def menu(self, bot, update):
        player = self.players.get(int(update.message.from_user.id))
        text, reply_markup = self._prepare_menu(player)
        update.message.reply_text(text, reply_markup=reply_markup)

    def _prepare_menu(self, player):
        text, buttons = player.menu()
        keyboard = [[InlineKeyboardButton(b_text, callback_data=b_callback)] for b_text, b_callback in buttons]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return text, reply_markup


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
with open('config.json') as json_data_file:
    config = json.load(json_data_file)
token = config['token']
bot_name = config['bot']

updater = Updater(token=token)
dispatcher = updater.dispatcher

h = Handler(bot_name)
dispatcher.add_handler(CommandHandler("start", h.join_game))
dispatcher.add_handler(CommandHandler("setup_game", h.setup_game))
dispatcher.add_handler(CommandHandler('end_turn', h.end_turn))
dispatcher.add_handler(CommandHandler('menu', h.menu))
dispatcher.add_handler(MessageHandler(Filters.command, h.help))
dispatcher.add_error_handler(h.error)
updater.dispatcher.add_handler(CallbackQueryHandler(h.menu_button))


updater.start_polling()

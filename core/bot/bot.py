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
            self.players[user_id].send_message(text)
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
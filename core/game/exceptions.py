class GameException(Exception):
    def __init__(self, desc):
        self.desc = desc


class NoActionInQueueException(GameException):
    def __init__(self, action_num):
        self.action_num = action_num


class UncancelableActionException(GameException):
    def __init__(self, action):
        self.action = action


class WrongTurnException(GameException):
    def __init__(self, ability, turn):
        self.ability = ability
        self.turn = turn

class BanishedFromClassException(GameException):
    def __init__(self):
        pass

class NoSuchPlayerException(GameException):
    def __init__(self, user_id):
        self.user_id = user_id

class MissingArgumentException(GameException):
    def __init__(self, argument):
        self.argument = argument
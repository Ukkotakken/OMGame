import random

from core.game.common import State, Step, TurnType
from core.game.events.common import ActionPlayedEvent
from core.game.victory import check_victory


class Turn:
    STEP_ORDER = []

    def __init__(self, turn_info):
        self.actions = {phase: [] for phase in self.STEP_ORDER}
        self.turn_info = turn_info

    def add_action(self, action):
        self.actions[action.turn_step].append(action)

    def start(self, game):
        check_victory(game)

    def play(self, game):
        for character in game.characters:
            for action in character.action_queue:
                if character.can_play(action):
                    self.add_action(action)
                    character.set_action_played(action, game)
                    game.log(ActionPlayedEvent(action))
            character.action_queue[:] = []

        for phase, actions in self.actions.items():
            for action in actions:
                action.play(game)
            for character in game.characters:
                character.apply_effects()


class DayTurn(Turn):
    NAME = "Day"

    STEP_ORDER = [Step.DAY_PASSIVE_STEP, Step.DAY_ACTIVE_STEP, Step.DAY_VOTE_STEP]

    def __init__(self, turn_info):
        super().__init__(turn_info)
        magic_mul = 1. / turn_info.setdefault('magic_nights', 1)
        divine_mul = 1. / turn_info.setdefault('divine_nights', 1)
        if random.random() * (magic_mul + divine_mul) > magic_mul:
            self.turn_type = TurnType.DIVINE_POWER
            turn_info['divine_nights'] += 1
        else:
            self.turn_type = TurnType.DIVINE_POWER
            turn_info['magic_nights'] += 1
        self.turn_info['turn_type'] = self.turn_type

    def _apply_death(self, game):
        for character in game.characters:
            if character.dies():
                character.death()

    def start(self, game):
        self._apply_death(game)
        super().start(game)


class NightTurn(Turn):
    NAME = "Night"

    STEP_ORDER = [Step.NIGHT_PASSIVE_STEP, Step.NIGHT_ACTIVE_STEP]

    def __init__(self, turn_info):
        super().__init__(turn_info)
        self.turn_type = turn_info['turn_type']

    def _apply_prison_sentence(self, game):
        max_votes, max_votes_char = 0, None
        for character in game.characters:
            if character.state != State.DEAD:
                if character.votes_number > max_votes:
                    max_votes = character.votes_number
                    max_votes_char = character
                elif character.votes_number == max_votes:
                    # In case of a tie nobody goes to prison
                    max_votes_char = None
                character.votes_number = 0  # TODO(ukkotakken): Test it
        if max_votes_char is not None:
            max_votes_char.imprison()

    def start(self, game):
        self._apply_prison_sentence(game)
        super().start(game)

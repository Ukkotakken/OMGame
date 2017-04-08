from mongoengine.fields import ReferenceField, ListField, EmbeddedDocumentListField, IntField

from core.game.events.common import TurnEndEvent, TurnStartEvent, InstantEvent
from core.game.turn import DayTurn, NightTurn
from core.mongo.documents import GameHandlerDocument, CharacterDocument, GameDocument, EventDocument, TurnDocument


class Game(GameDocument):
    """Workflow:

    0. start_new_turn is called.
    0.0. phase start game-level effects (death/victory conditions/information, death first).
    1. Users add ability requests to action queue via request_ability_apply
    1.0. If ability has instant user-visible effect - it is shown to all users.
    2. On time, play_turn is called.
    2.0. Game effects are played (victory conditions, player removal, etc).
    2.1. Actions (instance of ability-class) are sorted by phase.
    2.2. Actions in every phase are played simultaneously. Effects are applied after the phase.

    Main game effects:
    Death (Morning - <1 HP)
    Prison (Evening - MAX votes, clear votes)
    Winning condition check (including judge winning)
    Information morning:
        Night events (Investigator)
    Information evening:
        Night type (Inquisitor & Archmage)
    Special effect caller.
    """

    game_handler = ReferenceField(GameHandlerDocument)
    characters = ListField(ReferenceField(CharacterDocument))
    event_log = EmbeddedDocumentListField(EventDocument)
    new_events = EmbeddedDocumentListField(EventDocument)
    day_num = IntField(default=0)
    turn_id = IntField()
    turn = ReferenceField(TurnDocument)

    TURN_ORDER = [DayTurn, NightTurn]

    def __init__(self, characters, game_handler, turn_type_generator=None):
        super().__init__(characters=characters, game_handler=game_handler)
        self.turn_id = len(self.TURN_ORDER) - 1

        for c in characters:
            c.game = self

        self.start_new_turn()

    def log(self, event):
        if isinstance(event, InstantEvent):
            event.play(self.game_handler)
            self.event_log.append(event)
        else:
            self.new_events.append(event)

    def pop_new_events(self):
        new_events = self.new_events
        self.new_events = []
        self.event_log += new_events
        return new_events

    def start_new_turn(self):
        self.turn_id += 1
        if self.turn_id >= len(self.TURN_ORDER):
            self.turn_id -= len(self.TURN_ORDER)
            self.day_num += 1
        turn_info = {} if self.turn is None else self.turn.turn_info
        self.turn = self.TURN_ORDER[self.turn_id](turn_info)
        self.log(TurnStartEvent(self.turn))
        self.turn.start(self)
        self.apply_effects_turn_start()

    def play_turn(self):
        self.turn.play(self)
        self.apply_effects_turn_end()
        self.log(TurnEndEvent(self.turn))

    def play_and_start_new_turn(self, character=None):
        # TODO(ukkotakken): Implement waiting other players
        self.play_turn()
        self.start_new_turn()

    def message(self, text):
        self.game_handler.send_message(text)

    def over(self):
        self.game_handler.end_game()

    def apply_effects_turn_end(self):
        for character in self.characters:
            character.on_turn_end(self.turn)
            character.remove_passed_effects()

    def apply_effects_turn_start(self):
        for character in self.characters:
            character.on_turn_start(self.turn)
            character.remove_passed_effects()

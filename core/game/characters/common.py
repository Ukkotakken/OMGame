from mongoengine.fields import FloatField, IntField, ListField, StringField, EmbeddedDocumentListField, DictField, \
    ReferenceField

from core.game.action.common import Vote, BaseAttack
from core.game.common import DamageType, State
from core.game.events.common import DamageEvent, DeathEvent, ImprisonEvent, VoteInstantEvent
from core.game.exceptions import NoActionInQueueException, UncancelableActionException, WrongTurnException
from core.game.turn import NightTurn
from core.mongo.documents import CharacterDocument, EffectDocument, ActionDocument, GameDocument


def check_effects(method):
    def apply_effects(character, *args, **kwargs):
        try:
            progress = character.effects_progress.get(method.__name__, 0)
            is_applied = False
            return_value = None
            for i, effect in enumerate(character.effects[progress:], start=progress):
                if not hasattr(effect, method.__name__):
                    continue
                effect_method = getattr(effect, method.__name__)
                character.effects_progress[method.__name__] = i + 1
                is_applied = True
                return_value = effect_method(character, *args, **kwargs)
                break
            character.effects_progress[method.__name__] = 0
            if not is_applied:
                return_value = method(character, *args, **kwargs)
            return return_value
        except Exception as e:
            character.effects_progress[method.__name__] = 0
            raise e

    return apply_effects


class Character(CharacterDocument):
    health = FloatField()
    max_health = FloatField()
    mana = FloatField()
    sides = ListField(IntField())
    state = StringField()
    effects = EmbeddedDocumentListField(EffectDocument)
    action_queue = ListField(ReferenceField(ActionDocument))
    ability_played_time = DictField()
    game = ReferenceField(GameDocument)
    damaged_by = ListField(StringField)
    damaged_by_characters = ListField(ReferenceField(CharacterDocument))
    caused_damage = ListField(ReferenceField(CharacterDocument))
    killed = ListField(ReferenceField(CharacterDocument))

    start_health = 3
    start_max_health = 3
    start_mana = 0
    base_attack = 1
    vote_strength = 1
    attack_type = DamageType.PHISICAL
    role_abilities_list = []
    role_effects_list = []
    role_sides = set()
    attack_action = BaseAttack
    vote_action = Vote

    def __init__(self, player):
        if not hasattr(self.__class__, 'abilities'):
            self.__class__.abilities = {x.name: x for x in self.role_abilities_list}

        super().__init__(
            health=self.start_health,
            max_health=self.start_max_health,
            mana=self.start_mana,
            sides=list(self.role_sides),
            state=State.ALIVE,
            effects=list(self.role_effects_list),
            action_queue=[],
            ability_played_time={}
        )
        self.player = player
        self.player.set_character(self)

        self.effects_progress = {}
        self.votes_number = 0
        self.next_step_effects = []

    # Passive effects #####################################################

    @check_effects
    def receive_damage(self, strength, type, action):
        if strength > 0:
            if type not in self.damaged_by: self.damaged_by.append(type)
            self.health -= strength
            self.game.log(DamageEvent(self, strength, type, action))
            if action.executor:
                self.damaged_by_characters.append(action.executor)
                action.executor.on_cause_damage(self)

    @property
    def name(self):
        return str(self.player.user_id)

    @check_effects
    def receive_heal(self, strength, action):
        self.health = min(self.health + strength, self.max_health)
        if strength > 0:
            if DamageType.BLOODY_MESS in self.damaged_by:
                self.damaged_by = [DamageType.BLOODY_MESS]
            else:
                self.damaged_by = list()

    @check_effects
    def add_votes(self, number):
        self.votes_number += number

    @check_effects
    def add_effect(self, effect):
        self.next_step_effects.append(effect)

    @check_effects
    def dies(self):
        return self.state is not State.DEAD and self.health <= 0

    @check_effects
    def death(self):
        self.state = State.DEAD
        self.game.log(DeathEvent(self))
        for character in self.damaged_by_characters:
            character.on_kill(self)

    @check_effects
    def imprison(self):
        self.state = State.IMPRISONED
        self.game.log(ImprisonEvent(self))

    def apply_effects(self):
        self.effects += self.next_step_effects
        self.effects.sort(reverse=True)
        self.next_step_effects[:] = []

    def remove_effect(self, effect):
        effect.on_self_removal(self)
        self.effects.remove(effect)

    # Playable actions: ###################################################

    @check_effects
    def vote(self, character):
        vote = self.play(Vote, caller=self, target=character)
        self.game.log(VoteInstantEvent(vote))
        return vote

    @check_effects
    def attack(self, character):
        return self.play(BaseAttack, caller=self, target=character)

    @check_effects
    def play(self, ability, target=None, **kwargs):
        # TODO(ukkotakken): Check that action can be played (no CD problems in perspective, etc).
        if ability.turn_step not in self.game.turn.STEP_ORDER:
            raise WrongTurnException(ability, self.game.turn)
        action = ability(executor=self, target=target, **kwargs)
        action.play_user_visible_effect(self)
        self.action_queue.append(action)
        return action

    def cancel(self, action_num):
        if action_num >= len(self.action_queue):
            raise NoActionInQueueException(action_num)
        if not self.action_queue[action_num].can_cancel:
            raise UncancelableActionException(self.action_queue[action_num])
        del self.action_queue[action_num]

    # Game effects and so on #########################################

    @property
    @check_effects
    def attack_strength(self):
        return self.base_attack

    @check_effects
    def can_play(self, action):
        # Check if dead or imprisoned
        if self.state is not State.ALIVE:
            return False
        # Check cooldown
        played_day, played_turn = (
            self.ability_played_time.get(action.name, (0, 0)))
        time_passed = (self.game.day_num - played_day, self.game.turn_id - played_turn)
        if time_passed <= (action.cooldown, 1):
            return False
        # Check mana cost
        if action.mana_cost is not None:
            if self.mana < action.mana_cost:
                return False
        return action.can_play_check(self)

    def set_action_played(self, action, game):
        self.ability_played_time[action.name] = (game.day_num, game.turn_id)
        if action.mana_cost is not None:
            self.mana -= action.mana_cost

    @check_effects
    def on_turn_start(self, turn):
        if isinstance(turn, NightTurn):
            self.damaged_by_characters = list()

    @check_effects
    def on_turn_end(self, turn):
        pass

    @check_effects
    def on_cause_damage(self, character):
        if character not in self.caused_damage:
            self.caused_damage.append(character)

    @check_effects
    def on_kill(self, character):
        if character not in self.killed:
            self.killed.append(character)

    @check_effects
    def can_win(self):
        return self.state != State.IMPRISONED and self.state != State.DEAD

    @check_effects
    def prevents_victory(self, side):
        return side not in self.sides and self.state is State.ALIVE

    def remove_passed_effects(self):
        self.effects = [e for e in self.effects if not e.passed()]

    @check_effects
    def in_play(self):
        return self.state is not State.DEAD

    @check_effects
    def status(self):
        return {
            'health': self.health,
            'max_health': self.max_health,
            'mana': self.mana,
            'base_attack': self.base_attack,
            'vote_strength': self.vote_strength,
            'abilities': list(self.abilities.keys())
        }
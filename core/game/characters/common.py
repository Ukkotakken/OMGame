from core.game.action.common import Vote, BaseAttack
from core.game.common import DamageType, State
from core.game.events.common import DamageEvent, DeathEvent, ImprisonEvent, VoteInstantEvent
from core.game.exceptions import NoActionInQueueException, UncancelableActionException, WrongTurnException


def check_effects(method):
    """
    There are two different types of effects in this game:
    "__before" effects do some action on call of the effect, transform input or return another value.
    They must return two values - first one is return value, second one is transformed arguments (dict).
    If there transformed arguments are None, pipe will stop execution and apply "__after" effects.
    Example: Paladin protection is a pipe effect. It makes paladin suffer all damage instead of a character.
    Example: If a character is controlled by Puppeter, all can_play calls for his actions should return False this night.
    "__after" effects are for chaging actual return value, they get it and return something else.
    Example: There are buffs for base attack increase.
    """
    before_effect = "before__" + method.__name__
    after_effect = "after__" + method.__name__

    def _apply_before_effects(obj, *args, **kwargs):
        for effect in obj.effects:
            if not hasattr(effect, before_effect):
                continue
            effect_method = getattr(effect, before_effect)
            return_value, transformed_args = effect_method(
                obj, *args, **kwargs)
            if transformed_args is None:
                return return_value
            args, kwargs = transformed_args
        return method(obj, *args, **kwargs)

    def _apply_after_effects(obj, value, *args, **kwargs):
        for effect in obj.effects:
            if not hasattr(effect, after_effect):
                continue
            effect_method = getattr(effect, after_effect)
            value = effect_method(obj, value, *args, **kwargs)
        return value

    def check_effects_impl(obj, *args, **kwargs):
        value = _apply_before_effects(obj, *args, **kwargs)
        return _apply_after_effects(obj, value, *args, **kwargs)

    return check_effects_impl


class Character:
    start_health = 3
    start_max_health = 3
    start_mana = 0
    role_base_attack = 1
    role_vote_strength = 1
    role_attack_type = DamageType.PHISICAL
    role_abilities_list = []
    role_effects_list = []
    role_sides = set()

    def __init__(self, player):
        self.player = player
        self.player.set_character(self)

        self.health = self.start_health
        self.max_health = self.start_max_health
        self.mana = self.start_mana
        self.base_attack = self.role_base_attack
        self.vote_strength = self.role_vote_strength
        self.attack_type = self.role_attack_type
        self.sides = self.role_sides
        self.abilities = {x.name: x for x in self.role_abilities_list}
        self.effects = list(self.role_effects_list)
        self.state = State.ALIVE

        self.votes_number = 0
        self.damaged_by = set()
        self.next_step_effects = []
        self.action_queue = []
        self.last_played_time = {}  # Action -> (day_num, turn_id)
        self.game = None

    # Passive effects #####################################################

    @check_effects
    def receive_damage(self, strength, type, action):
        if strength > 0:
            self.damaged_by.add(type)
            self.health -= strength
            self.game.log(DamageEvent(self, strength, type, action))

    @property
    def name(self):
        return str(self.player.user_id)

    @check_effects
    def receive_heal(self, strength, action):
        self.health = min(self.health + strength, self.max_health)
        if strength > 0:
            if DamageType.BLOODY_MESS in self.damaged_by:
                self.damaged_by = {DamageType.BLOODY_MESS}
            else:
                self.damaged_by = set()

    @check_effects
    def add_votes(self, number):
        self.votes_number += number

    @check_effects
    def add_effect(self, effect):
        self.next_step_effects.append(effect)

    @check_effects
    def is_dead(self):
        return self.health <= 0

    @check_effects
    def death(self):
        self.state = State.DEAD
        self.game.log(DeathEvent(self))

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
        self.game.log(VoteInstantEvent(self.play(Vote, caller=self, target=character)))

    @check_effects
    def attack(self, character):
        self.play(BaseAttack, caller=self, target=character)

    @check_effects
    def play(self, ability, **kwargs):
        # TODO(ukkotakken): Check that action can be played (no CD problems, etc).
        if ability.turn_step not in self.game.turn.STEP_ORDER:
            raise WrongTurnException(ability, self.game.turn)
        action = ability(executor=self, **kwargs)
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
            self.last_played_time.get(action, (0, 0)))
        if (self.game.day_num - played_day, self.game.turn_id - played_turn) < (action.cooldown, 0):
            return False
        # Check mana cost
        if action.mana_cost is not None:
            if self.mana < action.mana_cost:
                return False
            else:
                self.mana -= action.mana_cost
        return True

    def set_action_played(self, action, game):
        self.last_played_time[action] = (game.day_num, game.turn_id)
        if action.mana_cost is not None:
            self.mana -= action.mana_cost

    @check_effects
    def turn_start(self, turn):
        pass

    @check_effects
    def turn_end(self, turn):
        pass

    @check_effects
    def can_win(self):
        return self.state != State.IMPRISONED and self.state != State.DEAD

    @check_effects
    def prevents_victory(self, side):
        return side not in self.sides and self.state is not State.ALIVE

    def remove_passed_effects(self):
        self.effects = [e for e in self.effects if not e.passed()]

from core.game.events.common import VictoryEvent


def check_victory(game):
    game_over = False
    for side in collect_sides(game):
        if wins(game, side):
            game_over = True
            victory(game, side)
    if game_over:
        game.over()


def collect_sides(game):
    sides = set()
    for character in game.characters:
        if character.can_win():
            sides |= set(character.sides)
    return sides


def wins(game, side):
    for character in game.characters:
        if character.prevents_victory(side):
            return False
    return True


def victory(game, side):
    characters = [c for c in game.characters if side in c.sides]
    game.log(VictoryEvent(side, characters))

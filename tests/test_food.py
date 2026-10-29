import random

from snake_game.food import spawn_food


def test_food_is_inside_board_and_not_on_snake():                   # SNK-F-007
    rng = random.Random(1)
    snake = [(2, 2), (1, 2), (0, 2)]
    for _ in range(100):
        x, y = spawn_food(5, 5, snake, rng)
        assert 0 <= x < 5 and 0 <= y < 5
        assert (x, y) not in snake


def test_food_uses_the_only_free_cell():                            # boundary case
    occupied = [(x, y) for x in range(3) for y in range(3) if (x, y) != (2, 2)]
    assert spawn_food(3, 3, occupied, random.Random(0)) == (2, 2)


def test_no_food_when_board_is_full():                              # boundary case
    occupied = [(x, y) for x in range(3) for y in range(3)]
    assert spawn_food(3, 3, occupied, random.Random(0)) is None

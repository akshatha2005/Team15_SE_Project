"""Integration tests: Snake + food + score working together in the engine."""
import random

import pytest

from snake_game.game_engine import GameEngine
from snake_game.score_manager import POINTS_PER_FOOD
from snake_game.snake import Snake


def make_engine(width=10, height=10):
    engine = GameEngine(width, height, rng=random.Random(1))
    engine.food = (0, 0)          # keep food out of the way unless a test needs it
    return engine


def test_new_game_snake_is_centred_with_three_segments():           # SNK-F-002/003
    e = GameEngine(20, 20)
    assert len(e.snake.body) == 3
    assert e.snake.head == (10, 10)
    assert e.food not in e.snake.body
    assert not e.game_over


def test_tick_moves_snake_one_cell():                               # SNK-F-004
    e = make_engine()
    start = e.snake.head
    e.tick()
    assert e.snake.head == (start[0] + 1, start[1])


def test_direction_change_applies_on_next_tick():                   # SNK-NF-002
    e = make_engine()
    start = e.snake.head
    e.set_direction("UP")
    e.tick()
    assert e.snake.head == (start[0], start[1] - 1)


@pytest.mark.parametrize("start,direction", [
    ((0, 5), "LEFT"),
    ((9, 5), "RIGHT"),
    ((5, 0), "UP"),
    ((5, 9), "DOWN"),
])
def test_hitting_any_wall_ends_the_game(start, direction):          # SNK-F-006
    e = make_engine()
    e.snake = Snake(start, direction=direction)
    e.tick()
    assert e.game_over


def test_eating_food_grows_snake_scores_and_respawns_food():        # SNK-F-007/008/009
    e = make_engine()
    e.food = (e.snake.head[0] + 1, e.snake.head[1])
    old_food = e.food
    e.tick()
    assert len(e.snake.body) == 4
    assert e.score.score == POINTS_PER_FOOD
    assert e.food != old_food
    assert e.food not in e.snake.body


def test_self_collision_ends_the_game():                            # SNK-F-010
    e = make_engine()
    e.snake.body = [(5, 5), (6, 5), (6, 4), (5, 4), (4, 4)]
    e.snake.direction = e.snake.next_direction = "UP"
    e.tick()
    assert e.game_over


def test_moving_into_the_cell_the_tail_just_left_is_allowed():      # boundary case
    e = make_engine()
    e.snake.body = [(5, 5), (6, 5), (6, 4), (5, 4)]
    e.snake.direction = e.snake.next_direction = "UP"
    e.tick()
    assert not e.game_over


def test_tick_does_nothing_after_game_over():
    e = make_engine()
    e.game_over = True
    before = list(e.snake.body)
    e.tick()
    assert e.snake.body == before


def test_reset_starts_a_fresh_game():                               # SNK-F-012
    e = make_engine()
    e.score.add_food()
    e.game_over = True
    e.reset()
    assert not e.game_over
    assert e.score.score == 0
    assert len(e.snake.body) == 3


def test_random_play_never_crashes():                               # SNK-NF-003
    rng = random.Random(0)
    for seed in range(20):
        e = GameEngine(10, 10, rng=random.Random(seed))
        for _ in range(300):
            e.set_direction(rng.choice(["UP", "DOWN", "LEFT", "RIGHT"]))
            e.tick()
        assert e.game_over or len(e.snake.body) >= 3

import pytest

from snake_game.difficulty import tick_interval
from snake_game.game_engine import GameEngine


@pytest.mark.parametrize("score,expected", [
    (0, 150), (49, 150), (50, 130), (51, 130),
    (99, 130), (100, 110), (101, 110),
    (149, 110), (150, 90), (151, 90),
    (199, 90), (200, 70), (201, 70),
    (249, 70), (250, 50), (251, 50), (1000000, 50),
])
def test_fixed_threshold_boundaries_and_minimum_interval(score, expected):
    assert tick_interval(score) == expected


def test_eating_food_crosses_threshold_and_reset_restores_speed():
    e = GameEngine()
    for _ in range(4):
        e.score.add_food()
    e.food = (e.snake.head[0] + 1, e.snake.head[1])
    assert e.tick_ms == 150
    e.tick()
    assert e.score.score == 50
    assert e.tick_ms == 130
    e.toggle_pause()
    assert e.tick_ms == 130
    e.reset()
    assert e.tick_ms == 150

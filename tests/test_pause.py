import random

from snake_game.game_engine import GameEngine


def test_pause_freezes_movement_food_score_and_direction():
    e = GameEngine(rng=random.Random(1))
    e.food = (e.snake.head[0] + 1, e.snake.head[1])
    before = list(e.snake.body), e.food, e.score.score
    e.toggle_pause()
    e.set_direction("UP")
    for _ in range(100):
        e.tick()
    assert (e.snake.body, e.food, e.score.score) == before
    assert e.snake.next_direction == "RIGHT"
    e.toggle_pause()
    e.tick()
    assert len(e.snake.body) == 4
    assert e.score.score == 10


def test_reset_clears_pause_and_game_over_cannot_be_resumed():
    e = GameEngine()
    e.toggle_pause()
    e.reset()
    assert not e.paused
    e.game_over = True
    e.toggle_pause()
    assert not e.paused

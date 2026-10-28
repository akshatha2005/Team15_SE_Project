"""Integration test: UI + engine together, run without a real window."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest

pygame = pytest.importorskip("pygame")

from snake_game.score_manager import POINTS_PER_FOOD
from snake_game.ui import GameUI


def test_score_starts_at_zero_and_is_drawn():                       # SNK-F-013
    ui = GameUI()
    assert ui.engine.score.score == 0
    ui.draw()
    pygame.quit()


def test_score_updates_after_eating_food():                         # SNK-F-013
    ui = GameUI()
    head_x, head_y = ui.engine.snake.head
    ui.engine.food = (head_x + 1, head_y)     # food directly in front of the snake
    ui.step()
    assert ui.engine.score.score == POINTS_PER_FOOD
    ui.draw()
    pygame.quit()


def test_board_and_centred_snake_are_drawn_before_first_tick():
    from snake_game.ui import CELL, GRID, GRID_W, GRID_H, HEAD, HUD

    ui = GameUI()
    try:
        initial_body = list(ui.engine.snake.body)
        ui.draw()
        assert ui.engine.snake.head == (GRID_W // 2, GRID_H // 2)
        assert len(initial_body) == 3
        assert ui.engine.snake.body == initial_body
        assert ui.screen.get_at((CELL, HUD + CELL))[:3] == GRID
        x, y = ui.engine.snake.head
        assert ui.screen.get_at((x * CELL + CELL // 2, HUD + y * CELL + CELL // 2))[:3] == HEAD
    finally:
        pygame.quit()



def test_pause_key_freezes_ui_and_resume_waits_for_next_tick(monkeypatch):
    from snake_game.ui import TICK_MS

    ui = GameUI()
    try:
        ui.engine.food = (0, 0)
        before = list(ui.engine.snake.body)
        ui.handle_key(pygame.K_p)
        ui.handle_key(pygame.K_UP)
        ui.advance(ui.last_tick + 10000)
        ui.step()
        ui.draw()
        assert ui.engine.paused
        assert ui.engine.snake.body == before
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 20000)
        ui.handle_key(pygame.K_p)
        assert not ui.engine.paused
        ui.advance(20000 + TICK_MS - 1)
        assert ui.engine.snake.body == before
        ui.advance(20000 + TICK_MS)
        assert ui.engine.snake.head == (before[0][0] + 1, before[0][1])
    finally:
        pygame.quit()

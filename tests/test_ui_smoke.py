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
"""Integration test: UI + engine together, run without a real window."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest

pygame = pytest.importorskip("pygame")

from snake_game.score_manager import POINTS_PER_FOOD
from snake_game.ui import GameUI


def test_menu_is_shown_first_and_start_begins_game():               # SNK-F-001
    ui = GameUI()
    assert ui.state == "menu"
    ui.draw()
    ui.handle_key(pygame.K_RETURN)            # "Start" is selected by default
    assert ui.state == "playing"
    ui.draw()
    pygame.quit()


def test_menu_navigation_wraps_around():                            # SNK-F-001
    ui = GameUI()
    ui.handle_key(pygame.K_UP)
    assert ui.selected == 2                   # wraps from "Start" to "Exit"
    pygame.quit()


def test_exit_menu_item_quits():                                    # SNK-F-001
    ui = GameUI()
    ui.handle_key(pygame.K_UP)                # wraps to "Exit"
    assert ui.handle_key(pygame.K_RETURN) is False
    pygame.quit()


def test_score_starts_at_zero_and_is_drawn():                       # SNK-F-013
    ui = GameUI()
    ui.start_game()
    assert ui.engine.score.score == 0
    ui.draw()
    pygame.quit()


def test_score_updates_after_eating_food():                         # SNK-F-013
    ui = GameUI()
    ui.start_game()
    head_x, head_y = ui.engine.snake.head
    ui.engine.food = (head_x + 1, head_y)     # food directly in front of the snake
    ui.step()
    assert ui.engine.score.score == POINTS_PER_FOOD
    ui.draw()
    pygame.quit()



def test_game_over_screen_after_hitting_a_wall():                   # SNK-F-011
    ui = GameUI()
    ui.start_game()
    for _ in range(100):                      # snake runs into the right wall
        ui.step()
        if ui.state == "game_over":
            break
    assert ui.state == "game_over"
    ui.draw()
    pygame.quit()


def test_game_over_shows_the_final_score():                         # SNK-F-011
    ui = GameUI()
    ui.start_game()
    ui.engine.score.add_food()
    ui.engine.game_over = True
    ui.step()
    assert ui.state == "game_over"
    assert ui.engine.score.score > 0
    ui.draw()
    pygame.quit()


def test_escape_on_game_over_returns_to_menu():                     # SNK-F-011
    ui = GameUI()
    ui.start_game()
    ui.engine.game_over = True
    ui.step()
    ui.handle_key(pygame.K_ESCAPE)
    assert ui.state == "menu"
    pygame.quit()
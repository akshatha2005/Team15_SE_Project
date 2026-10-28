"""Integration test: UI + engine together, run without a real window."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest

pygame = pytest.importorskip("pygame")

from snake_game.ui import FPS, GameUI


def test_menu_to_play_to_game_over_to_restart():                    # SNK-F-001/011/012
    ui = GameUI()
    assert ui.state == "menu"
    ui.draw()

    ui.handle_key(pygame.K_RETURN)            # "Start" is selected by default
    assert ui.state == "playing"
    ui.draw()

    for _ in range(100):                      # snake runs into the right wall
        ui.step()
        if ui.state == "game_over":
            break
    assert ui.state == "game_over"
    ui.draw()

    ui.handle_key(pygame.K_r)                 # restart
    assert ui.state == "playing"
    assert ui.engine.score.score == 0
    pygame.quit()


def test_exit_menu_item_quits():
    ui = GameUI()
    ui.handle_key(pygame.K_UP)                # wraps to "Exit"
    assert ui.handle_key(pygame.K_RETURN) is False
    pygame.quit()


def test_target_fps_is_60():                                        # SNK-NF-001
    ui = GameUI()
    assert ui.target_fps == 60
    assert FPS == 60
    pygame.quit()

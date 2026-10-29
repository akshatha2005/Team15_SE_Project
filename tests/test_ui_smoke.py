"""Integration tests: UI + engine + storage together, run without a real window."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest

pygame = pytest.importorskip("pygame")

from snake_game.score_manager import POINTS_PER_FOOD
from snake_game.storage import load_high_score, save_high_score
from snake_game.ui import CELL, FPS, GRID, GRID_H, GRID_W, HEAD, HUD, TICK_MS, GameUI


@pytest.fixture
def hs_path(tmp_path):
    return str(tmp_path / "hs.json")


@pytest.fixture
def ui(hs_path):
    game = GameUI(highscore_path=hs_path)
    yield game
    pygame.quit()


def play_until_game_over(ui):
    for _ in range(200):
        ui.step()
        if ui.state == "game_over":
            return
    raise AssertionError("game never ended")


def test_menu_to_play_to_game_over_to_restart(ui):                  # SNK-F-001/011/012
    assert ui.state == "menu"
    ui.draw()
    ui.handle_key(pygame.K_RETURN)            # "Start" is selected by default
    assert ui.state == "playing"
    ui.draw()
    play_until_game_over(ui)                  # snake runs into the right wall
    ui.draw()
    ui.handle_key(pygame.K_r)                 # restart
    assert ui.state == "playing"
    assert ui.engine.score.score == 0


def test_exit_menu_item_quits(ui):
    ui.handle_key(pygame.K_UP)                # wraps to "Exit"
    assert ui.handle_key(pygame.K_RETURN) is False


def test_target_fps_is_60(ui):                                      # SNK-NF-001
    assert ui.target_fps == 60 == FPS


def test_score_starts_at_zero_and_is_drawn(ui):                     # SNK-F-013
    ui.start_game()
    assert ui.engine.score.score == 0
    ui.draw()


def test_score_updates_after_eating_food(ui):                       # SNK-F-013
    ui.start_game()
    head_x, head_y = ui.engine.snake.head
    ui.engine.food = (head_x + 1, head_y)     # food directly in front of the snake
    ui.step()
    assert ui.engine.score.score == POINTS_PER_FOOD
    ui.draw()


def test_board_and_centred_snake_are_drawn_before_first_tick(ui):   # SNK-F-002/003
    ui.start_game()
    initial_body = list(ui.engine.snake.body)
    ui.draw()
    assert ui.engine.snake.head == (GRID_W // 2, GRID_H // 2)
    assert len(initial_body) == 3
    assert ui.engine.snake.body == initial_body
    assert ui.screen.get_at((CELL, HUD + CELL))[:3] == GRID
    x, y = ui.engine.snake.head
    assert ui.screen.get_at((x * CELL + CELL // 2, HUD + y * CELL + CELL // 2))[:3] == HEAD


def test_pause_key_freezes_ui_and_resume_waits_for_next_tick(ui, monkeypatch):   # SNK-F-016
    ui.start_game()
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


def test_ui_schedules_using_score_dependent_interval(ui):           # SNK-F-018
    ui.start_game()
    ui.engine.food = (0, 0)
    for _ in range(10):
        ui.engine.score.add_food()
    assert ui.engine.tick_ms == 110
    before = ui.engine.snake.head
    ui.last_tick = 1000
    ui.advance(1109)
    assert ui.engine.snake.head == before
    ui.advance(1110)
    assert ui.engine.snake.head == (before[0] + 1, before[1])


def test_game_over_saves_a_new_high_score(ui, hs_path):             # SNK-F-014/015
    ui.start_game()
    ui.engine.score.add_food()
    ui.engine.score.add_food()
    play_until_game_over(ui)
    assert ui.high_score == 2 * POINTS_PER_FOOD
    assert ui.new_high_score
    assert load_high_score(hs_path) == 2 * POINTS_PER_FOOD
    ui.draw()


def test_lower_score_does_not_replace_high_score(hs_path):          # SNK-F-015
    save_high_score(100, hs_path)
    game = GameUI(highscore_path=hs_path)
    try:
        assert game.high_score == 100
        game.start_game()
        play_until_game_over(game)
        assert load_high_score(hs_path) == 100
        assert not game.new_high_score
    finally:
        pygame.quit()


def test_high_score_menu_item_shows_saved_score(hs_path):           # SNK-F-014
    save_high_score(70, hs_path)
    game = GameUI(highscore_path=hs_path)
    try:
        game.handle_key(pygame.K_DOWN)        # "High Score"
        game.handle_key(pygame.K_RETURN)
        assert "70" in game.message
        game.draw()
    finally:
        pygame.quit()


def test_unusable_save_path_does_not_crash(tmp_path):               # SNK-NF-003 / SR-004
    game = GameUI(highscore_path=str(tmp_path))      # a folder, not a .json file
    try:
        game.start_game()
        play_until_game_over(game)
        game.draw()
        assert game.state == "game_over"
    finally:
        pygame.quit()

"""Run the real launchers in a fresh process on every target OS."""
import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize("launcher", ["script", "module"])
def test_desktop_launcher_plays_pauses_and_quits(launcher):
    script = r"""
import runpy
import sys
import pygame

frames = iter([
    [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)],
    [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)],
    [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)],
    # A later key in the same event batch must not undo window closure.
    [pygame.event.Event(pygame.QUIT), pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)],
])
pygame.event.get = lambda: next(frames)
if sys.argv[1] == "script":
    runpy.run_path("main.py", run_name="__main__")
else:
    runpy.run_module("snake_game", run_name="__main__")
assert not pygame.get_init()
print("PORTABILITY_SMOKE_OK")
"""
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    result = subprocess.run(
        [sys.executable, "-c", script, launcher],
        cwd=Path(__file__).resolve().parents[1],
        env=env, capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PORTABILITY_SMOKE_OK" in result.stdout

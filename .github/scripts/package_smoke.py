"""Check a wheel's checksums, install it, and run both installed launchers."""

import hashlib
import importlib.metadata
import os
from pathlib import Path
import subprocess
import sys
import tempfile


PLAY_AND_QUIT = r'''
import importlib.metadata
from pathlib import Path
import runpy
import sys

import pygame
import snake_game

expected = importlib.metadata.distribution("team15-snake-game").locate_file("snake_game").resolve()
assert Path(snake_game.__file__).resolve().parent == expected, "Must load the installed package"
frames = iter([
    [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)],
    [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)],
    [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)],
    [pygame.event.Event(pygame.QUIT)],
])
pygame.event.get = lambda: next(frames)
if sys.argv[1] == "module":
    runpy.run_module("snake_game", run_name="__main__")
else:
    entry = next(item for item in importlib.metadata.distribution("team15-snake-game").entry_points
                 if item.group == "console_scripts" and item.name == "team15-snake")
    entry.load()()
assert not pygame.get_init(), "The launcher must release Pygame resources"
print("INSTALLED_GAME_SMOKE_OK")
'''


def main():
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist").resolve()
    for line in (dist / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        expected, name = line.split(maxsplit=1)
        path = dist / name.lstrip("*")
        if path.parent != dist or not path.is_file():
            raise ValueError(f"Invalid artifact path: {name}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Checksum mismatch: {name}")
    wheels = list(dist.glob("*.whl"))
    if len(wheels) != 1:
        raise ValueError(f"Expected exactly one wheel, found {len(wheels)}")
    subprocess.run([sys.executable, "-m", "pip", "install", "--force-reinstall", str(wheels[0])], check=True)
    environment = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    environment.pop("PYTHONPATH", None)
    with tempfile.TemporaryDirectory() as directory:
        for launcher in ("module", "command"):
            result = subprocess.run(
                [sys.executable, "-I", "-c", PLAY_AND_QUIT, launcher],
                cwd=directory, env=environment, text=True, capture_output=True, timeout=30,
            )
            print(result.stdout)
            if result.returncode or "INSTALLED_GAME_SMOKE_OK" not in result.stdout:
                raise RuntimeError(f"Installed {launcher} launcher failed: {result.stderr}")
    print(f"Installed package {importlib.metadata.version('team15-snake-game')}: both launchers passed")


if __name__ == "__main__":
    main()

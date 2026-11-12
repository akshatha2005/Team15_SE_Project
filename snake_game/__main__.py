"""Launch the desktop game with python -m snake_game."""
from snake_game.ui import GameUI


def main():
    """Start the desktop game from the module or installed command."""
    GameUI().run()


if __name__ == "__main__":
    main()

"""Core game rules. (SNK-F-002, F-006, F-010, NF-005)

No pygame in here, so it can be unit tested without a display.
"""
import random

from snake_game.food import spawn_food
from snake_game.score_manager import ScoreManager
from snake_game.snake import Snake


class GameEngine:
    def __init__(self, width=20, height=20, rng=None):
        self.width = width
        self.height = height
        self.rng = rng or random.Random()
        self.score = ScoreManager()
        self.reset()

    def reset(self):
        self.snake = Snake((self.width // 2, self.height // 2))
        self.score.reset()
        self.food = spawn_food(self.width, self.height, self.snake.body, self.rng)
        self.game_over = False

    def set_direction(self, direction):
        self.snake.set_direction(direction)

    def in_bounds(self, cell):
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def tick(self):
        if self.game_over:
            return
        new_head = self.snake.next_head()
        if not self.in_bounds(new_head):
            self.game_over = True
            return

        ate = new_head == self.food
        # the tail cell is free again after a normal move, but not when growing
        body_to_check = self.snake.body if ate else self.snake.body[:-1]
        if new_head in body_to_check:
            self.game_over = True
            return

        self.snake.move(grow=ate)
        if ate:
            self.score.add_food()
            self.food = spawn_food(self.width, self.height, self.snake.body, self.rng)
            if self.food is None:      # board completely full
                self.game_over = True

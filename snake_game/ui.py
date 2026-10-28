"""Pygame front end: menu, board and live score. (SNK-F-001, F-013)"""
import pygame

from snake_game.game_engine import GameEngine
from snake_game.input_handler import key_to_direction

CELL = 24
GRID_W, GRID_H = 20, 20
HUD = 40
WIDTH, HEIGHT = GRID_W * CELL, GRID_H * CELL + HUD
TICK_MS = 150
MENU_ITEMS = ["Start", "High Score", "Exit"]

BG = (20, 24, 28)
GREEN = (80, 200, 120)
HEAD = (40, 150, 80)
RED = (220, 70, 70)
WHITE = (235, 235, 235)
GREY = (140, 140, 140)


class GameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.big = pygame.font.SysFont(None, 56)
        self.engine = GameEngine(GRID_W, GRID_H)
        self.state = "menu"          # menu / playing
        self.selected = 0
        self.message = ""
        self.last_tick = 0

    # ---------- logic ----------
    def start_game(self):
        self.engine.reset()
        self.state = "playing"
        self.message = ""
        self.last_tick = pygame.time.get_ticks()

    def step(self):
        """Advance the game by one tick."""
        self.engine.tick()

    def handle_key(self, key):
        """Handle one key press. Returns False when the game should quit."""
        name = pygame.key.name(key)
        if self.state == "menu":
            return self._menu_key(name)
        if self.state == "playing":
            direction = key_to_direction(name)
            if direction:
                self.engine.set_direction(direction)
            elif name == "escape":
                self.state = "menu"
        return True

    def _menu_key(self, name):
        if name in ("up", "w"):
            self.selected = (self.selected - 1) % len(MENU_ITEMS)
        elif name in ("down", "s"):
            self.selected = (self.selected + 1) % len(MENU_ITEMS)
        elif name == "return":
            item = MENU_ITEMS[self.selected]
            if item == "Start":
                self.start_game()
            elif item == "High Score":
                self.message = "High score arrives in Sprint 2"
            else:
                return False
        return True

    # ---------- drawing ----------
    def _text(self, text, font, color, center):
        img = font.render(text, True, color)
        self.screen.blit(img, img.get_rect(center=center))

    def draw(self):
        self.screen.fill(BG)
        if self.state == "menu":
            self._draw_menu()
        else:
            self._draw_board()
        pygame.display.flip()

    def _draw_menu(self):
        self._text("SNAKE", self.big, GREEN, (WIDTH // 2, 120))
        for i, item in enumerate(MENU_ITEMS):
            color = WHITE if i == self.selected else GREY
            label = f"> {item}" if i == self.selected else item
            self._text(label, self.font, color, (WIDTH // 2, 220 + i * 45))
        if self.message:
            self._text(self.message, self.font, RED, (WIDTH // 2, 420))
        self._text("Up/Down + Enter", self.font, GREY, (WIDTH // 2, HEIGHT - 30))

    def _draw_board(self):
        self._text(f"Score: {self.engine.score.score}", self.font, WHITE, (70, HUD // 2))
        if self.engine.food:
            fx, fy = self.engine.food
            pygame.draw.rect(self.screen, RED, (fx * CELL + 2, HUD + fy * CELL + 2, CELL - 4, CELL - 4))
        for i, (x, y) in enumerate(self.engine.snake.body):
            color = HEAD if i == 0 else GREEN
            pygame.draw.rect(self.screen, color, (x * CELL + 1, HUD + y * CELL + 1, CELL - 2, CELL - 2))

    # ---------- main loop ----------
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self.handle_key(event.key)
            if self.state == "playing":
                now = pygame.time.get_ticks()
                if now - self.last_tick >= TICK_MS:
                    self.step()
                    self.last_tick = now
            self.draw()
            self.clock.tick(60)
        pygame.quit()
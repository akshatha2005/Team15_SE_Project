"""Pygame front end: board and live score. (SNK-F-013)"""
import pygame

from snake_game.difficulty import BASE_TICK_MS
from snake_game.game_engine import GameEngine
from snake_game.input_handler import key_to_direction

CELL = 24
GRID_W, GRID_H = 20, 20
HUD = 40
WIDTH, HEIGHT = GRID_W * CELL, GRID_H * CELL + HUD
TICK_MS = BASE_TICK_MS

BG = (20, 24, 28)
GREEN = (80, 200, 120)
HEAD = (40, 150, 80)
RED = (220, 70, 70)
WHITE = (235, 235, 235)
GRID = (35, 40, 45)


class GameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.engine = GameEngine(GRID_W, GRID_H)
        self.last_tick = pygame.time.get_ticks()

    # ---------- logic ----------
    def step(self):
        """Advance the game by one tick."""
        self.engine.tick()

    def advance(self, now=None):
        """Schedule movement independently from rendering; paused time is ignored."""
        if now is None:
            now = pygame.time.get_ticks()
        if self.engine.paused or self.engine.game_over:
            return
        if now - self.last_tick >= self.engine.tick_ms:
            self.step()
            self.last_tick = now

    def handle_key(self, key):
        """Handle one key press."""
        if key == pygame.K_p:
            was_paused = self.engine.paused
            self.engine.toggle_pause()
            if was_paused and not self.engine.paused:
                # Resume with a full interval instead of catching up paused ticks.
                self.last_tick = pygame.time.get_ticks()
            return True
        direction = key_to_direction(pygame.key.name(key))
        if direction:
            self.engine.set_direction(direction)
        return True

    # ---------- drawing ----------
    def _text(self, text, font, color, center):
        img = font.render(text, True, color)
        self.screen.blit(img, img.get_rect(center=center))

    def draw(self):
        self.screen.fill(BG)
        self._draw_board()
        if self.engine.paused:
            panel = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 30, 240, 90)
            pygame.draw.rect(self.screen, BG, panel)
            pygame.draw.rect(self.screen, GRID, panel, 2)
            self._text("PAUSED", self.font, WHITE, (WIDTH // 2, HEIGHT // 2))
            self._text("P = resume", self.font, WHITE, (WIDTH // 2, HEIGHT // 2 + 30))
        pygame.display.flip()

    def _draw_board(self):
        # Fixed board is visible before the first movement tick (SNK-F-002).
        for x in range(GRID_W + 1):
            px = min(x * CELL, WIDTH - 1)
            pygame.draw.line(self.screen, GRID, (px, HUD), (px, HEIGHT - 1))
        for y in range(GRID_H + 1):
            py = min(HUD + y * CELL, HEIGHT - 1)
            pygame.draw.line(self.screen, GRID, (0, py), (WIDTH - 1, py))
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
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        running = self.handle_key(event.key)
                        if not running:
                            break
                if not running:
                    break
                self.advance()
                self.draw()
                self.clock.tick(60)
        finally:
            pygame.quit()

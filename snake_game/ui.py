"""Pygame front end: menu, board, score, pause, game-over and high score.
(SNK-F-001, F-011, F-012, F-013, F-014, F-015, F-016, F-018, NF-001)
"""
import pygame

from snake_game.difficulty import BASE_TICK_MS
from snake_game.game_engine import GameEngine
from snake_game.input_handler import key_to_direction
from snake_game.storage import DEFAULT_FILE, load_high_score, update_high_score

CELL = 24
GRID_W, GRID_H = 20, 20
HUD = 40
WIDTH, HEIGHT = GRID_W * CELL, GRID_H * CELL + HUD
TICK_MS = BASE_TICK_MS
FPS = 60
MENU_ITEMS = ["Start", "High Score", "Exit"]

BG = (20, 24, 28)
GREEN = (80, 200, 120)
HEAD = (40, 150, 80)
RED = (220, 70, 70)
WHITE = (235, 235, 235)
GREY = (140, 140, 140)
GRID = (35, 40, 45)


class GameUI:
    def __init__(self, highscore_path=DEFAULT_FILE):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.big = pygame.font.SysFont(None, 56)
        self.engine = GameEngine(GRID_W, GRID_H)
        self.state = "menu"          # menu / playing / game_over
        self.selected = 0
        self.message = ""
        self.last_tick = pygame.time.get_ticks()
        self.target_fps = FPS
        self.highscore_path = highscore_path
        self.high_score = load_high_score(highscore_path)
        self.new_high_score = False

    # ---------- logic ----------
    def start_game(self):
        self.engine.reset()
        self.state = "playing"
        self.message = ""
        self.new_high_score = False
        self.last_tick = pygame.time.get_ticks()

    def step(self):
        """Advance the game by one tick and update the screen state."""
        self.engine.tick()
        if self.engine.game_over and self.state != "game_over":
            self.state = "game_over"
            self._save_high_score()

    def _save_high_score(self):
        try:
            self.high_score, self.new_high_score = update_high_score(
                self.engine.score.score, self.highscore_path)
        except (OSError, ValueError):
            pass                      # a broken save file must never crash the game

    def advance(self, now=None):
        """Schedule movement independently from rendering; paused time is ignored."""
        if now is None:
            now = pygame.time.get_ticks()
        if self.state != "playing" or self.engine.paused or self.engine.game_over:
            return
        if now - self.last_tick >= self.engine.tick_ms:
            self.step()
            self.last_tick = now

    def handle_key(self, key):
        """Handle one key press. Returns False when the game should quit."""
        if self.state == "menu":
            return self._menu_key(pygame.key.name(key))
        if self.state == "playing":
            if key == pygame.K_p:
                was_paused = self.engine.paused
                self.engine.toggle_pause()
                if was_paused and not self.engine.paused:
                    # Resume with a full interval instead of catching up paused ticks.
                    self.last_tick = pygame.time.get_ticks()
                return True
            name = pygame.key.name(key)
            direction = key_to_direction(name)
            if direction:
                self.engine.set_direction(direction)
            elif name == "escape":
                self.state = "menu"
        elif self.state == "game_over":
            name = pygame.key.name(key)
            if name == "r":
                self.start_game()
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
                self.high_score = load_high_score(self.highscore_path)
                self.message = f"High score: {self.high_score}"
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
            if self.engine.paused:
                self._draw_paused()
            if self.state == "game_over":
                self._draw_game_over()
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
        # Fixed board is visible before the first movement tick (SNK-F-002).
        for x in range(GRID_W + 1):
            px = min(x * CELL, WIDTH - 1)
            pygame.draw.line(self.screen, GRID, (px, HUD), (px, HEIGHT - 1))
        for y in range(GRID_H + 1):
            py = min(HUD + y * CELL, HEIGHT - 1)
            pygame.draw.line(self.screen, GRID, (0, py), (WIDTH - 1, py))
        self._text(f"Score: {self.engine.score.score}", self.font, WHITE, (70, HUD // 2))
        self._text(f"High: {self.high_score}", self.font, GREY, (WIDTH - 70, HUD // 2))
        if self.engine.food:
            fx, fy = self.engine.food
            pygame.draw.rect(self.screen, RED, (fx * CELL + 2, HUD + fy * CELL + 2, CELL - 4, CELL - 4))
        for i, (x, y) in enumerate(self.engine.snake.body):
            color = HEAD if i == 0 else GREEN
            pygame.draw.rect(self.screen, color, (x * CELL + 1, HUD + y * CELL + 1, CELL - 2, CELL - 2))

    def _draw_paused(self):
        panel = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 30, 240, 90)
        pygame.draw.rect(self.screen, BG, panel)
        pygame.draw.rect(self.screen, GRID, panel, 2)
        self._text("PAUSED", self.font, WHITE, (WIDTH // 2, HEIGHT // 2))
        self._text("P = resume", self.font, WHITE, (WIDTH // 2, HEIGHT // 2 + 30))

    def _draw_game_over(self):
        self._text("GAME OVER", self.big, RED, (WIDTH // 2, HEIGHT // 2 - 50))
        self._text(f"Final score: {self.engine.score.score}", self.font, WHITE, (WIDTH // 2, HEIGHT // 2))
        if self.new_high_score:
            self._text("New high score!", self.font, GREEN, (WIDTH // 2, HEIGHT // 2 + 30))
        self._text("R = restart    Esc = menu", self.font, GREY, (WIDTH // 2, HEIGHT // 2 + 65))

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
                self.clock.tick(self.target_fps)
        finally:
            pygame.quit()

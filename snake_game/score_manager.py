"""Score tracking. (SNK-F-009, F-013)"""

POINTS_PER_FOOD = 10


class ScoreManager:
    def __init__(self):
        self.score = 0

    def add_food(self):
        self.score += POINTS_PER_FOOD

    def reset(self):
        self.score = 0

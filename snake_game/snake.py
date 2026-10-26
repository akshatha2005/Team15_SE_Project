"""Snake: body, direction and movement. (SNK-F-003, F-004, F-005, F-008)"""

DIRECTIONS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}


class Snake:
    def __init__(self, start, length=3, direction="RIGHT"):
        dx, dy = DIRECTIONS[direction]
        x, y = start
        # body[0] is the head
        self.body = [(x - dx * i, y - dy * i) for i in range(length)]
        self.direction = direction        # direction used for the last move
        self.next_direction = direction   # direction requested for the next move

    @property
    def head(self):
        return self.body[0]

    def set_direction(self, new_direction):
        """Ignore unknown directions and a direct reversal into the body."""
        if new_direction not in DIRECTIONS:
            return
        if new_direction == OPPOSITE[self.direction]:
            return
        self.next_direction = new_direction

    def next_head(self):
        dx, dy = DIRECTIONS[self.next_direction]
        x, y = self.head
        return (x + dx, y + dy)

    def move(self, grow=False):
        new_head = self.next_head()
        self.direction = self.next_direction
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

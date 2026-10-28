"""Food spawning. (SNK-F-007)"""


def spawn_food(width, height, occupied, rng):
    """Return a random free cell, or None if the board is full."""
    taken = set(occupied)
    free = [(x, y) for x in range(width) for y in range(height) if (x, y) not in taken]
    return rng.choice(free) if free else None

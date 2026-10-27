"""Maps key names to directions. (SNK-F-005, NF-002)"""

KEY_MAP = {
    "up": "UP", "w": "UP",
    "down": "DOWN", "s": "DOWN",
    "left": "LEFT", "a": "LEFT",
    "right": "RIGHT", "d": "RIGHT",
}


def key_to_direction(key_name):
    """Return 'UP'/'DOWN'/'LEFT'/'RIGHT', or None for any other key."""
    if not isinstance(key_name, str):
        return None
    return KEY_MAP.get(key_name.lower())

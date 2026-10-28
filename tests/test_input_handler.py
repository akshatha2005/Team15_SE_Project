from snake_game.input_handler import key_to_direction


def test_arrow_keys_map_to_directions():                            # SNK-F-005
    assert key_to_direction("up") == "UP"
    assert key_to_direction("down") == "DOWN"
    assert key_to_direction("left") == "LEFT"
    assert key_to_direction("right") == "RIGHT"


def test_wasd_keys_map_to_directions():
    assert key_to_direction("w") == "UP"
    assert key_to_direction("a") == "LEFT"
    assert key_to_direction("s") == "DOWN"
    assert key_to_direction("d") == "RIGHT"


def test_uppercase_key_names_work():
    assert key_to_direction("W") == "UP"


def test_unknown_or_invalid_keys_return_none():                     # error case
    assert key_to_direction("x") is None
    assert key_to_direction("") is None
    assert key_to_direction(None) is None

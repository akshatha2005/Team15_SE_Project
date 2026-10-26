from snake_game.snake import Snake


def make():
    return Snake((10, 10))   # length 3, heading RIGHT


def test_initial_snake_has_three_segments_heading_right():          # SNK-F-003
    s = make()
    assert s.body == [(10, 10), (9, 10), (8, 10)]
    assert s.direction == "RIGHT"


def test_move_advances_one_cell_and_keeps_length():                 # SNK-F-004
    s = make()
    s.move()
    assert s.body == [(11, 10), (10, 10), (9, 10)]


def test_move_with_grow_adds_one_segment():                         # SNK-F-008
    s = make()
    s.move(grow=True)
    assert len(s.body) == 4
    assert s.head == (11, 10)


def test_turn_up_changes_direction():                               # SNK-F-005
    s = make()
    s.set_direction("UP")
    s.move()
    assert s.head == (10, 9)


def test_direct_reversal_is_ignored():                              # SNK-F-005 (error case)
    s = make()
    s.set_direction("LEFT")
    s.move()
    assert s.head == (11, 10)


def test_two_quick_presses_cannot_reverse_into_body():              # boundary case
    s = make()
    s.set_direction("UP")
    s.set_direction("LEFT")      # would be a reversal of RIGHT once UP is applied
    s.move()
    assert s.head == (10, 9)     # the UP press wins, the LEFT press is ignored


def test_unknown_direction_is_ignored():                            # error case
    s = make()
    s.set_direction("DIAGONAL")
    s.move()
    assert s.head == (11, 10)

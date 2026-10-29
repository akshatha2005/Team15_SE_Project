from snake_game.score_manager import POINTS_PER_FOOD, ScoreManager


def test_score_starts_at_zero():                                    # SNK-F-013
    assert ScoreManager().score == 0


def test_score_increases_per_food():                                # SNK-F-009
    s = ScoreManager()
    s.add_food()
    s.add_food()
    assert s.score == 2 * POINTS_PER_FOOD


def test_reset_sets_score_to_zero():
    s = ScoreManager()
    s.add_food()
    s.reset()
    assert s.score == 0

import json

import pytest

from snake_game.storage import load_high_score, save_high_score


def test_missing_file_gives_zero(tmp_path):                         # SNK-F-014
    assert load_high_score(str(tmp_path / "none.json")) == 0


def test_saved_score_is_loaded_back(tmp_path):                      # SNK-F-014
    path = str(tmp_path / "hs.json")
    save_high_score(120, path)
    assert load_high_score(path) == 120


def test_saving_again_overwrites(tmp_path):
    path = str(tmp_path / "hs.json")
    save_high_score(50, path)
    save_high_score(90, path)
    assert load_high_score(path) == 90


def test_zero_is_a_valid_score(tmp_path):                           # boundary case
    path = str(tmp_path / "hs.json")
    save_high_score(0, path)
    assert load_high_score(path) == 0


def test_hand_edited_score_is_rejected(tmp_path):                   # SNK-SR-003
    path = tmp_path / "hs.json"
    save_high_score(50, str(path))
    data = json.loads(path.read_text())
    data["high_score"] = 99999
    path.write_text(json.dumps(data))
    assert load_high_score(str(path)) == 0


def test_missing_checksum_is_rejected(tmp_path):                    # SNK-SR-003
    path = tmp_path / "hs.json"
    path.write_text(json.dumps({"high_score": 70}))
    assert load_high_score(str(path)) == 0


def test_garbage_file_gives_zero(tmp_path):                         # error case
    path = tmp_path / "hs.json"
    path.write_text("not json at all {{{")
    assert load_high_score(str(path)) == 0


def test_wrong_json_shape_gives_zero(tmp_path):                     # error case
    path = tmp_path / "hs.json"
    path.write_text("[1, 2, 3]")
    assert load_high_score(str(path)) == 0


@pytest.mark.parametrize("bad", [-1, 3.5, "10", None, True])
def test_saving_an_invalid_score_raises(tmp_path, bad):             # error case
    with pytest.raises(ValueError):
        save_high_score(bad, str(tmp_path / "hs.json"))

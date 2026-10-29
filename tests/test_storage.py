import json
import os
import stat

import pytest

from snake_game.storage import (
    load_high_score,
    save_high_score,
    update_high_score,
)


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


# ---------- SNK-F-015: update high score only if higher ----------

def test_update_high_score_when_file_is_new(tmp_path):              # SNK-F-015
    path = str(tmp_path / "hs.json")
    score, updated = update_high_score(80, path)
    assert score == 80
    assert updated is True
    assert load_high_score(path) == 80


def test_update_high_score_when_higher(tmp_path):                   # SNK-F-015
    path = str(tmp_path / "hs.json")
    save_high_score(50, path)
    score, updated = update_high_score(70, path)
    assert score == 70
    assert updated is True
    assert load_high_score(path) == 70


def test_update_high_score_when_lower_keeps_old(tmp_path):          # SNK-F-015
    path = str(tmp_path / "hs.json")
    save_high_score(100, path)
    score, updated = update_high_score(60, path)
    assert score == 100
    assert updated is False
    assert load_high_score(path) == 100


def test_update_high_score_when_equal_does_not_update(tmp_path):    # SNK-F-015
    path = str(tmp_path / "hs.json")
    save_high_score(100, path)
    score, updated = update_high_score(100, path)
    assert score == 100
    assert updated is False
    assert load_high_score(path) == 100


@pytest.mark.parametrize("bad", [-5, "50", 12.3, None, True])
def test_update_high_score_invalid_score_raises(tmp_path, bad):     # SNK-F-015
    with pytest.raises(ValueError):
        update_high_score(bad, str(tmp_path / "hs.json"))


# ---------- SNK-SR-004: restrict file access to own save file ----------

@pytest.mark.skipif(os.name == 'nt', reason='POSIX file permissions do not apply on Windows')
def test_save_sets_owner_only_permissions(tmp_path):                # SNK-SR-004
    path = str(tmp_path / "hs.json")
    save_high_score(40, path)
    mode = stat.S_IMODE(os.stat(path).st_mode)
    assert mode == 0o600


def test_path_traversal_is_blocked(tmp_path):                       # SNK-SR-004
    dangerous = str(tmp_path / "subdir" / ".." / ".." / "escape.json")
    with pytest.raises(ValueError, match="Directory traversal is restricted"):
        save_high_score(50, dangerous)


def test_non_json_path_is_blocked(tmp_path):                        # SNK-SR-004
    bad_ext = str(tmp_path / "save.txt")
    with pytest.raises(ValueError, match="must have a .json extension"):
        save_high_score(50, bad_ext)


def test_load_from_traversal_path_returns_zero(tmp_path):           # SNK-SR-004
    dangerous = str(tmp_path / "sub" / ".." / ".." / "hs.json")
    assert load_high_score(dangerous) == 0

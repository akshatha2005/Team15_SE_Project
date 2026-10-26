"""High score save/load with a tamper check. (SNK-F-014, SNK-SR-003)

The score is stored as JSON next to a checksum. If the file is missing,
broken or edited by hand, load_high_score() falls back to 0.
"""
import hashlib
import json
import os

DEFAULT_FILE = "highscore.json"
_SALT = "snake-game-v1"


def _checksum(score):
    return hashlib.sha256(f"{_SALT}:{score}".encode()).hexdigest()


def save_high_score(score, path=DEFAULT_FILE):
    if isinstance(score, bool) or not isinstance(score, int) or score < 0:
        raise ValueError("score must be a non-negative integer")
    data = {"high_score": score, "checksum": _checksum(score)}
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(tmp, path)          # never leaves a half-written file


def load_high_score(path=DEFAULT_FILE):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return 0
    if not isinstance(data, dict):
        return 0
    score = data.get("high_score")
    if isinstance(score, bool) or not isinstance(score, int) or score < 0:
        return 0
    if data.get("checksum") != _checksum(score):
        return 0
    return score

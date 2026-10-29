"""High score save/load with checksum and access restrictions.
(SNK-F-014, SNK-F-015, SNK-SR-003, SNK-SR-004)

The score is stored as JSON next to a SHA-256 checksum. If the file is missing,
broken or edited by hand, load_high_score() falls back to 0.
File access is restricted to safe paths and owner-only permissions.
"""
import hashlib
import json
import os
import stat

DEFAULT_FILE = "highscore.json"
_SALT = "snake-game-v1"


def _checksum(score):
    return hashlib.sha256(f"{_SALT}:{score}".encode()).hexdigest()


def _validate_safe_path(path):
    """Ensure path is a valid JSON file and avoids directory traversal. (SNK-SR-004)"""
    if not isinstance(path, str) or not path.strip():
        raise ValueError("File path must be a non-empty string")
    # Reject paths attempting directory traversal with parent navigation
    raw_parts = path.replace("\\", "/").split("/")
    if ".." in raw_parts:
        raise ValueError(f"Directory traversal is restricted: {path}")
    norm = os.path.normpath(path)
    if not norm.endswith(".json"):
        raise ValueError("High score file must have a .json extension")
    return norm


def _restrict_permissions(path):
    """Restrict file permissions to owner read/write only (0o600). (SNK-SR-004)"""
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, NotImplementedError):
        pass


def save_high_score(score, path=DEFAULT_FILE):
    """Persist high score with SHA-256 checksum and restricted permissions. (SNK-F-014, SR-003, SR-004)"""
    if isinstance(score, bool) or not isinstance(score, int) or score < 0:
        raise ValueError("score must be a non-negative integer")
    safe_path = _validate_safe_path(path)
    data = {"high_score": score, "checksum": _checksum(score)}
    tmp = safe_path + ".tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(tmp, flags, stat.S_IRUSR | stat.S_IWUSR)
    with open(fd, "w", encoding="utf-8") as f:
        json.dump(data, f)
    _restrict_permissions(tmp)
    os.replace(tmp, safe_path)          # never leaves a half-written file
    _restrict_permissions(safe_path)


def load_high_score(path=DEFAULT_FILE):
    """Load high score validating checksum and safe path. Returns 0 on corruption or error."""
    try:
        safe_path = _validate_safe_path(path)
    except ValueError:
        return 0
    try:
        with open(safe_path, "r", encoding="utf-8") as f:
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


def update_high_score(score, path=DEFAULT_FILE):
    """Update and persist high score only if new score is strictly higher. (SNK-F-015)

    Returns tuple (current_high_score, was_updated).
    """
    if isinstance(score, bool) or not isinstance(score, int) or score < 0:
        raise ValueError("score must be a non-negative integer")
    current = load_high_score(path)
    if score > current:
        save_high_score(score, path)
        return score, True
    return current, False

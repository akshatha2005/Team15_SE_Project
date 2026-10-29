"""Fixed movement intervals in milliseconds for SNK-F-018.

Rendering remains independent of these movement intervals.
"""
BASE_TICK_MS = 150
SPEED_THRESHOLDS = ((50, 130), (100, 110), (150, 90), (200, 70), (250, 50))


def tick_interval(score):
    interval = BASE_TICK_MS
    for threshold, faster_interval in SPEED_THRESHOLDS:
        if score < threshold:
            break
        interval = faster_interval
    return interval

from __future__ import annotations
import time
from datetime import timedelta


def _countdown(minutes: int, label: str) -> None:
    seconds = minutes * 60
    end_message_shown = False
    while seconds > 0:
        remaining = str(timedelta(seconds=seconds))
        print(f"\r{label}: {remaining}   ", end="", flush=True)
        time.sleep(1)
        seconds -= 1
    print(f"\r{label}: done!           ")


def run_pomodoro(work: int, short_break: int, long_break: int, cycles: int) -> int:
    for cycle in range(1, cycles + 1):
        _countdown(work, f"Work {cycle}/{cycles}")
        if cycle < cycles:
            _countdown(short_break, "Short break")
        else:
            _countdown(long_break, "Long break")
    print("Pomodoro session complete.")
    return 0

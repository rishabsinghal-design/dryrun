"""
readme.py — Dynamic Visitor Counter
====================================
Tracks how many times this script has been run (i.e. "visited") by
persisting a count in a local JSON file (visitor_count.json).

Usage:
    python readme.py

Each invocation increments the counter and prints the current total.
"""

import json
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COUNTER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "visitor_count.json")


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def load_count(filepath: str = COUNTER_FILE) -> int:
    """Read the current visitor count from *filepath*.

    Returns 0 if the file does not exist or cannot be parsed.
    """
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return int(data.get("visitors", 0))
    except (json.JSONDecodeError, ValueError, OSError):
        return 0


def save_count(count: int, filepath: str = COUNTER_FILE) -> None:
    """Persist *count* to *filepath* as JSON."""
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump({"visitors": count}, fh, indent=2)


def increment_and_get(filepath: str = COUNTER_FILE) -> int:
    """Increment the visitor count by 1, save it, and return the new value."""
    new_count = load_count(filepath) + 1
    save_count(new_count, filepath)
    return new_count


def print_visitor_count(filepath: str = COUNTER_FILE) -> int:
    """Increment the counter, print a dynamic message, and return the count."""
    count = increment_and_get(filepath)

    # Dynamic suffix for a friendlier message
    if count == 1:
        suffix = "You are the very first visitor! 🎉"
    elif count < 10:
        suffix = "Welcome, early visitor! 👋"
    elif count < 100:
        suffix = "Thanks for stopping by! 😊"
    else:
        suffix = "You are part of a growing community! 🚀"

    print(f"👀  Total visitors: {count}  —  {suffix}")
    return count


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print_visitor_count()

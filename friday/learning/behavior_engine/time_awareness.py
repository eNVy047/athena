"""
F.R.I.D.A.Y. Time Awareness

Tracks time-of-day usage patterns and generates gentle suggestions
based on repeated behavior at specific times.

Design:
    - Divides the day into 4 buckets: morning, afternoon, evening, night
    - Records which actions (app opens, searches) happen in each bucket
    - After 3+ consistent observations → generates a suggestion
    - Never assumes — only suggests
    - Suggestions are phrased as observations, not commands

Example:
    "You usually open VS Code around this time. Would you like me to open it?"
"""
import logging
from datetime import datetime
from typing import List, Optional, Tuple

from friday.learning.behavior_engine.behavior_models import TimeOfDay
from friday.learning.behavior_engine.behavior_store import BehaviorStore

logger = logging.getLogger(__name__)

# Minimum observations before a suggestion is generated
_MIN_OBSERVATIONS = 3

# How much stronger the top action must be vs the second to generate a suggestion
_DOMINANCE_RATIO = 1.5


class TimeAwareness:
    """
    Tracks time-of-day usage patterns and generates suggestions.

    Relies on BehaviorStore for persistence (time_patterns bucket).
    """

    def __init__(self, store: BehaviorStore):
        self._store = store

    def record(self, action: str, time_of_day: Optional[str] = None) -> None:
        """
        Record that an action occurred at a given time of day.
        Uses current time if not specified.
        """
        tod = time_of_day or TimeOfDay.now().value
        self._store.record_time_pattern(tod, action)
        logger.debug("[TimeAwareness] Recorded: action=%r at %s", action, tod)

    def get_suggestion(self, time_of_day: Optional[str] = None) -> Optional[str]:
        """
        Return a natural language suggestion if a clear time-based pattern exists.
        Returns None if no strong pattern found.
        """
        tod = time_of_day or TimeOfDay.now().value
        top = self._store.top_time_actions(tod, n=2)

        if not top:
            return None

        top_action, top_count = top[0]

        # Need minimum observations
        if top_count < _MIN_OBSERVATIONS:
            return None

        # Need dominance over second place (or be the only one)
        if len(top) > 1:
            _, second_count = top[1]
            if second_count > 0 and top_count / second_count < _DOMINANCE_RATIO:
                return None  # No clear winner

        label = self._action_to_label(top_action)
        greeting = self._time_greeting(tod)

        return f"{greeting} — you usually {label} around this time. Shall I do that?"

    def get_all_patterns(self) -> List[Tuple[str, str, int]]:
        """
        Return all time-based patterns as (time_of_day, action, count) tuples.
        Sorted by count descending.
        """
        result = []
        for tod in ("morning", "afternoon", "evening", "night"):
            for action, count in self._store.get_time_pattern(tod).items():
                result.append((tod, action, count))
        return sorted(result, key=lambda x: x[2], reverse=True)

    # ── Natural language helpers ──────────────────────────────────────────────

    @staticmethod
    def _action_to_label(action: str) -> str:
        labels = {
            "open_editor":   "open your editor",
            "open_browser":  "open your browser",
            "open_music":    "open your music app",
            "open_terminal": "open the terminal",
            "open_email":    "check email",
            "open_calendar": "check your calendar",
            "browser.search": "search the web",
        }
        return labels.get(action, action.replace("_", " "))

    @staticmethod
    def _time_greeting(time_of_day: str) -> str:
        greetings = {
            "morning":   "Good morning",
            "afternoon": "Good afternoon",
            "evening":   "Good evening",
            "night":     "Working late",
        }
        return greetings.get(time_of_day, "Hey")

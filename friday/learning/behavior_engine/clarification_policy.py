"""
F.R.I.D.A.Y. Clarification Policy

Translates confidence levels into natural language conversation decisions.
This is the single place that determines HOW Friday communicates based on
how confident it is about a behavioral pattern.

Policy:
    LOW    (<0.40)  → Always ask with full menu
    MEDIUM (0.40-0.75) → Soft-confirm the top choice, allow easy override
    HIGH   (≥0.75)  → Execute directly, briefly mention it can be changed
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from friday.learning.behavior_engine.behavior_models import (
    BehaviorEntry,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)


# ── Option menus for each pattern ────────────────────────────────────────────

PATTERN_OPTIONS: Dict[str, List[str]] = {
    "open_browser":       ["Chrome", "Brave", "Safari", "Firefox", "Arc"],
    "open_editor":        ["VS Code", "Cursor", "PyCharm", "Xcode", "Vim"],
    "open_terminal":      ["Terminal", "iTerm2", "Warp", "Kitty"],
    "open_music":         ["Spotify", "Apple Music", "YouTube Music"],
    "open_email":         ["Mail", "Spark", "Superhuman", "Outlook"],
    "open_calendar":      ["Calendar", "Google Calendar", "Fantastical"],
    "search_engine":      ["Google", "DuckDuckGo", "Brave Search", "Bing"],
    "open_pdf":           ["Preview", "Adobe Acrobat", "PDF Expert"],
    "open_video":         ["QuickTime", "VLC", "IINA"],
    "open_communication": ["Slack", "Discord", "Teams", "Zoom"],
}


@dataclass
class ClarificationDecision:
    """
    The output of ClarificationPolicy.decide().
    ConversationManager uses this to formulate its response.
    """
    level: ConfidenceLevel
    should_ask: bool              # True = ask or soft-confirm before executing
    execute_immediately: bool     # True = execute without any question
    suggested_choice: Optional[str] = None   # The inferred top choice
    ask_text: str = ""            # The question / confirmation text to show
    options: List[str] = field(default_factory=list)  # For LOW-level menus
    post_execute_note: str = ""   # Optional note after execution ("Let me know if…")


class ClarificationPolicy:
    """
    Translates a (pattern, confidence_level, entry) into a conversation action.

    Used by ConversationManager before any tool execution that has
    multiple valid choices.
    """

    def decide(
        self,
        pattern: str,
        level: ConfidenceLevel,
        entry: Optional[BehaviorEntry],
        all_entries: Optional[Dict[str, BehaviorEntry]] = None,
    ) -> ClarificationDecision:
        """
        Return the clarification decision for the given pattern and confidence.
        """
        options = PATTERN_OPTIONS.get(pattern, [])
        best_choice = entry.choice if entry else None

        if level == ConfidenceLevel.HIGH:
            return self._high_confidence(pattern, best_choice, entry, options)
        elif level == ConfidenceLevel.MEDIUM:
            return self._medium_confidence(pattern, best_choice, entry, options, all_entries)
        else:
            return self._low_confidence(pattern, options)

    # ── HIGH confidence ───────────────────────────────────────────────────────

    def _high_confidence(
        self,
        pattern: str,
        choice: Optional[str],
        entry: Optional[BehaviorEntry],
        options: List[str],
    ) -> ClarificationDecision:
        """Execute immediately. Optionally add a brief note."""
        if not choice:
            return self._low_confidence(pattern, options)

        pct = round((entry.confidence if entry else 0.9) * 100)
        note = f"Just say so if you'd prefer a different option."

        return ClarificationDecision(
            level=ConfidenceLevel.HIGH,
            should_ask=False,
            execute_immediately=True,
            suggested_choice=choice,
            ask_text="",
            post_execute_note=note,
        )

    # ── MEDIUM confidence ─────────────────────────────────────────────────────

    def _medium_confidence(
        self,
        pattern: str,
        choice: Optional[str],
        entry: Optional[BehaviorEntry],
        options: List[str],
        all_entries: Optional[Dict[str, BehaviorEntry]] = None,
    ) -> ClarificationDecision:
        """Soft-confirm the top choice. Ask if they'd prefer something else."""
        if not choice:
            return self._low_confidence(pattern, options)

        verb = self._pattern_verb(pattern)
        label = self._pattern_label(pattern)
        ask = f"I'll {verb} {choice} — your usual {label}. Would you prefer a different one?"

        return ClarificationDecision(
            level=ConfidenceLevel.MEDIUM,
            should_ask=True,
            execute_immediately=False,
            suggested_choice=choice,
            ask_text=ask,
            options=[o for o in options if o != choice],
        )

    # ── LOW confidence ────────────────────────────────────────────────────────

    def _low_confidence(
        self,
        pattern: str,
        options: List[str],
    ) -> ClarificationDecision:
        """Full menu — ask every time."""
        label = self._pattern_label(pattern)
        if options:
            opts_str = "\n".join(f"• {o}" for o in options)
            ask = f"Which {label} would you like?\n{opts_str}"
        else:
            ask = f"Which {label} would you like?"

        return ClarificationDecision(
            level=ConfidenceLevel.LOW,
            should_ask=True,
            execute_immediately=False,
            suggested_choice=None,
            ask_text=ask,
            options=options,
        )

    # ── Natural language helpers ──────────────────────────────────────────────

    @staticmethod
    def _pattern_verb(pattern: str) -> str:
        verbs: Dict[str, str] = {
            "open_browser": "open",
            "open_editor":  "open",
            "open_terminal":"open",
            "open_music":   "open",
            "open_email":   "open",
            "open_calendar":"open",
            "search_engine":"search using",
            "open_pdf":     "open it in",
            "open_video":   "play it in",
            "open_communication": "open",
        }
        return verbs.get(pattern, "use")

    @staticmethod
    def _pattern_label(pattern: str) -> str:
        labels: Dict[str, str] = {
            "open_browser":       "browser",
            "open_editor":        "editor",
            "open_terminal":      "terminal",
            "open_music":         "music app",
            "open_email":         "email client",
            "open_calendar":      "calendar",
            "search_engine":      "search engine",
            "open_pdf":           "PDF reader",
            "open_video":         "video player",
            "open_communication": "communication app",
        }
        return labels.get(pattern, "option")

    # ── Parse user answers ────────────────────────────────────────────────────

    def parse_confirmation(self, user_text: str, suggested_choice: str) -> Optional[bool]:
        """
        Returns:
            True  → user confirmed the suggested choice
            False → user rejected it (negative feedback needed)
            None  → answer is a specific new choice, not a yes/no
        """
        text = user_text.lower().strip()
        YES = {"yes", "yeah", "yep", "sure", "ok", "okay", "go ahead", "do it",
               "sounds good", "fine", "alright", "please", "yup", "that's fine",
               "go on", "proceed", "correct", "right"}
        NO  = {"no", "nope", "nah", "not", "different", "another", "change",
               "switch", "other", "something else", "no thanks"}

        if text in YES or any(text.startswith(y) for y in YES):
            return True
        if text in NO or any(n in text for n in NO):
            return False
        return None  # The text is a specific choice

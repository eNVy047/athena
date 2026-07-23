"""
F.R.I.D.A.Y. Clarification Engine

Generates natural, context-aware follow-up questions when the assistant
doesn't have enough information to act. Uses the PreferenceManager to skip
clarification when a preference is already stored.
"""
import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ClarificationEngine:
    """
    Decides when clarification is needed and generates the right question.
    Uses LLM to generate natural, conversational follow-ups.
    Falls back to deterministic templates if LLM is unavailable.
    """

    # ── Templates for common clarification types ────────────────────────────
    _TEMPLATES: Dict[str, str] = {
        "preferred_editor": (
            "Which editor would you like me to open?\n"
            "• VS Code\n• Cursor\n• PyCharm\n• Xcode"
        ),
        "preferred_browser": (
            "Which browser would you like?\n"
            "• Chrome\n• Brave\n• Safari\n• Firefox"
        ),
        "preferred_music_app": (
            "Would you like Spotify, Apple Music, or YouTube Music?"
        ),
        "preferred_terminal": (
            "Which terminal would you like?\n"
            "• Terminal\n• iTerm2\n• Warp"
        ),
        "preferred_email_client": (
            "Which email client would you like me to open?\n"
            "• Mail\n• Spark\n• Outlook"
        ),
        "preferred_calendar": (
            "Would you like Calendar, Google Calendar, or Fantastical?"
        ),
        "generic": (
            "Could you be a bit more specific? What exactly would you like me to do?"
        ),
    }

    # ── Follow-up questions for multi-step tasks ─────────────────────────────
    _MULTI_STEP_STARTERS: Dict[str, str] = {
        "react": "Which React framework would you like?\n• Next.js\n• Vite\n• Remix",
        "python": "Which Python framework would you like to use?\n• Flask\n• FastAPI\n• Django",
        "project": "Which project would you like to work on? (or say 'continue' to resume the last one)",
    }

    def __init__(self, preference_manager=None, provider_manager=None):
        self._prefs = preference_manager
        self._pm = provider_manager

    def generate_question(
        self,
        clarification_topic: str,
        options: Optional[List[str]] = None,
        context: Optional[str] = None,
    ) -> str:
        """
        Generate a natural clarification question.
        Uses templates; can be upgraded to LLM generation.
        """
        if clarification_topic in self._TEMPLATES:
            question = self._TEMPLATES[clarification_topic]
        elif options:
            opts_str = "\n".join(f"• {o}" for o in options)
            question = f"Which would you prefer?\n{opts_str}"
        else:
            question = self._TEMPLATES["generic"]

        return question

    def parse_answer(
        self,
        user_answer: str,
        clarification_topic: str,
        options: List[str],
    ) -> Optional[str]:
        """
        Parse a user's answer to a clarification question.
        Matches against the provided options (fuzzy).
        Returns the matched option or None if not matched.
        """
        answer_lower = user_answer.lower().strip()

        # Direct match
        for opt in options:
            if opt.lower() == answer_lower:
                return opt

        # Substring match
        for opt in options:
            if opt.lower() in answer_lower or answer_lower in opt.lower():
                return opt

        # Common shorthand mappings
        shortcuts: Dict[str, Dict[str, str]] = {
            "preferred_editor": {
                "code": "VS Code", "vscode": "VS Code", "vs": "VS Code",
                "cursor": "Cursor", "pycharm": "PyCharm", "xcode": "Xcode",
                "vim": "Vim", "neovim": "Neovim",
            },
            "preferred_browser": {
                "chrome": "Chrome", "google": "Chrome",
                "brave": "Brave", "safari": "Safari",
                "firefox": "Firefox", "ff": "Firefox",
                "arc": "Arc",
            },
            "preferred_music_app": {
                "spotify": "Spotify", "apple": "Apple Music", "yt": "YouTube Music",
                "youtube": "YouTube Music", "youtube music": "YouTube Music",
            },
            "preferred_terminal": {
                "iterm": "iTerm2", "warp": "Warp", "term": "Terminal", "kitty": "Kitty",
            },
        }

        topic_shortcuts = shortcuts.get(clarification_topic, {})
        for shorthand, full in topic_shortcuts.items():
            if shorthand in answer_lower:
                return full

        return None

    def should_ask(
        self,
        clarification_topic: str,
        conversation_context: Optional[Dict] = None,
    ) -> bool:
        """
        Return True if clarification is actually needed.
        False if the preference is already known.
        """
        if self._prefs and self._prefs.has(clarification_topic):
            return False
        # Check if we just asked this question (avoid infinite loops)
        if conversation_context:
            last_clarification = conversation_context.get("last_clarification_topic")
            if last_clarification == clarification_topic:
                return False
        return True

    def build_proactive_suggestion(
        self,
        executed_intent: str,
        executed_params: Dict[str, Any],
        preference_manager=None,
    ) -> Optional[str]:
        """
        After successfully executing an action, generate a proactive follow-up suggestion.
        Returns None if no suggestion is warranted.
        """
        suggestions: Dict[str, str] = {
            "launcher.open_application": {
                "VS Code": "Would you also like me to open your last project?",
                "Google Chrome": "Should I restore your previous tabs?",
                "Chrome": "Should I restore your previous tabs?",
                "Spotify": "Any specific song or playlist you'd like me to start?",
                "Terminal": "Would you like me to navigate to your project directory?",
            }.get(executed_params.get("app_name", ""), None),
            "browser.open_url": (
                "Would you like me to summarize the page after it loads?"
                if "youtube" not in executed_params.get("url", "")
                else None
            ),
            "browser.search": "Would you like me to open any of the results for you?",
            "memory.store": "Got it! I'll remember that for future conversations.",
        }

        suggestion = suggestions.get(executed_intent)
        return suggestion if suggestion else None

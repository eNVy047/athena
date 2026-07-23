"""
F.R.I.D.A.Y. Preference Manager

Stores, retrieves, and auto-learns user preferences.
Backed by a local JSON file with optional Mem0 sync.
Preferences are loaded on startup and cached in-memory for fast access.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ── Canonical preference keys ───────────────────────────────────────────────
PREF_EDITOR = "preferred_editor"
PREF_BROWSER = "preferred_browser"
PREF_MUSIC_APP = "preferred_music_app"
PREF_TERMINAL = "preferred_terminal"
PREF_SEARCH_ENGINE = "preferred_search_engine"
PREF_LANGUAGE = "preferred_language"
PREF_SHELL = "preferred_shell"
PREF_EMAIL_CLIENT = "preferred_email_client"
PREF_CALENDAR = "preferred_calendar"
PREF_IDE = "preferred_ide"
PREF_LLM = "preferred_llm"
PREF_VOICE = "preferred_voice"

# ── Options for clarification menus ────────────────────────────────────────
PREFERENCE_OPTIONS: Dict[str, list] = {
    PREF_EDITOR:        ["VS Code", "Cursor", "PyCharm", "Xcode", "Vim", "Neovim"],
    PREF_BROWSER:       ["Chrome", "Brave", "Safari", "Firefox", "Arc"],
    PREF_MUSIC_APP:     ["Spotify", "Apple Music", "YouTube Music"],
    PREF_TERMINAL:      ["Terminal", "iTerm2", "Warp", "Kitty"],
    PREF_SEARCH_ENGINE: ["Google", "DuckDuckGo", "Bing", "Brave Search"],
    PREF_LANGUAGE:      ["Python", "JavaScript", "TypeScript", "Go", "Rust", "Swift"],
    PREF_EMAIL_CLIENT:  ["Mail", "Spark", "Superhuman", "Outlook"],
    PREF_CALENDAR:      ["Calendar", "Google Calendar", "Fantastical"],
}


class PreferenceManager:
    """
    Manages persistent user preferences across conversations.

    Preferences are stored in `friday_data/preferences/user_prefs.json`
    and kept in an in-memory cache for O(1) reads.
    Auto-learns from repeated interactions via `observe()`.
    """

    def __init__(self, storage_root: Path = Path("friday_data")):
        self._prefs_file = storage_root / "preferences" / "user_prefs.json"
        self._prefs: Dict[str, Any] = {}
        self._usage_counts: Dict[str, Dict[str, int]] = {}  # for auto-learning
        self._load()

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load preferences from disk."""
        try:
            if self._prefs_file.exists():
                with open(self._prefs_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self._prefs = data.get("preferences", {})
                    self._usage_counts = data.get("usage_counts", {})
                logger.debug("[Prefs] Loaded %d preference(s) from disk.", len(self._prefs))
        except Exception as exc:
            logger.warning("[Prefs] Failed to load preferences: %s", exc)
            self._prefs = {}
            self._usage_counts = {}

    def _save(self) -> None:
        """Persist preferences to disk."""
        try:
            self._prefs_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._prefs_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "preferences": self._prefs,
                        "usage_counts": self._usage_counts,
                        "updated_at": datetime.utcnow().isoformat(),
                    },
                    f,
                    indent=2,
                )
        except Exception as exc:
            logger.error("[Prefs] Failed to save preferences: %s", exc)

    # ── Core API ─────────────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Return a preference value, or default if not set."""
        return self._prefs.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Explicitly set a preference and persist."""
        self._prefs[key] = value
        logger.info("[Prefs] Set: %s = %r", key, value)
        self._save()

    def has(self, key: str) -> bool:
        """Return True if a preference is set and non-empty."""
        val = self._prefs.get(key)
        return val is not None and val != ""

    def all(self) -> Dict[str, Any]:
        """Return all stored preferences."""
        return dict(self._prefs)

    # ── Auto-learning ────────────────────────────────────────────────────────

    def observe(self, key: str, value: str) -> None:
        """
        Observe a usage event (e.g., user picked 'VS Code').
        After 2 consistent uses of the same value, it becomes the stored preference.
        """
        if not value:
            return
        bucket = self._usage_counts.setdefault(key, {})
        bucket[value] = bucket.get(value, 0) + 1
        # Auto-promote to preference after 2 consistent uses
        if bucket[value] >= 2 and self._prefs.get(key) != value:
            logger.info("[Prefs] Auto-learned: %s = %r (used %d times)", key, value, bucket[value])
            self.set(key, value)

    # ── Convenience helpers ──────────────────────────────────────────────────

    def get_editor(self) -> Optional[str]:
        return self.get(PREF_EDITOR) or self.get(PREF_IDE)

    def get_browser(self) -> Optional[str]:
        return self.get(PREF_BROWSER)

    def get_music_app(self) -> Optional[str]:
        return self.get(PREF_MUSIC_APP)

    def get_terminal(self) -> Optional[str]:
        return self.get(PREF_TERMINAL)

    def parse_and_store_explicit(self, user_text: str) -> Optional[str]:
        """
        Detect explicit preference statements in user text.
        E.g. "I prefer VS Code", "Always use Chrome", "My editor is Cursor".
        Returns the key set if one was found, else None.
        """
        text_lower = user_text.lower()

        patterns = [
            (PREF_EDITOR,    ["vs code", "vscode", "cursor", "pycharm", "xcode", "vim", "neovim"]),
            (PREF_BROWSER,   ["chrome", "brave", "safari", "firefox", "arc"]),
            (PREF_MUSIC_APP, ["spotify", "apple music", "youtube music"]),
            (PREF_TERMINAL,  ["iterm", "warp", "kitty", "terminal"]),
            (PREF_LANGUAGE,  ["python", "javascript", "typescript", "go", "rust", "swift"]),
        ]

        # Only act if the text has a preference signal
        trigger_words = ["prefer", "use ", "always", "favorite", "favourite", "my editor", "my browser",
                         "default", "i like", "set", "remember"]
        if not any(t in text_lower for t in trigger_words):
            return None

        for pref_key, options in patterns:
            for opt in options:
                if opt in text_lower:
                    display = opt.title() if opt != "vs code" else "VS Code"
                    self.set(pref_key, display)
                    logger.info("[Prefs] Detected explicit preference: %s = %s", pref_key, display)
                    return pref_key
        return None

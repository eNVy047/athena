"""
Completion — Tab-completion for the F.R.I.D.A.Y. interactive shell.

Provides readline-based completion for:
- Slash commands  (/status, /providers, /memory, /doctor …)
- Common Friday commands (open, play, search, remember …)
- App names, known websites
"""
from __future__ import annotations

import readline
from typing import List, Optional

# ── Built-in completions ───────────────────────────────────────────────────────

SLASH_COMMANDS = [
    "/status", "/providers", "/memory", "/doctor",
    "/benchmark", "/logs", "/voice", "/reset-memory",
    "/reset-learning", "/history", "/clear", "/help", "/exit", "/quit",
]

VERB_PREFIXES = [
    "open ", "play ", "search ", "find ", "remember ", "forget ",
    "summarize ", "explain ", "show ", "close ", "create ", "send ",
    "read ", "write ", "run ", "stop ", "pause ", "resume ", "cancel ",
    "what is ", "who is ", "how do ", "tell me about ",
]

APP_COMPLETIONS = [
    "Chrome", "Brave", "Safari", "Firefox", "Arc",
    "VS Code", "Cursor", "PyCharm", "Xcode", "Vim", "Zed",
    "Terminal", "iTerm", "Warp",
    "Slack", "Discord", "Zoom", "Teams", "WhatsApp", "Telegram",
    "Spotify", "Music", "VLC",
    "Figma", "Sketch",
    "Docker", "Postman",
    "Finder", "Notes", "Calendar", "Reminders", "Mail",
    "Activity Monitor", "System Settings",
    "Notion", "Obsidian", "Todoist",
]

WEBSITE_COMPLETIONS = [
    "YouTube", "Google", "GitHub", "Reddit", "Twitter",
    "Netflix", "Amazon", "Instagram", "LinkedIn", "ChatGPT",
]

ALL_COMPLETIONS = (
    SLASH_COMMANDS
    + VERB_PREFIXES
    + [f"open {a}" for a in APP_COMPLETIONS]
    + [f"open {w}" for w in WEBSITE_COMPLETIONS]
    + [f"play music", f"play lofi", f"play relaxing music"]
    + ["status", "providers", "memory", "doctor", "benchmark", "exit", "quit", "help"]
)


class FridayCompleter:
    """readline completer for the interactive shell."""

    def __init__(self) -> None:
        self._matches: List[str] = []

    def complete(self, text: str, state: int) -> Optional[str]:
        if state == 0:
            lower = text.lower()
            self._matches = [c for c in ALL_COMPLETIONS if c.lower().startswith(lower)]
        try:
            return self._matches[state]
        except IndexError:
            return None


def setup_completion() -> None:
    """Register the completer with readline."""
    completer = FridayCompleter()
    readline.set_completer(completer.complete)
    readline.set_completer_delims(" \t\n")
    try:
        # macOS uses libedit by default — different bind syntax
        import sys
        if sys.platform == "darwin":
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")
    except Exception:
        pass

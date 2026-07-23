"""
History — CLI conversation session history.

Persists the current session to friday_data/cli_history.json.
Also provides readline integration for up-arrow navigation.
"""
from __future__ import annotations

import json
import os
import readline
import time
from pathlib import Path
from typing import Dict, List

_HISTORY_FILE = Path("friday_data") / "cli_history.json"
_READLINE_FILE = Path("friday_data") / ".cli_readline_history"

MAX_SESSION_TURNS = 200
MAX_STORED_SESSIONS = 20


# ── Session turn model ─────────────────────────────────────────────────────────

class Turn:
    def __init__(self, role: str, content: str, ts: float | None = None):
        self.role = role      # "user" | "friday"
        self.content = content
        self.ts = ts or time.time()

    def to_dict(self) -> Dict:
        return {"role": self.role, "content": self.content, "ts": self.ts}

    @classmethod
    def from_dict(cls, d: Dict) -> "Turn":
        return cls(d["role"], d["content"], d.get("ts"))


# ── Session history ────────────────────────────────────────────────────────────

class SessionHistory:
    """
    In-memory conversation history for the current CLI session.
    Optionally persisted to disk for developer review.
    """

    def __init__(self):
        self._turns: List[Turn] = []
        self._session_start = time.time()

    def add_user(self, text: str) -> None:
        self._turns.append(Turn("user", text))
        if len(self._turns) > MAX_SESSION_TURNS * 2:
            self._turns = self._turns[-MAX_SESSION_TURNS * 2:]

    def add_friday(self, text: str) -> None:
        self._turns.append(Turn("friday", text))

    def all_turns(self) -> List[Turn]:
        return list(self._turns)

    def last_n(self, n: int) -> List[Turn]:
        return self._turns[-n:]

    def clear(self) -> None:
        self._turns.clear()

    def save(self) -> None:
        """Append this session to the on-disk history file."""
        _HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        existing = []
        if _HISTORY_FILE.exists():
            try:
                existing = json.loads(_HISTORY_FILE.read_text())
            except Exception:
                existing = []

        session = {
            "start": self._session_start,
            "end": time.time(),
            "turns": [t.to_dict() for t in self._turns],
        }
        existing.append(session)
        # Keep only last N sessions
        existing = existing[-MAX_STORED_SESSIONS:]
        _HISTORY_FILE.write_text(json.dumps(existing, indent=2))

    @classmethod
    def load_recent(cls, n_sessions: int = 1) -> List[Dict]:
        """Load recent sessions from disk."""
        if not _HISTORY_FILE.exists():
            return []
        try:
            data = json.loads(_HISTORY_FILE.read_text())
            return data[-n_sessions:]
        except Exception:
            return []

    @classmethod
    def clear_all(cls) -> None:
        """Wipe all stored sessions."""
        if _HISTORY_FILE.exists():
            _HISTORY_FILE.unlink()


# ── Readline history ───────────────────────────────────────────────────────────

def setup_readline() -> None:
    """Enable up-arrow history and tab completion in the interactive shell."""
    _READLINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        if _READLINE_FILE.exists():
            readline.read_history_file(str(_READLINE_FILE))
        readline.set_history_length(500)
        # Enable tab completion
        readline.parse_and_bind("tab: complete")
    except Exception:
        pass


def save_readline() -> None:
    try:
        _READLINE_FILE.parent.mkdir(parents=True, exist_ok=True)
        readline.write_history_file(str(_READLINE_FILE))
    except Exception:
        pass

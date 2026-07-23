"""
F.R.I.D.A.Y. Behavior Store

Atomic JSON persistence for all learned behavioral patterns.
Stored at: friday_data/learning/behaviors.json

Design:
  behaviors[pattern][choice] = BehaviorEntry dict
  time_patterns[time_of_day][action] = count

Writes are atomic: write to .tmp then rename to prevent corruption.
"""
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from friday.learning.behavior_engine.behavior_models import BehaviorEntry

logger = logging.getLogger(__name__)

_SCHEMA_VERSION = 2


class BehaviorStore:
    """
    Persistent JSON store for all learned behavior patterns.

    Structure:
        behaviors: Dict[pattern_key, Dict[choice, BehaviorEntry]]
        time_patterns: Dict[time_of_day, Dict[action, int]]
        metadata: schema version + timestamps
    """

    def __init__(self, storage_root: Path = Path("friday_data")):
        self._path = storage_root / "learning" / "behaviors.json"
        self._tmp_path = self._path.with_suffix(".json.tmp")
        self._data: Dict = {}
        self._load()

    # ── Persistence ─────────────────────────────────────────────────────────

    def _empty_store(self) -> Dict:
        return {
            "version": _SCHEMA_VERSION,
            "behaviors": {},
            "time_patterns": {
                "morning": {},
                "afternoon": {},
                "evening": {},
                "night": {},
            },
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "total_interactions": 0,
            },
        }

    def _load(self) -> None:
        try:
            if self._path.exists():
                with open(self._path, encoding="utf-8") as f:
                    raw = json.load(f)
                # Migrate if needed
                if raw.get("version", 1) < _SCHEMA_VERSION:
                    raw = self._migrate(raw)
                self._data = raw
                logger.debug(
                    "[BehaviorStore] Loaded %d pattern(s) from %s",
                    len(self._data.get("behaviors", {})),
                    self._path,
                )
            else:
                self._data = self._empty_store()
        except Exception as exc:
            logger.warning("[BehaviorStore] Load failed (%s) — starting fresh.", exc)
            self._data = self._empty_store()

    def _migrate(self, raw: Dict) -> Dict:
        """Upgrade old schema to current version."""
        base = self._empty_store()
        base["behaviors"] = raw.get("behaviors", {})
        base["version"] = _SCHEMA_VERSION
        logger.info("[BehaviorStore] Migrated schema v%d → v%d", raw.get("version", 1), _SCHEMA_VERSION)
        return base

    def save(self) -> None:
        """Atomically save to disk."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
            payload = json.dumps(self._data, indent=2, ensure_ascii=False)
            # Write to tmp first
            with open(self._tmp_path, "w", encoding="utf-8") as f:
                f.write(payload)
            # Atomic rename
            os.replace(self._tmp_path, self._path)
        except Exception as exc:
            logger.error("[BehaviorStore] Save failed: %s", exc)

    # ── Behavior CRUD ────────────────────────────────────────────────────────

    def get_entries(self, pattern: str) -> Dict[str, BehaviorEntry]:
        """Return all BehaviorEntry choices for a pattern key."""
        raw = self._data["behaviors"].get(pattern, {})
        return {
            choice: BehaviorEntry.from_dict(entry_dict)
            for choice, entry_dict in raw.items()
        }

    def get_best(self, pattern: str) -> Optional[Tuple[str, BehaviorEntry]]:
        """Return the highest-confidence (choice, entry) for a pattern, or None."""
        entries = self.get_entries(pattern)
        if not entries:
            return None
        best_choice = max(entries, key=lambda c: entries[c].confidence)
        return best_choice, entries[best_choice]

    def upsert_entry(self, pattern: str, entry: BehaviorEntry) -> None:
        """Write or update a BehaviorEntry."""
        if pattern not in self._data["behaviors"]:
            self._data["behaviors"][pattern] = {}
        self._data["behaviors"][pattern][entry.choice] = entry.to_dict()
        self._data["metadata"]["total_interactions"] = (
            self._data["metadata"].get("total_interactions", 0) + 1
        )
        self.save()

    def all_patterns(self) -> List[str]:
        return list(self._data["behaviors"].keys())

    def all_behaviors(self) -> Dict[str, Dict[str, BehaviorEntry]]:
        """Return all patterns with their entries."""
        return {
            pattern: self.get_entries(pattern)
            for pattern in self._data["behaviors"]
        }

    def forget_pattern(self, pattern: str) -> bool:
        """Remove all learned choices for a pattern. Returns True if existed."""
        if pattern in self._data["behaviors"]:
            del self._data["behaviors"][pattern]
            self.save()
            logger.info("[BehaviorStore] Forgot pattern: %s", pattern)
            return True
        return False

    def forget_choice(self, pattern: str, choice: str) -> bool:
        """Remove a single choice from a pattern."""
        choices = self._data["behaviors"].get(pattern, {})
        if choice in choices:
            del choices[choice]
            if not choices:
                del self._data["behaviors"][pattern]
            self.save()
            logger.info("[BehaviorStore] Forgot choice %r in pattern %r", choice, pattern)
            return True
        return False

    def reset_all(self) -> None:
        """Clear all learned behaviors."""
        self._data = self._empty_store()
        self.save()
        logger.info("[BehaviorStore] All behaviors reset.")

    # ── Time patterns ────────────────────────────────────────────────────────

    def record_time_pattern(self, time_of_day: str, action: str) -> None:
        """Increment the usage count for an action at a given time of day."""
        bucket = self._data["time_patterns"].setdefault(time_of_day, {})
        bucket[action] = bucket.get(action, 0) + 1
        self.save()

    def get_time_pattern(self, time_of_day: str) -> Dict[str, int]:
        return self._data["time_patterns"].get(time_of_day, {})

    def top_time_actions(self, time_of_day: str, n: int = 3) -> List[Tuple[str, int]]:
        """Return the top N actions for a given time of day."""
        bucket = self.get_time_pattern(time_of_day)
        return sorted(bucket.items(), key=lambda x: x[1], reverse=True)[:n]

    # ── Stats ────────────────────────────────────────────────────────────────

    def total_interactions(self) -> int:
        return self._data["metadata"].get("total_interactions", 0)

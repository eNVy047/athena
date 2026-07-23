"""
F.R.I.D.A.Y. Behavior Learning — Data Models

Core data structures for the confidence-based behavior learning system.
Every learned behavior is tracked with frequency, success rate, and recency
to compute a confidence score that drives clarification decisions.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ── Confidence thresholds ───────────────────────────────────────────────────

class ConfidenceLevel(Enum):
    """
    Drives the clarification policy.

    LOW    → always ask user for their choice
    MEDIUM → soft-confirm the inferred choice, allow easy override
    HIGH   → execute directly, mention it can be changed
    """
    LOW    = "low"     # < 0.40
    MEDIUM = "medium"  # 0.40 – 0.75
    HIGH   = "high"    # ≥ 0.75

    @classmethod
    def from_score(cls, score: float) -> "ConfidenceLevel":
        if score >= 0.75:
            return cls.HIGH
        if score >= 0.40:
            return cls.MEDIUM
        return cls.LOW


# ── Time of day ─────────────────────────────────────────────────────────────

class TimeOfDay(Enum):
    MORNING   = "morning"    # 06:00 – 11:59
    AFTERNOON = "afternoon"  # 12:00 – 16:59
    EVENING   = "evening"    # 17:00 – 21:59
    NIGHT     = "night"      # 22:00 – 05:59

    @classmethod
    def now(cls) -> "TimeOfDay":
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return cls.MORNING
        if 12 <= hour < 17:
            return cls.AFTERNOON
        if 17 <= hour < 22:
            return cls.EVENING
        return cls.NIGHT


# ── Behavior context ─────────────────────────────────────────────────────────

@dataclass
class BehaviorContext:
    """
    Optional context attached to a behavior observation.
    Used for context-aware learning (e.g. "open browser for banking" vs "for development").
    """
    time_of_day: Optional[str] = None     # morning / afternoon / evening / night
    day_of_week: Optional[int] = None     # 0=Monday … 6=Sunday
    trigger_topic: Optional[str] = None   # e.g. "banking", "coding", "streaming"
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def now(cls, trigger_topic: str = "") -> "BehaviorContext":
        tod = TimeOfDay.now()
        return cls(
            time_of_day=tod.value,
            day_of_week=datetime.now().weekday(),
            trigger_topic=trigger_topic,
        )

    def to_key_suffix(self) -> str:
        """Returns a string suffix for context-aware pattern keys."""
        if self.trigger_topic:
            return f":{self.trigger_topic}"
        return ""


# ── Behavior entry ───────────────────────────────────────────────────────────

@dataclass
class BehaviorEntry:
    """
    A single learned choice within a behavior pattern.

    Example: pattern="open_browser", choice="Chrome"
    """
    choice: str
    frequency: int = 0              # total number of times this choice was made
    successes: int = 0              # successful executions
    failures: int = 0               # failed executions
    overrides: int = 0              # times user said "no, use something else"
    confidence: float = 0.0         # computed score 0.0–1.0
    first_seen: str = ""            # ISO timestamp
    last_used: str = ""             # ISO timestamp
    last_confirmed: str = ""        # last time user explicitly confirmed this choice

    def __post_init__(self):
        if not self.first_seen:
            self.first_seen = datetime.now(timezone.utc).isoformat()
        if not self.last_used:
            self.last_used = self.first_seen

    @property
    def total_attempts(self) -> int:
        return self.successes + self.failures

    @property
    def success_rate(self) -> float:
        if self.total_attempts == 0:
            return 1.0  # optimistic prior
        return self.successes / self.total_attempts

    @property
    def level(self) -> ConfidenceLevel:
        return ConfidenceLevel.from_score(self.confidence)

    @property
    def days_since_last_use(self) -> float:
        try:
            last = datetime.fromisoformat(self.last_used)
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            delta = datetime.now(timezone.utc) - last
            return delta.total_seconds() / 86400
        except Exception:
            return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "choice": self.choice,
            "frequency": self.frequency,
            "successes": self.successes,
            "failures": self.failures,
            "overrides": self.overrides,
            "confidence": round(self.confidence, 4),
            "first_seen": self.first_seen,
            "last_used": self.last_used,
            "last_confirmed": self.last_confirmed,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "BehaviorEntry":
        return cls(
            choice=d["choice"],
            frequency=d.get("frequency", 0),
            successes=d.get("successes", 0),
            failures=d.get("failures", 0),
            overrides=d.get("overrides", 0),
            confidence=d.get("confidence", 0.0),
            first_seen=d.get("first_seen", ""),
            last_used=d.get("last_used", ""),
            last_confirmed=d.get("last_confirmed", ""),
        )


# ── App launch result ────────────────────────────────────────────────────────

class AppErrorType(Enum):
    NOT_FOUND        = "not_found"
    ALREADY_RUNNING  = "already_running"
    PERMISSION_DENIED= "permission_denied"
    FROZEN           = "frozen"
    LAUNCH_TIMEOUT   = "launch_timeout"
    OS_ERROR         = "os_error"
    UNKNOWN          = "unknown"


@dataclass
class AppLaunchResult:
    """Result of an application launch attempt, with recovery suggestions."""
    success: bool
    app_name: str
    message: str = ""
    error_type: Optional[AppErrorType] = None
    recovery_question: Optional[str] = None
    recovery_options: List[str] = field(default_factory=list)
    raw_error: str = ""


# ── Memory pressure ──────────────────────────────────────────────────────────

class MemoryPressureLevel(Enum):
    NORMAL   = "normal"   # < 70%
    ELEVATED = "elevated" # 70–85%
    HIGH     = "high"     # > 85%


@dataclass
class MemoryPressure:
    used_gb: float
    total_gb: float
    percent: float
    level: MemoryPressureLevel
    closeable_apps: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def freeable_gb(self) -> float:
        return sum(a.get("memory_gb", 0) for a in self.closeable_apps)

    def to_suggestion(self) -> Optional[str]:
        if self.level == MemoryPressureLevel.NORMAL:
            return None
        apps = self.closeable_apps[:3]
        if not apps:
            return f"Memory usage is at {self.percent:.0f}% ({self.used_gb:.1f}/{self.total_gb:.1f} GB)."
        app_names = " and ".join(a["name"] for a in apps)
        gb = self.freeable_gb
        return (
            f"Memory usage is high ({self.percent:.0f}%). "
            f"Closing {app_names} could free about {gb:.1f} GB. "
            f"Would you like me to do that?"
        )

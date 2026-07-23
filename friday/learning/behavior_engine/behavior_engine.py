"""
F.R.I.D.A.Y. Behavior Engine

Core learning engine that tracks observed behavior patterns with
confidence scores. Replaces the static PreferenceManager with a
system that learns from real usage.

Confidence Formula:
    raw_conf = frequency / (frequency + DECAY_K)
    recency  = max(0.5, 1.0 - days_since_use * RECENCY_DECAY_PER_DAY)
    confidence = raw_conf * success_rate * recency

    DECAY_K = 4   → confidence reaches ~50% at 4 uses, ~75% at 12 uses
    RECENCY_DECAY_PER_DAY = 0.02  → halved after 25 days of no use

Learning Lifecycle:
    1. User action observed → record_outcome() called
    2. confidence recomputed for that choice
    3. All competing choices get a small decay (COMPETE_DECAY)
    4. On override ("no, use something else") → immediate 30% decay
    5. On repeated override → confidence may drop below threshold → ask again
"""
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from friday.learning.behavior_engine.behavior_models import (
    BehaviorEntry,
    BehaviorContext,
    ConfidenceLevel,
    TimeOfDay,
)
from friday.learning.behavior_engine.behavior_store import BehaviorStore

logger = logging.getLogger(__name__)

# ── Tuning constants ─────────────────────────────────────────────────────────
DECAY_K              = 4      # Uses to reach ~50% raw confidence
RECENCY_DECAY_PER_DAY= 0.02   # Confidence decays 2%/day after last use
RECENCY_FLOOR        = 0.5    # Minimum recency multiplier
COMPETE_DECAY        = 0.05   # How much competing choices are penalised per observation
OVERRIDE_PENALTY     = 0.30   # Immediate confidence drop on user override
CONSECUTIVE_OVERRIDE_PENALTY = 0.50  # If overridden 3+ times in a row


class BehaviorEngine:
    """
    Confidence-based behavior learning engine.

    Usage:
        engine = BehaviorEngine()

        # Query: what is the preferred choice for "open_browser"?
        choice, level, entry = engine.query("open_browser")
        # choice = "Chrome" (or None if unknown)
        # level  = ConfidenceLevel.HIGH / MEDIUM / LOW

        # Record: user picked "Chrome" and it succeeded
        engine.record_outcome("open_browser", "Chrome", success=True)

        # Override: user said "no, use Brave instead"
        engine.on_negative_feedback("open_browser", "Chrome")
    """

    def __init__(self, storage_root: Path = Path("friday_data")):
        self._store = BehaviorStore(storage_root)
        self._consecutive_overrides: Dict[str, int] = {}  # pattern → count

    # ── Core API ─────────────────────────────────────────────────────────────

    def query(
        self,
        pattern: str,
        context: Optional[BehaviorContext] = None,
    ) -> Tuple[Optional[str], ConfidenceLevel, Optional[BehaviorEntry]]:
        """
        Query the best known choice for a pattern.

        Returns:
            (choice, confidence_level, entry)
            choice=None and level=LOW if no data exists.
        """
        key = self._make_key(pattern, context)
        result = self._store.get_best(key)

        # If context-specific key has no data, fall back to base pattern
        if result is None and context and context.trigger_topic:
            result = self._store.get_best(pattern)

        if result is None:
            return None, ConfidenceLevel.LOW, None

        choice, entry = result

        # Recompute confidence to account for recency
        entry.confidence = self._compute_confidence(entry)
        return choice, entry.level, entry

    def record_outcome(
        self,
        pattern: str,
        choice: str,
        success: bool = True,
        context: Optional[BehaviorContext] = None,
        user_override: bool = False,
    ) -> BehaviorEntry:
        """
        Record that the user chose `choice` for `pattern` with the given outcome.

        - Increments frequency + success/failure counters
        - Recomputes confidence
        - Applies small decay to competing choices
        - Resets override counter if not an override
        """
        key = self._make_key(pattern, context)
        entries = self._store.get_entries(key)

        # Get or create entry for this choice
        entry = entries.get(choice, BehaviorEntry(choice=choice))
        entry.frequency += 1
        if success:
            entry.successes += 1
        else:
            entry.failures += 1
        if user_override:
            entry.overrides += 1

        entry.last_used = datetime.now(timezone.utc).isoformat()
        entry.confidence = self._compute_confidence(entry)
        self._store.upsert_entry(key, entry)

        # Decay competing choices
        for other_choice, other_entry in entries.items():
            if other_choice != choice:
                other_entry.confidence = max(
                    0.0,
                    self._compute_confidence(other_entry) - COMPETE_DECAY
                )
                self._store.upsert_entry(key, other_entry)

        # Record time pattern
        if context and context.time_of_day:
            self._store.record_time_pattern(context.time_of_day, pattern)

        # Reset consecutive override counter
        if not user_override:
            self._consecutive_overrides.pop(key, None)

        logger.info(
            "[BehaviorEngine] Recorded: pattern=%r choice=%r freq=%d conf=%.2f level=%s",
            key, choice, entry.frequency, entry.confidence, entry.level.value,
        )
        return entry

    def on_negative_feedback(
        self,
        pattern: str,
        rejected_choice: str,
        context: Optional[BehaviorContext] = None,
    ) -> None:
        """
        User said "no" or chose something different.
        Immediately apply penalty to the rejected choice.
        """
        key = self._make_key(pattern, context)
        entries = self._store.get_entries(key)

        if rejected_choice in entries:
            entry = entries[rejected_choice]
            self._consecutive_overrides[key] = self._consecutive_overrides.get(key, 0) + 1
            consecutive = self._consecutive_overrides[key]

            penalty = OVERRIDE_PENALTY
            if consecutive >= 3:
                penalty = CONSECUTIVE_OVERRIDE_PENALTY
                logger.info(
                    "[BehaviorEngine] Consecutive override #%d for %r/%r — applying %.0f%% penalty",
                    consecutive, key, rejected_choice, penalty * 100,
                )

            entry.overrides += 1
            entry.confidence = max(0.0, entry.confidence - penalty)
            self._store.upsert_entry(key, entry)
            logger.info(
                "[BehaviorEngine] Negative feedback: %r/%r confidence → %.2f",
                key, rejected_choice, entry.confidence,
            )

    def learn_explicit(
        self,
        pattern: str,
        choice: str,
        context: Optional[BehaviorContext] = None,
    ) -> BehaviorEntry:
        """
        User explicitly stated a preference ("always use VS Code").
        Immediately boosts confidence to HIGH.
        """
        key = self._make_key(pattern, context)
        entries = self._store.get_entries(key)

        entry = entries.get(choice, BehaviorEntry(choice=choice))
        # Simulate having 20 uses — pushes straight to HIGH
        entry.frequency = max(entry.frequency, 20)
        entry.successes = max(entry.successes, 18)
        entry.confidence = 0.92
        entry.last_used = datetime.now(timezone.utc).isoformat()
        entry.last_confirmed = entry.last_used
        self._store.upsert_entry(key, entry)

        logger.info(
            "[BehaviorEngine] Explicit preference: %r/%r confidence set to HIGH",
            key, choice,
        )
        return entry

    # ── Forget / Reset ────────────────────────────────────────────────────────

    def forget(self, pattern: str, context: Optional[BehaviorContext] = None) -> bool:
        key = self._make_key(pattern, context)
        return self._store.forget_pattern(key)

    def forget_choice(self, pattern: str, choice: str) -> bool:
        return self._store.forget_choice(pattern, choice)

    def reset_all(self) -> None:
        self._store.reset_all()
        self._consecutive_overrides.clear()
        logger.info("[BehaviorEngine] All behaviors reset.")

    # ── Inspection ────────────────────────────────────────────────────────────

    def all_behaviors(self) -> List[Dict]:
        """
        Return a flat list of all behaviors for UI display.
        Sorted by confidence descending.
        """
        result = []
        for pattern, choices in self._store.all_behaviors().items():
            for choice, entry in choices.items():
                entry.confidence = self._compute_confidence(entry)
                result.append({
                    "pattern": pattern,
                    "choice": choice,
                    "confidence": round(entry.confidence * 100, 1),
                    "confidence_level": entry.level.value,
                    "frequency": entry.frequency,
                    "success_rate": round(entry.success_rate * 100, 1),
                    "last_used": entry.last_used,
                    "days_ago": round(entry.days_since_last_use, 1),
                })
        return sorted(result, key=lambda x: x["confidence"], reverse=True)

    def get_time_suggestion(self, time_of_day: Optional[str] = None) -> Optional[str]:
        """
        Return a time-based suggestion if a clear pattern exists.
        Only suggests if an action has been done 3+ times at this time.
        """
        tod = time_of_day or TimeOfDay.now().value
        top = self._store.top_time_actions(tod, n=1)
        if top and top[0][1] >= 3:
            action, count = top[0]
            return f"You usually {action.replace('_', ' ')} around this time."
        return None

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _make_key(pattern: str, context: Optional[BehaviorContext] = None) -> str:
        """Build a storage key, optionally with context suffix."""
        if context:
            suffix = context.to_key_suffix()
            if suffix:
                return f"{pattern}{suffix}"
        return pattern

    @staticmethod
    def _compute_confidence(entry: BehaviorEntry) -> float:
        """
        Compute confidence score from frequency, success rate, and recency.

        confidence = (f / (f + K)) × success_rate × recency_factor
        """
        if entry.frequency == 0:
            return 0.0

        # Frequency factor: sigmoid-like curve reaching ~0.9 at f=36
        raw = entry.frequency / (entry.frequency + DECAY_K)

        # Recency factor: decays 2% per day, floor at 50%
        days = entry.days_since_last_use
        recency = max(RECENCY_FLOOR, 1.0 - days * RECENCY_DECAY_PER_DAY)

        # Success rate
        sr = entry.success_rate

        # Override penalty: each override permanently reduced confidence
        override_factor = max(0.3, 1.0 - (entry.overrides * 0.08))

        score = raw * sr * recency * override_factor
        return round(min(1.0, score), 4)

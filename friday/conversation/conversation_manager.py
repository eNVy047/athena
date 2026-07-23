"""
F.R.I.D.A.Y. Conversation Manager

The brain of conversational interaction. Routes every user input through
the full reasoning pipeline:

  Preference Detection
  → Behavior Engine Query (confidence-based)
  → Clarification Policy (LOW/MEDIUM/HIGH)
  → Tool Execution
  → Outcome Recording
  → Time Pattern Update
  → Proactive Suggestions

This module makes Friday feel like a human assistant rather than a command parser.
It NEVER hardcodes defaults — every choice is learned from real usage.
"""
import asyncio
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from friday.learning.behavior_engine.behavior_engine import BehaviorEngine
from friday.learning.behavior_engine.behavior_models import (
    BehaviorContext,
    ConfidenceLevel,
    TimeOfDay,
)
from friday.learning.behavior_engine.behavior_store import BehaviorStore
from friday.learning.behavior_engine.clarification_policy import ClarificationPolicy
from friday.learning.behavior_engine.memory_monitor import MemoryMonitor
from friday.learning.behavior_engine.time_awareness import TimeAwareness

logger = logging.getLogger(__name__)


# ── Conversation state ────────────────────────────────────────────────────────

@dataclass
class ConversationTurn:
    role: str
    content: str
    intent: Optional[str] = None
    executed_tool: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    history: List[ConversationTurn] = field(default_factory=list)
    # Pending action state (waiting for clarification answer)
    awaiting_clarification: bool = False
    pending_pattern: Optional[str] = None       # e.g. "open_browser"
    pending_intent: Optional[str] = None        # e.g. "launcher.open_application"
    pending_params: Dict[str, Any] = field(default_factory=dict)
    pending_suggested_choice: Optional[str] = None
    pending_confidence_level: Optional[ConfidenceLevel] = None
    pending_options: List[str] = field(default_factory=list)
    # Last execution for proactive suggestions
    last_executed_intent: Optional[str] = None
    last_executed_params: Dict[str, Any] = field(default_factory=dict)

    def add_user(self, text: str) -> None:
        self.history.append(ConversationTurn(role="user", content=text))

    def add_assistant(self, text: str, intent: str = None) -> None:
        self.history.append(ConversationTurn(role="assistant", content=text, intent=intent))

    def as_chat_history(self) -> List[Dict[str, str]]:
        return [{"role": t.role, "content": t.content} for t in self.history[-20:]]


# ── Pattern detection helpers ─────────────────────────────────────────────────

# Maps ambiguous open targets → behavior pattern key + intent
# Only GENERIC category words go here (triggers clarification + behavior learning).
# Specific app names (chrome, firefox, vscode, etc.) are handled by the kernel/planner directly.
_OPEN_PATTERNS: Dict[str, Tuple[str, str]] = {
    "browser":      ("open_browser",   "launcher.open_application"),
    "editor":       ("open_editor",    "launcher.open_application"),
    "code editor":  ("open_editor",    "launcher.open_application"),
    "ide":          ("open_editor",    "launcher.open_application"),
    "terminal":     ("open_terminal",  "launcher.open_application"),
    "music":        ("open_music",     "launcher.open_application"),
    "music app":    ("open_music",     "launcher.open_application"),
    "email":        ("open_email",     "launcher.open_application"),
    "mail":         ("open_email",     "launcher.open_application"),
    "calendar":     ("open_calendar",  "launcher.open_application"),
}

_MUSIC_AMBIGUOUS = re.compile(
    r"^(?:play|put on|start)\s+(?:some\s+)?(?:music|something|songs?|"
    r"(?:something\s+)?(?:relaxing|chill|upbeat|sad|happy|calm|ambient|lo.?fi)(?:\s+music)?)"
    r"$",
    re.I,
)

_CONTINUATIONS = {
    "yes", "yeah", "yep", "sure", "ok", "okay", "go ahead", "do it",
    "continue", "proceed", "alright", "fine", "sounds good", "please",
    "yup", "go", "go on",
}

_CANCELLATIONS = {
    "no", "nope", "cancel", "stop", "never mind", "nevermind",
    "abort", "quit it", "forget it", "nah",
}

_MEMORY_STORE_RE = re.compile(
    r"\b(remember|note|always use|my .+ is|i prefer|i use|i like|"
    r"favorite|favourite|default to|set .+ to)\b",
    re.I,
)

_MEMORY_RECALL_RE = re.compile(
    r"\b(recall|what is my|what do i use|what do i prefer|"
    r"what was my|do you remember)\b",
    re.I,
)

_MULTI_STEP_RE = re.compile(
    r"\b(build|create|set up|scaffold|initialize|start a new|deploy)\b.+"
    r"\b(app|project|website|service|api|repo|server)\b",
    re.I,
)


class ConversationManager:
    """
    Full conversational pipeline with confidence-based behavior learning.

    Never hardcodes preferences. Every choice is learned from observed behavior.
    """

    SYSTEM_PROMPT = (
        "You are F.R.I.D.A.Y. (Female Replacement Intelligent Digital Assistant Youth), "
        "Tony Stark's AI — now serving a real user. You are warm, witty, and precise. "
        "You can control the user's computer, browse the web, manage files, play music, "
        "and hold natural conversations. You proactively offer help. "
        "Respond in plain text — no markdown. Keep responses short and natural."
    )

    def __init__(
        self,
        kernel,
        provider_manager=None,
        storage_root: Path = Path("friday_data"),
        status_callback: Optional[Callable[[str], None]] = None,
    ):
        self.kernel = kernel
        self.provider_manager = provider_manager
        self.status_callback = status_callback

        # Behavior learning stack
        self._engine = BehaviorEngine(storage_root)
        self._store = self._engine._store
        self._policy = ClarificationPolicy()
        self._memory = MemoryMonitor()
        self._time = TimeAwareness(self._store)

        # Conversation state
        self._ctx = ConversationContext()

    # ── Status emission ───────────────────────────────────────────────────────

    def _emit(self, status: str) -> None:
        logger.debug("[CM] Status: %s", status)
        if self.status_callback:
            try:
                self.status_callback(status)
            except Exception:
                pass

    # ── Main entry point ──────────────────────────────────────────────────────

    async def process(self, user_text: str, stream_callback=None) -> str:
        """
        Route user text through the full pipeline.

        Args:
            user_text: Raw user input.
            stream_callback: Optional callable(token: str) for live LLM token
                             delivery. Passed through to the kernel/LLM layer.
        """
        user_text = user_text.strip()
        if not user_text:
            return "I didn't catch that. Could you say it again?"

        self._ctx.add_user(user_text)
        self._emit("Thinking...")

        try:
            response = await self._run_pipeline(user_text, stream_callback=stream_callback)
        except Exception as exc:
            logger.error("[CM] Pipeline error: %s", exc, exc_info=True)
            response = f"Something went wrong: {exc}"

        self._ctx.add_assistant(response)
        return response

    async def _run_pipeline(self, user_text: str, stream_callback=None) -> str:
        q = user_text.lower().strip()

        # ── 1. Cancellation ──────────────────────────────────────────────────
        if q in _CANCELLATIONS:
            self._ctx.awaiting_clarification = False
            self._ctx.pending_intent = None
            return "Alright, cancelled. Let me know if you need anything else."

        # ── 2. In clarification loop? ────────────────────────────────────────
        if self._ctx.awaiting_clarification:
            return await self._handle_clarification_answer(user_text)

        # ── 3. Explicit memory/preference statement ──────────────────────────
        pref_result = self._detect_explicit_preference(user_text)
        if pref_result:
            pattern, choice = pref_result
            self._engine.learn_explicit(pattern, choice)
            self._emit("Saving preference...")
            return f"Got it! I'll remember to use {choice} whenever you ask."

        # ── 4. Memory recall ─────────────────────────────────────────────────
        if _MEMORY_RECALL_RE.search(user_text):
            return await self._handle_memory_recall(user_text)

        # ── 5. Continuation ──────────────────────────────────────────────────
        if q in _CONTINUATIONS and self._ctx.pending_intent:
            return await self._execute_pending()

        # ── 6. Multi-step task ───────────────────────────────────────────────
        if _MULTI_STEP_RE.search(user_text):
            return await self._handle_multi_step(user_text, stream_callback=stream_callback)

        # ── 7. Detect ambiguous open/play/launch requests ────────────────────
        pattern_result = self._detect_learnable_pattern(user_text)
        if pattern_result:
            pattern, intent, default_opts = pattern_result
            return await self._handle_learnable_action(user_text, pattern, intent, default_opts)

        # ── 8. Route to kernel (LLM + tool dispatch) ─────────────────────────
        self._emit("Planning...")
        result = await self.kernel.execute(user_text, stream_callback=stream_callback)
        return result

    # ── Clarification answer handler ─────────────────────────────────────────

    async def _handle_clarification_answer(self, user_text: str) -> str:
        """User is answering a clarification question."""
        pattern = self._ctx.pending_pattern
        intent  = self._ctx.pending_intent
        suggested = self._ctx.pending_suggested_choice
        options = self._ctx.pending_options
        level   = self._ctx.pending_confidence_level

        # Is this a yes/no for MEDIUM-level soft-confirm?
        if level == ConfidenceLevel.MEDIUM and suggested:
            confirmation = self._policy.parse_confirmation(user_text, suggested)
            if confirmation is True:
                # Confirmed the suggested choice
                return await self._execute_choice(pattern, intent, suggested, confirmed=True)
            elif confirmation is False:
                # Rejected — apply negative feedback, fall back to asking
                self._engine.on_negative_feedback(pattern, suggested)
                # Re-ask with full menu
                decision = self._policy.decide(pattern, ConfidenceLevel.LOW, None)
                self._ctx.pending_confidence_level = ConfidenceLevel.LOW
                self._ctx.pending_suggested_choice = None
                return decision.ask_text
            # else: they gave a specific answer (falls through)

        # Try to parse as a specific choice
        parsed = self._parse_choice_answer(user_text, options or [], pattern)
        if parsed:
            self._ctx.awaiting_clarification = False
            return await self._execute_choice(pattern, intent, parsed, confirmed=False)

        # Couldn't match — give them the menu again once
        self._ctx.awaiting_clarification = False
        return await self.kernel.execute(user_text)

    # ── Learnable action handler ─────────────────────────────────────────────

    async def _handle_learnable_action(
        self,
        user_text: str,
        pattern: str,
        intent: str,
        default_options: List[str],
    ) -> str:
        """Handle an action that should go through the behavior learning system."""
        from friday.learning.behavior_engine.clarification_policy import PATTERN_OPTIONS

        ctx = BehaviorContext.now()
        choice, level, entry = self._engine.query(pattern, ctx)
        all_entries = self._store.get_entries(pattern)

        decision = self._policy.decide(pattern, level, entry, all_entries)

        # Check memory pressure before heavy apps
        if decision.execute_immediately or decision.suggested_choice:
            app = decision.suggested_choice or choice
            if app:
                mem_prompt = self._check_memory_pressure(app)
                if mem_prompt:
                    return mem_prompt

        # HIGH confidence → execute directly
        if decision.execute_immediately and decision.suggested_choice:
            self._emit(f"Opening {decision.suggested_choice}...")
            result = await self._execute_choice(pattern, intent, decision.suggested_choice)
            if decision.post_execute_note:
                return f"{result}\n{decision.post_execute_note}"
            return result

        # MEDIUM confidence → soft-confirm
        if level == ConfidenceLevel.MEDIUM:
            self._ctx.awaiting_clarification = True
            self._ctx.pending_pattern = pattern
            self._ctx.pending_intent = intent
            self._ctx.pending_suggested_choice = decision.suggested_choice
            self._ctx.pending_confidence_level = ConfidenceLevel.MEDIUM
            self._ctx.pending_options = decision.options
            return decision.ask_text

        # LOW confidence → full menu
        opts = PATTERN_OPTIONS.get(pattern, default_options)
        self._ctx.awaiting_clarification = True
        self._ctx.pending_pattern = pattern
        self._ctx.pending_intent = intent
        self._ctx.pending_suggested_choice = None
        self._ctx.pending_confidence_level = ConfidenceLevel.LOW
        self._ctx.pending_options = opts
        return decision.ask_text

    async def _execute_choice(
        self,
        pattern: str,
        intent: str,
        choice: str,
        confirmed: bool = False,
    ) -> str:
        """Execute a chosen action and record the outcome."""
        self._ctx.awaiting_clarification = False
        self._emit(f"Opening {choice}...")
        ctx = BehaviorContext.now()

        try:
            result = await self._run_tool(intent, {"app_name": choice})
            success = not result.lower().startswith("execution failed")

            # Record outcome
            entry = self._engine.record_outcome(pattern, choice, success=success, context=ctx)
            if confirmed:
                entry.last_confirmed = ctx.time_of_day or ""

            # Record time pattern
            self._time.record(pattern, ctx.time_of_day)

            # Build proactive suggestion
            suggestion = self._build_proactive_suggestion(intent, choice, pattern, entry)
            if suggestion:
                return f"{result}\n{suggestion}"
            return result

        except Exception as exc:
            self._engine.record_outcome(pattern, choice, success=False, context=ctx)
            return f"I ran into an issue opening {choice}: {exc}"

    # ── Memory check ──────────────────────────────────────────────────────────

    def _check_memory_pressure(self, app_name: str) -> Optional[str]:
        """Return a memory prompt if RAM is high before launching a heavy app."""
        if self._memory.should_warn_before_launch(app_name):
            prompt = self._memory.get_prompt()
            if prompt:
                return prompt
        return None

    # ── Memory recall ─────────────────────────────────────────────────────────

    async def _handle_memory_recall(self, user_text: str) -> str:
        q = user_text.lower()
        pref_keywords = {
            "editor": "open_editor",      "ide": "open_editor",
            "browser": "open_browser",    "music": "open_music",
            "terminal": "open_terminal",  "email": "open_email",
            "calendar": "open_calendar",
        }
        for kw, pat in pref_keywords.items():
            if kw in q:
                choice, level, entry = self._engine.query(pat)
                if choice and level != ConfidenceLevel.LOW:
                    pct = round((entry.confidence if entry else 0) * 100)
                    return f"Based on your usage, you prefer {choice} ({pct}% confidence)."
                elif choice:
                    return f"You've used {choice} before, but I'm not confident enough to call it a preference yet."
        return await self._execute_via_llm(user_text)

    # ── Multi-step handler ────────────────────────────────────────────────────

    async def _handle_multi_step(self, user_text: str, stream_callback=None) -> str:
        self._emit("Planning multi-step task...")
        return await self._execute_via_llm(user_text, stream_callback=stream_callback)

    # ── Pending execution ─────────────────────────────────────────────────────

    async def _execute_pending(self) -> str:
        intent = self._ctx.pending_intent
        params = self._ctx.pending_params
        self._ctx.pending_intent = None
        self._ctx.pending_params = {}
        return await self._run_tool(intent, params)

    # ── Tool runner ───────────────────────────────────────────────────────────

    async def _run_tool(self, intent: str, params: Dict[str, Any]) -> str:
        tool = self.kernel.tool_registry.get_tool_by_intent(intent)
        if not tool:
            text = " ".join(str(v) for v in params.values())
            return await self.kernel.execute(text)

        from friday.domain.tool import ToolExecutionContext
        tool_ctx = ToolExecutionContext(session_id="session_current", user_id="user_current")

        if intent == "conversation.dialog":
            params.setdefault("chat_history", self._ctx.as_chat_history())
            params.setdefault("provider_manager", self.provider_manager)

        try:
            result = await tool.execute(tool_ctx, params)
            self._emit("Done ✓")
            self._ctx.last_executed_intent = intent
            self._ctx.last_executed_params = params
            return str(result)
        except Exception as exc:
            logger.error("[CM] Tool error: %s", exc, exc_info=True)
            return f"Execution failed: {exc}"

    async def _execute_via_llm(self, user_text: str, stream_callback=None) -> str:
        self._emit("Thinking...")
        try:
            from friday.providers.llm.base import LLMMessage
            if not self.provider_manager:
                return await self._run_tool("conversation.dialog", {"query": user_text})
            messages = [LLMMessage(role="system", content=self.SYSTEM_PROMPT)]
            for turn in self._ctx.history[-16:]:
                if turn.role in ("user", "assistant"):
                    messages.append(LLMMessage(role=turn.role, content=turn.content))
            if stream_callback is not None:
                result = await self.provider_manager.execute_with_fallback_stream(
                    messages=messages,
                    stream_callback=stream_callback,
                )
                self._emit("Done ✓")
                return result
            result = await self.provider_manager.execute_with_fallback(
                "llm", lambda p: p.chat(messages=messages)
            )
            self._emit("Done ✓")
            return result.content.strip()
        except Exception as exc:
            logger.error("[CM] LLM error: %s", exc)
            return f"I'm having trouble thinking right now: {exc}"

    # ── Pattern detectors ─────────────────────────────────────────────────────

    @staticmethod
    def _detect_learnable_pattern(
        user_text: str,
    ) -> Optional[Tuple[str, str, List[str]]]:
        """
        Detect if the query matches an ambiguous open/play/launch request.
        Returns (pattern, intent, default_options) or None.
        """
        q = user_text.lower().strip()

        # "open X" / "launch X" / "start X"
        open_m = re.match(r"(?:open|launch|start|show)\s+(?:my\s+|the\s+)?(.+)", q)
        if open_m:
            target = open_m.group(1).strip().rstrip("?. ")
            target = re.split(r"\s+and\s+|\s+then\s+", target)[0].strip()
            if target in _OPEN_PATTERNS:
                pattern, intent = _OPEN_PATTERNS[target]
                from friday.learning.behavior_engine.clarification_policy import PATTERN_OPTIONS
                return pattern, intent, PATTERN_OPTIONS.get(pattern, [])

        # "play music / play something relaxing"
        if _MUSIC_AMBIGUOUS.match(q):
            from friday.learning.behavior_engine.clarification_policy import PATTERN_OPTIONS
            return "open_music", "launcher.open_application", PATTERN_OPTIONS.get("open_music", [])

        return None

    @staticmethod
    def _detect_explicit_preference(user_text: str) -> Optional[Tuple[str, str]]:
        """
        Detect explicit preference statements like "always use VS Code".
        Returns (pattern, choice) or None.
        """
        text_lower = user_text.lower()
        trigger_words = ["prefer", "always use", "always open", "my editor is",
                         "my browser is", "i use ", "set my", "remember"]
        if not any(t in text_lower for t in trigger_words):
            return None

        # Map specific values to patterns
        checks = [
            ("open_editor",   ["vs code", "vscode", "cursor", "pycharm", "xcode",
                                "vim", "neovim", "zed", "fleet"]),
            ("open_browser",  ["chrome", "brave", "safari", "firefox", "arc"]),
            ("open_music",    ["spotify", "apple music", "youtube music"]),
            ("open_terminal", ["iterm", "warp", "kitty", "terminal"]),
        ]

        for pattern, values in checks:
            for v in values:
                if v in text_lower:
                    display = {
                        "vs code": "VS Code", "vscode": "VS Code",
                        "iterm": "iTerm2", "chrome": "Chrome",
                        "apple music": "Apple Music",
                        "youtube music": "YouTube Music",
                    }.get(v, v.title())
                    return pattern, display
        return None

    @staticmethod
    def _parse_choice_answer(
        user_text: str,
        options: List[str],
        pattern: str,
    ) -> Optional[str]:
        """Match user's text to one of the known options."""
        text = user_text.lower().strip()

        for opt in options:
            if opt.lower() == text or opt.lower() in text or text in opt.lower():
                return opt

        # Shorthand maps
        shortcuts = {
            "open_editor":   {
                "code": "VS Code", "vscode": "VS Code",
                "cursor": "Cursor", "pycharm": "PyCharm",
                "xcode": "Xcode", "vim": "Vim",
            },
            "open_browser":  {
                "chrome": "Chrome", "google": "Chrome",
                "brave": "Brave", "safari": "Safari",
                "firefox": "Firefox", "arc": "Arc",
            },
            "open_music":    {
                "spotify": "Spotify", "apple": "Apple Music",
                "youtube": "YouTube Music", "yt": "YouTube Music",
            },
            "open_terminal": {
                "iterm": "iTerm2", "warp": "Warp",
                "terminal": "Terminal", "kitty": "Kitty",
            },
            "open_email":    {
                "mail": "Mail", "spark": "Spark",
                "outlook": "Outlook",
            },
        }
        for short, full in shortcuts.get(pattern, {}).items():
            if short in text:
                return full
        return None

    # ── Proactive suggestions ─────────────────────────────────────────────────

    def _build_proactive_suggestion(
        self,
        intent: str,
        choice: str,
        pattern: str,
        entry=None,
    ) -> Optional[str]:
        # Only suggest when confidence is still rising (under HIGH)
        if entry and entry.level == ConfidenceLevel.HIGH:
            return None  # Already confident — don't spam suggestions

        suggestions = {
            "open_editor":   "Would you also like me to open your last project?",
            "open_browser":  "Should I restore your previous tabs?",
            "open_music":    "Any specific song or playlist you'd like?",
            "open_terminal": "Would you like me to navigate to your project directory?",
        }
        return suggestions.get(pattern)

    # ── Public inspection API ─────────────────────────────────────────────────

    def get_all_behaviors(self) -> List[Dict]:
        """For the UI — return all learned behaviors with confidence."""
        return self._engine.all_behaviors()

    def forget_behavior(self, pattern: str) -> bool:
        return self._engine.forget(pattern)

    def forget_choice(self, pattern: str, choice: str) -> bool:
        return self._engine.forget_choice(pattern, choice)

    def reset_all_behaviors(self) -> None:
        self._engine.reset_all()

    def get_chat_history(self) -> List[Dict[str, str]]:
        return self._ctx.as_chat_history()

    def reset(self) -> None:
        self._ctx = ConversationContext()

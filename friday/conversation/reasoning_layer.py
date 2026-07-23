"""
F.R.I.D.A.Y. Reasoning Layer

Pre-execution analysis that determines WHAT the assistant should do
before committing to any tool call. Eliminates the command-parser mindset
by reasoning about intent, context, and required information.
"""
import logging
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RequestType(Enum):
    """Classification of what a user request fundamentally is."""
    CONVERSATION   = auto()   # General chat, questions, opinions
    TOOL_ACTION    = auto()   # Definite tool invocation (open app, search, play)
    MULTI_STEP     = auto()   # Complex task requiring a plan (build a project)
    MEMORY_STORE   = auto()   # User is teaching Friday something
    MEMORY_RECALL  = auto()   # User is asking Friday to recall something
    CONTINUATION   = auto()   # "Continue", "go ahead", "yes", "do it"
    CLARIFICATION  = auto()   # User answered a question Friday asked
    PREFERENCE_SET = auto()   # "I prefer X", "always use Y"
    CANCELLATION   = auto()   # "Stop", "cancel", "never mind"


@dataclass
class ReasoningResult:
    """
    The output of pre-execution reasoning.
    Guides the ConversationManager on what to do next.
    """
    request_type: RequestType = RequestType.CONVERSATION
    needs_clarification: bool = False
    clarification_topic: str = ""          # e.g. "preferred_editor"
    clarification_options: List[str] = field(default_factory=list)
    intent: Optional[str] = None           # pre-resolved intent if confident
    params: Dict[str, Any] = field(default_factory=dict)
    is_multi_step: bool = False
    plan_steps: List[str] = field(default_factory=list)
    confidence: float = 1.0
    reasoning_notes: str = ""              # debug trace


class ReasoningLayer:
    """
    Analyzes incoming user queries before the planner runs.
    Determines request type, detects ambiguity, builds multi-step plans.
    Runs fast using rule-based heuristics — no LLM call needed here.
    """

    # Commands that signal continuation / confirmation
    CONTINUATIONS = {"yes", "yeah", "yep", "sure", "ok", "okay", "go ahead", "do it",
                     "continue", "proceed", "go", "go on", "alright", "fine", "sounds good",
                     "please", "yup", "affirmative"}

    CANCELLATIONS = {"no", "nope", "cancel", "stop", "never mind", "nevermind",
                     "don't", "abort", "quit it", "forget it", "forget", "nah"}

    # Patterns that are clearly multi-step tasks
    MULTI_STEP_PATTERNS = [
        r"build\s+(a|an|the|my)?\s+\w+\s+(app|project|website|service|api)",
        r"create\s+(a|an|the|my)?\s+(react|next|vue|angular|flask|django|fastapi)\s+",
        r"set up\s+(my|a|the)?\s+",
        r"install\s+and\s+",
        r"deploy\s+(my|the|a)?\s+",
        r"start\s+(a|my|the)?\s+(new\s+)?project",
        r"scaffold\s+",
        r"initialize\s+",
    ]

    # Patterns that signal explicit memory storage
    MEMORY_STORE_PATTERNS = [
        r"\b(remember|note|record|store|save|keep\s+in\s+mind)\b",
        r"\bmy\s+\w+\s+is\b",
        r"\bi\s+(prefer|use|like|love|hate|want)\s+\w+",
        r"\balways\s+use\b",
        r"\bfavorite\b|\bfavourite\b",
        r"\bdefault\s+(to|is)\b",
    ]

    # Patterns that signal memory retrieval
    MEMORY_RECALL_PATTERNS = [
        r"\b(recall|remember|what\s+did\s+i|do\s+you\s+remember|what\s+is\s+my)\b",
        r"\bwhat\s+(was|were)\s+(my|the)\b",
        r"\bwhat\s+do\s+(i|you)\s+(use|prefer|like)\b",
    ]

    # Ambiguous "open X" targets that need clarification
    AMBIGUOUS_OPENS: Dict[str, Dict] = {
        "editor":      {"key": "preferred_editor",    "options": ["VS Code", "Cursor", "PyCharm", "Xcode"]},
        "ide":         {"key": "preferred_editor",    "options": ["VS Code", "Cursor", "PyCharm", "Xcode"]},
        "browser":     {"key": "preferred_browser",   "options": ["Chrome", "Brave", "Safari", "Firefox"]},
        "music":       {"key": "preferred_music_app", "options": ["Spotify", "Apple Music", "YouTube Music"]},
        "terminal":    {"key": "preferred_terminal",  "options": ["Terminal", "iTerm2", "Warp"]},
        "email":       {"key": "preferred_email_client", "options": ["Mail", "Spark", "Outlook"]},
        "calendar":    {"key": "preferred_calendar",  "options": ["Calendar", "Google Calendar", "Fantastical"]},
        "music app":   {"key": "preferred_music_app", "options": ["Spotify", "Apple Music", "YouTube Music"]},
        "media player":{"key": "preferred_music_app", "options": ["Spotify", "Apple Music", "YouTube Music"]},
        "code editor": {"key": "preferred_editor",    "options": ["VS Code", "Cursor", "PyCharm"]},
        "text editor": {"key": "preferred_editor",    "options": ["VS Code", "Cursor", "Vim"]},
        "code":        {"key": "preferred_editor",    "options": ["VS Code", "Cursor", "PyCharm", "Xcode"]},
    }

    # Play/music ambiguous patterns
    MUSIC_AMBIGUOUS_PATTERNS = [
        r"^play\s+(something|music|some\s+music|a\s+song|songs)$",
        r"^play\s+(something\s+)?(relaxing|chill|upbeat|sad|happy|calm|ambient|lo.?fi)(\s+music)?$",
        r"^(put\s+on|start)\s+(some\s+)?music$",
    ]

    def __init__(self, preference_manager=None):
        self._prefs = preference_manager
        self._multi_step_re = [re.compile(p, re.I) for p in self.MULTI_STEP_PATTERNS]
        self._memory_store_re = [re.compile(p, re.I) for p in self.MEMORY_STORE_PATTERNS]
        self._memory_recall_re = [re.compile(p, re.I) for p in self.MEMORY_RECALL_PATTERNS]
        self._music_ambiguous_re = [re.compile(p, re.I) for p in self.MUSIC_AMBIGUOUS_PATTERNS]

    def analyze(self, user_query: str, conversation_context: Optional[Dict] = None) -> ReasoningResult:
        """
        Analyze a user query and return structured reasoning about what to do.
        This is a fast, synchronous, rule-based analysis step.
        """
        q = user_query.strip()
        q_lower = q.lower()
        result = ReasoningResult()

        # 1. Continuation / confirmation?
        if q_lower in self.CONTINUATIONS or any(
            q_lower.startswith(c + " ") for c in ("yes ", "sure ", "ok ")
        ):
            result.request_type = RequestType.CONTINUATION
            result.reasoning_notes = "Detected continuation/confirmation"
            # Carry forward the pending action from context if available
            if conversation_context and conversation_context.get("pending_intent"):
                result.intent = conversation_context["pending_intent"]
                result.params = conversation_context.get("pending_params", {})
            return result

        # 2. Cancellation?
        if q_lower in self.CANCELLATIONS:
            result.request_type = RequestType.CANCELLATION
            result.reasoning_notes = "Detected cancellation"
            return result

        # 3. Explicit preference setting?
        if self._prefs and self._prefs.parse_and_store_explicit(q):
            result.request_type = RequestType.PREFERENCE_SET
            result.reasoning_notes = "Explicit preference statement detected and stored"
            return result
        if any(p.search(q) for p in self._memory_store_re):
            # Let it fall through — conversation manager will route to memory.store intent
            result.request_type = RequestType.MEMORY_STORE
            result.reasoning_notes = "Memory storage pattern detected"

        # 4. Memory recall?
        if any(p.search(q) for p in self._memory_recall_re):
            result.request_type = RequestType.MEMORY_RECALL
            result.reasoning_notes = "Memory recall pattern detected"
            return result

        # 5. Multi-step task?
        if any(p.search(q) for p in self._multi_step_re):
            result.request_type = RequestType.MULTI_STEP
            result.is_multi_step = True
            result.reasoning_notes = "Multi-step task pattern detected"
            result.plan_steps = self._build_plan(q)
            return result

        # 6. Ambiguous "open X" → check if clarification needed
        open_match = re.match(r"(?:open|launch|start|show)\s+(?:my\s+|the\s+)?(.+)", q_lower)
        if open_match:
            target = open_match.group(1).strip().rstrip("?. ")
            # Split compound queries: "open youtube and play X" → only check "youtube"
            target = re.split(r"\s+and\s+|\s+then\s+", target)[0].strip()

            if target in self.AMBIGUOUS_OPENS:
                spec = self.AMBIGUOUS_OPENS[target]
                pref_key = spec["key"]
                stored = self._prefs.get(pref_key) if self._prefs else None
                if stored:
                    # Preference known — no clarification needed
                    result.request_type = RequestType.TOOL_ACTION
                    result.intent = "launcher.open_application"
                    result.params = {"app_name": stored}
                    result.reasoning_notes = f"Resolved '{target}' from preference: {stored}"
                else:
                    # Ambiguous — ask user
                    result.request_type = RequestType.TOOL_ACTION
                    result.needs_clarification = True
                    result.clarification_topic = pref_key
                    result.clarification_options = spec["options"]
                    result.reasoning_notes = f"Ambiguous target '{target}' — need clarification"
                return result

        # 7. Ambiguous music/media request?
        if any(p.match(q_lower) for p in self._music_ambiguous_re):
            music_app = self._prefs.get("preferred_music_app") if self._prefs else None
            if music_app:
                result.request_type = RequestType.TOOL_ACTION
                result.intent = "launcher.open_application"
                result.params = {"app_name": music_app}
                result.reasoning_notes = f"Music request resolved via preference: {music_app}"
            else:
                result.request_type = RequestType.TOOL_ACTION
                result.needs_clarification = True
                result.clarification_topic = "preferred_music_app"
                result.clarification_options = ["Spotify", "Apple Music", "YouTube Music"]
                result.reasoning_notes = "Ambiguous music request — need preferred app"
            return result

        # 8. Default → let the planner handle it
        result.request_type = RequestType.TOOL_ACTION
        result.confidence = 0.9
        result.reasoning_notes = "No special pattern — routing to planner"
        return result

    def _build_plan(self, query: str) -> List[str]:
        """Build a rough multi-step execution plan for complex tasks."""
        q = query.lower()
        steps = []

        if "react" in q or "next" in q or "vite" in q:
            steps = [
                "Ask: Which framework? (Next.js / Vite / Remix)",
                "Create project directory",
                "Run npx create command",
                "Install dependencies",
                "Open VS Code",
                "Start dev server",
                "Open localhost in browser",
            ]
        elif "python" in q or "flask" in q or "fastapi" in q or "django" in q:
            steps = [
                "Create project directory",
                "Initialize virtual environment",
                "Install dependencies",
                "Open VS Code",
                "Create main entry file",
            ]
        elif "project" in q:
            steps = [
                "Check memory for recent project",
                "Open editor",
                "Open terminal",
                "Navigate to project folder",
            ]
        else:
            steps = ["Analyze request", "Execute primary action", "Confirm completion"]

        return steps

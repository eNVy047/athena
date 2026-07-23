"""
F.R.I.D.A.Y. Desktop State Manager.

Centralized state machine tracking all subsystem states.
Exposed to QML as a context property for reactive UI bindings.
"""
import logging
from enum import Enum, auto

from PySide6.QtCore import QObject, Signal, Property, Slot
from PySide6.QtQml import QmlElement

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    IDLE = auto()
    THINKING = auto()
    ANSWERING = auto()
    ERROR = auto()


class VoiceState(Enum):
    DISABLED = auto()
    IDLE = auto()
    LISTENING = auto()
    RECORDING = auto()
    PROCESSING = auto()
    SPEAKING = auto()
    ERROR = auto()


class ProviderStateInfo:
    def __init__(self):
        self.active_llm: str = "—"
        self.active_stt: str = "—"
        self.active_tts: str = "—"
        self.llm_latency_ms: float = 0.0
        self.stt_latency_ms: float = 0.0
        self.tts_latency_ms: float = 0.0
        self.memory_status: str = "—"
        self.browser_status: str = "—"
        self.vision_status: str = "—"


class DesktopStateManager(QObject):
    """
    Centralized reactive state manager for the F.R.I.D.A.Y. Desktop.

    Each state field emits a Qt signal when changed, which QML can
    bind to via the 'desktopState' context property.
    """

    # ── Qt Signals ──────────────────────────────────────────────────────────
    conversationStateChanged = Signal(str)
    voiceStateChanged = Signal(str)
    providerStateChanged = Signal()
    agentStatusChanged = Signal(str)
    errorOccurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._conversation_state = ConversationState.IDLE
        self._voice_state = VoiceState.DISABLED
        self._provider_info = ProviderStateInfo()
        self._agent_status = "Ready"

    # ── Conversation State ──────────────────────────────────────────────────

    @Property(str, notify=conversationStateChanged)
    def conversationState(self) -> str:
        return self._conversation_state.name

    def set_conversation_state(self, state: ConversationState) -> None:
        if self._conversation_state != state:
            self._conversation_state = state
            self.conversationStateChanged.emit(state.name)
            logger.debug("[DesktopState] Conversation → %s", state.name)

    # ── Voice State ─────────────────────────────────────────────────────────

    @Property(str, notify=voiceStateChanged)
    def voiceState(self) -> str:
        return self._voice_state.name

    def set_voice_state(self, state: VoiceState) -> None:
        if self._voice_state != state:
            self._voice_state = state
            self.voiceStateChanged.emit(state.name)
            logger.debug("[DesktopState] Voice → %s", state.name)

    # ── Provider Info ───────────────────────────────────────────────────────

    @Property(str, notify=providerStateChanged)
    def activeLLM(self) -> str:
        return self._provider_info.active_llm

    @Property(str, notify=providerStateChanged)
    def activeSTT(self) -> str:
        return self._provider_info.active_stt

    @Property(str, notify=providerStateChanged)
    def activeTTS(self) -> str:
        return self._provider_info.active_tts

    @Property(float, notify=providerStateChanged)
    def llmLatencyMs(self) -> float:
        return self._provider_info.llm_latency_ms

    @Property(str, notify=providerStateChanged)
    def memoryStatus(self) -> str:
        return self._provider_info.memory_status

    @Property(str, notify=providerStateChanged)
    def browserStatus(self) -> str:
        return self._provider_info.browser_status

    @Property(str, notify=providerStateChanged)
    def visionStatus(self) -> str:
        return self._provider_info.vision_status

    def update_provider_info(self, **kwargs) -> None:
        """Updates one or more provider info fields and emits providerStateChanged."""
        for key, value in kwargs.items():
            if hasattr(self._provider_info, key):
                setattr(self._provider_info, key, value)
        self.providerStateChanged.emit()

    # ── Agent Status ────────────────────────────────────────────────────────

    @Property(str, notify=agentStatusChanged)
    def agentStatus(self) -> str:
        return self._agent_status

    def set_agent_status(self, status: str) -> None:
        if self._agent_status != status:
            self._agent_status = status
            self.agentStatusChanged.emit(status)

    # ── Error reporting ─────────────────────────────────────────────────────

    def emit_error(self, message: str) -> None:
        logger.error("[DesktopState] Error: %s", message)
        self.errorOccurred.emit(message)
        self.set_conversation_state(ConversationState.ERROR)

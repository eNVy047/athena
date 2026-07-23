"""
F.R.I.D.A.Y. Desktop — SignalBridge.

Bridges QML signals to asyncio Python coroutines and vice versa.
Handles chat, voice, error signals, streaming token delivery,
and live status/thinking updates.
"""
import asyncio
import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot
from friday.kernel.runtime import FridayAgent

logger = logging.getLogger(__name__)


class SignalBridge(QObject):
    """
    Central bridge between QML UI events and F.R.I.D.A.Y. backend.

    Python → QML signals:
        responseReady(sender, message) — full response
        tokenReady(token)              — streaming token chunk
        statusChanged(status)          — agent status text ("Ready", "Error", etc.)
        thinkingUpdate(status)         — live thinking step ("Planning…", "Opening VS Code…")
        voiceStatusChanged(status)     — voice system status
        voiceTranscript(text)          — STT transcript from voice
        errorOccurred(error)           — error message
        providerInfoChanged()          — provider dashboard refresh

    QML → Python slots:
        sendMessage(text)    — chat message from user
        startVoice()         — begin push-to-talk recording
        stopVoice()          — stop recording and process
        cancelRequest()      — abort current agent task
    """

    # Python → QML
    responseReady       = Signal(str, str)   # sender, message
    tokenReady          = Signal(str)         # streaming token
    statusChanged       = Signal(str)         # overall status ("Ready", "Error")
    thinkingUpdate      = Signal(str)         # live step ("Thinking…", "Planning…", "Done ✓")
    voiceStatusChanged  = Signal(str)         # voice status
    voiceTranscript     = Signal(str, str)    # user_text, friday_response
    errorOccurred       = Signal(str)         # error description
    providerInfoChanged = Signal()            # trigger provider dashboard refresh
    behaviorsReady      = Signal(list)        # behavior list for BehaviorLearning.qml

    def __init__(self, agent: FridayAgent, desktop_state=None, voice_manager=None, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.desktop_state = desktop_state
        self.voice_manager = voice_manager
        self._current_task: Optional[asyncio.Task] = None

        # Wire status callback so ConversationManager can emit thinkingUpdate
        self.agent.set_status_callback(self._on_thinking_update)

    # ── Status callback ───────────────────────────────────────────────────────

    def _on_thinking_update(self, status: str) -> None:
        """Called by ConversationManager at each pipeline step."""
        self.thinkingUpdate.emit(status)

    # ── Chat ─────────────────────────────────────────────────────────────────

    @Slot(str)
    def sendMessage(self, message: str) -> None:
        """Called from QML when the user submits a chat message."""
        if not message.strip():
            return
        logger.info("[Bridge] User message: %r", message[:100])
        self.statusChanged.emit("Thinking...")
        self.thinkingUpdate.emit("Thinking...")

        if self.desktop_state:
            from friday.apps.desktop.desktop_state import ConversationState
            self.desktop_state.set_conversation_state(ConversationState.THINKING)

        # Cancel any in-flight task before starting a new one
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

        self._current_task = asyncio.create_task(self._process_message(message))

    async def _process_message(self, message: str) -> None:
        try:
            response = await self.agent.process_input(message)
            self.responseReady.emit("Friday", response)
            self.statusChanged.emit("Ready")
            self.thinkingUpdate.emit("Ready")
            if self.desktop_state:
                from friday.apps.desktop.desktop_state import ConversationState
                self.desktop_state.set_conversation_state(ConversationState.IDLE)

        except asyncio.CancelledError:
            logger.info("[Bridge] Message task cancelled.")
            self.statusChanged.emit("Ready")
            self.thinkingUpdate.emit("Cancelled")
        except Exception as exc:
            error_msg = str(exc)
            logger.error("[Bridge] Agent error: %s", error_msg, exc_info=True)
            self.responseReady.emit("System", f"⚠️ Error: {error_msg}")
            self.statusChanged.emit("Error")
            self.thinkingUpdate.emit("Error")
            self.errorOccurred.emit(error_msg)
            if self.desktop_state:
                self.desktop_state.emit_error(error_msg)

    @Slot()
    def cancelRequest(self) -> None:
        """Called from QML to cancel the current in-flight agent request."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self.statusChanged.emit("Cancelled")
            self.thinkingUpdate.emit("Cancelled — ready for next request.")
            logger.info("[Bridge] Request cancelled by user.")

    # ── Behavior Learning API ─────────────────────────────────────────────

    @Slot()
    def refreshBehaviors(self) -> None:
        """Called from QML to load and display all learned behaviors."""
        cm = getattr(self.agent, "_conversation_manager", None)
        if cm is None:
            self.behaviorsReady.emit([])
            return
        try:
            behaviors = cm.get_all_behaviors()
            self.behaviorsReady.emit(behaviors)
        except Exception as exc:
            logger.warning("[Bridge] refreshBehaviors failed: %s", exc)
            self.behaviorsReady.emit([])

    @Slot(str, str)
    def forgetBehavior(self, pattern: str, choice: str) -> None:
        """Called from QML to remove a specific learned choice."""
        cm = getattr(self.agent, "_conversation_manager", None)
        if cm:
            cm.forget_choice(pattern, choice)
            logger.info("[Bridge] Forgot behavior: %s/%s", pattern, choice)

    @Slot()
    def resetAllBehaviors(self) -> None:
        """Called from QML to wipe all learned behaviors."""
        cm = getattr(self.agent, "_conversation_manager", None)
        if cm:
            cm.reset_all_behaviors()
            logger.info("[Bridge] All behaviors reset.")

    # ── Voice ─────────────────────────────────────────────────────────────────

    @Slot()
    def startVoice(self) -> None:
        """Called from QML to start voice recording (push-to-talk begin)."""
        logger.info("[Bridge] Voice start requested.")
        self.voiceStatusChanged.emit("Listening...")
        if self.desktop_state:
            from friday.apps.desktop.desktop_state import VoiceState
            self.desktop_state.set_voice_state(VoiceState.RECORDING)

        if self.voice_manager:
            asyncio.create_task(self._start_voice())

    async def _start_voice(self) -> None:
        try:
            from friday.voice.speech_state import VoiceMode
            await self.voice_manager.start(mode=VoiceMode.PUSH_TO_TALK)
        except Exception as exc:
            logger.error("[Bridge] Voice start failed: %s", exc)
            self.voiceStatusChanged.emit("Voice Error")
            self.errorOccurred.emit(f"Voice failed to start: {exc}")

    @Slot()
    def stopVoice(self) -> None:
        """Called from QML to stop voice recording (push-to-talk end)."""
        logger.info("[Bridge] Voice stop requested.")
        self.voiceStatusChanged.emit("Processing...")
        if self.desktop_state:
            from friday.apps.desktop.desktop_state import VoiceState
            self.desktop_state.set_voice_state(VoiceState.PROCESSING)

        if self.voice_manager:
            asyncio.create_task(self._stop_voice())

    async def _stop_voice(self) -> None:
        try:
            await self.voice_manager.stop()
            self.voiceStatusChanged.emit("Ready")
            if self.desktop_state:
                from friday.apps.desktop.desktop_state import VoiceState
                self.desktop_state.set_voice_state(VoiceState.IDLE)
        except Exception as exc:
            logger.error("[Bridge] Voice stop failed: %s", exc)
            self.voiceStatusChanged.emit("Voice Error")

    async def on_voice_response(self, user_text: str, friday_response: str) -> None:
        """
        Callback invoked by SpeechPipeline when a voice command completes.
        Emits the transcript and response to QML.
        """
        logger.info("[Bridge] Voice response ready.")
        self.voiceTranscript.emit(user_text, friday_response)
        self.responseReady.emit("You (voice)", user_text)
        self.responseReady.emit("Friday", friday_response)
        self.voiceStatusChanged.emit("Listening...")

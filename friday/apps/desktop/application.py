"""
F.R.I.D.A.Y. Desktop Application — Entry point and boot orchestrator.

Boot sequence:
1. Create Qt + qasync event loop
2. Bootstrap FridayKernel (dirs, DI, tool registry)
3. Initialize all providers async (LLM, STT, TTS, memory…)
4. Create FridayAgent (kernel wrapper)
5. Create DesktopStateManager
6. Create VoiceManager wired to STT/TTS providers
7. Create SignalBridge (agent + state + voice)
8. Register QML context properties
9. Run Qt event loop
"""
import asyncio
import logging
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
import qasync  # type: ignore

from friday.kernel.kernel import FridayKernel
from friday.kernel.runtime import FridayAgent
from friday.apps.desktop.signal_bridge import SignalBridge
from friday.apps.desktop.theme_manager import ThemeManager
from friday.apps.desktop.desktop_state import DesktopStateManager, VoiceState

logger = logging.getLogger(__name__)


class DesktopApplication:
    """
    F.R.I.D.A.Y. Desktop Application — production client of the Friday OS.
    """

    def __init__(self):
        self.app = QGuiApplication(sys.argv)
        self.app.setApplicationName("F.R.I.D.A.Y.")
        self.app.setOrganizationName("Friday AI")

        # Merge Qt + asyncio event loops via qasync
        self.loop = qasync.QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)

        # ── 1. Bootstrap kernel (sync) ─────────────────────────────────────
        self.kernel = FridayKernel(storage_root=Path("friday_data"))
        self.kernel.bootstrap()
        logger.info("[DesktopApp] Kernel bootstrapped.")

        # ── 2. Create agent wrapper ────────────────────────────────────────
        self.agent = FridayAgent(kernel=self.kernel)

        # ── 3. Desktop state manager ───────────────────────────────────────
        self.desktop_state = DesktopStateManager(parent=self.app)

        # ── 4. Voice manager (lazy init — connected after provider init) ───
        self.voice_manager = None

        # ── 5. Signal bridge ───────────────────────────────────────────────
        self.bridge = SignalBridge(
            agent=self.agent,
            desktop_state=self.desktop_state,
            voice_manager=None,  # will be set after async init
            parent=self.app,
        )
        self.theme_manager = ThemeManager(parent=self.app)

        # ── 6. QML Engine ──────────────────────────────────────────────────
        self.engine = QQmlApplicationEngine()
        ctx = self.engine.rootContext()
        ctx.setContextProperty("bridge", self.bridge)
        ctx.setContextProperty("themeManager", self.theme_manager)
        ctx.setContextProperty("desktopState", self.desktop_state)

    def run(self) -> None:
        self.engine.load("friday/apps/desktop/qml/Main.qml")
        if not self.engine.rootObjects():
            logger.critical("[DesktopApp] Failed to load QML — check Main.qml path.")
            sys.exit(-1)

        with self.loop:
            # Schedule async initialization after the event loop starts
            self.loop.create_task(self._async_init())
            self.loop.run_forever()

    async def _async_init(self) -> None:
        """
        Performs all async initialization after the Qt event loop is running.
        This must be async to safely initialize providers and voice pipeline.
        """
        # 1. Initialize all providers
        logger.info("[DesktopApp] Initializing providers...")
        try:
            await self.kernel.initialize_providers()
            logger.info("[DesktopApp] All providers initialized.")
            pm = self.kernel.provider_manager

            # Update provider state for dashboard
            if pm:
                llm_name = pm.config.get("LLM_PROVIDER", "—")
                stt_name = pm.config.get("STT_PROVIDER", "—")
                tts_name = pm.config.get("TTS_PROVIDER", "—")
                self.desktop_state.update_provider_info(
                    active_llm=llm_name,
                    active_stt=stt_name,
                    active_tts=tts_name,
                    memory_status="Mem0 Connected" if pm.config.get("MEM0_API_KEY") else "Local",
                )

        except Exception as exc:
            logger.warning("[DesktopApp] Provider initialization had errors: %s", exc)

        # 1b. Wire ConversationManager now that providers are live
        pm = self.kernel.provider_manager
        self.agent.setup_conversation_manager(
            provider_manager=pm,
            storage_root=Path("friday_data"),
        )
        # Re-wire status callback (agent may have been created before bridge)
        self.agent.set_status_callback(self.bridge._on_thinking_update)
        logger.info("[DesktopApp] ConversationManager wired with live providers.")

        # 2. Initialize VoiceManager with active STT/TTS providers
        try:
            pm = self.kernel.provider_manager
            if pm is not None:
                # Read configured preferred providers from env (defaults to sarvam)
                stt_pref = pm.config.get("STT_PROVIDER", "sarvam")
                tts_pref = pm.config.get("TTS_PROVIDER", "sarvam")

                # Walk the fallback chain to find first connected provider
                def get_first_available(category: str, primary: str):
                    chain = pm.registry.get_fallback_chain(category, primary)
                    for p in chain:
                        if p.is_connected:
                            return p
                    # If none connected yet, return first in chain (will be connected by execute_with_fallback)
                    return chain[0] if chain else None

                stt_provider = get_first_available("stt", stt_pref)
                tts_provider = get_first_available("tts", tts_pref)

                if stt_provider and tts_provider:
                    from friday.voice.voice_manager import VoiceManager
                    self.voice_manager = VoiceManager(
                        agent=self.agent,
                        stt_provider=stt_provider,
                        tts_provider=tts_provider,
                    )
                    # Register voice response callback for UI emission
                    self.voice_manager.pipeline.response_callback = (
                        self.bridge.on_voice_response
                    )
                    self.voice_manager.pipeline.ui_callbacks = {
                        "transcript_update": self.bridge.emit_voice_transcript_update,
                        "live_response_start": self.bridge.emit_live_response_start,
                        "token_ready": self.bridge.emit_token_ready,
                        "voice_status": self.bridge.voiceStatusChanged.emit,
                    }
                    # Wire voice manager to bridge
                    self.bridge.voice_manager = self.voice_manager
                    self.desktop_state.set_voice_state(VoiceState.IDLE)
                    logger.info(
                        "[DesktopApp] VoiceManager ready (STT=%s, TTS=%s).",
                        stt_provider.metadata.name,
                        tts_provider.metadata.name,
                    )
                else:
                    logger.warning("[DesktopApp] No STT or TTS provider available. Voice disabled.")
                    self.desktop_state.set_voice_state(VoiceState.DISABLED)

        except Exception as exc:
            logger.error("[DesktopApp] VoiceManager init failed: %s", exc, exc_info=True)
            self.desktop_state.set_voice_state(VoiceState.DISABLED)


        logger.info("[DesktopApp] Async initialization complete. F.R.I.D.A.Y. is ready.")


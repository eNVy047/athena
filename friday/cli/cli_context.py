"""
CLIContext — Shared bootstrap for the F.R.I.D.A.Y. CLI.

Boots the exact same pipeline as DesktopApplication._async_init()
but without any Qt dependency.
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)

_STORAGE_ROOT = Path("friday_data")


class CLIContext:
    """
    Single shared runtime context for the entire CLI session.

    Lifecycle:
        ctx = CLIContext()
        await ctx.initialize()
        response = await ctx.process("hello")
        await ctx.shutdown()
    """

    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        self.kernel = None
        self.agent = None
        self.voice_manager = None
        self._status_callback = status_callback
        self._initialized = False
        self._init_time: Optional[float] = None

    # ── Bootstrap ─────────────────────────────────────────────────────────────

    async def initialize(self, verbose: bool = False) -> None:
        """
        Initialize the full Friday stack — identical to Desktop boot sequence.
        """
        from dotenv import load_dotenv
        load_dotenv()

        t0 = time.monotonic()

        # 1. Kernel bootstrap (sync — sets up DI, tool registry, dirs)
        from friday.kernel.kernel import FridayKernel
        self.kernel = FridayKernel(storage_root=_STORAGE_ROOT)
        self.kernel.bootstrap()
        if verbose:
            logger.info("[CLI] Kernel bootstrapped.")

        # 2. Create agent wrapper (providers not live yet)
        from friday.kernel.runtime import FridayAgent
        self.agent = FridayAgent(
            kernel=self.kernel,
            status_callback=self._status_callback,
        )

        # 3. Initialize all providers async
        if verbose:
            logger.info("[CLI] Initializing providers...")
        try:
            await self.kernel.initialize_providers()
            if verbose:
                logger.info("[CLI] All providers initialized.")
        except Exception as exc:
            logger.warning("[CLI] Provider initialization had errors: %s", exc)

        # 4. Wire ConversationManager with live providers
        pm = self.kernel.provider_manager
        self.agent.setup_conversation_manager(
            provider_manager=pm,
            storage_root=_STORAGE_ROOT,
        )
        self.agent.set_status_callback(self._status_callback)
        if verbose:
            logger.info("[CLI] ConversationManager initialized.")

        # 5. Wire VoiceManager (same logic as Desktop)
        try:
            if pm is not None:
                stt_pref = pm.config.get("STT_PROVIDER", "sarvam")
                tts_pref = pm.config.get("TTS_PROVIDER", "sarvam")

                def get_first_available(category: str, primary: str):
                    chain = pm.registry.get_fallback_chain(category, primary)
                    for p in chain:
                        if p.is_connected:
                            return p
                    return chain[0] if chain else None

                stt = get_first_available("stt", stt_pref)
                tts = get_first_available("tts", tts_pref)

                if stt and tts:
                    from friday.voice.voice_manager import VoiceManager
                    self.voice_manager = VoiceManager(
                        agent=self.agent,
                        stt_provider=stt,
                        tts_provider=tts,
                    )
                    if verbose:
                        logger.info(
                            "[CLI] VoiceManager ready (STT=%s, TTS=%s).",
                            stt.metadata.name,
                            tts.metadata.name,
                        )
        except Exception as exc:
            logger.warning("[CLI] VoiceManager init failed: %s", exc)

        self._initialized = True
        self._init_time = time.monotonic() - t0

    # ── Core process ──────────────────────────────────────────────────────────

    async def process(self, query: str, stream_callback=None) -> str:
        """Route a query through the full Friday pipeline.

        Args:
            query: Raw user text.
            stream_callback: Optional callable(token: str) for live LLM token delivery.
        """
        if not self._initialized:
            raise RuntimeError("CLIContext not initialized. Call initialize() first.")
        return await self.agent.process_input(query, stream_callback=stream_callback)

    # ── Convenience accessors ─────────────────────────────────────────────────

    @property
    def provider_manager(self):
        return self.kernel.provider_manager if self.kernel else None

    @property
    def conversation_manager(self):
        return getattr(self.agent, "_conversation_manager", None)

    def get_chat_history(self) -> list:
        if self.agent:
            return self.agent.get_chat_history()
        return []

    # ── Shutdown ──────────────────────────────────────────────────────────────

    async def shutdown(self) -> None:
        """Graceful cleanup."""
        if self.voice_manager:
            try:
                await self.voice_manager.stop()
            except Exception:
                pass
        self._initialized = False
        logger.info("[CLI] Shutdown complete.")

"""
F.R.I.D.A.Y. Runtime — FridayAgent

Conversation controller that routes all user input through the
ConversationManager for natural language understanding, preference learning,
clarification, and intelligent tool execution.
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable

from friday.kernel.kernel import FridayKernel

logger = logging.getLogger(__name__)


class FridayAgent:
    """
    High-level agent facade.

    Wraps ConversationManager and exposes `process_input()` as the
    single entry point for all user interactions (chat + voice).
    """

    def __init__(
        self,
        kernel: FridayKernel,
        status_callback: Optional[Callable[[str], None]] = None,
    ):
        self.kernel = kernel
        self._status_callback = status_callback
        self._conversation_manager = None  # lazy-initialized after providers ready

    def setup_conversation_manager(
        self,
        provider_manager=None,
        storage_root: Path = Path("friday_data"),
    ) -> None:
        """
        Initialize the ConversationManager with live providers.
        Must be called after ProviderManager.initialize_all() completes.
        """
        from friday.conversation.conversation_manager import ConversationManager

        self._conversation_manager = ConversationManager(
            kernel=self.kernel,
            provider_manager=provider_manager or self.kernel.provider_manager,
            storage_root=storage_root,
            status_callback=self._status_callback,
        )
        logger.info("[FridayAgent] ConversationManager initialized.")

    async def process_input(self, user_query: str, stream_callback=None) -> str:
        """
        Main entry point for all user interactions.
        Routes through ConversationManager for natural language understanding.
        Falls back to direct kernel execution if ConversationManager not ready.

        Args:
            user_query: Raw user text.
            stream_callback: Optional callable(token: str) for live LLM streaming.
        """
        if self._conversation_manager is not None:
            return await self._conversation_manager.process(
                user_query, stream_callback=stream_callback
            )

        # Fallback: ConversationManager not yet initialized — direct kernel call
        logger.warning(
            "[FridayAgent] ConversationManager not ready. "
            "Falling back to direct kernel execution for: %r",
            user_query[:60],
        )
        return await self.kernel.execute(user_query, stream_callback=stream_callback)

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        """Wire a UI status callback after construction."""
        self._status_callback = callback
        if self._conversation_manager:
            self._conversation_manager.status_callback = callback

    def get_chat_history(self) -> List[Dict[str, str]]:
        """Return chat history from the conversation manager."""
        if self._conversation_manager:
            return self._conversation_manager.get_chat_history()
        return []

    def reset(self) -> None:
        """Clear conversation context."""
        if self._conversation_manager:
            self._conversation_manager.reset()

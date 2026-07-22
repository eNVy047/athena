import logging
from typing import Dict, Any, List
from friday.kernel.kernel import FridayKernel

logger = logging.getLogger(__name__)

class FridayAgent:
    """Conversation Controller wrapper managing prompt injection loops."""
    def __init__(self, kernel: FridayKernel):
        self.kernel = kernel
        self.chat_history: List[Dict[str, str]] = []
        self._memory_store = {}

    async def process_input(self, user_query: str) -> str:
        """Processes transcription requests by delegating completely to the FridayKernel execution orchestration."""
        self.chat_history.append({"role": "user", "content": user_query})
        self.kernel.state.active_conversation_id = "conv_current"
        self.kernel.state.active_planner_goal = user_query[:50]
        
        # Completely delegate task execution orchestration to FridayKernel
        response_text = await self.kernel.execute(user_query)
        
        self.chat_history.append({"role": "assistant", "content": response_text})
        return response_text

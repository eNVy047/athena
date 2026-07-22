from __future__ import annotations

import logging
from typing import List, Callable, Coroutine, Any

logger = logging.getLogger("friday-agent")

class AgentHooks:
    def __init__(self):
        self.pre_hooks: List[Callable[[Any], Coroutine[Any, Any, None]]] = []
        self.post_hooks: List[Callable[[Any, Any], Coroutine[Any, Any, None]]] = []

    def register_pre_hook(self, hook: Callable[[Any], Coroutine[Any, Any, None]]) -> None:
        self.pre_hooks.append(hook)

    def register_post_hook(self, hook: Callable[[Any, Any], Coroutine[Any, Any, None]]) -> None:
        self.post_hooks.append(hook)

    async def run_pre_hooks(self, context: Any) -> None:
        for hook in self.pre_hooks:
            try:
                await hook(context)
            except Exception as e:
                logger.error(f"[AgentHooks] Pre-hook error: {e}")

    async def run_post_hooks(self, context: Any, result: Any) -> None:
        for hook in self.post_hooks:
            try:
                await hook(context, result)
            except Exception as e:
                logger.error(f"[AgentHooks] Post-hook error: {e}")

from typing import Dict, Any, Callable, List
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AgentMessage:
    id: str
    sender_id: str
    recipient_id: str
    content: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class MessageBus:
    """Internal message bus for agent-to-agent communication."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[AgentMessage], None]]] = {}
        
    def subscribe(self, agent_id: str, callback: Callable[[AgentMessage], None]) -> None:
        if agent_id not in self._subscribers:
            self._subscribers[agent_id] = []
        self._subscribers[agent_id].append(callback)
        logger.debug(f"Agent {agent_id} subscribed to MessageBus")
        
    async def publish(self, message: AgentMessage) -> None:
        logger.debug(f"Message from {message.sender_id} to {message.recipient_id}: {message.content}")
        
        # Route to specific recipient
        if message.recipient_id in self._subscribers:
            for callback in self._subscribers[message.recipient_id]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
                    
        # Route to broadcast
        if message.recipient_id == "broadcast" or message.recipient_id == "*":
            for agent_id, callbacks in self._subscribers.items():
                if agent_id != message.sender_id:
                    for callback in callbacks:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(message)
                        else:
                            callback(message)

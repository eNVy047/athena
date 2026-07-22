from __future__ import annotations

from typing import Dict, List, Any

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        self.conversations[conversation_id].append({"role": role, "content": content})

    def get_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        return self.conversations.get(conversation_id, [])

    def clear_history(self, conversation_id: str) -> None:
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]

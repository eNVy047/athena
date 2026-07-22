from typing import List
from friday.memory.memory_models import RetrievedMemory, MemoryContext


class MemoryContextFormatter:
    def format(self, retrieved: List[RetrievedMemory]) -> MemoryContext:
        """Formats retrieved memory entries into a user-friendly background context block."""
        if not retrieved:
            return MemoryContext(retrieved=[], formatted="")

        formatted_parts = []

        # Group by memory type for clean structure
        by_type = {}
        for r in retrieved:
            m_type = r.entry.memory_type.value.upper().replace("_", " ")
            if m_type not in by_type:
                by_type[m_type] = []
            by_type[m_type].append(r.entry.content)

        for m_type, contents in by_type.items():
            formatted_parts.append(f"### {m_type} MEMORIES:")
            for content in contents:
                formatted_parts.append(f"- {content}")

        formatted_str = (
            "[BACKGROUND MEMORY CONTEXT]\n" + "\n".join(formatted_parts) + "\n"
        )
        return MemoryContext(retrieved=retrieved, formatted=formatted_str)

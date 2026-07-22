import re
from typing import List
from friday.memory.memory_models import MemoryEntry, Relationship


class MemoryRelationships:
    def __init__(self):
        # A simple regex entity extractor to relate memories
        self.entity_pattern = re.compile(
            r"\b(stark|tony|jarvis|friday|python|mcp|openai|gemini)\b", re.I
        )

    def extract_relationships(
        self, entry: MemoryEntry, all_entries: List[MemoryEntry]
    ) -> List[Relationship]:
        """Extracts associations/relationships between the new entry and existing entries."""
        if not entry.id:
            return []

        relationships = []
        entry_entities = set(self.entity_pattern.findall(entry.content.lower()))
        if not entry_entities:
            return []

        for other in all_entries:
            if not other.id or other.id == entry.id:
                continue

            other_entities = set(self.entity_pattern.findall(other.content.lower()))
            overlap = entry_entities.intersection(other_entities)

            if overlap:
                # Create a bidirectional or undirected relationship represented as source -> target
                relationships.append(
                    Relationship(
                        source_id=entry.id,
                        target_id=other.id,
                        relation_type="entity_overlap",
                        weight=min(1.0, 0.2 + 0.3 * len(overlap)),
                    )
                )
        return relationships

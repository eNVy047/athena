import re
from typing import Dict, Any


class MemoryImportanceScorer:
    def __init__(self):
        # Keyword triggers for high-importance topics
        self.rules = [
            (re.compile(r"\b(api key|secret|password|credential|token)\b", re.I), 9.5),
            (re.compile(r"\b(always|never|must|strictly)\b", re.I), 8.5),
            (re.compile(r"\b(prefer|like|dislike|favorite|hate|love)\b", re.I), 7.5),
            (re.compile(r"\b(project|architect|codebase|feature|phase)\b", re.I), 7.0),
            (re.compile(r"\b(name|email|phone|contact|address|user)\b", re.I), 6.5),
            (re.compile(r"\b(error|bug|issue|failure|fix)\b", re.I), 6.0),
        ]

    def calculate_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculates importance score of a memory content on a scale of 1.0 to 10.0."""
        # Start with baseline importance based on metadata category
        category = metadata.get("category", "general").lower()
        if category == "user_profile":
            base_score = 7.0
        elif category in ["security", "credential"]:
            base_score = 9.0
        elif category == "reflection":
            base_score = 8.0
        else:
            base_score = 3.0

        # Apply rule overrides
        for regex, weight in self.rules:
            if regex.search(content):
                base_score = max(base_score, weight)

        # Length factor (longer context usually contains more detail up to a point)
        length_bonus = min(1.0, len(content) / 500.0)

        score = base_score + length_bonus
        return min(10.0, max(1.0, score))

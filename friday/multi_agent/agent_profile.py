from dataclasses import dataclass, field
from typing import List

@dataclass
class AgentProfile:
    agent_id: str
    name: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    max_concurrency: int = 1
    priority: int = 0

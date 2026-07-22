from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ProviderMetadata:
    category: str
    name: str
    version: str
    capabilities: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)

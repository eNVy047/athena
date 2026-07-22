from typing import List, Type, Dict, Any, Optional
from pydantic import BaseModel, Field

class ToolMetadata(BaseModel):
    """Metadata schema defining tool capabilities and constraints."""
    name: str
    description: str
    version: str = "1.0.0"
    category: str = "general"
    required_capabilities: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    timeout: float = 60.0
    retry_limit: int = 2
    parameter_schema: Type[BaseModel]
    examples: List[str] = Field(default_factory=list)

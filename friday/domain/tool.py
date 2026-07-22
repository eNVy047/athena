from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type
from pydantic import BaseModel

class ToolExecutionContext(BaseModel):
    session_id: str
    user_id: str
    metadata: Dict[str, Any] = {}

class AbstractTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def required_capabilities(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def parameter_schema(self) -> Type[BaseModel]:
        pass

    @abstractmethod
    async def execute(self, context: ToolExecutionContext, arguments: Dict[str, Any]) -> Any:
        pass

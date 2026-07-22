from typing import Dict, Any, Type
from pydantic import BaseModel, ValidationError

class ToolValidator:
    @staticmethod
    def validate_inputs(schema: Type[BaseModel], arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validates raw dict arguments against a Pydantic model schema."""
        try:
            return schema(**arguments).model_dump()
        except ValidationError as e:
            raise ValueError(f"Arguments failed schema validation: {e.errors()}")

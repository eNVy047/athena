import uuid
from typing import Dict, Any, Optional
from friday.core.cognition.models import Intent

class IntentEngine:
    """Parses raw text, voice, or system triggers into structured Friday intents."""
    def __init__(self):
        self._parsers: Dict[str, Any] = {}

    def register_parser(self, intent_name: str, parser_func: Any) -> None:
        self._parsers[intent_name] = parser_func

    async def parse(self, raw_input: str, context: Optional[Dict[str, Any]] = None) -> Intent:
        # Provider-agnostic base parsing (rules-based parsing fallback)
        lower_input = raw_input.lower()
        for name, parser in self._parsers.items():
            parsed_params = parser(lower_input)
            if parsed_params is not None:
                return Intent(
                    id=str(uuid.uuid4()),
                    name=name,
                    confidence=1.0,
                    parameters=parsed_params,
                    raw_request=raw_input
                )
        
        # Fallback default intent parsing
        return Intent(
            id=str(uuid.uuid4()),
            name="default.unknown",
            confidence=0.1,
            parameters={"query": raw_input},
            raw_request=raw_input
        )

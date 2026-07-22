import re

class InputSanitizer:
    """Prevents Prompt Injection attacks."""
    
    @staticmethod
    def sanitize(prompt: str) -> str:
        # Very basic mock sanitization
        bad_words = ["ignore previous instructions", "system prompt"]
        sanitized = prompt
        for word in bad_words:
            sanitized = re.sub(word, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        return sanitized

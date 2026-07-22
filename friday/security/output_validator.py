class OutputValidator:
    """Validates that outputs from LLMs don't contain malicious payloads."""
    
    @staticmethod
    def validate(output: str) -> bool:
        if "<script>" in output or "eval(" in output:
            return False
        return True

class CredentialManager:
    """Wraps SecretManager for specific service credentials."""
    def __init__(self, secret_manager):
        self.sm = secret_manager
        
    def get_provider_key(self, provider: str) -> str:
        key = self.sm.get_secret(f"{provider.upper()}_API_KEY")
        if not key:
            raise ValueError(f"Missing API key for provider {provider}")
        return key

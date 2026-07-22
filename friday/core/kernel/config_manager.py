import os
from typing import Dict, Any
from friday.providers.base.provider_config import ProviderConfig

class ConfigManager:
    """Loads and validates configuration environment variables for the Friday OS Core."""
    def __init__(self):
        self._config: Dict[str, Any] = {}

    def load(self) -> None:
        self._config["server_name"] = os.getenv("SERVER_NAME", "FRIDAY")
        self._config["sandbox_enabled"] = os.getenv("SANDBOX_ENABLED", "true").lower() == "true"
        
        # Merge global provider configurations
        provider_conf = ProviderConfig.get_global_config()
        self._config.update(provider_conf)

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)


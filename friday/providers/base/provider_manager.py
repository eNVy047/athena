import logging
import asyncio
from typing import Dict, Any, List, Callable, Coroutine
from friday.providers.base.provider import Provider
from friday.providers.base.provider_registry import ProviderRegistry
from friday.providers.base.provider_factory import ProviderFactory
from friday.providers.base.provider_config import ProviderConfig

logger = logging.getLogger(__name__)

class ProviderManager:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or ProviderConfig.get_global_config()
        self.registry = ProviderFactory.create_and_initialize_registry(self.config)

    async def initialize_all(self) -> None:
        """Initializes and connects all registered providers."""
        for category in self.registry._providers:
            for name, provider in self.registry._providers[category].items():
                try:
                    await provider.initialize()
                    await provider.connect()
                    logger.info(f"Initialized & connected provider: {category}/{name}")
                except Exception as e:
                    logger.warning(f"Deferred connection for provider {category}/{name}: {e}")

    async def shutdown_all(self) -> None:
        """Gracefully disconnects all registered providers."""
        for category in self.registry._providers:
            for name, provider in self.registry._providers[category].items():
                try:
                    await provider.disconnect()
                except Exception as e:
                    logger.error(f"Error disconnecting provider {category}/{name}: {e}")

    async def execute_with_fallback(self, category: str, operation: Callable[[Provider], Coroutine[Any, Any, Any]]) -> Any:
        """Resolves the configured primary provider. If it fails, tries fallbacks in priority order."""
        primary_env_key = f"{category.upper()}_PROVIDER"
        primary_name = self.config.get(primary_env_key, "")
        
        # If not specified, default to first registered or raise
        if not primary_name:
            providers = self.registry.list_providers(category)
            if not providers:
                raise RuntimeError(f"No providers registered for category: {category}")
            primary_name = providers[0].metadata.name

        chain = self.registry.get_fallback_chain(category, primary_name)
        if not chain:
            raise RuntimeError(f"No providers found for fallback chain in category: {category}")

        last_error = None
        for provider in chain:
            # Check availability or try executing
            try:
                # Ensure provider is connected
                if not provider.is_connected:
                    await provider.initialize()
                    await provider.connect()

                # Execute operation
                res = await operation(provider)
                return res
            except Exception as e:
                logger.warning(f"Provider {category}/{provider.metadata.name} failed: {e}. Trying fallback...")
                last_error = e
                # Record error in health monitor
                provider.health_tracker.record_call(success=False, latency_ms=0.0, error_msg=str(e))

        raise RuntimeError(f"All providers in fallback chain for category '{category}' failed. Last error: {last_error}")

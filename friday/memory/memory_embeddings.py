from typing import List, Optional
import logging
from friday.providers.base.provider_registry import ProviderRegistry
from friday.providers.embedding.base import EmbeddingProvider

logger = logging.getLogger("friday-agent")


class MemoryEmbeddingEngine:
    def __init__(
        self, registry: Optional[ProviderRegistry] = None, provider_name: str = "openai"
    ):
        self.registry = registry
        self.provider_name = provider_name
        self._fallback_engine = None

    def _get_provider(self) -> Optional[EmbeddingProvider]:
        if self.registry:
            provider = self.registry.get_provider("embedding", self.provider_name)
            if provider and isinstance(provider, EmbeddingProvider):
                return provider
            # fallback to any available embedding provider
            providers = self.registry.list_providers("embedding")
            if providers:
                return providers[0]
        return None

    def _get_fallback(self):
        if self._fallback_engine is None:
            # Local simple char frequency vector generator for cross-platform offline consistency
            class LocalMockEngine:
                async def get_embedding(self, text: str) -> List[float]:
                    vec = [0.1] * 128
                    for char in text.lower():
                        if "a" <= char <= "z":
                            idx = (ord(char) - ord("a")) % 128
                            vec[idx] += 1.0
                    return vec

                async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
                    return [await self.get_embedding(t) for t in texts]

            self._fallback_engine = LocalMockEngine()
        return self._fallback_engine

    async def get_embedding(self, text: str) -> List[float]:
        provider = self._get_provider()
        if provider:
            try:
                if not provider.is_connected:
                    await provider.connect()
                return await provider.get_embedding(text)
            except Exception as e:
                logger.warning(
                    f"[MemoryEmbeddings] Failed to get embedding from provider: {e}. Falling back."
                )
        return await self._get_fallback().get_embedding(text)

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        provider = self._get_provider()
        if provider:
            try:
                if not provider.is_connected:
                    await provider.connect()
                return await provider.get_embeddings(texts)
            except Exception as e:
                logger.warning(
                    f"[MemoryEmbeddings] Failed to get embeddings from provider: {e}. Falling back."
                )
        return await self._get_fallback().get_embeddings(texts)

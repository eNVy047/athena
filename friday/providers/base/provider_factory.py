import logging
from typing import Dict, Any
from friday.providers.base.provider import Provider
from friday.providers.base.provider_registry import ProviderRegistry
from friday.providers.base.provider_loader import ProviderLoader

logger = logging.getLogger(__name__)

class ProviderFactory:
    @staticmethod
    def create_and_initialize_registry(config: Dict[str, Any]) -> ProviderRegistry:
        """Creates a ProviderRegistry, loads all available providers, and initializes them."""
        registry = ProviderRegistry()
        
        # Load all providers
        ProviderLoader.load_and_register_all(registry, config)
        
        # Configure fallbacks
        # Default LLM fallbacks
        registry.set_fallbacks("llm", ["openai", "gemini", "anthropic", "groq", "openrouter", "ollama"])
        registry.set_fallbacks("vision", ["openai", "gemini", "openrouter", "ollama"])
        registry.set_fallbacks("stt", ["sarvam", "deepgram", "whisper", "azure"])
        registry.set_fallbacks("tts", ["sarvam", "elevenlabs", "openai", "deepgram"])
        registry.set_fallbacks("ocr", ["easyocr", "paddleocr"])
        registry.set_fallbacks("embedding", ["openai", "voyageai", "jina", "cohere"])
        registry.set_fallbacks("storage", ["sqlite", "redis"])
        registry.set_fallbacks("search", ["tavily", "serper", "brave", "exa", "firecrawl"])
        
        return registry

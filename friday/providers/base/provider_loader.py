import logging
from typing import Dict, Any
from friday.providers.base.provider_registry import ProviderRegistry

logger = logging.getLogger(__name__)

class ProviderLoader:
    @staticmethod
    def load_and_register_all(registry: ProviderRegistry, config: Dict[str, Any]) -> None:
        """Statically imports and registers all known providers with the registry."""
        
        # 1. LLM Providers
        try:
            from friday.providers.llm.openai import OpenAiLlmProvider
            registry.register(OpenAiLlmProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register OpenAI LLM Provider: {e}")
            
        try:
            from friday.providers.llm.gemini import GeminiLlmProvider
            registry.register(GeminiLlmProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Gemini LLM Provider: {e}")

        try:
            from friday.providers.llm.anthropic import AnthropicLlmProvider
            registry.register(AnthropicLlmProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Anthropic LLM Provider: {e}")

        try:
            from friday.providers.llm.groq import GroqLlmProvider
            registry.register(GroqLlmProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Groq LLM Provider: {e}")

        try:
            from friday.providers.llm.openrouter import OpenRouterLlmProvider
            registry.register(OpenRouterLlmProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register OpenRouter LLM Provider: {e}")

        try:
            from friday.providers.llm.ollama import OllamaLlmProvider
            registry.register(OllamaLlmProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Ollama LLM Provider: {e}")

        # 2. Vision Providers
        try:
            from friday.providers.vision.openai_provider import OpenAiVisionProvider
            registry.register(OpenAiVisionProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register OpenAI Vision Provider: {e}")

        try:
            from friday.providers.vision.gemini_provider import GeminiVisionProvider
            registry.register(GeminiVisionProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Gemini Vision Provider: {e}")

        try:
            from friday.providers.vision.openrouter_provider import OpenRouterVisionProvider
            registry.register(OpenRouterVisionProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register OpenRouter Vision Provider: {e}")

        try:
            from friday.providers.vision.ollama_provider import OllamaVisionProvider
            registry.register(OllamaVisionProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Ollama Vision Provider: {e}")

        # 3. STT Providers
        try:
            from friday.providers.stt.deepgram import DeepgramSttProvider
            registry.register(DeepgramSttProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Deepgram STT Provider: {e}")

        try:
            from friday.providers.stt.whisper import WhisperSttProvider
            registry.register(WhisperSttProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Whisper STT Provider: {e}")

        try:
            from friday.providers.stt.azure import AzureSpeechSttProvider
            registry.register(AzureSpeechSttProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Azure STT Provider: {e}")

        # 4. TTS Providers
        try:
            from friday.providers.tts.deepgram import DeepgramTtsProvider
            registry.register(DeepgramTtsProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Deepgram TTS Provider: {e}")

        try:
            from friday.providers.tts.elevenlabs import ElevenLabsTtsProvider
            registry.register(ElevenLabsTtsProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register ElevenLabs TTS Provider: {e}")

        try:
            from friday.providers.tts.openai import OpenAiTtsProvider
            registry.register(OpenAiTtsProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register OpenAI TTS Provider: {e}")

        # 5. OCR Providers
        try:
            from friday.providers.ocr.easyocr_provider import EasyOcrProvider
            registry.register(EasyOcrProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register EasyOCR Provider: {e}")

        try:
            from friday.providers.ocr.paddleocr_provider import PaddleOcrProvider
            registry.register(PaddleOcrProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register PaddleOCR Provider: {e}")

        # 6. Embedding Providers
        try:
            from friday.providers.embedding.openai import OpenAiEmbeddingProvider
            registry.register(OpenAiEmbeddingProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register OpenAI Embedding Provider: {e}")

        try:
            from friday.providers.embedding.voyage import VoyageEmbeddingProvider
            registry.register(VoyageEmbeddingProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Voyage Embedding Provider: {e}")

        try:
            from friday.providers.embedding.jina import JinaEmbeddingProvider
            registry.register(JinaEmbeddingProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Jina Embedding Provider: {e}")

        try:
            from friday.providers.embedding.cohere import CohereEmbeddingProvider
            registry.register(CohereEmbeddingProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Cohere Embedding Provider: {e}")

        # 7. Storage Providers
        try:
            from friday.providers.storage.sqlite import SqliteStorageProvider
            registry.register(SqliteStorageProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register SQLite Storage Provider: {e}")



        try:
            from friday.providers.storage.redis import RedisStorageProvider
            registry.register(RedisStorageProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Redis Storage Provider: {e}")

        # 8. Memory Providers
        try:
            from friday.providers.memory.mem0 import Mem0MemoryProvider
            registry.register(Mem0MemoryProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Mem0 Memory Provider: {e}")

        # 9. Search Providers
        try:
            from friday.providers.search.serper import SerperSearchProvider
            registry.register(SerperSearchProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Serper Search Provider: {e}")

        try:
            from friday.providers.search.brave import BraveSearchProvider
            registry.register(BraveSearchProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Brave Search Provider: {e}")

        try:
            from friday.providers.search.tavily import TavilySearchProvider
            registry.register(TavilySearchProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Tavily Search Provider: {e}")

        try:
            from friday.providers.search.exa import ExaSearchProvider
            registry.register(ExaSearchProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Exa Search Provider: {e}")

        try:
            from friday.providers.search.firecrawl import FirecrawlSearchProvider
            registry.register(FirecrawlSearchProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Firecrawl Search Provider: {e}")

        # 10. Database Providers
        try:
            from friday.providers.database.sqlite import SqliteDatabaseProvider
            registry.register(SqliteDatabaseProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register SQLite Database Provider: {e}")

        # 11. Browser Providers
        try:
            from friday.providers.browser.playwright import PlaywrightBrowserProvider
            registry.register(PlaywrightBrowserProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Playwright Browser Provider: {e}")

        # 12. Calendar Providers
        try:
            from friday.providers.calendar.google import GoogleCalendarProvider
            registry.register(GoogleCalendarProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Google Calendar Provider: {e}")

        # 13. Email Providers
        try:
            from friday.providers.email.smtp import SmtpEmailProvider
            registry.register(SmtpEmailProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register SMTP Email Provider: {e}")

        # 14. Messaging Providers
        try:
            from friday.providers.messaging.slack import SlackMessagingProvider
            registry.register(SlackMessagingProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Slack Messaging Provider: {e}")

        # 15. Notifications Providers
        try:
            from friday.providers.notifications.macos import MacOsNotificationsProvider
            registry.register(MacOsNotificationsProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register macOS Notifications Provider: {e}")

        # 16. Maps Providers
        try:
            from friday.providers.maps.google import GoogleMapsProvider
            registry.register(GoogleMapsProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Google Maps Provider: {e}")

        # 17. Weather Providers
        try:
            from friday.providers.weather.openweather import OpenWeatherProvider
            registry.register(OpenWeatherProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register OpenWeather Provider: {e}")

        # 18. Reranker Providers
        try:
            from friday.providers.reranker.cohere import CohereRerankerProvider
            registry.register(CohereRerankerProvider(config))
        except Exception as e:
            logger.debug(f"Failed to register Cohere Reranker Provider: {e}")

import os
from typing import Dict, Any

class ProviderConfig:
    @staticmethod
    def get_global_config() -> Dict[str, Any]:
        """Collects provider-related configurations from env variables."""
        return {
            # Selected Providers
            "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "openai"),
            "VISION_PROVIDER": os.getenv("VISION_PROVIDER", "openai"),
            "OCR_PROVIDER": os.getenv("OCR_PROVIDER", "easyocr"),
            "EMBEDDING_PROVIDER": os.getenv("EMBEDDING_PROVIDER", "openai"),
            "SEARCH_PROVIDER": os.getenv("SEARCH_PROVIDER", "tavily"),
            "STT_PROVIDER": os.getenv("STT_PROVIDER", "deepgram"),
            "TTS_PROVIDER": os.getenv("TTS_PROVIDER", "deepgram"),
            "DATABASE_PROVIDER": os.getenv("DATABASE_PROVIDER", "sqlite"),
            "STORAGE_PROVIDER": os.getenv("STORAGE_PROVIDER", "sqlite"),
            "MEMORY_PROVIDER": os.getenv("MEMORY_PROVIDER", "mem0"),

            # API Keys & Endpoints
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
            "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", ""),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
            "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY", ""),
            "DEEPGRAM_API_KEY": os.getenv("DEEPGRAM_API_KEY", ""),
            "MEM0_API_KEY": os.getenv("MEM0_API_KEY", ""),
            "OLLAMA_HOST": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            
            # Additional keys
            "SERPER_API_KEY": os.getenv("SERPER_API_KEY", ""),
            "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", ""),
            "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY", ""),
            "EXA_API_KEY": os.getenv("EXA_API_KEY", ""),
            "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY", ""),
            "VOYAGE_API_KEY": os.getenv("VOYAGE_API_KEY", ""),
            "JINA_API_KEY": os.getenv("JINA_API_KEY", ""),
            "COHERE_API_KEY": os.getenv("COHERE_API_KEY", ""),
            "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379"),

            # General Defaults
            "PROVIDER_TIMEOUT": float(os.getenv("PROVIDER_TIMEOUT", "30.0")),
            "PROVIDER_RETRY_COUNT": int(os.getenv("PROVIDER_RETRY_COUNT", "3")),
        }

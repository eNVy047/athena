import pytest
from friday.providers.base.provider_manager import ProviderManager
from friday.providers.vision.openai_provider import OpenAiVisionProvider
from friday.providers.ocr.easyocr_provider import EasyOcrProvider

def test_vision_provider_selection():
    config = {
        "VISION_PROVIDER": "openai",
        "OPENAI_API_KEY": "test_openai_key",
        "VISION_MODEL": "gpt-4o"
    }
    manager = ProviderManager(config)
    provider = manager.registry.get_provider("vision", "openai")
    
    assert isinstance(provider, OpenAiVisionProvider)
    assert provider.api_key == "test_openai_key"
    assert provider.model == "gpt-4o"

def test_ocr_provider_selection():
    config = {
        "OCR_PROVIDER": "easyocr"
    }
    manager = ProviderManager(config)
    provider = manager.registry.get_provider("ocr", "easyocr")
    assert isinstance(provider, EasyOcrProvider)

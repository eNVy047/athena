import pytest
from unittest.mock import MagicMock, AsyncMock

from friday.vision.vision_pipeline import VisionPipeline
from friday.vision.vision_context import VisionContext
from friday.providers.vision.base import VisionProvider
from friday.providers.ocr.base import OcrProvider

class MockVisionProvider(VisionProvider):
    def __init__(self):
        # We don't call super to avoid config issues
        pass
    async def initialize(self): pass
    async def connect(self): pass
    async def disconnect(self): pass
    async def health_check(self): return True
    async def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        if "key_value_pairs" in prompt:
            return '{"title": "Test Doc", "key_value_pairs": {"Name": "Friday"}}'
        elif "environment_type" in prompt:
            return '{"description": "A sunny day", "environment_type": "outdoor"}'
        elif "confidence" in prompt and "Person" in prompt:
            return '[{"label": "Person 1", "confidence": 0.99}]'
        elif "UI elements" in prompt:
            return '[{"label": "Start Button", "confidence": 0.95}]'
        elif "primary objects" in prompt:
            return '[{"label": "Car", "confidence": 0.88}]'
        elif "caption" in prompt:
            return "A test caption for the image."
        return "{}"

class MockOcrProvider(OcrProvider):
    def __init__(self):
        pass
    async def initialize(self): pass
    async def connect(self): pass
    async def disconnect(self): pass
    async def health_check(self): return True
    async def extract_text(self, image_bytes: bytes) -> str:
        return "Extracted test text that is significantly longer than fifty characters to ensure document analysis is triggered."

@pytest.mark.asyncio
async def test_vision_pipeline():
    vision_provider = MockVisionProvider()
    ocr_provider = MockOcrProvider()
    
    pipeline = VisionPipeline(vision_provider, ocr_provider)
    
    context = VisionContext(
        session_id="test_session",
        source_sensor="camera",
        require_ocr=True,
        require_face_analysis=True
    )
    
    image_bytes = b"dummy_image_data"
    result = await pipeline.process_frame(image_bytes, context)
    
    assert result.success is True
    assert result.extracted_text == "Extracted test text that is significantly longer than fifty characters to ensure document analysis is triggered."
    assert result.scene.environment_type == "outdoor"
    assert result.caption == "A test caption for the image."
    
    # Entities should contain objects and faces
    entity_labels = [e.label for e in result.entities]
    assert "Car" in entity_labels
    assert "Person 1" in entity_labels
    assert "Start Button" not in entity_labels # It's a camera, not a screen
    
    # Document analysis should have triggered
    assert result.document_layout.title == "Test Doc"

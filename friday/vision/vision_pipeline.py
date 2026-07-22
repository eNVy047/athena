import logging
import asyncio
from friday.providers.vision.base import VisionProvider
from friday.providers.ocr.base import OcrProvider

from friday.vision.vision_context import VisionContext
from friday.vision.vision_result import VisionResult
from friday.vision.vision_metrics import VisionMetrics
from friday.vision.text_reader import TextReader
from friday.vision.scene_analyzer import SceneAnalyzer
from friday.vision.object_detector import ObjectDetector
from friday.vision.document_analyzer import DocumentAnalyzer
from friday.vision.screen_analyzer import ScreenAnalyzer
from friday.vision.face_analyzer import FaceAnalyzer
from friday.vision.image_captioner import ImageCaptioner

logger = logging.getLogger(__name__)

class VisionPipeline:
    """Orchestrates the flow of image data through various semantic analyzers."""
    
    def __init__(self, vision_provider: VisionProvider, ocr_provider: OcrProvider):
        self.vision = vision_provider
        self.ocr = ocr_provider
        
        self.text_reader = TextReader(ocr_provider)
        self.scene_analyzer = SceneAnalyzer(vision_provider)
        self.object_detector = ObjectDetector(vision_provider)
        self.document_analyzer = DocumentAnalyzer(vision_provider)
        self.screen_analyzer = ScreenAnalyzer(vision_provider)
        self.face_analyzer = FaceAnalyzer(vision_provider)
        self.captioner = ImageCaptioner(vision_provider)

    async def process_frame(self, image_bytes: bytes, context: VisionContext) -> VisionResult:
        metrics = VisionMetrics(session_id=context.session_id)
        metrics.start_pipeline()
        
        result = VisionResult(success=True, source_sensor=context.source_sensor, metadata={"session_id": context.session_id})
        
        # 1. OCR
        if context.require_ocr:
            metrics.record_ocr_start()
            # We run OCR sequentially here for metric tracking, but it could be parallelized
            text = await self.text_reader.extract_text(image_bytes)
            result.extracted_text = text
            metrics.record_ocr_end()
            
        # 2. Scene & Semantics (Parallelize)
        async def run_scene():
            metrics.record_scene_start()
            result.scene = await self.scene_analyzer.analyze(image_bytes)
            metrics.record_scene_end()
            
        async def run_caption():
            result.caption = await self.captioner.generate_caption(image_bytes)
            
        async def run_objects():
            result.entities.extend(await self.object_detector.detect_objects(image_bytes))
            
        async def run_faces():
            if context.require_face_analysis:
                result.entities.extend(await self.face_analyzer.analyze(image_bytes))
                
        async def run_screen():
            if context.source_sensor == "screen":
                result.entities.extend(await self.screen_analyzer.analyze(image_bytes))
                
        async def run_document():
            # If OCR found text, maybe run document layout
            if result.extracted_text and len(result.extracted_text) > 50:
                result.document_layout = await self.document_analyzer.analyze(image_bytes)
                
        # Launch parallel tasks
        await asyncio.gather(
            run_scene(),
            run_caption(),
            run_objects(),
            run_faces(),
            run_screen(),
            run_document()
        )
        
        metrics.end_pipeline()
        result.duration_ms = metrics.total_duration_ms
        logger.info(f"VisionPipeline completed in {result.duration_ms:.2f}ms")
        
        return result

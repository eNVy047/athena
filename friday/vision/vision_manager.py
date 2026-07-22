import logging
from friday.providers.vision.base import VisionProvider
from friday.providers.ocr.base import OcrProvider
from friday.memory.memory_manager import MemoryManager
from friday.events.event_bus import EventBus
from friday.world.world_manager import WorldManager

from friday.vision.vision_pipeline import VisionPipeline
from friday.vision.visual_memory import VisualMemory
from friday.vision.vision_context import VisionContext

logger = logging.getLogger(__name__)

class VisionManager:
    """Facade for the Vision Intelligence Engine. Integrates sensors, pipeline, memory, and world model."""
    
    def __init__(self, 
                 vision_provider: VisionProvider, 
                 ocr_provider: OcrProvider, 
                 memory_manager: MemoryManager,
                 world_model: WorldManager,
                 event_bus: EventBus):
        self.pipeline = VisionPipeline(vision_provider, ocr_provider)
        self.visual_memory = VisualMemory(memory_manager)
        self.world_model = world_model
        self.event_bus = event_bus
        
        # Subscribe to raw frames from sensors
        self.event_bus.subscribe("perception.observation.camera", self._on_camera_frame)
        self.event_bus.subscribe("perception.observation.screen", self._on_screen_frame)

    async def _on_camera_frame(self, event_data: dict):
        if "image_data" not in event_data:
            return
            
        context = VisionContext(
            session_id=event_data.get("session_id", "default"),
            source_sensor="camera",
            require_ocr=False,
            require_face_analysis=True
        )
        
        # In a real setup, we might decode the base64 or pass bytes directly.
        # Assuming image_data is bytes or we can convert it.
        image_bytes = event_data["image_data"]
        if isinstance(image_bytes, str):
            import base64
            image_bytes = base64.b64decode(image_bytes)
            
        await self._process_and_store(image_bytes, context)

    async def _on_screen_frame(self, event_data: dict):
        if "image_data" not in event_data:
            return
            
        context = VisionContext(
            session_id=event_data.get("session_id", "default"),
            source_sensor="screen",
            require_ocr=True,
            require_face_analysis=False
        )
        
        image_bytes = event_data["image_data"]
        if isinstance(image_bytes, str):
            import base64
            image_bytes = base64.b64decode(image_bytes)
            
        await self._process_and_store(image_bytes, context)

    async def _process_and_store(self, image_bytes: bytes, context: VisionContext):
        """Processes the frame through the pipeline, stores memory, and updates world model."""
        try:
            result = await self.pipeline.process_frame(image_bytes, context)
            
            # Store Memory
            await self.visual_memory.store_observation(result)
            
            # Update World Model
            await self._update_world_model(result)
            
        except Exception as e:
            logger.error(f"VisionManager processing error: {e}")

    async def _update_world_model(self, result):
        """Pushes visual semantics into the World Model state."""
        # For instance, track people, apps, or screen context
        updates = {}
        if result.scene:
            updates[f"{result.source_sensor}_scene"] = result.scene.description
            
        if result.caption:
            updates[f"{result.source_sensor}_last_caption"] = result.caption
            
        if result.entities:
            entity_labels = [e.label for e in result.entities]
            updates[f"{result.source_sensor}_entities"] = entity_labels
            
        if updates:
            # Assuming world_model has an update_state method
            # We'll safely apply updates based on existing World Model architecture
            if hasattr(self.world_model, "update_state"):
                self.world_model.update_state("vision", updates)
            elif hasattr(self.world_model, "environment"):
                self.world_model.environment.update(updates)

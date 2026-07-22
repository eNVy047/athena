import logging
from friday.memory.memory_manager import MemoryManager
from friday.vision.vision_result import VisionResult

logger = logging.getLogger(__name__)

class VisualMemory:
    """Stores semantic visual observations into the Memory Subsystem."""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        
    async def store_observation(self, result: VisionResult):
        """Stores the structured semantic understanding, avoiding raw duplicates."""
        if not result.success:
            return
            
        memory_content = f"Visual Observation from {result.source_sensor}:\n"
        
        if result.caption:
            memory_content += f"Caption: {result.caption}\n"
            
        if result.scene:
            memory_content += f"Scene: {result.scene.description}\n"
            if result.scene.key_objects:
                memory_content += f"Objects: {', '.join(result.scene.key_objects)}\n"
                
        if result.document_layout and result.document_layout.title:
            memory_content += f"Document Title: {result.document_layout.title}\n"
            
        if result.extracted_text:
            # We truncate text if it's too long
            text = result.extracted_text[:500] + "..." if len(result.extracted_text) > 500 else result.extracted_text
            memory_content += f"Visible Text: {text}\n"

        logger.info(f"Storing visual memory: {memory_content.splitlines()[0]}...")
        # Assume MemoryManager has an add_memory method (from Phase H)
        await self.memory.add_memory(
            text=memory_content,
            metadata={
                "type": "visual_observation",
                "source": result.source_sensor,
                "session_id": result.metadata.get("session_id", "unknown")
            }
        )

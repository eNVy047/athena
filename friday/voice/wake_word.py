import logging

logger = logging.getLogger(__name__)

class WakeWordDetector:
    """Detects a specific wake word in the incoming text stream."""
    
    def __init__(self, wake_words: list[str] = None):
        self.wake_words = [w.lower() for w in (wake_words or ["friday", "hey friday", "jarvis"])]
        
    def detect(self, text: str) -> bool:
        """
        Checks if the text contains any of the configured wake words.
        In a production system, this would operate on the audio stream (e.g. Porcupine).
        Since we might use continuous STT, we can check the text stream.
        """
        if not text:
            return False
            
        text_lower = text.lower()
        for word in self.wake_words:
            if word in text_lower:
                logger.info(f"Wake word detected: '{word}'")
                return True
                
        return False

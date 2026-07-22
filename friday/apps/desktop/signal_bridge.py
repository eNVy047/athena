import asyncio
import logging
from PySide6.QtCore import QObject, Signal, Slot
from friday.agent.agent import FridayAgent

logger = logging.getLogger(__name__)

class SignalBridge(QObject):
    """Bridges QML Signals to asyncio Python tasks and vice versa."""
    
    # Emitted from Python to QML
    responseReady = Signal(str, str) # sender, message
    statusChanged = Signal(str)
    
    def __init__(self, agent: FridayAgent):
        super().__init__()
        self.agent = agent
        
    @Slot(str)
    def sendMessage(self, message: str):
        """Called from QML when user sends a chat message."""
        logger.info(f"UI sent message: {message}")
        self.statusChanged.emit("Thinking...")
        
        # Schedule the async task without blocking the Qt loop
        asyncio.create_task(self._process_message(message))
        
    async def _process_message(self, message: str):
        try:
            # Assuming agent.process_input returns a string response
            res = await self.agent.process_input(message)
            self.responseReady.emit("Friday", res)
            self.statusChanged.emit("Ready")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.responseReady.emit("System", f"Error: {str(e)}")
            self.statusChanged.emit("Error")

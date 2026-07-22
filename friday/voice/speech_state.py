from enum import Enum, auto

class SpeechState(Enum):
    IDLE = auto()
    LISTENING = auto()         # Wake word detected, listening for command
    PROCESSING = auto()        # Audio captured, STT/Agent processing
    SPEAKING = auto()          # Synthesizing and outputting TTS
    INTERRUPTED = auto()       # User interrupted during TTS
    ERROR = auto()             # Voice error state

class VoiceMode(Enum):
    CONTINUOUS = auto()        # Always listening (VAD -> Wake Word)
    PUSH_TO_TALK = auto()      # Manually triggered listening

class ConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    RECONNECTING = auto()

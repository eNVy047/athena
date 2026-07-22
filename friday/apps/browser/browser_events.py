from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BrowserEvent:
    event_type: str
    payload: Dict[str, Any]

class BrowserEvents:
    NAVIGATED = "browser.navigated"
    DOM_MUTATED = "browser.dom_mutated"
    DOWNLOAD_STARTED = "browser.download_started"
    DOWNLOAD_COMPLETED = "browser.download_completed"
    ERROR = "browser.error"
    SESSION_STARTED = "browser.session_started"
    SESSION_ENDED = "browser.session_ended"

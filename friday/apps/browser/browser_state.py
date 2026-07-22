from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class BrowserState:
    is_open: bool = False
    current_url: Optional[str] = None
    current_title: Optional[str] = None
    active_tab_id: Optional[str] = None
    tabs: List[str] = field(default_factory=list)
    windows: List[str] = field(default_factory=list)
    downloads_active: int = 0
    network_idle: bool = True

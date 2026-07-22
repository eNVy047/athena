from __future__ import annotations

import time
import uuid
from typing import Any, Dict
from pydantic import BaseModel, Field

class RequestContext(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: time.time())

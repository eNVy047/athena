from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

class GoalStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class Goal:
    id: str
    description: str
    priority: int = 0
    status: GoalStatus = GoalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Intent:
    id: str
    name: str
    confidence: float
    parameters: Dict[str, Any] = field(default_factory=dict)
    raw_request: str = ""

@dataclass
class ExecutionStep:
    id: str
    action_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    sensitive: bool = False
    timeout: float = 60.0

@dataclass
class ExecutionResult:
    step_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0

@dataclass
class Task:
    id: str
    name: str
    steps: List[ExecutionStep]
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    results: List[ExecutionResult] = field(default_factory=list)

@dataclass
class Plan:
    id: str
    goal_id: str
    tasks: Dict[str, Task] = field(default_factory=dict)  # Keyed by Task ID
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Decision:
    id: str
    chosen_action: str
    confidence: float
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Evaluation:
    success: bool
    efficiency_score: float
    report: str
    retry_recommended: bool = False

@dataclass
class Reflection:
    lessons_learned: List[str]
    success_insights: List[str]
    mistakes_identified: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Workflow:
    id: str
    name: str
    tasks: List[Task]
    state: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

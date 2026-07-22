from typing import Protocol, List, Dict, Any
from pydantic import BaseModel
from friday.domain.context import ExecutionContext

class TaskStep(BaseModel):
    step_id: str
    description: str
    assigned_agent: str
    dependencies: List[str] = []
    status: str = "pending"

class Plan(BaseModel):
    goal: str
    steps: List[TaskStep]

class Planner(Protocol):
    async def create_plan(self, goal: str, context: ExecutionContext) -> Plan:
        ...

    async def reflect(self, plan: Plan, current_step: TaskStep, result: Any) -> Plan:
        ...

class Agent(Protocol):
    @property
    def id(self) -> str: ...
    
    @property
    def capabilities(self) -> List[str]: ...

    async def execute(self, task: str, context: ExecutionContext) -> Any:
        ...

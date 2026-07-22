import json
import os
from typing import Dict, Any, Optional
from friday.core.cognition.models import Workflow, Task, TaskStatus

class WorkflowEngine:
    """Orchestrates long-running workflows, maintaining state across reboots."""
    def __init__(self, state_path: str = "./workflow_state.json"):
        self.state_path = state_path
        self._workflows: Dict[str, Workflow] = {}

    def register_workflow(self, workflow: Workflow) -> None:
        self._workflows[workflow.id] = workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)

    def save_state(self) -> None:
        serialized = {}
        for wid, wf in self._workflows.items():
            serialized[wid] = {
                "id": wf.id,
                "name": wf.name,
                "is_active": wf.is_active,
                "state": wf.state,
                "tasks": [
                    {"id": t.id, "name": t.name, "status": t.status.value}
                    for t in wf.tasks
                ]
            }
        with open(self.state_path, "w") as f:
            json.dump(serialized, f)

    def load_state(self) -> None:
        if not os.path.exists(self.state_path):
            return
        with open(self.state_path, "r") as f:
            data = json.load(f)
            for wid, item in data.items():
                tasks = [
                    Task(id=t["id"], name=t["name"], steps=[], status=TaskStatus(t["status"]))
                    for t in item["tasks"]
                ]
                self._workflows[wid] = Workflow(
                    id=item["id"],
                    name=item["name"],
                    tasks=tasks,
                    state=item["state"],
                    is_active=item["is_active"]
                )

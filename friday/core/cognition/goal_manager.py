import json
import os
from typing import List, Dict, Optional
from friday.core.cognition.models import Goal, GoalStatus

class GoalManager:
    """Manages active goal queues, priority ranking, rescheduling, and state persistence."""
    def __init__(self, persistence_path: str = "./goal_store.json"):
        self.persistence_path = persistence_path
        self._goals: Dict[str, Goal] = {}

    def add_goal(self, goal: Goal) -> None:
        self._goals[goal.id] = goal

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        return self._goals.get(goal_id)

    def get_active_queue(self) -> List[Goal]:
        # Return pending or running goals sorted by priority desc
        active = [g for g in self._goals.values() if g.status in (GoalStatus.PENDING, GoalStatus.RUNNING)]
        return sorted(active, key=lambda x: x.priority, reverse=True)

    def cancel_goal(self, goal_id: str) -> None:
        if goal_id in self._goals:
            self._goals[goal_id].status = GoalStatus.CANCELLED

    def save_state(self) -> None:
        data = {}
        for gid, goal in self._goals.items():
            data[gid] = {
                "id": goal.id,
                "description": goal.description,
                "priority": goal.priority,
                "status": goal.status.value,
                "dependencies": goal.dependencies,
                "metadata": goal.metadata
            }
        with open(self.persistence_path, "w") as f:
            json.dump(data, f)

    def load_state(self) -> None:
        if not os.path.exists(self.persistence_path):
            return
        with open(self.persistence_path, "r") as f:
            data = json.load(f)
            for gid, item in data.items():
                self._goals[gid] = Goal(
                    id=item["id"],
                    description=item["description"],
                    priority=item["priority"],
                    status=GoalStatus(item["status"]),
                    dependencies=item["dependencies"],
                    metadata=item["metadata"]
                )

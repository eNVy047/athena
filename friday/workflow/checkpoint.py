import json
from pathlib import Path
from typing import Optional
from friday.workflow.state import WorkflowState

class WorkflowCheckpointManager:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, state: WorkflowState) -> None:
        """Saves workflow state context atomically to disk."""
        target_path = self.storage_dir / f"{state.workflow_id}.json"
        temp_path = target_path.with_suffix(".tmp")
        
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))
            
        os = __import__("os")
        os.replace(temp_path, target_path)

    def load_checkpoint(self, workflow_id: str) -> Optional[WorkflowState]:
        """Loads workflow state context from disk if present."""
        target_path = self.storage_dir / f"{workflow_id}.json"
        if not target_path.exists():
            return None
            
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return WorkflowState(**data)

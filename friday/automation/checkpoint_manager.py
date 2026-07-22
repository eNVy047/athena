from __future__ import annotations

import os
import json
import logging
from typing import Optional
from friday.automation.workflow_state import WorkflowState

logger = logging.getLogger("friday-agent")

class CheckpointManager:
    def __init__(self, checkpoint_dir: str = "friday_data/checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)

    def save_checkpoint(self, state: WorkflowState) -> None:
        file_path = os.path.join(self.checkpoint_dir, f"{state.workflow_id}.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(state.model_dump_json())
            logger.debug(f"[CheckpointManager] Saved checkpoint for workflow {state.workflow_id}")
        except Exception as e:
            logger.error(f"[CheckpointManager] Failed to save checkpoint for {state.workflow_id}: {e}")

    def load_checkpoint(self, workflow_id: str) -> Optional[WorkflowState]:
        file_path = os.path.join(self.checkpoint_dir, f"{workflow_id}.json")
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return WorkflowState.model_validate(data)
        except Exception as e:
            logger.error(f"[CheckpointManager] Failed to load checkpoint for {workflow_id}: {e}")
            return None

    def clear_checkpoint(self, workflow_id: str) -> None:
        file_path = os.path.join(self.checkpoint_dir, f"{workflow_id}.json")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

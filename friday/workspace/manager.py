import shutil
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel

class Project(BaseModel):
    project_id: str
    root_path: Path
    description: str

class WorkspaceManager:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self._active_projects: Dict[str, Project] = {}
        self._temp_dirs: List[Path] = []

    def create_project(self, project_id: str, description: str = "") -> Project:
        project_path = self.workspace_root / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        project = Project(project_id=project_id, root_path=project_path, description=description)
        self._active_projects[project_id] = project
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        return self._active_projects.get(project_id)

    def create_temp_workspace(self, session_id: str) -> Path:
        """Spawns an isolated session folder for runtime tasks."""
        temp_path = self.workspace_root / "temp" / session_id
        temp_path.mkdir(parents=True, exist_ok=True)
        self._temp_dirs.append(temp_path)
        return temp_path

    def cleanup_temp_workspaces(self):
        """Cleans up temporary directory references."""
        for path in self._temp_dirs:
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
        self._temp_dirs.clear()

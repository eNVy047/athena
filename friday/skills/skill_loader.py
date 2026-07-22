import importlib
import sys
from pathlib import Path
from typing import Any, Type
from friday.skills.skill import Skill

class SkillLoader:
    """Handles runtime loading of Python packages conforming to the Skill protocol."""
    def __init__(self, search_path: str = "./skills"):
        self.search_path = Path(search_path)

    def load_skill_class(self, module_name: str, class_name: str) -> Type[Skill]:
        sys.path.insert(0, str(self.search_path.absolute()))
        try:
            module = importlib.import_module(module_name)
            skill_cls = getattr(module, class_name)
            return skill_cls
        finally:
            if str(self.search_path.absolute()) in sys.path:
                sys.path.remove(str(self.search_path.absolute()))

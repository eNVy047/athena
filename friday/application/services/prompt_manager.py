import os
from pathlib import Path
from typing import Dict, Any, Optional

class PromptManager:
    def __init__(self, prompts_dir: Path):
        self.prompts_dir = prompts_dir
        self._cache: Dict[str, str] = {}

    def load_prompt_template(self, category: str, name: str) -> str:
        """Loads a raw prompt template from disk, checking cache first."""
        cache_key = f"{category}/{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        target_path = self.prompts_dir / category / f"{name}.txt"
        if not target_path.exists():
            # Standard default fallback if missing
            return "System Prompt Protocol: {profile}. Available capabilities: {caps_summary}."
            
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
            self._cache[cache_key] = content
            return content

    def render_prompt(self, category: str, name: str, variables: Dict[str, Any]) -> str:
        """Renders a loaded prompt template by substituting variables."""
        template = self.load_prompt_template(category, name)
        try:
            return template.format(**variables)
        except KeyError as e:
            # Return basic backup prompt if mapping fails
            return template
            
    def clear_cache(self):
        self._cache.clear()

import pytest
from pathlib import Path
from friday.application.services.prompt_manager import PromptManager

def test_prompt_manager_rendering():
    # Use real prompts dir or sandbox path
    prompts_dir = Path(__file__).parent.parent / "friday" / "prompts"
    manager = PromptManager(prompts_dir=prompts_dir)
    
    rendered = manager.render_prompt(
        category="system",
        name="default",
        variables={"profile": "Iron Man Mark 85", "caps_summary": "Browser, Terminal"}
    )
    
    assert "F.R.I.D.A.Y." in rendered
    assert "Iron Man Mark 85" in rendered
    assert "Browser, Terminal" in rendered

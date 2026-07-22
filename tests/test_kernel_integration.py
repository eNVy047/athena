import pytest
import shutil
import subprocess
import webbrowser
import asyncio
from pathlib import Path
from friday.kernel.kernel import FridayKernel
from friday.kernel.runtime import FridayAgent
from friday.core.activity_store import ActivityStore

@pytest.fixture
def agent_and_kernel(monkeypatch):
    import shutil
    import subprocess
    monkeypatch.setattr(shutil, "which", lambda cmd: "/usr/bin/chrome" if "chrome" in cmd or "chromium" in cmd or "python" in cmd or "firefox" in cmd or "safari" in cmd else None)
    
    def mock_subprocess_run(*args, **kwargs):
        class MockCompletedProcess:
            returncode = 1 # Not running
            stdout = ""
            stderr = ""
        return MockCompletedProcess()
    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)

    storage_root = Path(__file__).parent.parent / "friday" / "prompts" / "temp_integration_test"
    kernel = FridayKernel(storage_root=storage_root)
    kernel.bootstrap()
    agent = FridayAgent(kernel=kernel)
    yield agent, kernel
    kernel.shutdown()
    shutil.rmtree(storage_root, ignore_errors=True)

@pytest.mark.asyncio
async def test_all_e2e_commands(agent_and_kernel, monkeypatch):
    agent, kernel = agent_and_kernel

    # Capture and mock boundary OS actions
    commands_run = []
    async def mock_subprocess_shell(cmd, *args, **kwargs):
        commands_run.append(cmd)
        class MockProcess:
            def __init__(self):
                self.pid = 12345
                self.returncode = 0
            async def communicate(self):
                return b"", b""
        return MockProcess()
    monkeypatch.setattr(asyncio, "create_subprocess_shell", mock_subprocess_shell)

    opened_urls = []
    def mock_webbrowser_open(url: str):
        opened_urls.append(url)
    monkeypatch.setattr(webbrowser, "open", mock_webbrowser_open)

    # 1. Open Chrome
    res = await agent.process_input("Open Chrome")
    assert "Opening Google Chrome" in res or "Google Chrome launched successfully" in res
    assert kernel.activity_store.get_records()[-1].user_request == "Open Chrome"

    # 2. Open github.com
    res = await agent.process_input("Open github.com")
    assert "github.com" in res or "github.com" in opened_urls[-1]

    # 3. Search OpenAI
    res = await agent.process_input("Search OpenAI")
    assert "OpenAI" in res

    # 4. Play Believer
    res = await agent.process_input("Play Believer by Imagine Dragons")
    assert "Playing Believer by Imagine Dragons" in res

    # 5. Store memory
    res = await agent.process_input("Remember my favorite IDE is VS Code.")
    assert "Stored" in res

    # 6. Retrieve memory
    res = await agent.process_input("What is my favorite IDE?")
    assert "VS Code" in res

    # 7. Workspace creation
    res = await agent.process_input("Create hello.py")
    assert "created in workspace" in res

    # 8. Knowledge summary
    res = await agent.process_input("Summarize README.md")
    assert "Friday OS is a production-grade" in res

    # 9. Scheduler reminder
    res = await agent.process_input("Create a reminder for tomorrow.")
    assert "Scheduler task created" in res

@pytest.mark.asyncio
async def test_negative_scenarios(agent_and_kernel):
    agent, kernel = agent_and_kernel
    
    # Unknown command
    res = await agent.process_input("Unknown command")
    assert "don't understand" in res.lower()
    
    # Invalid URL
    res = await agent.process_input("Open invalid url")
    assert "failed" in res.lower()
    
    # Missing browser
    res = await agent.process_input("Open Chrome force missing browser")
    assert "failed" in res.lower()
    
    # Browser crash
    res = await agent.process_input("Open Chrome and trigger browser crash")
    assert "failed" in res.lower()
    
    # Permission denied
    res = await agent.process_input("Open Chrome but permission denied")
    assert "failed" in res.lower()
    
    # Memory unavailable
    res = await agent.process_input("Search OpenAI but memory unavailable")
    assert "failed" in res.lower()
    
    # Knowledge unavailable
    res = await agent.process_input("Summarize README.md but knowledge unavailable")
    assert "failed" in res.lower()
    
    # Workspace unavailable
    res = await agent.process_input("Create hello.py but workspace unavailable")
    assert "failed" in res.lower()


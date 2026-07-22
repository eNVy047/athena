import os
import shutil
import asyncio
from pathlib import Path
from typing import Tuple, Dict

class ShellDetector:
    @staticmethod
    def detect_shell() -> Tuple[str, list]:
        """Detects the appropriate shell and execution arguments for the platform."""
        if os.name == "nt":
            pwsh = shutil.which("pwsh")
            if pwsh:
                return pwsh, ["-NoProfile", "-NonInteractive", "-Command"]
            return "cmd.exe", ["/c"]
        else:
            bash = shutil.which("bash")
            if bash:
                return bash, ["-c"]
            return "/bin/sh", ["-c"]

class SubprocessRegistry:
    def __init__(self):
        self._active_processes: Dict[str, asyncio.subprocess.Process] = {}

    def register(self, process_id: str, process: asyncio.subprocess.Process):
        self._active_processes[process_id] = process

    async def terminate(self, process_id: str):
        if process_id in self._active_processes:
            proc = self._active_processes[process_id]
            try:
                proc.terminate()
                await proc.wait()
            except ProcessLookupError:
                pass
            del self._active_processes[process_id]

    async def shutdown_all(self):
        for pid in list(self._active_processes.keys()):
            await self.terminate(pid)

class ProcessExecutor:
    def __init__(self, registry: SubprocessRegistry):
        self._registry = registry

    async def execute_command(self, command: str, timeout: float = 60.0) -> Tuple[int, str, str]:
        shell_path, shell_args = ShellDetector.detect_shell()
        
        proc = await asyncio.create_subprocess_exec(
            shell_path,
            *shell_args,
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        proc_id = str(proc.pid)
        self._registry.register(proc_id, proc)

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return proc.returncode, stdout.decode(errors="replace"), stderr.decode(errors="replace")
        except asyncio.TimeoutError:
            await self._registry.terminate(proc_id)
            raise TimeoutError(f"Command execution timed out after {timeout} seconds.")
        finally:
            await self._registry.terminate(proc_id)

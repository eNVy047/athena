from __future__ import annotations

import asyncio
from typing import Any, Dict

class TerminalActions:
    def __init__(self, platform_adapter: Any):
        self.adapter = platform_adapter

    async def execute_async(self, command: str, arguments: Dict[str, Any]) -> Any:
        if command == "run":
            cmd = arguments.get("cmd", "")
            timeout = float(arguments.get("timeout", 30.0))
            
            # Cross-platform execution
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                return {
                    "stdout": stdout.decode(errors="replace").strip(),
                    "stderr": stderr.decode(errors="replace").strip(),
                    "exit_code": proc.returncode
                }
            except asyncio.TimeoutError:
                proc.kill()
                raise TimeoutError(f"Command execution timed out after {timeout} seconds.")
        else:
            raise ValueError(f"Unknown terminal command: {command}")

from __future__ import annotations

import psutil
from typing import Any, Dict

class ProcessActions:
    def __init__(self, platform_adapter: Any):
        self.adapter = platform_adapter

    def execute(self, command: str, arguments: Dict[str, Any]) -> Any:
        if command == "list":
            procs = []
            for p in list(psutil.process_iter(["pid", "name"]))[:15]:
                try:
                    procs.append(p.info)
                except Exception:
                    pass
            return procs
            
        elif command == "kill":
            pid = int(arguments.get("pid", 0))
            if pid:
                p = psutil.Process(pid)
                p.terminate()
                return f"Terminated process with PID: {pid}"
            raise ValueError("PID is required to kill a process.")
            
        else:
            raise ValueError(f"Unknown process command: {command}")

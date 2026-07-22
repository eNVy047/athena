import json
from friday.observability.diagnostics import DiagnosticsCollector

class SystemReportGenerator:
    """Formats diagnostics into a CLI friendly report or JSON payload."""
    
    def __init__(self, collector: DiagnosticsCollector):
        self.collector = collector
        
    async def generate_json(self) -> str:
        data = await self.collector.get_diagnostics()
        return json.dumps(data, indent=2)
        
    async def generate_text(self) -> str:
        data = await self.collector.get_diagnostics()
        lines = ["=== F.R.I.D.A.Y. SYSTEM REPORT ==="]
        lines.append(f"OS: {data['system']['os']} {data['system']['release']}")
        lines.append(f"Python: {data['system']['python_version']}")
        lines.append("--- HEALTH ---")
        for k, v in data['health'].items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)

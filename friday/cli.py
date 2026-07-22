import sys
import asyncio
from friday.observability.health_manager import HealthManager
from friday.observability.diagnostics import DiagnosticsCollector
from friday.observability.system_report import SystemReportGenerator

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "doctor":
        asyncio.run(run_doctor())
    else:
        print("Usage: friday doctor")

async def run_doctor():
    manager = HealthManager()
    collector = DiagnosticsCollector(manager)
    report_gen = SystemReportGenerator(collector)
    
    print("Gathering diagnostic data...")
    report = await report_gen.generate_text()
    print(report)

if __name__ == "__main__":
    main()

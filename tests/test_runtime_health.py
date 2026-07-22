import pytest
from friday.kernel.runtime_state import RuntimeState
from friday.kernel.health import RuntimeHealthMonitor

def test_health_monitor_triggers():
    state = RuntimeState(background_task_count=100)
    monitor = RuntimeHealthMonitor(state=state)
    
    report = monitor.check_health()
    assert report["status"] == "degraded"
    assert "background task" in report["issues"][0]

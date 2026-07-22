import pytest
from friday.pal.detector import SystemDetector

def test_platform_capabilities():
    caps = SystemDetector.detect_capabilities()
    assert caps is not None
    # Telemetry should be compiled with active os details
    assert "os" in caps.metadata

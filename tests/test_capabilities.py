import pytest
from friday.kernel.capabilities import CapabilityManager

def test_capabilities_detection():
    caps = CapabilityManager.detect_system_capabilities()
    assert caps is not None
    assert isinstance(caps.os_name, str)

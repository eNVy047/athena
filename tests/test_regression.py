import pytest
from friday.infrastructure.memory import MemoryConfig

def test_regression_compatibility():
    # Verify that existing MemoryConfig still loads cleanly from environment
    config = MemoryConfig.from_env()
    assert config is not None
    assert config.enabled == True  # Default value check

import pytest
import shutil
from pathlib import Path
from friday.kernel.kernel import FridayKernel

def test_unified_storage_bootstrap():
    storage_root = Path(__file__).parent.parent / "friday" / "prompts" / "temp_data"
    kernel = FridayKernel(storage_root=storage_root)
    kernel.bootstrap()
    
    # 1. Verify target directory layout structures exist
    assert (storage_root / "VERSION").exists()
    assert (storage_root / "memory" / "episodic").exists()
    assert (storage_root / "knowledge" / "documents").exists()
    assert (storage_root / "activities" / "conversations").exists()
    
    # 2. Shutdown & Clean
    kernel.shutdown()
    shutil.rmtree(storage_root, ignore_errors=True)

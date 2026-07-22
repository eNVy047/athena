import pytest
import asyncio
from unittest.mock import MagicMock, patch
from friday.core.kernel.kernel import FridayKernel
from friday.events.event_bus import EventBus
from friday.perception.manager import PerceptionManager
from friday.perception.sensor_metadata import SensorStatus
from friday.perception.sensor_events import SensorEvent

# We mock psutil, cv2, mss, and sounddevice inside tests so they execute fast and run reliably in CI/CD without access to real laptop hardware.
@pytest.fixture
def mock_drivers():
    with patch("cv2.VideoCapture") as mock_cap, \
         patch("mss.mss") as mock_mss, \
         patch("sounddevice.rec") as mock_rec, \
         patch("sounddevice.wait") as mock_wait, \
         patch("psutil.sensors_battery") as mock_battery, \
         patch("psutil.net_io_counters") as mock_net_io, \
         patch("psutil.virtual_memory") as mock_mem, \
         patch("psutil.disk_usage") as mock_disk:
        
        # Setup VideoCapture mock
        cap_instance = MagicMock()
        cap_instance.isOpened.return_value = True
        import numpy as np
        fake_frame = np.zeros((10, 10, 3), dtype=np.uint8)
        cap_instance.read.return_value = (True, fake_frame)
        mock_cap.return_value = cap_instance
        
        # Setup mss mock
        mss_instance = MagicMock()
        mss_instance.monitors = [{}, {"width": 1920, "height": 1080}]
        screenshot = MagicMock()
        screenshot.rgb = b"0000"
        screenshot.size = (1920, 1080)
        screenshot.width = 1920
        screenshot.height = 1080
        mss_instance.grab.return_value = screenshot
        mock_mss.return_value = mss_instance
        
        # Setup psutil battery mock
        battery_instance = MagicMock()
        battery_instance.percent = 85
        battery_instance.power_plugged = True
        battery_instance.secsleft = -1
        mock_battery.return_value = battery_instance
        
        yield

@pytest.mark.asyncio
async def test_sensor_registry_and_lifecycle(mock_drivers):
    kernel = FridayKernel()
    bus = EventBus()
    
    config = {
        "CAMERA_ENABLED": "true",
        "SCREEN_ENABLED": "true",
        "MICROPHONE_ENABLED": "false",
        "CAMERA_CAPTURE_INTERVAL": 0.01
    }

    pm = PerceptionManager(kernel, bus, config)
    
    # Assert enabled sensors are loaded, and disabled are not
    assert pm.registry.get("camera") is not None
    assert pm.registry.get("screen") is not None
    assert pm.registry.get("microphone") is None

    camera = pm.registry.get("camera")
    assert camera.status == SensorStatus.OFFLINE

    events_received = []
    async def listen(event_data):
        events_received.append(event_data)

    bus.subscribe(SensorEvent.SENSOR_STARTED, listen)

    # Start
    await pm.start()
    await asyncio.sleep(0.02)

    assert camera.status == SensorStatus.RUNNING
    assert len(pm._running_tasks) >= 2
    assert len(events_received) >= 2

    # Pause
    await pm.pause()
    assert camera.status == SensorStatus.PAUSED

    # Resume
    await pm.resume()
    assert camera.status == SensorStatus.RUNNING

    # Stop
    await pm.stop()
    assert camera.status == SensorStatus.OFFLINE
    assert len(pm._running_tasks) == 0

@pytest.mark.asyncio
async def test_observation_pipeline_and_filtering(mock_drivers):
    kernel = FridayKernel()
    bus = EventBus()
    
    config = {
        "CAMERA_ENABLED": "true",
        "CAMERA_CAPTURE_INTERVAL": 0.01
    }

    pm = PerceptionManager(kernel, bus, config)

    readings = []
    async def obs_listener(event_data):
        readings.append(event_data)

    bus.subscribe("perception.observation.camera", obs_listener)

    await pm.start()
    await asyncio.sleep(0.02)
    await pm.stop()

    assert len(readings) > 0
    first_obs = readings[0]
    assert "id" in first_obs
    assert first_obs["sensor_name"] == "camera"

@pytest.mark.asyncio
async def test_health_monitoring(mock_drivers):
    kernel = FridayKernel()
    bus = EventBus()
    
    config = {
        "CAMERA_ENABLED": "true",
        "CAMERA_CAPTURE_INTERVAL": 0.01
    }

    pm = PerceptionManager(kernel, bus, config)
    
    await pm.start()
    await asyncio.sleep(0.02)
    await pm.stop()

    health = pm.get_health_status()
    assert "camera" in health
    camera_health = health["camera"]
    assert camera_health["is_alive"] is True
    assert camera_health["error_count"] == 0

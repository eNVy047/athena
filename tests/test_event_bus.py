import pytest
from friday.core.events import EventBus

@pytest.mark.asyncio
async def test_event_bus_publishing():
    bus = EventBus()
    events_received = []

    async def mock_subscriber(data):
        events_received.append(data.get("val"))

    bus.subscribe("UserMessageReceived", mock_subscriber)
    await bus.publish("UserMessageReceived", {"val": "test_message"})

    assert len(events_received) == 1
    assert events_received[0] == "test_message"

import pytest
import asyncio
from friday.core.kernel.kernel import FridayKernel
from friday.events.event_bus import EventBus
from friday.world.ontology import EntityType, RelationshipType
from friday.world.entity import WorldEntity
from friday.world.relationship import Relationship
from friday.world.world_manager import WorldManager
from friday.world.world_events import WorldEvent

@pytest.mark.asyncio
async def test_entity_creation_and_ontology():
    kernel = FridayKernel()
    bus = EventBus()
    world = WorldManager(kernel, bus)

    # Verify Entity Registration and validation
    entity = WorldEntity("narayan", EntityType.PERSON, {"name": "Narayan"})
    world.knowledge_graph.add_entity(entity)

    retrieved = world.knowledge_graph.get_entity("narayan")
    assert retrieved is not None
    assert retrieved.id == "narayan"
    assert retrieved.type == EntityType.PERSON
    assert retrieved.properties["name"] == "Narayan"

@pytest.mark.asyncio
async def test_relationship_and_graph_traversal():
    kernel = FridayKernel()
    bus = EventBus()
    world = WorldManager(kernel, bus)

    # Narayan -> Laptop -> VS Code -> Friday Project
    world.knowledge_graph.add_entity(WorldEntity("p_narayan", EntityType.PERSON, {"name": "Narayan"}))
    world.knowledge_graph.add_entity(WorldEntity("d_laptop", EntityType.DEVICE, {"name": "Macbook"}))
    world.knowledge_graph.add_entity(WorldEntity("a_vscode", EntityType.APPLICATION, {"name": "VS Code"}))
    world.knowledge_graph.add_entity(WorldEntity("prj_friday", EntityType.PROJECT, {"name": "Friday"}))

    world.knowledge_graph.add_relationship(Relationship("p_narayan", "d_laptop", RelationshipType.OWNS))
    world.knowledge_graph.add_relationship(Relationship("d_laptop", "a_vscode", RelationshipType.USES))
    world.knowledge_graph.add_relationship(Relationship("a_vscode", "prj_friday", RelationshipType.WORKING_ON))

    # Test get relationships
    rels = world.knowledge_graph.get_relationships(source_id="p_narayan")
    assert len(rels) == 1
    assert rels[0].target_id == "d_laptop"

    # Test BFS shortest path
    path = world.knowledge_graph.find_shortest_path("p_narayan", "prj_friday")
    assert path == ["p_narayan", "d_laptop", "a_vscode", "prj_friday"]

    # Test neighbors
    neighbors = world.knowledge_graph.get_neighbors("d_laptop")
    assert len(neighbors) == 2  # incoming from p_narayan, outgoing to a_vscode

@pytest.mark.asyncio
async def test_timeline_tracking():
    kernel = FridayKernel()
    bus = EventBus()
    world = WorldManager(kernel, bus)

    world.timeline.record_event("d_laptop", "creation", {"detail": "Initial setup"})
    world.timeline.record_event("d_laptop", "accessed")

    history = world.timeline.get_history(entity_id="d_laptop")
    assert len(history) == 2
    assert history[0].action == "creation"
    assert history[1].action == "accessed"

@pytest.mark.asyncio
async def test_environment_and_state_tracking():
    kernel = FridayKernel()
    bus = EventBus()
    world = WorldManager(kernel, bus)

    world.environment.update_hardware("Apple M2", "Integrated GPU", 16.0, 512.0)
    info = world.environment.get_environment_info()
    assert info["hardware"]["cpu"] == "Apple M2"

    world.state_tracker.set_activity("coding")
    world.state_tracker.set_application("VS Code", "editor.py")
    state = world.state_tracker.get_state()
    assert state["current_activity"] == "coding"
    assert state["current_application"] == "VS Code"
    assert state["focused_window"] == "editor.py"

@pytest.mark.asyncio
async def test_device_and_project_managers():
    kernel = FridayKernel()
    bus = EventBus()
    world = WorldManager(kernel, bus)

    # Test using device manager
    world.device_manager.add_device("d1", "My Phone", "Phone")
    devices = world.device_manager.list_devices()
    assert len(devices) == 1
    assert devices[0].properties["name"] == "My Phone"

    # Test using project manager
    world.project_manager.add_project("p1", "Friday World Model")
    projects = world.project_manager.list_projects()
    assert len(projects) == 1
    assert projects[0].properties["name"] == "Friday World Model"

@pytest.mark.asyncio
async def test_world_manager_event_publishing():
    kernel = FridayKernel()
    bus = EventBus()
    world = WorldManager(kernel, bus)

    events_received = []
    async def listener(event_data):
        events_received.append(event_data)

    bus.subscribe(WorldEvent.DEVICE_ADDED, listener)
    bus.subscribe(WorldEvent.LOCATION_CHANGED, listener)

    await world.add_device("dev_phone", "iPhone", "Phone")
    await world.change_location("loc_home", "Home")

    # Give event bus a tiny moment to run tasks
    await asyncio.sleep(0.01)

    assert len(events_received) == 2
    assert events_received[0]["event_type"] == WorldEvent.DEVICE_ADDED
    assert events_received[0]["data"]["id"] == "dev_phone"
    assert events_received[1]["event_type"] == WorldEvent.LOCATION_CHANGED
    assert events_received[1]["data"]["id"] == "loc_home"

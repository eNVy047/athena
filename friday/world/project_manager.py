from typing import List, Dict, Any, Optional
from friday.world.knowledge_graph import KnowledgeGraph
from friday.world.entity import WorldEntity
from friday.world.ontology import EntityType

class ProjectManager:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.graph = knowledge_graph

    def add_project(self, project_id: str, name: str, properties: Optional[Dict[str, Any]] = None) -> WorldEntity:
        props = properties or {}
        props.update({"name": name})
        entity = WorldEntity(project_id, EntityType.PROJECT, props)
        self.graph.add_entity(entity)
        return entity

    def get_project(self, project_id: str) -> Optional[WorldEntity]:
        entity = self.graph.get_entity(project_id)
        if entity and entity.type == EntityType.PROJECT:
            return entity
        return None

    def list_projects(self) -> List[WorldEntity]:
        return self.graph.list_entities(EntityType.PROJECT)

    def remove_project(self, project_id: str) -> None:
        project = self.get_project(project_id)
        if project:
            self.graph.delete_entity(project_id)

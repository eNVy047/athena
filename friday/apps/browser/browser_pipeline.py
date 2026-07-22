from friday.apps.browser.browser_models import BrowserResult
from friday.apps.browser.browser_manager import BrowserManager
from friday.apps.browser.dom.dom_snapshot import DOMSnapshotManager
from friday.apps.browser.dom.dom_parser import DOMParser
from friday.apps.browser.dom.semantic_tree import SemanticTreeBuilder

class BrowserPipeline:
    """Orchestrates the entire reasoning and automation loop for a Browser Session."""
    
    def __init__(self, manager: BrowserManager):
        self.manager = manager
        self.dom_snapshot = DOMSnapshotManager()
        self.dom_parser = DOMParser()
        self.semantic_tree = SemanticTreeBuilder()
        
    async def process_task(self, task_prompt: str) -> BrowserResult:
        if not self.manager.session or not self.manager.context_manager:
            return BrowserResult(success=False, message="Browser not initialized")
            
        page = await self.manager.context_manager.get_active_page()
        if not page:
            return BrowserResult(success=False, message="No active page")
            
        # 1. Capture DOM & A11y Tree
        tree_res = await self.dom_snapshot.capture_accessibility_tree(page)
        if not tree_res.success:
            return tree_res
            
        # 2. Parse into Elements
        elements = self.dom_parser.parse_accessibility_tree(tree_res.data["tree"])
        
        # 3. Build Semantic View for Cognition Engine
        markdown_view = self.semantic_tree.build_markdown_representation(elements)
        
        # (In a full implementation, this text would go to the LLM for step planning, 
        # and then the Pipeline would route commands to the Action Engines)
        
        return BrowserResult(
            success=True, 
            message="Task processed successfully", 
            data={"semantic_dom": markdown_view, "task": task_prompt}
        )

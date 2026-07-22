from typing import Dict, Any, List
from friday.apps.browser.browser_models import BrowserElement

class DOMParser:
    """Parses raw DOM representations into structured BrowserElements."""
    
    def parse_accessibility_tree(self, tree: Dict[str, Any]) -> List[BrowserElement]:
        elements = []
        
        def _traverse(node: Dict[str, Any], path: str):
            if not node:
                return
            
            role = node.get("role", "")
            name = node.get("name", "")
            
            if role and name:
                elements.append(BrowserElement(
                    selector=f"role={role}[name=\"{name}\"]",
                    tag_name=role,
                    inner_text=name,
                    is_visible=True,
                    is_interactive=role in ["button", "link", "textbox", "checkbox", "combobox"]
                ))
                
            children = node.get("children", [])
            for i, child in enumerate(children):
                _traverse(child, f"{path}_{i}")
                
        _traverse(tree, "0")
        return elements

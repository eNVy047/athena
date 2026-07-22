from typing import List
from friday.apps.browser.browser_models import BrowserElement

class SemanticTreeBuilder:
    """Transforms raw DOM elements into LLM-friendly semantic text formats."""
    
    def build_markdown_representation(self, elements: List[BrowserElement]) -> str:
        lines = []
        for el in elements:
            if not el.is_visible:
                continue
            
            if el.is_interactive:
                lines.append(f"[{el.tag_name}] {el.inner_text} (Selector: {el.selector})")
            else:
                lines.append(f"{el.inner_text}")
                
        return "\n".join(lines)

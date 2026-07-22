from friday.apps.browser.dom.dom_parser import DOMParser
from friday.apps.browser.dom.semantic_tree import SemanticTreeBuilder
from friday.apps.browser.browser_models import BrowserElement

def test_dom_parser():
    parser = DOMParser()
    mock_tree = {
        "role": "WebArea",
        "name": "Test Page",
        "children": [
            {
                "role": "button",
                "name": "Submit"
            },
            {
                "role": "link",
                "name": "Home"
            }
        ]
    }
    
    elements = parser.parse_accessibility_tree(mock_tree)
    assert len(elements) == 3
    assert elements[0].tag_name == "WebArea"
    assert elements[1].tag_name == "button"
    assert elements[1].inner_text == "Submit"

def test_semantic_tree_builder():
    builder = SemanticTreeBuilder()
    elements = [
        BrowserElement(selector="role=button[name=\"Click Me\"]", tag_name="button", inner_text="Click Me", is_visible=True, is_interactive=True)
    ]
    markdown = builder.build_markdown_representation(elements)
    assert "[button] Click Me" in markdown
    assert "role=button[name=\"Click Me\"]" in markdown

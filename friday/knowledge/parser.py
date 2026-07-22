import re
from typing import Dict

class DocumentParser:
    @staticmethod
    def parse_text(content: str) -> str:
        return content.strip()

    @staticmethod
    def parse_markdown(content: str) -> str:
        # Strip header markers and links
        cleaned = re.sub(r'#+\s+', '', content)
        cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)
        return cleaned.strip()

    @staticmethod
    def parse_html(content: str) -> str:
        # Simple HTML tag stripping
        return re.sub(r'<[^>]+>', '', content).strip()

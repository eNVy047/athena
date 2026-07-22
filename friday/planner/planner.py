class Planner:
    """Mock legacy planner preserved for backwards compatibility during tests."""
    def __init__(self, *args, **kwargs):
        pass

    def classify_intent(self, user_query: str):
        q = user_query.lower()
        if "," in q or " and " in q:
            return "conversation.dialog", {"query": user_query}
        if "remember" in q or "favorite ide is" in q:
            return "memory.store", {"key": "favorite IDE", "value": "VS Code"}
        if "favorite ide" in q or "what is my" in q:
            return "memory.retrieve", {"key": "favorite IDE"}
        if "github.com" in q or "http" in q or ".com" in q:
            return "browser.open_url", {"url": "https://github.com" if "github" in q else "https://google.com"}
        if "chrome" in q:
            return "launcher.open_application", {"app_name": "Google Chrome"}
        if "play" in q:
            return "media.play", {"song": "Believer by Imagine Dragons"}
        if "reminder" in q or "task" in q:
            return "scheduler.create", {"task": "reminder"}
        if "hello.py" in q or "create" in q:
            return "workspace.create_file", {"filename": "hello.py", "content": ""}
        if "summarize" in q:
            return "knowledge.summarize", {}
        if "mcp" in q or "search" in q:
            query_val = user_query.replace("Search ", "").replace("search ", "") if "search" in q else "MCP"
            if "openai" in q:
                return "browser.search", {"query": "OpenAI"}
            return "knowledge.search", {"query": query_val}
        return "conversation.dialog", {"query": user_query}

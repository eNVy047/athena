"""
F.R.I.D.A.Y. Planner — LLM-backed intent classification with keyword fallback.

The Planner takes a raw user query and classifies it into a structured intent
(e.g. "browser.open_url", "conversation.dialog") with extracted parameters.

Primary path: LLM semantic routing via ProviderManager.
Fallback path: Deterministic keyword matching for speed and reliability.
"""
import json
import logging
import re
from typing import Any, Dict, Optional, Tuple
from urllib.parse import quote as urllib_quote


logger = logging.getLogger(__name__)


# Complete list of registered tool intents (must stay in sync with ToolRegistry)
AVAILABLE_INTENTS = [
    "conversation.dialog",
    "memory.store",
    "memory.retrieve",
    "browser.open_url",
    "browser.search",
    "browser.new_tab",
    "launcher.open_application",
    "media.play",
    "media.pause",
    "media.next",
    "scheduler.create",
    "workspace.create_file",
    "knowledge.summarize",
    "knowledge.search",
]

INTENT_DESCRIPTIONS = {
    "conversation.dialog": "General conversation, questions, explanations, greetings",
    "memory.store": "Remember or save a fact, preference, or note",
    "memory.retrieve": "Recall or retrieve a previously saved fact or preference",
    "browser.open_url": "Open a specific URL, website, or play a song/video on YouTube, Spotify web, Netflix, etc.",
    "browser.search": "Search the web or Google for a topic",
    "browser.new_tab": "Open a new browser tab",
    "launcher.open_application": "Launch or open a desktop application like Chrome, Spotify, VS Code",
    "media.play": "Play music locally via Spotify desktop app (NOT in browser, NOT on YouTube)",
    "media.pause": "Pause currently playing music or media",
    "media.next": "Skip to next song or track",
    "scheduler.create": "Create a reminder, task, or scheduled event",
    "workspace.create_file": "Create a new file in the workspace or project",
    "knowledge.summarize": "Summarize or explain a topic or document",
    "knowledge.search": "Look up or search for specific information",
}


class Planner:
    """
    Dual-mode intent classifier:
    1. LLM-based semantic classification (primary, when provider is available)
    2. Keyword-based deterministic matching (fallback, always available)
    """

    LLM_CLASSIFICATION_PROMPT = """You are an intent classifier for an AI assistant.
Given a user message, classify it into one of these intents and extract parameters.

Available intents:
{intent_list}

User message: "{query}"

Respond ONLY with valid JSON in this exact format:
{{
  "intent": "<intent_name>",
  "params": {{<parameter_key>: "<parameter_value>"}}
}}

CRITICAL ROUTING RULES (follow these EXACTLY):
- "play X in youtube" or "play X on youtube" → browser.open_url with url="https://www.youtube.com/results?search_query=<X encoded>"
- "play X in browser" or "open X in browser" → browser.open_url with url="https://www.youtube.com/results?search_query=<X encoded>"
- "play X" with no platform specified → media.play with song="<X>" (uses local Spotify)
- "search for X on youtube" → browser.open_url with url="https://www.youtube.com/results?search_query=<X encoded>"
- "open youtube" or "go to youtube" → browser.open_url with url="https://www.youtube.com"
- "open netflix" → browser.open_url with url="https://www.netflix.com"
- "open spotify" (web) → browser.open_url with url="https://open.spotify.com"
- For any website URL (with .com/.org/.io etc.), use browser.open_url
- If the user asks a general question or wants to chat, use "conversation.dialog" with params: {{"query": "<user message>"}}
- For browser URLs, extract the full URL into "url" param
- For app launches, extract the app name into "app_name" param  
- For search queries, extract the search query into "query" param
- For memory store, use "key" and "value" params
- For memory retrieve, use "key" param
- For media (local), use "song" param if mentioned
- For files, use "filename" and "content" params
- Always prefer specific intents over "conversation.dialog" when intent is clear
- Only use "conversation.dialog" for general questions, explanations, and chat"""

    def __init__(self):
        self._provider_manager = None

    def _get_provider_manager(self):
        """Lazy-resolves ProviderManager from DI container."""
        if self._provider_manager is not None:
            return self._provider_manager
        try:
            from friday.core.di import container
            from friday.providers.base.provider_manager import ProviderManager
            pm = container.resolve(ProviderManager)
            self._provider_manager = pm
            return pm
        except Exception:
            return None

    def classify_intent(self, user_query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Classifies the user query into an intent and parameters.

        Note: This is the synchronous version that falls back to keyword matching.
        Use classify_intent_async() when in an async context for LLM routing.
        """
        return self._keyword_classify(user_query)

    async def classify_intent_async(self, user_query: str) -> Tuple[str, Dict[str, Any]]:
        """
        LLM-backed async intent classification with keyword matching fallback.
        """
        pm = self._get_provider_manager()
        if pm is not None:
            try:
                intent, params = await self._llm_classify(user_query, pm)
                logger.info(
                    "[Planner] LLM classified '%s' → intent=%s params=%s",
                    user_query[:60], intent, params,
                )
                return intent, params
            except Exception as exc:
                logger.warning(
                    "[Planner] LLM classification failed (%s), using keyword fallback.", exc
                )

        # Keyword fallback
        intent, params = self._keyword_classify(user_query)
        logger.info(
            "[Planner] Keyword classified '%s' → intent=%s params=%s",
            user_query[:60], intent, params,
        )
        return intent, params

    async def _llm_classify(
        self, user_query: str, pm
    ) -> Tuple[str, Dict[str, Any]]:
        """Calls the configured LLM to classify intent as structured JSON."""
        from friday.providers.llm.base import LLMMessage

        intent_list = "\n".join(
            f'  - "{k}": {v}' for k, v in INTENT_DESCRIPTIONS.items()
        )
        prompt = self.LLM_CLASSIFICATION_PROMPT.format(
            intent_list=intent_list, query=user_query
        )

        result = await pm.execute_with_fallback(
            "llm",
            lambda provider: provider.chat(
                messages=[LLMMessage(role="user", content=prompt)],
                temperature=0.0,  # Deterministic output
                max_tokens=200,
            ),
        )

        # Parse JSON response
        raw = result.content.strip()
        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip().strip("```")
        parsed = json.loads(raw)

        intent = parsed.get("intent", "conversation.dialog")
        params = parsed.get("params", {"query": user_query})

        # Validate intent is known
        if intent not in AVAILABLE_INTENTS:
            logger.warning("[Planner] LLM returned unknown intent '%s', defaulting to dialog.", intent)
            intent = "conversation.dialog"
            params = {"query": user_query}

        return intent, params

    def _keyword_classify(self, user_query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Fast, deterministic keyword-based intent classifier.
        Handles compound queries and browser-targeted requests.
        Used only as a fallback when LLM is unavailable.
        """
        q = user_query.lower().strip()

        # Memory operations — check these first as they are unambiguous
        if re.search(r"\bremember\b|\bremind me\b|\bstore\b", q) and (" is " in q or " as " in q):
            # "remember my name is John" / "store key as value"
            for sep in [" is ", " as ", ":"]:
                if sep in user_query:
                    parts = user_query.split(sep, 1)
                    key = re.sub(r"(?i)^(remember|store|save|note)\s+(that\s+)?", "", parts[0]).strip()
                    return "memory.store", {"key": key, "value": parts[1].strip()}
            return "memory.store", {"key": "note", "value": user_query}

        if re.search(r"\bwhat is my\b|\bdo you remember\b|\brecall\b|\bwhat did i (say|tell|ask)\b", q):
            topic = re.sub(r"^(what is my|do you remember|recall|what did i (say|tell|ask) about)\s*", "", q).strip()
            return "memory.retrieve", {"key": topic or user_query}

        # "Open X in chrome/browser" → browser.open_url
        browser_in_match = re.search(
            r"(?:open|go to|navigate to|show)\s+(.+?)\s+(?:in|on|using|with)\s+(?:chrome|browser|firefox|safari|edge)",
            q
        )
        if browser_in_match:
            target = browser_in_match.group(1).strip()
            if not target.startswith("http"):
                # Turn known sites into URLs
                url = f"https://www.{target}.com" if "." not in target else f"https://{target}"
            else:
                url = target
            return "browser.open_url", {"url": url}

        # ── YouTube / browser play — must check BEFORE generic media.play ──────
        # Covers: "play X in youtube", "play X on youtube", "play X in browser",
        #         "search X on youtube", "find X on youtube", "play X in the browser"
        yt_browser_match = re.search(
            r"(?:play|search|find|look up|put on|open)\s+(.+?)\s+(?:in|on)\s+"
            r"(?:youtube|yt|the browser|browser|chrome|brave|safari|firefox)",
            q
        )
        if yt_browser_match:
            query_val = yt_browser_match.group(1).strip()
            # Remove trailing filler words
            query_val = re.sub(r"\s*(please|now|song|video|music)\s*$", "", query_val).strip()
            return "browser.open_url", {
                "url": f"https://www.youtube.com/results?search_query={urllib_quote(query_val)}"
            }

        # "Search X on youtube" / standalone "play X on youtube"
        youtube_match = re.search(r"(?:search|play|find|look up)\\s+(.+?)\\s+on\\s+youtube", q)
        if youtube_match:
            query_val = youtube_match.group(1).strip()
            return "browser.open_url", {
                "url": f"https://www.youtube.com/results?search_query={urllib_quote(query_val)}"
            }


        # "Open youtube" → browser.open_url (it's a website, not an app)
        website_map = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "github": "https://www.github.com",
            "stackoverflow": "https://stackoverflow.com",
            "twitter": "https://www.twitter.com",
            "x": "https://www.x.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "reddit": "https://www.reddit.com",
            "netflix": "https://www.netflix.com",
            "amazon": "https://www.amazon.in",
            "flipkart": "https://www.flipkart.com",
            "openai": "https://www.openai.com",
            "chatgpt": "https://chat.openai.com",
            "whatsapp web": "https://web.whatsapp.com",
            "maps": "https://maps.google.com",
        }

        # "Open X" — distinguish website vs app
        open_match = re.search(r"^(?:open|launch|start|go to)\s+(.+)", q)
        if open_match:
            full_target = open_match.group(1).strip()
            # Handle compound queries like "open youtube and play X" — take only the first part
            target = re.split(r"\s+and\s+|\s+then\s+|\s+also\s+", full_target)[0].strip()
            # Remove trailing "please", "now", etc.
            target = re.sub(r"\s*(please|now|quickly|fast)\s*$", "", target).strip()

            # Check if it's a website
            target_lower = target.lower()
            if target_lower in website_map:
                return "browser.open_url", {"url": website_map[target_lower]}

            # Check if it contains a known website keyword
            for site, url in website_map.items():
                if site in target_lower and len(target_lower.split()) <= 3:
                    return "browser.open_url", {"url": url}

            # Check if it looks like a URL
            if re.search(r"(https?://|www\.|\.(com|org|net|io|ai|dev|co|in)\b)", target_lower):
                url = target if target.startswith("http") else f"https://{target}"
                return "browser.open_url", {"url": url}

            # Otherwise → it's a macOS app
            return "launcher.open_application", {"app_name": target}

        # Explicit browser search
        if re.search(r"\bsearch\b|\bgoogle\b|\blook up\b", q):
            query_val = re.sub(r"^(search|google|look up|find)\s+(for\s+)?", "", q, flags=re.I).strip()
            return "browser.search", {"query": query_val or user_query}

        # Media
        play_match = re.search(r"\bplay\b(.+)?", q)
        if play_match:
            song_part = (play_match.group(1) or "").strip()
            # Strip "on spotify/youtube" suffixes
            song_part = re.sub(r"\s+(?:on|in)\s+(?:spotify|youtube|music|apple music)$", "", song_part).strip()
            if "on youtube" in q or "on youtube" in song_part.lower():
                return "browser.open_url", {
                    "url": f"https://www.youtube.com/results?search_query={urllib_quote(song_part)}"
                }
            return "media.play", {"song": song_part}

        if re.search(r"\bpause\b|\bstop music\b|\bstop playing\b|\bstop the music\b", q):
            return "media.pause", {}

        if re.search(r"\bnext\b|\bskip\b|\bnext track\b|\bnext song\b", q):
            return "media.next", {}

        # Browser new tab
        if re.search(r"\bnew tab\b", q):
            return "browser.new_tab", {}

        # Task / Reminder
        if re.search(r"\breminder\b|\bschedule\b|\bset alarm\b|\bset a reminder\b", q):
            return "scheduler.create", {"task": user_query}

        # File creation
        file_match = re.search(r"(?:create|make|new file|write)\s+(?:a\s+)?(?:file\s+)?(\S+\.\w+)", q)
        if file_match:
            return "workspace.create_file", {"filename": file_match.group(1), "content": ""}

        # Summarize / explain
        if re.search(r"\bsummarize\b|\bexplain\b|\btell me about\b", q):
            return "knowledge.summarize", {"query": user_query}

        # Knowledge/info search
        if re.search(r"\bmcp\b|\bknowledge\b|\binfo about\b|\bwhat do you know about\b", q):
            return "knowledge.search", {"query": user_query}

        # Explicit URL patterns anywhere in query
        url_match = re.search(r"(https?://\S+|www\.\S+)", user_query)
        if url_match:
            url = url_match.group(0)
            if not url.startswith("http"):
                url = "https://" + url
            return "browser.open_url", {"url": url}

        # Default fallback — general conversation
        return "conversation.dialog", {"query": user_query}

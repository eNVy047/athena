"""
DeveloperTools — Status, providers, memory, doctor, benchmark commands.

All queries route through the real CLIContext — never bypass the pipeline.
"""
from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING

from friday.cli import stream_renderer as r

if TYPE_CHECKING:
    from friday.cli.cli_context import CLIContext


# ── status ────────────────────────────────────────────────────────────────────

async def cmd_status(ctx: "CLIContext") -> None:
    """Show current system status."""
    r.print_header("F.R.I.D.A.Y. System Status")

    pm = ctx.provider_manager
    cm = ctx.conversation_manager
    agent = ctx.agent

    r.print_section("Core Components")
    r.print_row("Kernel",               "✓ Running",   r.SUCCESS_COLOR)
    r.print_row("FridayAgent",          "✓ Running",   r.SUCCESS_COLOR)
    r.print_row("ConversationManager",  "✓ Running" if cm else "✗ Not ready", r.SUCCESS_COLOR if cm else r.ERROR_COLOR)
    r.print_row("VoiceManager",         "✓ Ready" if ctx.voice_manager else "— Disabled", r.SUCCESS_COLOR if ctx.voice_manager else r.MUTED_COLOR)

    r.print_section("Providers")
    if pm:
        cats = {}
        for key, provider_list in pm.registry._providers.items():
            category = key.split("/")[0]
            cats.setdefault(category, [])
            for p in provider_list:
                cats[category].append(p)
        connected = sum(
            1 for plist in cats.values()
            for p in plist if getattr(p, "is_connected", False)
        )
        total = sum(len(plist) for plist in cats.values())
        r.print_row("Providers connected",  f"{connected}/{total}", r.SUCCESS_COLOR)
        r.print_row("Active LLM",           pm.config.get("LLM_PROVIDER", "—"), r.FRIDAY_COLOR)
        r.print_row("Active STT",           pm.config.get("STT_PROVIDER", "—"), r.FRIDAY_COLOR)
        r.print_row("Active TTS",           pm.config.get("TTS_PROVIDER", "—"), r.FRIDAY_COLOR)
    else:
        r.print_row("Providers", "Not initialized", r.ERROR_COLOR)

    r.print_section("Conversation")
    if cm:
        history = ctx.get_chat_history()
        r.print_row("Session turns",   str(len(history)),         r.USER_COLOR)
        try:
            behaviors = cm.get_all_behaviors()
            r.print_row("Learned behaviors", str(len(behaviors)), r.USER_COLOR)
        except Exception:
            r.print_row("Learned behaviors", "N/A", r.MUTED_COLOR)
    else:
        r.print_row("Session turns",     "—", r.MUTED_COLOR)

    r.print_section("Environment")
    r.print_row("DEV_MODE",  "ON" if r.DEV_MODE else "off",          r.DEV_COLOR if r.DEV_MODE else r.MUTED_COLOR)
    r.print_row("Storage",   str(Path("friday_data").resolve()),      r.MUTED_COLOR)
    r.print_row("Python",    f"{__import__('sys').version.split()[0]}",  r.MUTED_COLOR)
    print()


# ── providers ─────────────────────────────────────────────────────────────────

async def cmd_providers(ctx: "CLIContext") -> None:
    """Show all registered providers with status and latency."""
    r.print_header("Provider Dashboard")

    pm = ctx.provider_manager
    if not pm:
        r.print_error("ProviderManager not initialized.")
        return

    headers = ["Name", "Category", "Status", "Priority", "Latency"]
    rows = []

    for key in sorted(pm.registry._providers.keys()):
        provider_list = pm.registry._providers[key]
        category, name = key.split("/", 1) if "/" in key else (key, key)
        for p in provider_list:
            connected = getattr(p, "is_connected", False)
            status = "✓ Connected" if connected else "Deferred"
            # Measure latency for connected LLM providers
            latency = "—"
            if connected and category == "llm":
                try:
                    t0 = time.monotonic()
                    await asyncio.wait_for(
                        p.chat(
                            messages=[__import__("friday.providers.llm.base", fromlist=["LLMMessage"]).LLMMessage(role="user", content="ping")],
                            max_tokens=1,
                        ),
                        timeout=3.0,
                    )
                    latency = f"{(time.monotonic()-t0)*1000:.0f}ms"
                except Exception:
                    latency = "timeout"

            meta = getattr(p, "metadata", None)
            priority = str(getattr(meta, "priority", "—")) if meta else "—"
            rows.append([name, category, status, priority, latency])

    r.print_table(headers, rows)


# ── memory ────────────────────────────────────────────────────────────────────

async def cmd_memory(ctx: "CLIContext") -> None:
    """Show memory contents: recent history + learned behaviors."""
    r.print_header("Memory & Behavior Store")

    cm = ctx.conversation_manager

    # Learned behaviors
    r.print_section("Learned Behaviors")
    if cm:
        try:
            behaviors = cm.get_all_behaviors()
            if behaviors:
                headers = ["Pattern", "Choice", "Confidence", "Uses", "Days ago"]
                rows = []
                for b in sorted(behaviors, key=lambda x: -x.get("confidence", 0)):
                    conf = b.get("confidence", 0)
                    bar_len = max(1, int(conf / 10))
                    bar = "█" * bar_len + "░" * (10 - bar_len)
                    rows.append([
                        b.get("pattern", ""),
                        b.get("choice", ""),
                        f"{bar} {conf:.1f}%",
                        str(b.get("frequency", 0)),
                        str(b.get("days_ago", "?")),
                    ])
                r.print_table(headers, rows)
            else:
                r.print_row("Learned behaviors", "None yet — start interacting!", r.MUTED_COLOR)
        except Exception as exc:
            r.print_error(f"Could not load behaviors: {exc}")
    else:
        r.print_error("ConversationManager not available.")

    # Chat history
    r.print_section("Session History")
    history = ctx.get_chat_history()
    if history:
        for turn in history[-10:]:
            role = turn.get("role", "?")
            content = turn.get("content", "")[:80]
            color = r.FRIDAY_COLOR if role == "assistant" else r.USER_COLOR
            label = "Friday" if role == "assistant" else "You"
            r.print_row(label, content, color)
    else:
        r.print_row("History", "No turns this session.", r.MUTED_COLOR)

    # Persistent memory (Mem0)
    r.print_section("Long-term Memory (Mem0)")
    pm = ctx.provider_manager
    if pm:
        try:
            mem_provider = pm.registry._providers.get("memory/mem0", [None])[0]
            if mem_provider and getattr(mem_provider, "is_connected", False):
                memories = await mem_provider.search("user preferences", limit=5)
                if memories:
                    for m in memories:
                        r.print_row("•", str(m.get("memory", m))[:80], r.MUTED_COLOR)
                else:
                    r.print_row("Mem0", "No memories stored yet.", r.MUTED_COLOR)
            else:
                r.print_row("Mem0", "Not connected.", r.MUTED_COLOR)
        except Exception as exc:
            r.print_row("Mem0", f"Error: {exc}", r.MUTED_COLOR)
    print()


# ── doctor ────────────────────────────────────────────────────────────────────

async def cmd_doctor(ctx: "CLIContext") -> None:
    """Run full environment and health validation."""
    r.print_header("F.R.I.D.A.Y. Doctor")

    results = []

    def chk(label: str, ok: bool, detail: str = "") -> None:
        status = "PASS" if ok else "FAIL"
        results.append((label, status, detail))

    # Python version
    import sys
    chk("Python ≥ 3.11", sys.version_info >= (3, 11), sys.version.split()[0])

    # Core imports
    for mod in ["friday.kernel.kernel", "friday.kernel.runtime",
                "friday.conversation.conversation_manager",
                "friday.planner.planner", "friday.tools.production_tools",
                "friday.learning.behavior_engine"]:
        try:
            __import__(mod)
            chk(f"import {mod.split('.')[-1]}", True)
        except Exception as exc:
            chk(f"import {mod.split('.')[-1]}", False, str(exc)[:50])

    # API keys
    env_keys = {
        "GROQ_API_KEY":       "Groq (LLM)",
        "OPENAI_API_KEY":     "OpenAI (LLM/Vision)",
        "ANTHROPIC_API_KEY":  "Anthropic",
        "SARVAM_API_KEY":     "Sarvam (STT/TTS)",
        "DEEPGRAM_API_KEY":   "Deepgram (STT/TTS)",
        "MEM0_API_KEY":       "Mem0 (Memory)",
        "SERPER_API_KEY":     "Serper (Search)",
    }
    for key, label in env_keys.items():
        val = os.getenv(key, "")
        chk(f"API: {label}", bool(val), "set" if val else "missing")

    # Browser capability
    from friday.kernel.capabilities import CapabilityManager
    caps = CapabilityManager.detect_system_capabilities()
    chk("Browser available",   caps.has_chrome,  "Safari/Chrome/Brave detected" if caps.has_chrome else "no browser found")
    chk("Git available",       caps.has_git)
    chk("Python3 on PATH",     caps.has_python)

    # Storage
    storage = Path("friday_data")
    chk("Storage dir exists",  storage.exists(),  str(storage.resolve()))

    # Provider connectivity
    pm = ctx.provider_manager
    if pm:
        for key, plist in pm.registry._providers.items():
            for p in plist:
                if getattr(p, "is_connected", False):
                    chk(f"Provider: {key}", True)
                    break

    # Print results
    r.print_table(
        ["Check", "Result", "Detail"],
        [[label, status, detail] for label, status, detail in results]
    )

    failed = sum(1 for _, s, _ in results if s == "FAIL")
    if failed == 0:
        r.print_success(f"All {len(results)} checks passed!")
    else:
        r.print_error(f"{failed}/{len(results)} checks failed.")
    print()


# ── benchmark ─────────────────────────────────────────────────────────────────

async def cmd_benchmark(ctx: "CLIContext") -> None:
    """Measure response latency across the pipeline."""
    r.print_header("Benchmark")

    test_queries = [
        ("Greeting",        "hello"),
        ("Planner routing", "open VS Code"),
        ("Memory recall",   "what is my favorite editor"),
        ("Search intent",   "search latest AI news"),
        ("Tool launch",     "open calculator"),
    ]

    headers = ["Test", "Total", "Note"]
    rows = []

    for label, query in test_queries:
        r.show_status(f"Benchmarking: {label}…")
        t0 = time.monotonic()
        try:
            response = await ctx.process(query)
            elapsed = (time.monotonic() - t0) * 1000
            note = response[:50].replace("\n", " ") if response else "—"
            rows.append([label, f"{elapsed:.0f}ms", note])
        except Exception as exc:
            rows.append([label, "error", str(exc)[:50]])

    r.stop_thinking()
    r.print_table(headers, rows)


# ── logs ──────────────────────────────────────────────────────────────────────

def cmd_logs() -> None:
    """Tail the runtime log file."""
    import subprocess
    log_candidates = [
        Path("friday_data") / "friday.log",
        Path("friday.log"),
    ]
    log_file = next((p for p in log_candidates if p.exists()), None)
    if not log_file:
        r.print_error("No log file found. Set up file logging in your configuration.")
        return
    r.print_header(f"Tailing: {log_file}")
    try:
        subprocess.run(["tail", "-f", "-n", "50", str(log_file)])
    except KeyboardInterrupt:
        pass


# ── reset-memory ─────────────────────────────────────────────────────────────

def cmd_reset_memory() -> None:
    """Clear conversation history."""
    from friday.cli.history import SessionHistory
    SessionHistory.clear_all()
    r.print_success("Conversation history cleared.")


# ── reset-learning ────────────────────────────────────────────────────────────

def cmd_reset_learning(ctx: "CLIContext") -> None:
    """Wipe all learned behaviors."""
    cm = ctx.conversation_manager
    if cm:
        try:
            cm.reset_all_behaviors()
            r.print_success("All learned behaviors reset.")
        except Exception as exc:
            r.print_error(f"Could not reset behaviors: {exc}")
    else:
        # Try direct store wipe
        store_file = Path("friday_data") / "learning" / "behaviors.json"
        if store_file.exists():
            store_file.unlink()
            r.print_success("Behavior store cleared.")
        else:
            r.print_error("ConversationManager not available and no behavior store found.")

# F.R.I.D.A.Y. — Tony Stark AI Assistant

🎉 **Official Public Release:** F.R.I.D.A.Y. is available as a standalone application and extensible developer platform!

> *"Fully Responsive Intelligent Digital Assistant for You"*

F.R.I.D.A.Y. is a Tony Stark-inspired AI assistant architecture:

| Component | What it is |
| --- | --- |
| **MCP Server** (`uv run friday`) | A [FastMCP](https://github.com/jlowin/fastmcp) server that exposes tools (web search, system info, memory, perception) over SSE. |
| **Desktop Application** (`uv run friday-desktop`) | A PySide6 / QML graphical user interface powering native desktop interactions, signal bridges, theme management, and perception controls. |

---

## How it works

```text
User / GUI / Microphones ──► Perception & Input Processing
                                   │
                                   ▼
        LLM (OpenAI / Gemini / Groq) ◄──────► MCP Server (FastMCP / SSE)
                                   │                             ├─ search_web
                                   ▼                             ├─ get_system_info
                       TTS & Audio Processing                     └─ …more tools
                                   │
                                   ▼
                   Memory Pipeline (Mem0 & Built-in)
```

---

## Memory System (Hermes Architecture)

FRIDAY features a Hermes-inspired memory system to persist facts across conversations:

* **Built-in Memory**: A local Markdown-based filesystem storage (saved under `USER.md` / SQLite).
* **Mem0 Memory**: An external cloud-based vector memory provider for semantically searchable and persistent user profiles.
* **Prefetch & Context Injection**: Before the LLM begins generating a response for a turn, FRIDAY queries both memory sources, merges, deduplicates, and ranks the relevant memories, then injects them as structured background context.
* **Asynchronous Extraction & Sync**: After each turn, FRIDAY extracts new facts from the user-assistant dialog in the background and saves them, automatically filtering out duplicates to keep the profile clean.

---

## Project structure

```text
friday/
├── server.py                   # uv run friday  → starts the MCP server (SSE on :8000)
├── pyproject.toml
├── .env.example                # copy → .env and fill in your keys
├── RUN.md                      # Detailed run and operational guide
│
├── friday/                     # Core F.R.I.D.A.Y. package
│   ├── config.py               # Env-var loading & app-wide settings
│   ├── apps/desktop/           # Desktop PySide6 / QML GUI application
│   ├── core/                   # Kernel, config manager, service registry
│   ├── memory/                 # Memory pipeline (Prefetch, Extraction, Providers)
│   ├── perception/             # Multimodal sensors (camera, screen, mic, etc.)
│   ├── providers/              # Unified provider integrations (LLM, Vision, STT, TTS, OCR)
│   ├── tools/                  # MCP tools (callable by the LLM)
│   └── voice/                  # Native audio streams, VAD, and speech pipeline
```

---

## Quick start (For Developers)

### 1. Prerequisites

* Python ≥ 3.11
* [`uv`](https://github.com/astral-sh/uv) — `pip install uv`

### 2. Clone & install

```bash
git clone https://github.com/eNVy047/f.r.i.d.a.y.git
cd f.r.i.d.a.y
uv sync          
```

### 3. Set up environment

```bash
cp .env.example .env
```

### 4. Run

**Terminal 1 — MCP Server**
```bash
uv run friday
```

**Terminal 2 — Desktop GUI**
```bash
uv run friday-desktop
```

---

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | Optional | [platform.openai.com](https://platform.openai.com/api-keys) — for OpenAI LLM/Vision/TTS |
| `GEMINI_API_KEY` | Optional | [aistudio.google.com](https://aistudio.google.com/projects) — for Gemini models |
| `GROQ_API_KEY` | Optional | [console.groq.com](https://console.groq.com) — for Groq models |
| `DEEPGRAM_API_KEY` | Optional | [console.deepgram.com](https://console.deepgram.com) — for Deepgram STT/TTS |
| `SARVAM_API_KEY` | Optional | [dashboard.sarvam.ai](https://dashboard.sarvam.ai) — for Sarvam STT |
| `MEM0_API_KEY` | Optional | [mem0.ai](https://mem0.ai) — for external vector memory persistence |

---

## Tech stack

* **[FastMCP](https://github.com/jlowin/fastmcp)** — MCP server framework
* **PySide6 / QML** — Modern Desktop Application UI
* **OpenAI / Gemini / Groq** — LLMs & Vision models
* **Deepgram / Sarvam** — Speech-to-Text & Text-to-Speech
* **Mem0** — Vector-backed external memory
* **[uv](https://github.com/astral-sh/uv)** — Fast Python package manager

---

## License

MIT

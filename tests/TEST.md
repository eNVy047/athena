# Friday AI OS Subsystems Test & Guide

This file outlines the purpose, files, expected behavior, manual testing steps, and Hinglish explanations ("Ye Kya Kaam Karta Hai?") for every Friday AI OS subsystem.

---

## 1. Planner

### Purpose
Goal decomposition, multi-step goal execution, and reflection.

### Files Involved
*   `friday/planner/goal.py`
*   `friday/planner/plan.py`
*   `friday/planner/decomposition.py`
*   `friday/planner/reasoning.py`
*   `friday/planner/reflection.py`
*   `friday/planner/executor.py`
*   `friday/planner/planner.py`

### Expected Behaviour
Decomposes user commands into clean lists of dependency-ordered execution steps, reasoning through each step and reflecting on the result.

### Ye Kya Kaam Karta Hai?
*   **Planner user ke goal ko chhote-chhote steps mein todta hai.**
*   **Kaunsa tool use karna hai decide karta hai.**
*   **Agar koi step fail ho jaye to naya plan banata hai.**
*   **Final result verify karta hai.**

### Friday Kaise Use Karta Hai?
```
Voice command aati hai
        ↓
Planner goal banata hai
        ↓
Tools choose karta hai
        ↓
Executor run karta hai
        ↓
Answer return karta hai
```

---

## 2. Context Builder

### Purpose
Centralized assembly of LLM prompt context blocks.

### Files Involved
*   `friday/application/services/context_builder.py`

### Expected Behaviour
Aggregates session parameters, capabilities, clock times, memory, and workspace configurations into a single context block.

### Ye Kya Kaam Karta Hai?
*   **Context Builder saare sources (conversation history, memories, workspace status, capabilities) se data collect karta hai.**
*   **Pura context ek single structured string block me compile karke LLM ko bhejta hai.**

---

## 3. Prompt Manager

### Purpose
Template loading and variable substitution for prompts.

### Files Involved
*   `friday/application/services/prompt_manager.py`
*   `friday/prompts/system/default.txt`

### Expected Behaviour
Loads template files from disk and formats variables dynamically.

### Ye Kya Kaam Karta Hai?
*   **Prompt Manager templates file ko disk se dynamically load karta hai.**
*   **Variables (profile name, environment caps) substitute karke final system prompt render karta hai.**

---

## 4. Tool Registry

### Purpose
Tool schema metadata, validation, permissions, and pipeline execution.

### Files Involved
*   `friday/tools/metadata.py`
*   `friday/tools/registry.py`
*   `friday/tools/validators.py`
*   `friday/tools/permissions.py`
*   `friday/tools/executor.py`

### Expected Behaviour
Registers tools, validates execution args, checks scopes, and runs with timeout/retry bounds.

### Ye Kya Kaam Karta Hai?
*   **Tool Registry saare available tools ko store aur track karta hai.**
*   **Input parameters valid hai ya nahi check karta hai.**
*   **Scope aur authorization verify karta hai.**
*   **Timeouts aur retry loops manage karta hai.**

---

## 5. Workflow Engine

### Purpose
Parallel, sequential, and conditional step execution state machines.

### Files Involved
*   `friday/workflow/state.py`
*   `friday/workflow/checkpoint.py`
*   `friday/workflow/executor.py`
*   `friday/workflow/scheduler.py`
*   `friday/workflow/engine.py`

### Expected Behaviour
Transitions execution flows through sequential or parallel steps, saving checkpoints to disk.

### Ye Kya Kaam Karta Hai?
*   **Workflow Engine steps ko sequential ya parallel loops me execute karta hai.**
*   **Milestones ko disk par save (checkpoint) karta hai taaki recovery safe ho.**

---

## 6. Task Scheduler

### Purpose
Manages cron, delayed, and recurring task priority queues.

### Files Involved
*   `friday/scheduler/cron.py`
*   `friday/scheduler/recurring.py`
*   `friday/scheduler/delayed.py`
*   `friday/scheduler/queue.py`
*   `friday/scheduler/scheduler.py`

### Expected Behaviour
Triggers delayed or recurring callbacks, queuing them according to priorities.

### Ye Kya Kaam Karta Hai?
*   **Scheduler delayed aur recurring tasks (cron jobs, reminders) ko track karta hai.**
*   **Agnostic loops me runs trigger karke priorities queue me process karta hai.**

---

## 7. Knowledge RAG Layer

### Purpose
Local vector indexing and retrieval for external documentation files.

### Files Involved
*   `friday/knowledge/parser.py`
*   `friday/knowledge/chunker.py`
*   `friday/knowledge/embeddings.py`
*   `friday/knowledge/index.py`
*   `friday/knowledge/retriever.py`

### Expected Behaviour
Parses HTML/Markdown files, chunks text, generates embeddings, and retrieves matching blocks.

### Ye Kya Kaam Karta Hai?
*   **Knowledge Layer files (PDF/MD/HTML) se details load karke chunk karta hai.**
*   **Local similarity index search run karke query relative segments extract karta hai.**

---

## 8. Playwright Browser Runtime

### Purpose
Browser automation pools, profiles, tabs, and page inspection.

### Files Involved
*   `friday/browser/browser_pool.py`
*   `friday/browser/session_manager.py`
*   `friday/browser/tab_manager.py`
*   `friday/browser/dom.py`
*   `friday/browser/manager.py`

### Expected Behaviour
Runs browser engines, handles cookie/session isolation, and extracts accessibility/DOM text.

### Ye Kya Kaam Karta Hai?
*   **Browser subsystem actual Chromium/Firefox processes launch karta hai.**
*   **Tabs, cookie profiles, downloads, aur DOM elements dynamically control karta hai.**

---

## 9. Workspace Manager

### Purpose
Tracks session folders and artifact workspaces.

### Files Involved
*   `friday/workspace/manager.py`

### Expected Behaviour
Creates project directories and runs isolated folder cleanups.

### Ye Kya Kaam Karta Hai?
*   **Workspace Manager user ke code, generated files, aur temporary workspace folders manage karta hai.**
*   **Runs complete hone par space cleanup trigger karta hai.**

---

## 10. Observability

### Purpose
Telemetry profiling, health monitoring, and tracing.

### Files Involved
*   `friday/observability/logger.py`
*   `friday/observability/metrics.py`
*   `friday/observability/tracing.py`
*   `friday/observability/profiler.py`
*   `friday/observability/health.py`

### Expected Behaviour
Logs JSON telemetry, profiles CPU/RAM limits, tracks span durations, and checks system health thresholds.

### Ye Kya Kaam Karta Hai?
*   **Observability system log tracing aur CPU/RAM profiling coordinates karta hai.**
*   **Duration metrics aur health check status log reports compile karta hai.**

---

## 11. Security Guardrails

### Purpose
Audit logging, filesystem path traversal prevention, and confirmation workflow hooks.

### Files Involved
*   `friday/security/permissions.py`
*   `friday/security/approval.py`
*   `friday/security/sandbox.py`
*   `friday/security/secrets.py`
*   `friday/security/audit.py`

### Expected Behaviour
Prevents path traversal, checks permission scopes, and manages keychains and action logging.

### Ye Kya Kaam Karta Hai?
*   **Security guardrails system file paths and sandbox containment check karta hai.**
*   **Dangerous actions par user verification checks run karta hai.**

---

## 12. Multi-Agent Runtime

### Purpose
Task routing across cooperating specialist agents.

### Files Involved
*   `friday/application/orchestrators/coordinator.py`
*   `friday/domain/agent.py`

### Expected Behaviour
Coordinates execution capabilities across registered agent configurations.

### Ye Kya Kaam Karta Hai?
*   **Multi-Agent system tasks ko correct specialist agent (Executor, Browser, etc.) ko route karta hai.**

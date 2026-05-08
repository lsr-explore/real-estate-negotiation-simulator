# Real Estate Negotiation Workshop
## Learn MCP · A2A · Google ADK

A **4-hour hands-on workshop** teaching modern AI agent frameworks through a concrete, runnable project: an autonomous real estate negotiation between a Buyer Agent and a Seller Agent.

---

## What You'll Learn

| Concept | What It Is | How We Use It |
|---|---|---|
| **MCP** | Standard protocol for agents to access external tools | Agents query pricing/inventory servers via MCP |
| **A2A** | Agent-to-Agent protocol (Agent Card discovery + JSON-RPC over HTTP, task lifecycle, streaming) | Module 3 uses the true networked A2A protocol via `a2a-sdk` |
| **Google ADK** | Production-grade agent framework (LlmAgent, workflow agents, sessions, MCPToolset, callbacks) | Module 3 builds the buyer and seller agents with ADK |

---

## The Scenario

**Property**: 742 Evergreen Terrace, Austin, TX 78701
*(4 BR / 3 BA / 2,400 sqft / Single Family / Built 2005)*

| Party | Goal | Starting Position | Walk-Away |
|---|---|---|---|
| **Buyer Agent** (GPT-4o) | Buy at lowest price | Offer $425,000 | Over $460,000 |
| **Seller Agent** (GPT-4o) | Sell at highest price | Counter $477,000 | Below $445,000 |

The negotiation runs for a maximum of **5 rounds**. Agents use real market data (via MCP) to justify every offer.

---

## Project Structure

Folders are numbered in teaching order. Each module introduces one new concept.

```
real-estate-negotiation-simulator/
│
├── m1_baseline/                       # MODULE 1 — Start here. Watch it break.
│   ├── README.md                      # Module guide for learners
│   ├── naive_negotiation.py           # Intentionally broken (10 failure modes)
│   ├── state_machine.py               # FSM that fixes termination
│   └── notes/
│       └── agents_fundamentals.md     # Reference: agent fundamentals
│
├── m2_mcp/                            # MODULE 2 — External data via MCP
│   ├── README.md                      # Module guide for learners
│   ├── github_agent_client.py         # LLM agent that calls GitHub tools via MCP
│   ├── sse_agent_client.py             # SSE agent client (LLM picks tools over HTTP)
│   ├── pricing_server.py              # Custom MCP: market pricing tools
│   ├── inventory_server.py            # Custom MCP: inventory + seller constraints
│   ├── demos/                          # Standalone deep-dive demos (handshake, tool loop, primitives, content types, HTTP transport)
│   ├── exercises/                      # Hands-on coding exercises for Module 2
│   ├── solution/                       # Worked solutions for Module 2 exercises
│   └── notes/
│       └── mcp_deep_dive.md           # Reference: MCP protocol deep dive
│
├── m3_adk_multiagents/                # MODULE 3 — Google ADK + A2A protocol
│   ├── README.md                      # Module guide for learners
│   ├── negotiation_agents/            # adk web-launchable agent packages
│   │   ├── buyer_agent/agent.py         # Buyer LlmAgent + MCPToolset (pricing)
│   │   ├── seller_agent/agent.py        # Seller LlmAgent + MCPToolset (pricing + inventory)
│   │   └── negotiation/agent.py         # LoopAgent + SequentialAgent + MCP tools + submit_decision
│   ├── adk_demos/                      # adk web-launchable demos (d01–d09) + A2A scripts (10–13)
│   ├── a2a_14_orchestrated_negotiation.py  # A2A multi-round buyer↔seller negotiation
│   ├── exercises/                      # Hands-on coding exercises for Module 3
│   ├── solution/                       # Worked solutions for Module 3 exercises
│   └── notes/
│       ├── a2a_protocols.md           # Reference: A2A protocol deep dive
│       ├── adk_quick_reference.md     # Reference: ADK API quick reference
│       └── google_adk_overview.md     # Reference: Google ADK overview
│
├── Week 6 _ ... Google ADK.pptx.pdf   # Workshop slide deck (97 slides)
├── .env.example                       # Copy to .env and add your API keys
└── requirements.txt
```

If module files feel overwhelming, start with the README inside each module folder.

### Deep-dive demos

Modules 2 and 3 ship a `demos/` folder of small, single-purpose, runnable scripts that crack open the protocols on the wire — designed to pair with the `notes/` reference docs. See each module README for the per-demo table:

- [m2_mcp/demos/](m2_mcp/demos/) — MCP handshake, tool loop trace, primitives, content types, Streamable HTTP
- [m3_adk_multiagents/adk_demos/](m3_adk_multiagents/adk_demos/) — ADK concept demos (basic agent, MCP tools, sessions, sequential, parallel, loop, agent-as-tool, callbacks, event stream) + A2A protocol scripts (wire format, context threading, parts/artifacts, streaming)

### Notes live inside each module

Each module has a `notes/` subfolder with reference documentation. There are
two flavors: **demo study notes** (read while running the demos, narrate
expected output and key observations) and **conceptual deep-dives** (read any
time after the workshop for the theory and production patterns).

Every note has a header block stating its audience, prerequisites, what to
read before/after it, and a 3-point TL;DR. Open any note — the first thing
you'll see is whether it's the right one for you right now.

#### Recommended reading order

| When | Read | Why |
|---|---|---|
| **While running M1 demos** | [`m1_baseline/notes/M1_DEMO_STUDY_NOTES.md`](m1_baseline/notes/M1_DEMO_STUDY_NOTES.md) | Per-demo narration of `naive_negotiation.py` and `state_machine.py` |
| **After M1** | [`m1_baseline/notes/agents_fundamentals.md`](m1_baseline/notes/agents_fundamentals.md) | Conceptual deep-dive — what an agent *is*, where the FSM fits, when not to use agents |
| **While running M2 demos** | [`m2_mcp/notes/M2_DEMO_STUDY_NOTES.md`](m2_mcp/notes/M2_DEMO_STUDY_NOTES.md) | Per-demo narration of all 5 MCP demos plus the GitHub + SSE clients |
| **After M2** | [`m2_mcp/notes/mcp_deep_dive.md`](m2_mcp/notes/mcp_deep_dive.md) | Full MCP protocol reference — primitives, transports, design patterns |
| **While running M3 demos** | [`m3_adk_multiagents/notes/M3_DEMO_STUDY_NOTES.md`](m3_adk_multiagents/notes/M3_DEMO_STUDY_NOTES.md) | Per-demo narration of all 9 ADK demos + the 4 A2A demos + the negotiation system |
| **After M3 (start here)** | [`m3_adk_multiagents/notes/adk_quick_reference.md`](m3_adk_multiagents/notes/adk_quick_reference.md) | One-page lookup for every ADK + A2A construct |
| **After M3 (go deep)** | [`m3_adk_multiagents/notes/google_adk_overview.md`](m3_adk_multiagents/notes/google_adk_overview.md) | Full ADK reference — every agent type, callbacks, sessions, event stream |
| **After M3 (network layer)** | [`m3_adk_multiagents/notes/a2a_protocols.md`](m3_adk_multiagents/notes/a2a_protocols.md) | Full A2A reference — wire format, contextId, parts, artifacts, streaming, production patterns |

Module 3 has three notes because it spans two distinct topics: the A2A protocol standard and the ADK runtime. Read `adk_quick_reference.md` first to get the construct names in your head; reach for the other two when you need depth on a specific construct.

---

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Node.js 18+ (for GitHub MCP demo in Module 2 only)

**Verify installation:**
```bash
python --version  # should be 3.10+
node --version    # should be 18+
```

### 2. Clone or open this repo

```bash
# If you already have the repo, skip this step
git clone <your-repo-url>
cd real-estate-negotiation-simulator
```

### 3. Create a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
```

**macOS/Linux:**
```bash
python3 -m venv .venv
```

### 4. Activate the virtual environment

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bat
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

> **Tip**: Your prompt will change to show `(.venv)` when the environment is active.
> To deactivate at any time, run `deactivate`.

### 5. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure API keys

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

Then edit `.env` and set:
```env
OPENAI_API_KEY=sk-your-key-here
GITHUB_TOKEN=ghp-your-token-here   # Optional — Module 2 GitHub demo only
```

### 7. Run a smoke test

```bash
# Smoke test (no API key needed — FSM only)
python m1_baseline/state_machine.py

# Full Module 1 demo (requires OPENAI_API_KEY)
python m1_baseline/naive_negotiation.py
```

If `state_machine.py` runs cleanly, your Python environment is ready.
If `naive_negotiation.py` runs (needs `OPENAI_API_KEY`), your API key is configured correctly.

### 8. Run the Workshop Modules in Order

```bash
# MODULE 1: Naive LLM negotiation (10 failure modes) + FSM fix
python m1_baseline/naive_negotiation.py   # requires OPENAI_API_KEY — real LLM calls, 10 failure modes
python m1_baseline/state_machine.py       # no API key needed — FSM termination guarantee

# MODULE 2: MCP protocol
python m2_mcp/github_agent_client.py      # GitHub MCP agent (needs GITHUB_TOKEN + OPENAI_API_KEY)
python m2_mcp/pricing_server.py           # Run MCP server standalone (stdio)
python m2_mcp/pricing_server.py --sse --port 8001  # SSE transport mode
# MCP deep-dive demos (no API key needed unless noted):
python m2_mcp/demos/01_initialize_handshake.py
python m2_mcp/demos/02_tool_loop_trace.py
python m2_mcp/demos/03_list_all_primitives.py
python m2_mcp/demos/04_content_types.py
python m2_mcp/demos/05_streamable_http_transport.py

# MODULE 3: Google ADK + A2A protocol (needs OPENAI_API_KEY)
adk web m3_adk_multiagents/adk_demos/               # ADK demos d01–d09 in dropdown
adk web m3_adk_multiagents/negotiation_agents/       # buyer, seller, negotiation in dropdown
adk web --a2a m3_adk_multiagents/negotiation_agents/ # same + A2A endpoints + Agent Cards
# A2A protocol demos (run in a second terminal against adk web --a2a):
python m3_adk_multiagents/adk_demos/a2a_10_wire_lifecycle.py --seller-url http://127.0.0.1:8000/a2a/seller_agent
python m3_adk_multiagents/adk_demos/a2a_11_context_threading.py --seller-url http://127.0.0.1:8000/a2a/seller_agent
python m3_adk_multiagents/adk_demos/a2a_12_parts_and_artifacts.py --seller-url http://127.0.0.1:8000/a2a/seller_agent
python m3_adk_multiagents/adk_demos/a2a_13_streaming.py --seller-url http://127.0.0.1:8000/a2a/seller_agent
# A2A orchestrated negotiation (buyer ↔ seller via Agent Cards):
python m3_adk_multiagents/a2a_14_orchestrated_negotiation.py
```

### 9. Module Exercises

Module 2 and Module 3 ship hands-on exercises with complete, runnable solutions. **These are designed for the 2-hour follow-up review session** held a few days after the workshop — students attempt them as homework, the instructor walks through each solution and runs it live in class. (Module 1 has no exercises — its purpose is conceptual motivation, not skill practice.)

| Module | Exercise | Difficulty | Task |
|---|---|---|---|
| M2 | `ex01_walk_score_tool.md` | `[Starter]` | Add a `get_walk_score` tool to the pricing server; watch the LLM auto-discover and use it |
| M2 | `ex02_multi_server_agent.md` | `[Core]` | Build an `LlmAgent` that connects to both pricing + inventory MCP servers from scratch |
| M3 | `ex01_budget_cap_callback.md` | `[Starter]` | Write a `before_tool_callback` that blocks `submit_decision` calls with `price > $460,000` |
| M3 | `ex02_stuck_detection.md` | `[Core]` | Modify the orchestrator to track offer history and escalate early when rounds stall |
| M3 | `ex03_a2a_multiround_client.md` | `[Core]` | Write an A2A client that drives buyer ↔ seller via `message/send` with `contextId` threading |
| M3 | `ex04_mediator_agent.md` | `[Core]` | Build a mediator that wraps buyer + seller as `AgentTool`s and proposes a midpoint |
| M3 | `ex05_prompt_injection_defense.md` | `[Core]` | Add a `before_model_callback` to detect and redact prompt injection attempts |
| M3 | `ex06_human_in_the_loop.md` | `[Core]` | Add a human-approval checkpoint with three-tier governance: auto-approve, checkpoint, block |
| M3 | `ex07_parallel_negotiation.md` | `[Stretch]` | Negotiate with two sellers in parallel using `ParallelAgent`, then pick the best deal |
| M3 | `ex08_shared_market_intel.md` | `[Core]` | Use `app:` state as shared market intelligence — cache pricing lookups for all agents |
| M3 | `ex09_adaptive_strategy.md` | `[Stretch]` | Episodic memory + strategy advisor `AgentTool` that analyses concession patterns |
| M3 | `stretch_streaming_client.md` | `[Stretch]` | Convert M3.3 to use `message/stream` and render task lifecycle events as they arrive |

Each solution lives in its module's `solution/` folder as a self-contained, runnable package — `agent.py` files you can launch directly with `adk web`, or scripts you can run with `python`. The instructor walks through each solution live during the review session.

---

## Module Run Reference

One-line summary of every runnable file in the workshop, grouped by module. Use this as a quick lookup or as slide content.

### Module 1 — Baseline (why naive agents break)

| # | Run | What it means (one line) |
|---|---|---|
| 1 | `python m1_baseline/naive_negotiation.py` | Intentionally broken negotiation — `while True` + raw strings + regex — shows the 10 failure modes of naive agents. |
| 2 | `python m1_baseline/state_machine.py` | Finite State Machine (`IDLE → NEGOTIATING → AGREED/FAILED`) — terminal states have no exits, so the loop is **mathematically guaranteed to end**. |

### Module 2 — MCP (give agents real tools)

| # | Run | What it means (one line) |
|---|---|---|
| 1 | `python m2_mcp/github_agent_client.py` | LLM agent talks to **GitHub's official MCP server** over `stdio` — proves the ReAct tool-loop on a familiar API. |
| 2 | `python m2_mcp/pricing_server.py` *(or `--sse --port 8001`)* | Custom MCP server exposing `get_market_price` + `calculate_discount` — the buyer/seller's source of market data. |
| 3 | `python m2_mcp/inventory_server.py` *(or `--sse --port 8002`)* | Custom MCP server with `get_inventory_level` (public) + `get_minimum_acceptable_price` (seller-only) — demonstrates **information asymmetry**. |
| 4 | `python m2_mcp/sse_agent_client.py` *(after starting servers in SSE mode)* | Same agent loop as the GitHub client, but over **HTTP/SSE** — proves the transport is irrelevant. |
| 5 | `python m2_mcp/demos/01_initialize_handshake.py` | Raw JSON-RPC frames of the MCP `initialize` handshake — see the protocol on the wire, no SDK. |
| 6 | `python m2_mcp/demos/02_tool_loop_trace.py` | Full **model ↔ host ↔ server** tool-calling loop, narrated step-by-step with timestamps. |
| 7 | `python m2_mcp/demos/03_list_all_primitives.py` | Lists **Tools, Resources, and Prompts** from both servers — proves MCP carries more than just tools. |
| 8 | `python m2_mcp/demos/04_content_types.py` | Inline server returning each Content block kind (text / image / embedded resource) so you see the JSON shapes. |
| 9 | `python m2_mcp/demos/05_streamable_http_transport.py --serve` *(then `--client`)* | Same MCP protocol over **Streamable HTTP** — the spec's recommended replacement for raw SSE. |

### Module 3 — Google ADK + A2A (multi-agent orchestration)

**ADK demos — interactive Web UI** (`adk web m3_adk_multiagents/adk_demos/`)

| # | Pick from dropdown | What it means (one line) |
|---|---|---|
| d01 | `d01_basic_agent` | Bare `LlmAgent` + a Python function tool — the simplest possible ADK agent. |
| d02 | `d02_mcp_tools` | `LlmAgent` + `MCPToolset` — ADK auto-spawns the MCP server and discovers its tools. |
| d03 | `d03_sessions_state` | `ToolContext` reads/writes session state that **persists across turns**. |
| d04 | `d04_sequential` | `SequentialAgent` pipeline — each step's `output_key` feeds the next via `{placeholder}`. |
| d05 | `d05_parallel` | `ParallelAgent` fan-out — concurrent agents writing to different state keys. |
| d06 | `d06_loop` | `LoopAgent` that iterates until a callback sets `actions.escalate = True`. |
| d07 | `d07_agent_as_tool` | `AgentTool` — wrap a whole agent as a callable tool for hierarchical delegation. |
| d08 | `d08_callbacks` | `before_model` / `before_tool` / `after_tool` hooks — PII redaction, allowlists, logging. |
| d09 | `d09_event_stream` | Inspect ADK's raw event stream — tool calls, state deltas, final-response markers. |

**A2A protocol demos — terminal scripts** (start `adk web --a2a m3_adk_multiagents/negotiation_agents/` first)

| # | Run | What it means (one line) |
|---|---|---|
| 10 | `python m3_adk_multiagents/adk_demos/a2a_10_wire_lifecycle.py --seller-url …/a2a/seller_agent` | Hand-crafted JSON-RPC `message/send` — see Agent Card discovery and task-state transitions. |
| 11 | `python m3_adk_multiagents/adk_demos/a2a_11_context_threading.py --seller-url …/a2a/seller_agent` | Reuse `contextId` across rounds — multiple A2A calls become **one threaded conversation**. |
| 12 | `python m3_adk_multiagents/adk_demos/a2a_12_parts_and_artifacts.py --seller-url …/a2a/seller_agent` | Multi-part Messages (`TextPart` + `DataPart`) and inspecting Artifacts returned by the agent. |
| 13 | `python m3_adk_multiagents/adk_demos/a2a_13_streaming.py --seller-url …/a2a/seller_agent` | `message/stream` over SSE — task lifecycle events arrive in real time. |
| 14 | `python m3_adk_multiagents/a2a_14_orchestrated_negotiation.py` | Full **buyer ↔ seller multi-round negotiation** over A2A — Agent Card discovery + threaded `message/send`. |

**Negotiation agents — interactive Web UI** (`adk web m3_adk_multiagents/negotiation_agents/`)

| Pick from dropdown | What it means (one line) |
|---|---|
| `buyer_agent` | `LlmAgent` + pricing `MCPToolset`; `before_tool_callback` enforces allowlist (cannot see seller's floor). |
| `seller_agent` | `LlmAgent` + **two** `MCPToolset`s (pricing + inventory) — has private access to `get_minimum_acceptable_price`. |
| `negotiation` | `LoopAgent` wrapping `SequentialAgent(buyer → seller)` — agreement detected via a structured `submit_decision` tool, not free text. |

---

## Architecture Deep Dive

### ADK + A2A Flow

```
adk web --a2a m3_adk_multiagents/negotiation_agents/
    │
    ├── buyer_agent (negotiation_agents/buyer_agent/agent.py)
    │     ├── root_agent = LlmAgent(model=AGENT_MODEL)  # default: openai/gpt-4o
    │     └── MCPToolset → m2_mcp/pricing_server.py
    │
    ├── seller_agent (negotiation_agents/seller_agent/agent.py)
    │     ├── root_agent = LlmAgent(model=AGENT_MODEL)  # default: openai/gpt-4o
    │     ├── MCPToolset → m2_mcp/pricing_server.py
    │     └── MCPToolset → m2_mcp/inventory_server.py (seller ONLY)
    │
    └── negotiation (negotiation_agents/negotiation/agent.py)
          └── root_agent = LoopAgent(sub_agents=[SequentialAgent(buyer, seller)])

A2A endpoints (auto-generated):
  GET /buyer_agent/.well-known/agent-card.json
  POST /buyer_agent                              (message/send)
  GET /seller_agent/.well-known/agent-card.json
  POST /seller_agent
```

### MCP Data Flow

```
BUYER AGENT                     MCP Protocol                PRICING SERVER
──────────────────────          ─────────────────────       ──────────────────
"I need market data"
await call_tool(
  "get_market_price",    ──►   tools/call request    ──►   Executes Python fn
  {"address": "742..."}) ◄──   CallToolResult        ◄──   Returns dict
"Comps avg $462K,
 listing is 4.9% above
 market. I'll offer
 $425K."
```

### A2A Message Exchange

```
Round 1: BUYER  ──[OFFER: $425,000]──────────────────────────────► SELLER
Round 1: BUYER ◄──[COUNTER_OFFER: $477,000]───────────────────── SELLER
Round 2: BUYER  ──[OFFER: $438,000]──────────────────────────────► SELLER
Round 2: BUYER ◄──[COUNTER_OFFER: $465,000]───────────────────── SELLER
Round 3: BUYER  ──[OFFER: $449,000]──────────────────────────────► SELLER
Round 3: BUYER ◄──[ACCEPT: $449,000]──────────────────────────── SELLER
                   ✅ DEAL REACHED at $449,000
                   (Buyer saved $36,000 from listing price)
```

---

## Workshop Schedule (4 Hours)

The full 97-slide deck ships as a PDF in the repo root.

| Time | Module | Topic | Key Files |
|---|---|---|---|
| 0:00–0:15 | Intro | What we're building | `README.md` |
| 0:15–0:45 | M1 | Why naive agents break + FSM fix | `m1_baseline/` |
| 0:45–1:30 | M2 | MCP with GitHub | `m2_mcp/github_agent_client.py` |
| 1:30–2:15 | M2 | MCP deep dive: protocol, primitives, transports, custom servers | `m2_mcp/notes/mcp_deep_dive.md`, `m2_mcp/pricing_server.py` |
| 2:15–3:00 | M3 | Google ADK deep dive: LlmAgent, workflow agents, sessions, callbacks | `adk web m3_adk_multiagents/adk_demos/` |
| 3:00–3:50 | M3 | A2A protocol: Agent Card, JSON-RPC, task lifecycle | `adk web --a2a m3_adk_multiagents/negotiation_agents/` |
| 3:50–4:00 | Wrap | Q&A + preview of follow-up exercise session | `m2_mcp/exercises/`, `m3_adk_multiagents/exercises/` |

---

## Running the MCP Servers Manually

### Inspect Available Tools

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def inspect_server(script: str):
    params = StdioServerParameters(command="python", args=[script])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            tools = await session.list_tools()
            for t in tools.tools:
                print(f"  • {t.name}: {t.description[:60]}")

asyncio.run(inspect_server("m2_mcp/pricing_server.py"))
asyncio.run(inspect_server("m2_mcp/inventory_server.py"))
```

### SSE Mode (Multiple Clients)

```bash
# Terminal 1 — start servers
python m2_mcp/pricing_server.py --sse --port 8001
python m2_mcp/inventory_server.py --sse --port 8002

# Terminal 2 — connect to SSE server
python -c "
import asyncio
from mcp.client.sse import sse_client
from mcp import ClientSession
async def test():
    async with sse_client('http://localhost:8001/sse') as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            result = await s.call_tool('get_market_price', {'address': '742 Evergreen Terrace, Austin, TX 78701'})
            print(result.content[0].text[:200])
asyncio.run(test())
"
```

---

## Customization Guide

### Change the Property

Edit these values in `m3_adk_multiagents/negotiation_agents/buyer_agent/agent.py` and `seller_agent/agent.py`:

```python
PROPERTY_ADDRESS = "1234 Oak Street, Dallas, TX 75201"
LISTING_PRICE = 520_000
BUYER_BUDGET = 495_000
MINIMUM_PRICE = 475_000
```

Add the property to `m2_mcp/pricing_server.py`'s `PROPERTY_DATABASE`.

### Add a New MCP Tool

In `m2_mcp/pricing_server.py`:

```python
@mcp.tool()
def get_neighborhood_score(zip_code: str) -> dict:
    """Get neighborhood safety and amenity score."""
    return {
        "zip_code": zip_code,
        "safety_score": 8.2,
        "walkability": 7.5,
        "school_rating": 8.0,
    }
```

### Change Negotiation Strategy

In `m3_adk_multiagents/negotiation_agents/buyer_agent/agent.py`, modify the `instruction` string:

```python
# Change from "start 12% below asking" to "start 8% below"
# Or add: "Always ask for seller to cover closing costs"
```

### Add a Mediator Agent

Use ADK's workflow agents — wrap buyer, mediator, and seller as `sub_agents` of a `SequentialAgent` (or a custom routing agent) and orchestrate over A2A.

---

## Key Files Reference

| File | Key Element | What It Does |
|---|---|---|
| `m2_mcp/pricing_server.py` | `get_market_price`, `calculate_discount` | MCP pricing tools |
| `m2_mcp/inventory_server.py` | `get_inventory_level`, `get_minimum_acceptable_price` | MCP inventory tools |
| `m3_adk_multiagents/negotiation_agents/buyer_agent/agent.py` | `root_agent = LlmAgent(...)` | Buyer agent with MCPToolset |
| `m3_adk_multiagents/negotiation_agents/seller_agent/agent.py` | `root_agent = LlmAgent(...)` | Seller agent with dual MCPToolsets |
| `m3_adk_multiagents/negotiation_agents/negotiation/agent.py` | `root_agent = LoopAgent(...)` | LoopAgent + SequentialAgent + MCP tools + submit_decision |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'mcp'`**
```bash
pip install mcp
```

**`AuthenticationError` from OpenAI**
```bash
export OPENAI_API_KEY=sk-your-actual-key
```

**`AuthenticationError` / provider auth failure in ADK runs**
```bash
export OPENAI_API_KEY=sk-your-actual-key
```

**`FileNotFoundError` running MCP servers**
```bash
# Run from the real-estate-negotiation-simulator/ directory
cd real-estate-negotiation-simulator
python m2_mcp/pricing_server.py  # Not: python real-estate-negotiation-simulator/m2_mcp/pricing_server.py
```

**GitHub MCP demo fails with `command not found: npx`**
```bash
# Install Node.js from: https://nodejs.org
node --version && npx --version
```

**PowerShell `UnauthorizedAccess` error activating venv**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\.venv\Scripts\Activate.ps1
```

**Unicode / encoding errors on Windows (`UnicodeEncodeError`, garbled output)**
```powershell
# Set UTF-8 mode before running any script
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
adk web m3_adk_multiagents/negotiation_agents/
```
Or add `PYTHONUTF8=1` to your `.env` file to make it permanent.

---

*Built for the AI Agent Systems Workshop — teaching MCP, A2A, and Google ADK through a real estate negotiation simulator.*

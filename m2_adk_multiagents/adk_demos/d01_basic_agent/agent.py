"""
Demo 01 — Basic LlmAgent
==========================
The simplest ADK agent: one LlmAgent with one function tool.
No MCP, no orchestration — just an agent that can call a tool.

ADK CONCEPTS:
  - LlmAgent: the core building block
  - Function tools: plain Python functions the LLM can call
  - root_agent: the variable adk web discovers

Run:
    adk web m2_adk_multiagents/adk_demos/d01_basic_agent/
"""

import os

from google.adk.agents import LlmAgent

# ── Load API keys (env > .env > Keychain) — shared bootstrap; see repo-root load_env.py ──
# adk web imports each agent module directly, so each agent loads keys for
# itself (the M2 counterpart to M1's per-script loading). Walk up to the repo
# root to find load_env.py regardless of how deeply this agent is nested.
import sys as _sys
from pathlib import Path as _Path
for _root in _Path(__file__).resolve().parents:
    if (_root / "load_env.py").exists():
        _sys.path.insert(0, str(_root))
        import load_env  # noqa: F401  (side-effect resolves OPENAI_API_KEY)
        break

MODEL = os.environ.get("AGENT_MODEL", "openai/gpt-4o")


def get_quick_estimate(address: str) -> dict:
    """Return a rough market estimate for a property address."""
    estimates = {
        "742 Evergreen Terrace": {"estimate_usd": 462_000, "confidence": "high"},
        "123 Main St": {"estimate_usd": 380_000, "confidence": "medium"},
    }
    for key, value in estimates.items():
        if key.lower() in address.lower():
            return {"address": address, **value}
    return {"address": address, "estimate_usd": 450_000, "confidence": "low"}


root_agent = LlmAgent(
    name="basic_agent",
    model=MODEL,
    description="A simple real estate assistant that estimates property values.",
    instruction=(
        "You are a helpful real estate assistant. When asked about a property, "
        "use the get_quick_estimate tool to look up its value, then give a "
        "brief summary including the estimate and confidence level."
    ),
    tools=[get_quick_estimate],
)

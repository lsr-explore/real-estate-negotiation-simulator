"""
Demo 03 — Sessions and State
==============================
LlmAgent that uses ToolContext to read/write session state across turns.
State persists within a session, letting the agent remember offer history.

ADK CONCEPTS:
  - ToolContext: injected into tools automatically by ADK
  - State scoping: "user:" prefix persists across sessions for the same user
  - Session state: tools can read/write shared state that the agent sees

Run:
    adk web m2_adk_multiagents/adk_demos/d03_sessions_state/
"""

import os

from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext


def record_offer(price: int, tool_context: ToolContext) -> dict:
    """Record the user's latest offer price in session state."""
    history = tool_context.state.get("offer_history", [])
    history.append(price)
    tool_context.state["offer_history"] = history
    tool_context.state["user:total_offers"] = len(history)
    return {
        "recorded_price": price,
        "total_offers": len(history),
        "all_offers": history,
    }


def get_offer_history(tool_context: ToolContext) -> dict:
    """Retrieve the full history of offers made in this session."""
    history = tool_context.state.get("offer_history", [])
    total = tool_context.state.get("user:total_offers", 0)
    return {"offers": history, "total_across_sessions": total}


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

root_agent = LlmAgent(
    name="stateful_agent",
    model=MODEL,
    description="Real estate agent that remembers offer history across turns.",
    instruction=(
        "You help users negotiate on 742 Evergreen Terrace (listed $485,000).\n\n"
        "When the user proposes an offer:\n"
        "  1. Call record_offer with their price\n"
        "  2. Review the offer history\n"
        "  3. Advise whether to hold firm, go higher, or walk away\n\n"
        "When the user asks about past offers, call get_offer_history.\n"
        "Use the history to give strategic advice."
    ),
    tools=[record_offer, get_offer_history],
)

"""
Demo 04 — SequentialAgent
==========================
Three sub-agents chained in declaration order.  Each writes to session
state via output_key; the next agent reads it via {placeholder} syntax.

Pipeline:  market_brief  →  offer_drafter  →  message_polisher

ADK CONCEPTS:
  - SequentialAgent: runs children in order, stops when the last finishes
  - output_key: each agent writes its output to a named state key
  - {state_key} in instructions: agents read prior outputs from state

Run:
    adk web m2_adk_multiagents/adk_demos/d04_sequential/
"""

from google.adk.agents import LlmAgent, SequentialAgent

import os

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

market_brief = LlmAgent(
    name="market_brief",
    model=MODEL,
    instruction=(
        "Write a 2-line market summary for the Austin 78701 ZIP. "
        "Include median price and days-on-market. Be concrete."
    ),
    output_key="market_summary",
)

offer_drafter = LlmAgent(
    name="offer_drafter",
    model=MODEL,
    instruction=(
        "Read {market_summary} and draft a one-line opening buyer offer "
        "for 742 Evergreen Terrace listed at $485k. Output ONLY the offer text."
    ),
    output_key="offer_text",
)

polisher = LlmAgent(
    name="message_polisher",
    model=MODEL,
    instruction=(
        "Polish {offer_text} into a professional one-paragraph email body "
        "suitable to send to the listing agent."
    ),
    output_key="final_email",
)

root_agent = SequentialAgent(
    name="negotiation_pipeline",
    description="Three-stage pipeline: research → draft → polish.",
    sub_agents=[market_brief, offer_drafter, polisher],
)

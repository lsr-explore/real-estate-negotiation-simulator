"""
Demo 02 — MCP Tools in ADK
============================
LlmAgent with MCPToolset auto-discovering tools from the pricing MCP server.
ADK spawns the MCP server as a subprocess, discovers tools via the MCP
protocol, and makes them available to the LLM as function-calling tools.

ADK CONCEPTS:
  - MCPToolset: connects to an MCP server and discovers tools automatically
  - StdioConnectionParams: tells ADK how to spawn the MCP server
  - The LLM sees MCP tools exactly like local function tools

Run:
    adk web m2_adk_multiagents/adk_demos/d02_mcp_tools/
"""

import os
import sys
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

_PRICING_SERVER = str(
    Path(__file__).resolve().parents[3] / "m1_mcp" / "pricing_server.py"
)

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
    name="mcp_tools_agent",
    model=MODEL,
    description="Real estate pricing agent with MCP-discovered tools.",
    instruction=(
        "You are a real estate pricing analyst for Austin, TX.\n\n"
        "You have MCP tools that were auto-discovered from a pricing server. "
        "You don't need to know their names in advance — ADK discovered them "
        "for you at startup via the MCP protocol.\n\n"
        "Always call your available tools before giving any estimates. "
        "Reference the tool results in your response."
    ),
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=[_PRICING_SERVER],
                )
            )
        )
    ],
)

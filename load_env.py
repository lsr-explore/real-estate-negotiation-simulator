"""load_env.py — load API keys for the ADK (M2) agents.

This is the M2 counterpart to the inline key-loading block in the M1 client
scripts (``m1_mcp/sse_agent_client.py``). M1 has a single entry point per script,
so it loads keys there. ``adk web`` instead imports each agent module directly,
so the agents share this bootstrap: importing it runs the SAME resolution M1
uses — **env var > .env > Keychain**:

    1. a real shell env var always wins
    2. then a ``.env`` file at the repo root
    3. then the macOS Keychain via ``get_secret.py``

The Keychain account is ``MY_OPENAI_API_KEY`` and the service is whatever
``get_secret.DEFAULT_SERVICE`` is set to (currently ``"veloce"``) — same as M1.

THE ONE DIFFERENCE FROM M1: the M1 clients call the OpenAI SDK directly and pass
``api_key=MY_OPENAI_API_KEY`` explicitly, so the variable name is free. The M2
agents run their ``openai/...`` models through LiteLLM, which authenticates by
reading the ``OPENAI_API_KEY`` env var *by name*. So after resolving the key we
also mirror its value into ``OPENAI_API_KEY`` so the agents authenticate.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent

# Keychain account name (matches M1). Its value is mirrored into OPENAI_API_KEY
# below, because that is the env var LiteLLM/OpenAI read.
_KEY_ACCOUNT = "MY_OPENAI_API_KEY"


def _load_env_file_if_present(env_path: Path) -> None:
    """Load KEY=VALUE pairs from a .env file. Existing env vars take priority.

    Mirrors ``_load_env_file_if_present`` in the M1 client scripts.
    """
    if not env_path.exists():
        return
    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except OSError:
        pass


# 1) .env at the repo root (env vars already set still win — see the guard above).
_load_env_file_if_present(_REPO_ROOT / ".env")

# 2) Keychain fallback for any key still unset (env > .env > Keychain). The
#    service is inherited from get_secret.DEFAULT_SERVICE ("veloce"), matching M1.
sys.path.insert(0, str(_REPO_ROOT))
try:
    from get_secret import load_secrets_into_env

    load_secrets_into_env(_KEY_ACCOUNT)
except ImportError:
    pass  # Keychain helper is optional; .env still works.

# 3) Mirror the resolved value into OPENAI_API_KEY for LiteLLM. A real
#    OPENAI_API_KEY already in the environment is left untouched (setdefault).
_key = os.environ.get(_KEY_ACCOUNT, "").strip()
if _key and not _key.startswith("sk-your"):
    os.environ.setdefault("OPENAI_API_KEY", _key)

# Surface a clear, early warning instead of a cryptic auth error at call time.
if not os.environ.get("OPENAI_API_KEY", "").strip():
    print(
        "WARNING [load_env]: OPENAI_API_KEY is unresolved (checked env > .env > "
        f"Keychain). Store the key with:\n"
        f"    security add-generic-password -s veloce -a {_KEY_ACCOUNT} -w",
        file=sys.stderr,
    )

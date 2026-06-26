# Troubleshooting — A2A / `adk web --a2a`

## Symptom 1: client gets `404` on the agent card

```
httpx.HTTPStatusError: Client error '404 Not Found' for url
  'http://127.0.0.1:8000/a2a/buyer_agent/.well-known/agent-card.json'
```

**Cause:** the server was started *without* `--a2a`, so the `/a2a/...` routes
don't exist. (A 404 means a server is up but the route is missing; a *connection
refused* would mean nothing is listening.)

**Fix:** restart the server with the flag:

```bash
adk web --a2a m2_adk_multiagents/negotiation_agents/
```

Verify before running a client (expect `200`, not `404`):

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:8000/a2a/buyer_agent/.well-known/agent-card.json
```

---

## Symptom 2: `--a2a` startup logs `Failed to setup A2A agent ... 'json'`

```
ERROR - fast_api.py:739 - Failed to setup A2A agent buyer_agent:
  cannot access local variable 'json' where it is not associated with a value
```

…repeated for every agent, and the `/a2a/...` card routes return 404 (→ Symptom 1).

**Cause:** a bug in **google-adk 2.3.0**. In `get_fast_api_app()` the A2A card is
loaded with `json.load(f)`, but the same function has a redundant nested
`import json` further down (in the unrelated `gemini_enterprise` block). That
nested import makes `json` a *function-local* name for the whole function, so the
earlier `json.load` raises `UnboundLocalError`. Classic Python local-shadowing.

**Fix:** delete the redundant nested import in the installed library:

- File: `.venv/lib/python3.12/site-packages/google/adk/cli/fast_api.py`
- Remove the line `    import json` (~line 749, inside `get_fast_api_app`, just
  after `import inspect`). The module-level `import json` at line 19 is all that's
  needed.

One-liner to locate it:

```bash
grep -n "import json" \
  "$(.venv/bin/python -c 'import google.adk.cli.fast_api as m; print(m.__file__)')"
# keep line 19 (module level); delete the second one inside the function
```

Restart `adk web --a2a` — you should now see `Successfully configured A2A agent:`
for each agent instead of the error.

### ⚠️ This patch is not durable

It edits an installed package inside `.venv`, so it is **lost** on any of:
`pip install --force-reinstall`, a venv rebuild, or a `google-adk` upgrade. It is
also local to this machine — a fresh clone hits the same bug. If A2A breaks again
after touching the venv, re-apply this note.

Durable options (not yet done):
- Pin a known-good `google-adk` in `requirements.txt` once one is identified
  (2.3.0 is affected).
- Report upstream to the google-adk repo (it's a genuine bug in their code).

---

## Where the key comes from (for reference)

The A2A *agents* (served in terminal 1) need an OpenAI key; the *client script*
(terminal 2) does not — it only speaks A2A over HTTP. Each agent auto-loads the
key on import via the repo-root `load_env.py` (env > `.env` > Keychain; Keychain
account `MY_OPENAI_API_KEY`, service `veloce`). If terminal 1 starts clean, the
key resolved fine.

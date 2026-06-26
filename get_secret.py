"""get_secret.py — read API keys from the macOS Keychain via the `security` CLI.

Adapted from the shared dev-toolkit snippet (scripts/keychain/get_secret.py).

Zero dependencies: shells out to the built-in `security` CLI (macOS only). The
convention is a single flat keyring — service ``lsr-dev-keys``, one account per
key name (e.g. ``MY_OPENAI_API_KEY``).

Store a key once:

    security add-generic-password -s veloce -a MY_OPENAI_API_KEY -w

Use as a library:

    from get_secret import get_secret
    key = get_secret("MY_OPENAI_API_KEY")

Or backfill ``os.environ`` for any keys not already supplied via the shell or a
``.env`` file (precedence: real env var > .env > Keychain):

    from get_secret import load_secrets_into_env
    load_secrets_into_env("MY_OPENAI_API_KEY", "GITHUB_TOKEN")

CLI:

    python get_secret.py MY_OPENAI_API_KEY [service]
"""

from __future__ import annotations

import os
import subprocess
import sys

DEFAULT_SERVICE = "veloce"

# Treat these as "not really set" so a copied-but-unedited .env doesn't shadow
# a real value stored in the Keychain. Matches the placeholders in .env.example.
PLACEHOLDER_PREFIXES = ("sk-your", "ghp_your", "your_", "your-", "<your")


def get_secret(account: str, service: str = DEFAULT_SERVICE) -> str:
    """Return the secret stored under (service, account), or raise if missing.

    Args:
        account: the key name, e.g. ``"MY_OPENAI_API_KEY"``.
        service: the keyring service; defaults to ``"veloce"``.

    Raises:
        KeyError: if the secret is absent, or the `security` CLI is unavailable
            (e.g. running off macOS). Callers that want a soft failure should
            use :func:`try_get_secret` instead.
    """
    try:
        out = subprocess.check_output(
            ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        raise KeyError(
            f"Keychain secret not found: service={service!r} account={account!r}. "
            f"Store it with: security add-generic-password -s {service} -a {account} -w"
        ) from exc
    except (FileNotFoundError, OSError) as exc:
        # `security` only exists on macOS — treat absence as "no secret".
        raise KeyError(
            f"`security` CLI unavailable; cannot read Keychain secret {account!r}."
        ) from exc
    # `-w` prints the password followed by a trailing newline.
    return out.rstrip("\n")


def try_get_secret(account: str, service: str = DEFAULT_SERVICE) -> str | None:
    """Like :func:`get_secret` but returns ``None`` instead of raising when absent."""
    try:
        return get_secret(account, service)
    except KeyError:
        return None


def _is_placeholder(value: str) -> bool:
    low = value.lower()
    return any(low.startswith(p) for p in PLACEHOLDER_PREFIXES)


def load_secrets_into_env(
    *accounts: str, service: str = DEFAULT_SERVICE
) -> list[str]:
    """Backfill ``os.environ`` from the Keychain for any keys not already set.

    A key is only fetched from the Keychain when the existing environment value
    is empty or an obvious placeholder, so a real value passed via the shell or
    a ``.env`` file always wins (precedence: env var > .env > Keychain).

    Returns the list of account names that were populated from the Keychain.
    """
    loaded: list[str] = []
    for account in accounts:
        current = os.environ.get(account, "").strip()
        if current and not _is_placeholder(current):
            continue  # already have a real value from the shell or .env
        value = try_get_secret(account, service)
        if value:
            os.environ[account] = value
            loaded.append(account)
    return loaded


if __name__ == "__main__":
    cli_args = sys.argv[1:]
    if not cli_args:
        print("usage: get_secret.py <ACCOUNT> [service]", file=sys.stderr)
        sys.exit(2)
    account_arg = cli_args[0]
    service_arg = cli_args[1] if len(cli_args) > 1 else DEFAULT_SERVICE
    try:
        sys.stdout.write(get_secret(account_arg, service_arg))
    except KeyError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

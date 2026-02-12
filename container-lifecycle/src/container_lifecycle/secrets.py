"""Secret resolution via 1Password Service Account or plaintext files.

Two strategies:
1. 1Password — when a Service Account token is available, resolve op:// URIs
   from .env.secrets.tpl via ``op read``. The SA token is passed via environment
   variable (not CLI args) to avoid ``ps`` exposure.
2. Plaintext files — legacy fallback, reads individual files from secrets_dir.

The host resolves secrets; containers never see the SA token or ``op`` CLI.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .config import settings
from .log import get_logger

log = get_logger()


def get_sa_token() -> str | None:
    """Return the 1Password Service Account token, or None."""
    token = os.environ.get("OP_SERVICE_ACCOUNT_TOKEN")
    if token:
        return token

    token_file = settings.op_sa_token_file
    try:
        return token_file.read_text().strip() or None
    except (FileNotFoundError, PermissionError):
        return None


def has_op_integration() -> bool:
    """Check whether 1Password integration is configured."""
    return get_sa_token() is not None


def parse_template(path: Path) -> dict[str, str]:
    """Parse a .env.secrets.tpl file into {NAME: "op://..."} pairs.

    Ignores blank lines and comments (lines starting with #).
    """
    entries: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if key and value:
            entries[key] = value
    return entries


def _op_read(uri: str, sa_token: str) -> str:
    """Resolve a single op:// URI via the ``op read`` CLI.

    The SA token is injected via the process environment to avoid leaking
    it through ``/proc`` or ``ps`` output.
    """
    env = {**os.environ, "OP_SERVICE_ACCOUNT_TOKEN": sa_token}
    result = subprocess.run(
        ["op", "read", uri],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"op read failed for {uri}: {stderr}")
    return result.stdout.strip()


def resolve_from_op(sa_token: str) -> dict[str, str]:
    """Resolve all template entries via 1Password. Fail-closed on any error."""
    template_path = settings.secrets_template
    if template_path is None:
        log.warning("secrets.no_template", metadata={"reason": "No .env.secrets.tpl found"})
        return {}

    entries = parse_template(template_path)
    if not entries:
        log.info("secrets.template_empty", metadata={"path": str(template_path)})
        return {}

    resolved: dict[str, str] = {}
    for name, uri in entries.items():
        if not uri.startswith("op://"):
            log.warning(
                "secrets.skip_non_op_uri",
                metadata={"name": name, "uri": uri},
            )
            continue
        try:
            resolved[name] = _op_read(uri, sa_token)
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            log.error(
                "secrets.op_read_failed",
                metadata={"name": name, "uri": uri, "error": str(exc)},
            )
            raise RuntimeError(
                f"Failed to resolve secret '{name}' from 1Password. "
                "Aborting — fix the template or remove the SA token to fall back to plaintext files."
            ) from exc

    log.info(
        "secrets.resolved_from_op",
        metadata={"count": len(resolved), "template": str(template_path)},
    )
    return resolved


def resolve_from_files() -> dict[str, str]:
    """Read secrets from plaintext files in secrets_dir (legacy fallback)."""
    secrets_dir = settings.secrets_dir
    resolved: dict[str, str] = {}
    try:
        for f in secrets_dir.iterdir():
            if f.is_file():
                resolved[f.name] = f.read_text().strip()
    except FileNotFoundError:
        pass

    log.info("secrets.resolved_from_files", metadata={"count": len(resolved)})
    return resolved


def resolve_secrets() -> dict[str, str]:
    """Resolve secrets using the best available strategy.

    Prefers 1Password when a Service Account token is configured,
    otherwise falls back to plaintext files.
    """
    sa_token = get_sa_token()
    if sa_token:
        return resolve_from_op(sa_token)
    return resolve_from_files()

#!/bin/bash
# Qdrant WebSearch auto-storage hook for Reflex
# Called by Claude Code PostToolUse hook
# Automatically stores WebSearch results in Qdrant when available

set -euo pipefail

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check toggle (default: enabled)
if [ "${REFLEX_QDRANT_AUTOSAVE:-true}" = "false" ]; then
    exit 0
fi

# Read tool data from stdin (JSON from Claude Code hook)
TOOL_DATA=$(cat)

# Extract tool name
TOOL_NAME=$(echo "$TOOL_DATA" | jq -r '.tool_name // empty' 2>/dev/null || echo "")

# Filter for WebSearch only
if [ "$TOOL_NAME" != "WebSearch" ]; then
    exit 0
fi

# Delegate to Python (fail silently on error)
uvx --quiet --python 3.12 --with qdrant-client --with fastembed \
    python "$SCRIPT_DIR/qdrant-websearch-store.py" <<< "$TOOL_DATA" 2>/dev/null || true

exit 0

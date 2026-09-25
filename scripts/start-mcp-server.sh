#!/bin/bash
# Start AbletonBridge MCP server in SSE mode (multi-client).
# Multiple Claude sessions can connect to http://localhost:9883/sse
#
# Usage: ./start-mcp-server.sh [port]
#   port defaults to 9883

set -euo pipefail

export ABLETON_BRIDGE_TRANSPORT="sse"
export ABLETON_BRIDGE_MCP_PORT="${1:-9883}"

cd "$(dirname "$0")/.."
exec uv run ableton-bridge

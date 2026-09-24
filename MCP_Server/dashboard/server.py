"""Web status dashboard HTTP server for AbletonBridge.

Provides a lightweight Starlette/Uvicorn HTTP server that serves the
real-time status dashboard and a JSON API endpoint.  All mutable state
is accessed via ``MCP_Server.state``.
"""

import logging
import time
import threading
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

import MCP_Server.state as state
from MCP_Server.dashboard.html import DASHBOARD_HTML

logger = logging.getLogger("AbletonBridge")


# ---------------------------------------------------------------------------
# Dashboard log handler
# ---------------------------------------------------------------------------

class DashboardLogHandler(logging.Handler):
    """Captures log records into the dashboard ring buffer.

    Stores lightweight tuples (created_float, level_str, message_str) to
    avoid formatting timestamps on every log message.  Timestamps are
    formatted only when the dashboard is actually viewed.
    """

    def emit(self, record):
        try:
            with state.server_log_lock:
                state.server_log_buffer.append(
                    (record.created, record.levelname, record.getMessage())
                )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Helper: summarize tool arguments for the dashboard log
# ---------------------------------------------------------------------------

def summarize_args(args: dict) -> str:
    """Create a short summary of tool arguments for the dashboard log."""
    if not args:
        return ""
    parts = []
    for k, v in list(args.items())[:3]:
        sv = str(v)
        if len(sv) > 40:
            sv = sv[:37] + "..."
        parts.append(f"{k}={sv}")
    suffix = f" +{len(args)-3} more" if len(args) > 3 else ""
    return ", ".join(parts) + suffix


# ---------------------------------------------------------------------------
# Status data helpers
# ---------------------------------------------------------------------------

def get_server_version() -> str:
    """Get server version from package metadata, with fallback."""
    try:
        from importlib.metadata import version as _pkg_version
        return _pkg_version("ableton-bridge")
    except Exception:
        from MCP_Server import __version__
        return __version__


def get_m4l_status() -> tuple:
    """Return (sockets_ready, bridge_responding) with cached ping."""
    sockets_ready = bool(state.m4l_connection and state.m4l_connection._connected)
    if not sockets_ready:
        return False, False

    now = time.time()
    if now - state.m4l_ping_cache["timestamp"] < state.M4L_PING_CACHE_TTL:
        return sockets_ready, state.m4l_ping_cache["result"]

    try:
        assert state.m4l_connection is not None
        result = state.m4l_connection.ping()
    except Exception as e:
        logger.debug("Dashboard M4L ping failed: %s", e)
        result = False

    state.m4l_ping_cache["result"] = result
    state.m4l_ping_cache["timestamp"] = now
    return sockets_ready, result


def build_status_json() -> dict:
    """Collect all dashboard status data into a JSON-serializable dict."""
    ableton_connected = False
    if state.ableton_connection and state.ableton_connection.sock:
        try:
            state.ableton_connection.sock.getpeername()
            ableton_connected = True
        except Exception:
            pass

    m4l_sockets_ready, m4l_connected = get_m4l_status()

    with state.tool_call_lock:
        recent = list(state.tool_call_log)
        total = sum(state.tool_call_counts.values())
        top_tools = sorted(state.tool_call_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    with state.server_log_lock:
        # Format timestamps from stored tuples (created_float, level, msg)
        server_logs = [
            {"ts": datetime.fromtimestamp(ts).strftime("%H:%M:%S"), "level": lvl, "msg": msg}
            for ts, lvl, msg in state.server_log_buffer
        ]

    # Dynamic tool count via the mcp instance stored in state
    mcp = state.mcp_instance
    tool_count = len(mcp._tool_manager._tools) if mcp and hasattr(mcp, '_tool_manager') else 331

    return {
        "version": get_server_version(),
        "uptime_seconds": round(time.time() - state.server_start_time, 1) if state.server_start_time else 0,
        "ableton_connected": ableton_connected,
        "m4l_connected": m4l_connected,
        "m4l_sockets_ready": m4l_sockets_ready,
        "store_counts": {
            "snapshots": len(state.snapshot_store),
            "macros": len(state.macro_store),
            "param_maps": len(state.param_map_store),
        },
        "total_tool_calls": total,
        "top_tools": top_tools,
        "recent_calls": recent,
        "server_logs": server_logs,
        "tool_count": tool_count,
    }


# ---------------------------------------------------------------------------
# Dashboard HTTP server lifecycle
# ---------------------------------------------------------------------------

def _do_reload_remote_script() -> dict:
    """Run deploy + send _reload_handlers to the Remote Script (sync)."""
    import subprocess
    import os

    script_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "scripts", "deploy-remote-script.sh"
    )
    script_path = os.path.normpath(script_path)

    # Step 1: Deploy
    try:
        deploy_result = subprocess.run(
            ["bash", script_path],
            capture_output=True, text=True, timeout=10,
        )
        if deploy_result.returncode != 0:
            return {"status": "error", "message": f"Deploy failed: {deploy_result.stderr.strip()}"}
        deploy_msg = deploy_result.stdout.strip()
    except Exception as e:
        return {"status": "error", "message": f"Deploy error: {e}"}

    # Step 2: Send _reload_handlers over TCP
    try:
        from MCP_Server.connections.ableton import get_ableton_connection
        ableton = get_ableton_connection()
        result = ableton.send_command("_reload_handlers", timeout=5.0)
        count = result.get("command_count", "?")
        return {
            "status": "ok",
            "message": f"Deployed and reloaded: {count} commands registered",
            "command_count": count,
            "deploy_output": deploy_msg,
        }
    except Exception as e:
        return {
            "status": "partial",
            "message": f"Deployed but reload failed (toggle off/on instead): {e}",
            "deploy_output": deploy_msg,
        }


def start_dashboard_server():
    """Start the dashboard HTTP server on a background thread."""
    from starlette.applications import Starlette
    from starlette.responses import HTMLResponse, JSONResponse
    from starlette.routing import Route
    import uvicorn

    async def dashboard_page(request):
        return HTMLResponse(DASHBOARD_HTML)

    async def api_status(request):
        return JSONResponse(build_status_json())

    async def api_reload_remote_script(request):
        import asyncio
        result = await asyncio.to_thread(_do_reload_remote_script)
        return JSONResponse(result)

    app = Starlette(routes=[
        Route("/", dashboard_page),
        Route("/api/status", api_status),
        Route("/api/reload-remote-script", api_reload_remote_script, methods=["POST"]),
    ])

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=state.DASHBOARD_PORT,
        log_level="warning",
        access_log=False,
    )
    state.dashboard_server = uvicorn.Server(config)

    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        assert state.dashboard_server is not None
        loop.run_until_complete(state.dashboard_server.serve())

    thread = threading.Thread(target=_run, daemon=True, name="dashboard-http")
    thread.start()
    logger.info("Dashboard started at http://127.0.0.1:%d", state.DASHBOARD_PORT)

    import webbrowser
    webbrowser.open(f"http://127.0.0.1:{state.DASHBOARD_PORT}")


def stop_dashboard_server():
    """Signal the dashboard server to shut down."""
    if state.dashboard_server:
        state.dashboard_server.should_exit = True
        state.dashboard_server = None
        logger.info("Dashboard server stopped")

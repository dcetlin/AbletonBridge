"""M4LConnection — UDP connection to the Max for Live bridge device."""

import socket
import json
import logging
import time
import threading
import uuid
import base64
import binascii
import struct
from dataclasses import dataclass, field
from typing import Dict, Any, List

from typing import Callable, NamedTuple

import MCP_Server.state as state

logger = logging.getLogger("AbletonBridge")


class _OscSpec(NamedTuple):
    address: str
    args: list  # list of (osc_type, param_key) or (osc_type, param_key, default)
    json_encode: str | None = None


_OSC_DISPATCH: dict[str, _OscSpec] = {
    "ping":                    _OscSpec("/ping", []),
    "discover_params":         _OscSpec("/discover_params", [("i", "track_index"), ("i", "device_index")]),
    "get_hidden_params":       _OscSpec("/get_hidden_params", [("i", "track_index"), ("i", "device_index")]),
    "set_hidden_param":        _OscSpec("/set_hidden_param", [("i", "track_index"), ("i", "device_index"), ("i", "parameter_index"), ("f", "value")]),
    "get_device_property":     _OscSpec("/get_device_property", [("i", "track_index"), ("i", "device_index"), ("s", "property_name")]),
    "set_device_property":     _OscSpec("/set_device_property", [("i", "track_index"), ("i", "device_index"), ("s", "property_name"), ("f", "value")]),
    "batch_set_hidden_params": _OscSpec("/batch_set_hidden_params", [("i", "track_index"), ("i", "device_index"), ("s", "parameters")], json_encode="parameters"),
    "get_cue_points":          _OscSpec("/get_cue_points", []),
    "jump_to_cue_point":       _OscSpec("/jump_to_cue_point", [("i", "cue_point_index")]),
    "get_groove_pool":         _OscSpec("/get_groove_pool", []),
    "set_groove_properties":   _OscSpec("/set_groove_properties", [("i", "groove_index"), ("s", "properties")], json_encode="properties"),
    "observe_property":        _OscSpec("/observe_property", [("s", "lom_path"), ("s", "property_name")]),
    "stop_observing":          _OscSpec("/stop_observing", [("s", "lom_path"), ("s", "property_name")]),
    "get_observed_changes":    _OscSpec("/get_observed_changes", []),
    "set_param_clean":         _OscSpec("/set_param_clean", [("i", "track_index"), ("i", "device_index"), ("i", "parameter_index"), ("f", "value")]),
    "analyze_spectrum":        _OscSpec("/analyze_spectrum", []),
    "analyze_cross_track":     _OscSpec("/analyze_cross_track", [("i", "track_index", 0), ("i", "wait_ms", 500)]),
    "get_app_version":         _OscSpec("/get_app_version", []),
    "get_automation_states":   _OscSpec("/get_automation_states", [("i", "track_index"), ("i", "device_index")]),
    "discover_chains":         _OscSpec("/discover_chains", [("i", "track_index"), ("i", "device_index"), ("s", "extra_path", "")]),
    "get_chain_device_params": _OscSpec("/get_chain_device_params", [("i", "track_index"), ("i", "device_index"), ("i", "chain_index"), ("i", "chain_device_index")]),
    "set_chain_device_param":  _OscSpec("/set_chain_device_param", [("i", "track_index"), ("i", "device_index"), ("i", "chain_index"), ("i", "chain_device_index"), ("i", "parameter_index"), ("f", "value")]),
    "get_clip_notes_by_id":    _OscSpec("/get_clip_notes_by_id", [("i", "track_index"), ("i", "clip_index")]),
    "modify_clip_notes":       _OscSpec("/modify_clip_notes", [("i", "track_index"), ("i", "clip_index"), ("s", "modifications")], json_encode="modifications"),
    "remove_clip_notes_by_id": _OscSpec("/remove_clip_notes_by_id", [("i", "track_index"), ("i", "clip_index"), ("s", "note_ids")], json_encode="note_ids"),
    "get_chain_mixing":        _OscSpec("/get_chain_mixing", [("i", "track_index"), ("i", "device_index"), ("i", "chain_index")]),
    "set_chain_mixing":        _OscSpec("/set_chain_mixing", [("i", "track_index"), ("i", "device_index"), ("i", "chain_index"), ("s", "properties")], json_encode="properties"),
    "device_ab_compare":       _OscSpec("/device_ab_compare", [("i", "track_index"), ("i", "device_index"), ("s", "action")]),
    "clip_scrub":              _OscSpec("/clip_scrub", [("i", "track_index"), ("i", "clip_index"), ("s", "action"), ("f", "beat_time", 0.0)]),
    "get_split_stereo":        _OscSpec("/get_split_stereo", [("i", "track_index")]),
    "set_split_stereo":        _OscSpec("/set_split_stereo", [("i", "track_index"), ("f", "left"), ("f", "right")]),
    "rack_insert_chain":       _OscSpec("/rack_insert_chain", [("i", "track_index"), ("i", "device_index"), ("i", "chain_index", 0)]),
    "chain_insert_device_m4l": _OscSpec("/chain_insert_device_m4l", [("i", "track_index"), ("i", "device_index"), ("i", "chain_index"), ("s", "device_uri"), ("i", "target_index", 0)]),
    "set_drum_chain_note":     _OscSpec("/set_drum_chain_note", [("i", "track_index"), ("i", "device_index"), ("i", "chain_index"), ("i", "note")]),
    "get_take_lanes":          _OscSpec("/get_take_lanes", [("i", "track_index")]),
    "rack_store_variation":    _OscSpec("/rack_store_variation", [("i", "track_index"), ("i", "device_index")]),
    "rack_recall_variation":   _OscSpec("/rack_recall_variation", [("i", "track_index"), ("i", "device_index"), ("i", "variation_index")]),
    "create_arrangement_midi_clip_m4l":  _OscSpec("/create_arrangement_midi_clip_m4l", [("i", "track_index"), ("f", "time"), ("f", "length")]),
    "create_arrangement_audio_clip_m4l": _OscSpec("/create_arrangement_audio_clip_m4l", [("i", "track_index"), ("f", "time"), ("f", "length")]),
}


def _build_analyze_audio(conn: "M4LConnection", params: Dict[str, Any], request_id: str) -> bytes:
    track_index = params.get("track_index", -1) if params else -1
    return conn._build_osc_message("/analyze_audio", [("i", track_index), ("s", request_id)])


_SPECIAL_BUILDERS: dict[str, Callable[["M4LConnection", Dict[str, Any], str], bytes]] = {
    "analyze_audio": _build_analyze_audio,
}


@dataclass
class M4LConnection:
    """UDP connection to the Max for Live bridge device.

    The M4L bridge provides deep LOM access for hidden device parameters.
    Communication uses two UDP ports:
      - send_port (9878): MCP server -> M4L device (commands)
      - recv_port (9879): M4L device -> MCP server (responses)
    """
    send_host: str = "127.0.0.1"
    send_port: int = 9878
    recv_port: int = 9879
    send_sock: socket.socket | None = None
    recv_sock: socket.socket | None = None
    _connected: bool = False
    _send_lock: threading.Lock = field(default_factory=threading.Lock)

    def connect(self) -> bool:
        """Set up UDP sockets for M4L communication."""
        try:
            self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Use exclusive binding -- prevents a second instance from sharing this port
            so_exclusive = getattr(socket, "SO_EXCLUSIVEADDRUSE", None)
            if so_exclusive is not None:
                self.recv_sock.setsockopt(socket.SOL_SOCKET, so_exclusive, 1)
            self.recv_sock.bind(("127.0.0.1", self.recv_port))
            self.recv_sock.settimeout(5.0)
            self._connected = True
            logger.info("M4L UDP sockets ready (send->:%d, recv<-:%d)", self.send_port, self.recv_port)
            return True
        except Exception as e:
            logger.error("Failed to set up M4L UDP connection: %s", e)
            self.disconnect()
            return False

    def disconnect(self):
        """Close UDP sockets."""
        for s in (self.send_sock, self.recv_sock):
            if s:
                try:
                    s.close()
                except Exception:
                    pass
        self.send_sock = None
        self.recv_sock = None
        self._connected = False

    @staticmethod
    def _build_osc_message(address: str, osc_args: list | None = None) -> bytes:
        """Build an OSC message with typed arguments.

        Each arg is a tuple of (type, value):
          ('i', 42)  -- 32-bit int
          ('f', 3.14) -- 32-bit float
          ('s', 'hi') -- null-terminated padded string
        """
        def _osc_string(s: str) -> bytes:
            b = s.encode("utf-8") + b"\x00"
            b += b"\x00" * ((4 - len(b) % 4) % 4)
            return b

        osc_args = osc_args or []
        msg = _osc_string(address)
        type_tag = "," + "".join(t for t, _ in osc_args)
        msg += _osc_string(type_tag)
        for t, v in osc_args:
            if t == "s":
                msg += _osc_string(str(v))
            elif t == "i":
                msg += struct.pack(">i", int(v))
            elif t == "f":
                msg += struct.pack(">f", float(v))
        return msg

    def _build_osc_packet(self, command_type: str, params: Dict[str, Any], request_id: str) -> bytes:
        """Build the OSC packet for a given command type."""
        if command_type in _SPECIAL_BUILDERS:
            return _SPECIAL_BUILDERS[command_type](self, params, request_id)
        spec = _OSC_DISPATCH.get(command_type)
        if spec is None:
            raise ValueError(f"Unknown M4L command: {command_type}")
        return self._build_from_spec(spec, params, request_id)

    def _build_from_spec(self, spec: "_OscSpec", params: Dict[str, Any], request_id: str) -> bytes:
        """Build an OSC packet from a declarative spec."""
        if spec.json_encode:
            payload = json.dumps(params[spec.json_encode], separators=(",", ":"))
            encoded = base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii").rstrip("=")
            params = dict(params, **{spec.json_encode: encoded})

        osc_args: list[tuple[str, Any]] = []
        for arg_spec in spec.args:
            if len(arg_spec) == 3:
                osc_type, key, default = arg_spec
                value = params.get(key, default)
                if value == "" and osc_type == "s":
                    continue
                osc_args.append((osc_type, value))
            else:
                osc_type, key = arg_spec
                osc_args.append((osc_type, params[key]))
        osc_args.append(("s", request_id))
        return self._build_osc_message(spec.address, osc_args)

    def _drain_recv_socket(self):
        """Drain any stale data from the receive socket."""
        assert self.recv_sock is not None
        self.recv_sock.setblocking(False)
        try:
            for _ in range(100):
                self.recv_sock.recvfrom(65535)
        except (BlockingIOError, OSError):
            pass
        self.recv_sock.setblocking(True)

    def send_command(self, command_type: str, params: Dict[str, Any] | None = None, timeout: float | None = None) -> Dict[str, Any]:
        """Send a command to the M4L bridge using native OSC messages.

        Includes automatic reconnect: if the send or receive fails, the
        UDP sockets are recreated and the command is retried once.

        A threading.Lock serializes access so that concurrent tool threads
        cannot interleave send/recv operations on the shared UDP sockets.
        """
        params = params or {}
        request_id = str(uuid.uuid4())[:8]
        osc = self._build_osc_packet(command_type, params, request_id)

        # Commands that use chunked async processing in the M4L bridge
        # need longer timeouts to account for discovery + response delays.
        if timeout is not None:
            pass  # caller override takes priority
        elif command_type == "batch_set_hidden_params":
            param_count = len(params.get("parameters", []))
            # ~150ms per param (chunk delay + LOM overhead), minimum 10s
            timeout = max(10.0, param_count * 0.15)
        elif command_type in ("discover_params", "get_hidden_params"):
            # Chunked discovery: ~50ms per 4 params + chunked response sending
            timeout = 15.0
        elif command_type == "analyze_cross_track":
            # Cross-track: wait_ms + overhead for send routing + restore + response
            wait_ms = params.get("wait_ms", 500)
            timeout = max(3.0, (wait_ms / 1000.0) + 1.5)
        else:
            timeout = 5.0

        max_attempts = 2
        for attempt in range(1, max_attempts + 1):
            with self._send_lock:
                if not self._connected:
                    if not self.connect():
                        raise ConnectionError("Could not establish M4L UDP connection.")

                # Drain any stale data in the recv socket before sending
                self._drain_recv_socket()
                assert self.recv_sock is not None and self.send_sock is not None
                self.recv_sock.settimeout(timeout)

                try:
                    self.send_sock.sendto(osc, (self.send_host, self.send_port))
                except Exception as e:
                    logger.error("Failed to send UDP command to M4L (attempt %d): %s", attempt, e)
                    if attempt < max_attempts:
                        self.disconnect()
                        time.sleep(0.2)
                        continue
                    raise ConnectionError("Failed to send command to M4L bridge.")

                try:
                    data, _addr = self.recv_sock.recvfrom(65535)
                    result = self._parse_m4l_response(data)

                    # Handle chunked responses from the M4L bridge.
                    # Large responses (>1500 chars JSON) are split into multiple
                    # UDP packets, each wrapped in an envelope: {"_c":idx,"_t":total,"_d":"base64piece"}
                    if "_c" in result and "_t" in result:
                        result = self._reassemble_chunked_response(result)

                    # Verify request_id matches -- drain stale responses if mismatch
                    resp_id = result.get("id", "")
                    if resp_id and resp_id != request_id:
                        for _drain in range(5):
                            logger.warning("M4L response id mismatch: expected %s, got %s -- draining", request_id, resp_id)
                            try:
                                data, _addr = self.recv_sock.recvfrom(65535)
                                result = self._parse_m4l_response(data)
                                if "_c" in result and "_t" in result:
                                    result = self._reassemble_chunked_response(result)
                                resp_id = result.get("id", "")
                                if not resp_id or resp_id == request_id:
                                    break
                            except socket.timeout:
                                raise Exception(f"Timeout waiting for correct M4L response (expected {request_id})")
                        else:
                            raise Exception(
                                f"M4L response ID mismatch: expected {request_id}, "
                                f"could not find matching response after 5 drain attempts"
                            )
                    return result
                except socket.timeout:
                    logger.warning("M4L response timeout (attempt %d)", attempt)
                    if attempt < max_attempts:
                        self.disconnect()
                        time.sleep(0.2)
                        continue
                    raise Exception("Timeout waiting for M4L bridge response. Is the M4L device loaded?")
        raise RuntimeError("unreachable")

    def send_command_with_retry(self, command_type: str, params: Dict[str, Any] | None = None, timeout: float | None = None, max_attempts: int = 3) -> Dict[str, Any]:
        """Send command with retry logic for 'busy' responses from M4L bridge."""
        if max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer")
        last_result = None
        for attempt in range(max_attempts):
            result = self.send_command(command_type, params, timeout)
            if result.get("status") == "error" and "busy" in result.get("message", "").lower():
                delay = 0.5 * (attempt + 1)
                logger.warning("M4L bridge busy, retrying in %.1fs (attempt %d/%d)", delay, attempt + 1, max_attempts)
                time.sleep(delay)
                last_result = result
                continue
            return result
        logger.error("M4L bridge remained busy after %d attempts for '%s'", max_attempts, command_type)
        return last_result or {}

    @staticmethod
    def _parse_m4l_response(data: bytes) -> Dict[str, Any]:
        """Parse the response from the M4L bridge.

        Max's udpsend wraps the base64 string as an OSC message:
          [base64_string\\0...padding][,\\0\\0\\0]
        The OSC address (first null-terminated string) contains our
        base64-encoded JSON response.  The bridge uses URL-safe base64
        (- instead of +, _ instead of /, no = padding).
        """
        # Extract the OSC address = first null-terminated string in the packet
        null_pos = data.find(b"\x00")
        if null_pos > 0:
            osc_address = data[:null_pos].decode("utf-8", errors="replace").strip()
        else:
            osc_address = data.decode("utf-8", errors="replace").strip()

        # The OSC address is our base64-encoded JSON response
        # (udpsend uses the outlet symbol as the OSC address)
        # URL-safe base64 is the common path (v2.0.0+ bridge)
        try:
            padded = osc_address + "=" * (-len(osc_address) % 4)
            decoded = base64.urlsafe_b64decode(padded).decode("utf-8")
            return json.loads(decoded)
        except (ValueError, binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
            pass

        # Fallback: try standard base64
        try:
            decoded = base64.b64decode(osc_address).decode("utf-8")
            return json.loads(decoded)
        except (ValueError, binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
            pass

        # Fallback: try raw JSON (in case response wasn't base64-encoded)
        try:
            return json.loads(osc_address)
        except (json.JSONDecodeError, ValueError):
            pass

        # Last resort: strip all nulls and try
        cleaned = data.replace(b"\x00", b"").strip()
        text = cleaned.decode("utf-8", errors="replace").strip()
        # Remove trailing comma from OSC type tag
        text = text.rstrip(",").strip()
        try:
            padded = text + "=" * (-len(text) % 4)
            decoded = base64.urlsafe_b64decode(padded).decode("utf-8")
            return json.loads(decoded)
        except (ValueError, binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
            pass
        try:
            decoded = base64.b64decode(text).decode("utf-8")
            return json.loads(decoded)
        except (ValueError, binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
            pass

        raise json.JSONDecodeError("Could not parse M4L response", text, 0)

    def _reassemble_chunked_response(self, first_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Reassemble a chunked response from the M4L bridge.

        Large responses are split into multiple UDP packets, each containing:
          {"_c": chunk_index, "_t": total_chunks, "_d": "url_safe_base64_piece"}
        Each _d piece decodes to a fragment of the original JSON string.
        We collect all chunks, decode each _d, concatenate, and parse.
        """
        total = first_chunk["_t"]
        logger.info("M4L chunked response: %d total chunks", total)

        # Store chunks by index
        chunks: Dict[int, str] = {first_chunk["_c"]: first_chunk["_d"]}

        # Collect remaining chunks
        # Give extra time: 100ms per chunk + 5s base
        chunk_timeout = max(5.0, total * 0.1 + 5.0)
        assert self.recv_sock is not None
        self.recv_sock.settimeout(chunk_timeout)

        while len(chunks) < total:
            try:
                data, _ = self.recv_sock.recvfrom(65535)
                parsed = self._parse_m4l_response(data)
                if "_c" in parsed and "_t" in parsed:
                    idx = parsed["_c"]
                    if idx in chunks:
                        logger.warning("M4L chunk reassembly: duplicate chunk %d, ignoring", idx)
                        continue
                    chunks[idx] = parsed["_d"]
                    if len(chunks) % 5 == 0:
                        logger.info("M4L chunk reassembly: %d/%d", len(chunks), total)
                else:
                    # Got a non-chunk response (maybe from another command?)
                    logger.warning("M4L chunk reassembly: got non-chunk packet, ignoring")
            except socket.timeout:
                missing = sorted(set(range(total)) - set(chunks.keys()))
                logger.error(
                    "M4L chunk reassembly: timeout after %d/%d chunks, missing: %s",
                    len(chunks), total, missing[:10]
                )
                raise Exception(
                    f"Timeout receiving chunked M4L response ({len(chunks)}/{total} chunks, "
                    f"missing: {missing[:10]})"
                )

        # Reassemble: decode each piece and concatenate
        json_parts = []
        for i in range(total):
            piece_b64 = chunks[i]
            padded = piece_b64 + "=" * (-len(piece_b64) % 4)
            piece_json = base64.urlsafe_b64decode(padded).decode("utf-8")
            json_parts.append(piece_json)

        full_json = "".join(json_parts)
        logger.info("M4L chunked response reassembled: %d chars from %d chunks", len(full_json), total)
        return json.loads(full_json)

    def ping(self) -> bool:
        """Check if the M4L bridge device is responding."""
        try:
            result = self.send_command("ping")
            success = result.get("status") == "success"
            if success:
                self._check_bridge_version(result)
            return success
        except Exception as e:
            logger.debug("M4L ping failed: %s", e)
            return False

    @staticmethod
    def _check_bridge_version(ping_result: Dict[str, Any]):
        """Extract bridge version from ping response and compare with server version.

        Stores the bridge version in state and logs a warning if the major/minor
        versions don't match the MCP server version.
        """
        from MCP_Server import __version__ as server_version

        inner = ping_result.get("result") or {}
        bridge_version = inner.get("version", "") if isinstance(inner, dict) else ""
        if not bridge_version:
            # Older bridge versions may not include a version field
            logger.info("M4L bridge did not report a version (older bridge?)")
            return

        state.m4l_bridge_version = bridge_version

        # Compare major.minor parts for compatibility
        try:
            server_parts = server_version.split(".")[:2]
            bridge_parts = bridge_version.split(".")[:2]
            if server_parts != bridge_parts:
                logger.warning(
                    "Version mismatch: MCP server v%s, M4L bridge v%s. "
                    "Some features may not work correctly. "
                    "Please update both components to matching versions.",
                    server_version,
                    bridge_version,
                )
            else:
                logger.info(
                    "M4L bridge version %s matches server version %s",
                    bridge_version,
                    server_version,
                )
        except (ValueError, IndexError):
            logger.warning(
                "Could not parse versions for comparison: server=%s, bridge=%s",
                server_version,
                bridge_version,
            )


def get_m4l_connection() -> M4LConnection:
    """Get or create a connection to the M4L bridge device.

    Always attempts a fresh connection if the existing one is dead.
    Uses a cached ping result to avoid a full UDP round trip on every call.
    """
    # If we have a connected instance, verify it still works
    if state.m4l_connection is not None and state.m4l_connection._connected:
        # Use cached ping result if recent enough (avoids ~50-200ms round trip)
        now = time.time()
        if (now - state.m4l_ping_cache["timestamp"]) < state.M4L_PING_CACHE_TTL:
            if state.m4l_ping_cache["result"]:
                return state.m4l_connection
        # Cache expired or stale, do a live ping
        if state.m4l_connection.ping():
            state.m4l_ping_cache["result"] = True
            state.m4l_ping_cache["timestamp"] = now
            return state.m4l_connection
        # Ping failed -- tear down and try fresh
        logger.warning("M4L bridge ping failed on existing connection, reconnecting...")
        state.m4l_connection.disconnect()
        state.m4l_connection = None

    # Create a fresh connection
    state.m4l_connection = M4LConnection()
    if not state.m4l_connection.connect():
        state.m4l_connection = None
        raise ConnectionError(
            "Could not initialise M4L bridge UDP sockets. "
            "Check that port 9879 is not already in use."
        )

    # Quick ping to verify the device is actually responding
    if not state.m4l_connection.ping():
        logger.warning("M4L UDP sockets ready but bridge device is not responding.")
        # Keep the sockets open -- the device might be loaded later
        # Don't tear down, so the next call can retry the ping
        raise ConnectionError(
            "M4L bridge device is not responding. "
            "Make sure the AbletonBridge M4L device is loaded on a track in Ableton."
        )

    logger.info("M4L bridge connection established and verified.")
    return state.m4l_connection


def _m4l_batch_set_params(
    m4l: M4LConnection,
    track_index: int,
    device_index: int,
    parameters: List[Dict],
) -> Dict[str, Any]:
    """Set multiple hidden parameters by sending individual set_hidden_param
    commands sequentially.  More reliable than the base64-encoded batch OSC
    approach which can fail with longer payloads in Max.

    Returns a dict with keys: params_set, params_failed, total_requested, errors.
    """
    ok = 0
    failed = 0
    errors: List[str] = []
    for p in parameters:
        try:
            result = m4l.send_command("set_hidden_param", {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": int(p["index"]),
                "value": float(p["value"]),
            })
            if result.get("status") == "success":
                ok += 1
            else:
                failed += 1
                errors.append(f"[{p['index']}]: {result.get('message', '?')}")
        except Exception as e:
            failed += 1
            errors.append(f"[{p['index']}]: {str(e)}")
        # Small delay to let Ableton breathe when setting many params
        if len(parameters) > 6:
            time.sleep(0.05)
    return {
        "params_set": ok,
        "params_failed": failed,
        "total_requested": ok + failed,
        "errors": errors,
    }


def _m4l_result(result: dict) -> dict:
    """Extract result data from M4L response, or raise on error."""
    if result.get("status") == "success":
        return result.get("result", {})
    msg = result.get("message", "Unknown error")
    raise Exception(f"M4L bridge error: {msg}")

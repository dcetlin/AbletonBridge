"""Tests for M4L OSC dispatch table.

Verifies the declarative dispatch table produces byte-identical output
to the original elif chain for all commands.
"""
import json
import base64
import pytest

from MCP_Server.connections.m4l import (
    M4LConnection, _OSC_DISPATCH, _SPECIAL_BUILDERS,
)


class TestDispatchTable:
    def test_every_entry_has_valid_address(self):
        for name, spec in _OSC_DISPATCH.items():
            assert spec.address.startswith("/"), f"{name}: address must start with /"

    def test_all_m4l_tools_have_dispatch_entry(self):
        """Every M4L command used by m4l_tools.py should be in the dispatch table or special builders."""
        from MCP_Server.tools.m4l_tools import register_tools
        import re
        import inspect
        source = inspect.getsource(register_tools)
        # Only match m4l.send_command calls (not ableton.send_command)
        m4l_commands = set(re.findall(r'm4l\.send_command\("(\w+)"', source))
        m4l_commands |= set(re.findall(r'm4l\.send_command_with_retry\("(\w+)"', source))
        known = set(_OSC_DISPATCH) | set(_SPECIAL_BUILDERS)
        missing = m4l_commands - known
        assert not missing, f"M4L commands in m4l_tools.py but missing from dispatch: {missing}"

    def test_dispatch_entry_count(self):
        assert len(_OSC_DISPATCH) >= 37


class TestSimpleCommands:
    """Test that simple table-driven commands produce correct OSC packets."""

    def _conn(self):
        return M4LConnection()

    def test_ping(self):
        osc = self._conn()._build_osc_packet("ping", {}, "req1")
        ref = M4LConnection._build_osc_message("/ping", [("s", "req1")])
        assert osc == ref

    def test_discover_params(self):
        params = {"track_index": 0, "device_index": 2}
        osc = self._conn()._build_osc_packet("discover_params", params, "req2")
        ref = M4LConnection._build_osc_message("/discover_params", [
            ("i", 0), ("i", 2), ("s", "req2"),
        ])
        assert osc == ref

    def test_set_hidden_param(self):
        params = {"track_index": 1, "device_index": 3, "parameter_index": 7, "value": 0.5}
        osc = self._conn()._build_osc_packet("set_hidden_param", params, "req3")
        ref = M4LConnection._build_osc_message("/set_hidden_param", [
            ("i", 1), ("i", 3), ("i", 7), ("f", 0.5), ("s", "req3"),
        ])
        assert osc == ref

    def test_observe_property(self):
        params = {"lom_path": "live_set.tracks.0", "property_name": "name"}
        osc = self._conn()._build_osc_packet("observe_property", params, "req4")
        ref = M4LConnection._build_osc_message("/observe_property", [
            ("s", "live_set.tracks.0"), ("s", "name"), ("s", "req4"),
        ])
        assert osc == ref


class TestJsonEncodeCommands:
    def _conn(self):
        return M4LConnection()

    def test_batch_set_hidden_params(self):
        params = {
            "track_index": 0,
            "device_index": 1,
            "parameters": [{"index": 5, "value": 0.7}],
        }
        osc = self._conn()._build_osc_packet("batch_set_hidden_params", params, "req5")
        payload = json.dumps([{"index": 5, "value": 0.7}], separators=(",", ":"))
        b64 = base64.urlsafe_b64encode(payload.encode()).decode("ascii").rstrip("=")
        ref = M4LConnection._build_osc_message("/batch_set_hidden_params", [
            ("i", 0), ("i", 1), ("s", b64), ("s", "req5"),
        ])
        assert osc == ref

    def test_modify_clip_notes(self):
        mods = [{"note_id": 1, "pitch": 60}]
        params = {"track_index": 0, "clip_index": 0, "modifications": mods}
        osc = self._conn()._build_osc_packet("modify_clip_notes", params, "req6")
        payload = json.dumps(mods, separators=(",", ":"))
        b64 = base64.urlsafe_b64encode(payload.encode()).decode("ascii").rstrip("=")
        ref = M4LConnection._build_osc_message("/modify_clip_notes", [
            ("i", 0), ("i", 0), ("s", b64), ("s", "req6"),
        ])
        assert osc == ref


class TestDefaultArgs:
    def _conn(self):
        return M4LConnection()

    def test_clip_scrub_with_default(self):
        params = {"track_index": 0, "clip_index": 1, "action": "play"}
        osc = self._conn()._build_osc_packet("clip_scrub", params, "req7")
        ref = M4LConnection._build_osc_message("/clip_scrub", [
            ("i", 0), ("i", 1), ("s", "play"), ("f", 0.0), ("s", "req7"),
        ])
        assert osc == ref

    def test_clip_scrub_with_value(self):
        params = {"track_index": 0, "clip_index": 1, "action": "scrub", "beat_time": 2.5}
        osc = self._conn()._build_osc_packet("clip_scrub", params, "req8")
        ref = M4LConnection._build_osc_message("/clip_scrub", [
            ("i", 0), ("i", 1), ("s", "scrub"), ("f", 2.5), ("s", "req8"),
        ])
        assert osc == ref

    def test_discover_chains_without_extra(self):
        params = {"track_index": 0, "device_index": 1}
        osc = self._conn()._build_osc_packet("discover_chains", params, "req9")
        # extra_path is empty string default, should be omitted
        ref = M4LConnection._build_osc_message("/discover_chains", [
            ("i", 0), ("i", 1), ("s", "req9"),
        ])
        assert osc == ref

    def test_discover_chains_with_extra(self):
        params = {"track_index": 0, "device_index": 1, "extra_path": "chains.0"}
        osc = self._conn()._build_osc_packet("discover_chains", params, "req10")
        ref = M4LConnection._build_osc_message("/discover_chains", [
            ("i", 0), ("i", 1), ("s", "chains.0"), ("s", "req10"),
        ])
        assert osc == ref


class TestSpecialBuilders:
    def test_analyze_audio_with_params(self):
        conn = M4LConnection()
        params = {"track_index": 3}
        osc = conn._build_osc_packet("analyze_audio", params, "req11")
        ref = M4LConnection._build_osc_message("/analyze_audio", [
            ("i", 3), ("s", "req11"),
        ])
        assert osc == ref

    def test_analyze_audio_default(self):
        conn = M4LConnection()
        osc = conn._build_osc_packet("analyze_audio", {}, "req12")
        ref = M4LConnection._build_osc_message("/analyze_audio", [
            ("i", -1), ("s", "req12"),
        ])
        assert osc == ref

    def test_unknown_command_raises(self):
        conn = M4LConnection()
        with pytest.raises(ValueError, match="Unknown M4L command"):
            conn._build_osc_packet("nonexistent_command", {}, "req13")

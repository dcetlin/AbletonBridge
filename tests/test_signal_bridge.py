"""Tests for the add_signal_track workflow tool and SignalBridge maxpat."""
import json
import pathlib
import pytest
from unittest.mock import MagicMock
from mcp.server.fastmcp import FastMCP

from MCP_Server.tools.workflows import register_tools

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAXPAT_PATH = ROOT / "M4L_Device" / "SignalBridge.maxpat"


@pytest.fixture
def mcp_with_tools(patch_ableton):
    """Register workflow tools on a fresh MCP instance."""
    mcp = FastMCP("test")
    register_tools(mcp)
    return mcp, patch_ableton


class TestAddSignalTrack:
    def _get_tool(self, mcp):
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "add_signal_track":
                return tool
        raise AssertionError("add_signal_track tool not found")

    def _make_side_effects(self, track_idx=11):
        return [
            {"index": track_idx},  # create_audio_track
            {"name": "onset_signal"},  # set_track_name
            {"created": True},  # load_audio_to_arrangement
            {"status": "ok"},  # lom_set warping
            {"status": "ok"},  # lom_set loop_start
            {"status": "ok"},  # lom_set start_marker
            {"status": "ok"},  # load_instrument_or_effect
            {"results": [{"name": "Param Name", "value": 3}]},  # set_device_parameters_batch
            {"parameters": [  # get_device_parameters readback
                {"name": "Param Name", "value": 3},
                {"name": "Attack", "value": 5.0},
                {"name": "Release", "value": 50.0},
                {"name": "Gate", "value": 0.0},
                {"name": "Invert", "value": 0},
                {"name": "Active", "value": 1},
                {"name": "Dest Port", "value": 3333},
            ]},
            {"mute": True},  # set_track_mute
        ]

    @pytest.mark.asyncio
    async def test_creates_track_and_configures(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.side_effect = self._make_side_effects(11)

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={
                "name": "onset",
                "wav_path": "/path/to/onset.wav",
                "param_index": 3,
            },
            context=MagicMock(),
        )
        parsed = json.loads(result)

        assert parsed["track_index"] == 11
        assert parsed["track_name"] == "onset_signal"
        assert parsed["param_index"] == 3
        assert "device_state" in parsed
        assert "error" not in parsed

        commands = [c[0][0] for c in mock_conn.send_command.call_args_list]
        assert commands[0] == "create_audio_track"
        assert commands[1] == "set_track_name"
        assert commands[2] == "load_audio_to_arrangement"
        assert commands[6] == "load_instrument_or_effect"
        assert commands[7] == "set_device_parameters_batch"
        assert commands[8] == "get_device_parameters"
        assert commands[9] == "set_track_mute"

    @pytest.mark.asyncio
    async def test_device_state_from_readback_not_inputs(self, mcp_with_tools):
        """device_state values come from get_device_parameters, not echoed inputs."""
        mcp, mock_conn = mcp_with_tools
        effects = self._make_side_effects()
        effects[8] = {"parameters": [
            {"name": "Attack", "value": 4.8},
            {"name": "Release", "value": 51.2},
        ]}
        mock_conn.send_command.side_effect = effects

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0,
                       "attack_ms": 5.0, "release_ms": 50.0},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert parsed["device_state"]["Attack"] == 4.8
        assert parsed["device_state"]["Release"] == 51.2

    @pytest.mark.asyncio
    async def test_param_index_out_of_range(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 9},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert "error" in parsed
        mock_conn.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_device_load_failure_is_error(self, mcp_with_tools):
        """Device load failure must be an error, not graceful degradation."""
        mcp, mock_conn = mcp_with_tools

        def side_effect(cmd, params):
            if cmd == "load_instrument_or_effect":
                raise RuntimeError("SignalBridge.amxd not found")
            return {"index": 5, "status": "ok", "created": True}

        mock_conn.send_command.side_effect = side_effect

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert "error" in parsed
        assert "SignalBridge" in parsed["error"]

    @pytest.mark.asyncio
    async def test_batch_errors_surfaced_as_warnings(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        effects = self._make_side_effects()
        effects[7] = {"results": [
            {"name": "Param Name", "value": 0},
            {"name": "Attack", "error": "parameter not found"},
        ]}
        mock_conn.send_command.side_effect = effects

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert "warnings" in parsed
        assert any("Attack" in w for w in parsed["warnings"])

    @pytest.mark.asyncio
    async def test_gate_and_invert_sent_to_device(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.side_effect = self._make_side_effects()

        tool = self._get_tool(mcp)
        await tool.run(
            arguments={
                "name": "t", "wav_path": "/t.wav", "param_index": 0,
                "gate": 0.3, "invert": True,
            },
            context=MagicMock(),
        )

        batch_call = mock_conn.send_command.call_args_list[7]
        params = batch_call[0][1]["parameters"]
        gate_param = next(p for p in params if p["name"] == "Gate")
        invert_param = next(p for p in params if p["name"] == "Invert")
        assert gate_param["value"] == 0.3
        assert invert_param["value"] == 1

    @pytest.mark.asyncio
    async def test_dest_port_always_sent(self, mcp_with_tools):
        """Dest Port is always sent, even when it equals the default."""
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.side_effect = self._make_side_effects()

        tool = self._get_tool(mcp)
        await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )

        batch_call = mock_conn.send_command.call_args_list[7]
        params = batch_call[0][1]["parameters"]
        port_param = next(p for p in params if p["name"] == "Dest Port")
        assert port_param["value"] == 3333


class TestSignalBridgeMaxpat:
    """Structural tests over the maxpat JSON — catches wiring bugs in CI."""

    @pytest.fixture
    def patch_data(self):
        with open(MAXPAT_PATH) as f:
            return json.load(f)

    def _get_box(self, data, obj_id):
        for b in data["patcher"]["boxes"]:
            if b["box"].get("id") == obj_id:
                return b["box"]
        return None

    def _get_lines_from(self, data, source_id):
        """Return all patchlines originating from source_id."""
        lines = []
        for line in data["patcher"]["lines"]:
            pl = line["patchline"]
            if pl["source"][0] == source_id:
                lines.append(pl)
        return lines

    def test_valid_json(self, patch_data):
        assert "patcher" in patch_data
        assert len(patch_data["patcher"]["boxes"]) > 0

    def test_osc_message_boxes_no_prepend_in_set(self, patch_data):
        """A2: message boxes must be 'set /Params/...' not 'set prepend /Params/...'."""
        for b in patch_data["patcher"]["boxes"]:
            box = b["box"]
            if box.get("maxclass") == "message":
                text = box.get("text", "")
                if text.startswith("set "):
                    assert "set prepend" not in text, f"Box {box.get('id')}: '{text}'"

    def test_route_all_outlets_connected(self, patch_data):
        """A3: every route outlet must have a patchline."""
        route_box = self._get_box(patch_data, "obj-menu-to-prefix")
        if route_box is None:
            pytest.skip("route box not found")
        num_outlets = route_box.get("numoutlets", 0)
        lines = self._get_lines_from(patch_data, "obj-menu-to-prefix")
        connected_outlets = {pl["source"][1] for pl in lines}
        for i in range(num_outlets - 1):  # last outlet is unmatched
            assert i in connected_outlets, f"Route outlet {i} has no patchline"

    def test_dest_port_range(self, patch_data):
        """A4: Dest Port must support values > 255."""
        port_box = self._get_box(patch_data, "obj-dest-port")
        if port_box is None:
            pytest.skip("dest port box not found")
        attrs = port_box.get("saved_attribute_attributes", {})
        vr = attrs.get("valueof", {})
        param_type = vr.get("parameter_type", -1)
        assert param_type != 1, "parameter_type 1 is Int(0-255), cannot hold port numbers"
        mmax = vr.get("parameter_mmax", 0)
        assert mmax >= 65535, f"parameter_mmax={mmax}, need >=65535"

    def test_no_loadbang_to_active_toggle(self, patch_data):
        """A8: loadbang must not connect to the Active toggle."""
        for line in patch_data["patcher"]["lines"]:
            pl = line["patchline"]
            assert not (pl["source"][0] == "obj-loadbang" and pl["destination"][0] == "obj-active"), \
                "loadbang → active toggle connection causes Active to toggle off on load"

    def test_envelope_uses_signal_rate(self, patch_data):
        """A9: envelope stage must use abs~ (signal rate), not peakamp~ (control rate)."""
        for b in patch_data["patcher"]["boxes"]:
            box = b["box"]
            text = box.get("text", "")
            assert "peakamp~" not in text, f"Found peakamp~ in {box.get('id')} — should be abs~"

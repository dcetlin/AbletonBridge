"""Tests for the add_signal_track workflow tool."""
import json
import pytest
from unittest.mock import MagicMock, patch, call
from mcp.server.fastmcp import FastMCP

from MCP_Server.tools.workflows import register_tools


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

    @pytest.mark.asyncio
    async def test_creates_track_and_configures(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.side_effect = [
            {"index": 11, "name": "Audio"},  # create_audio_track
            {"name": "onset_signal"},  # set_track_name
            {"created": True},  # load_audio_to_arrangement
            {"status": "ok"},  # lom_set warping
            {"status": "ok"},  # lom_set loop_start
            {"status": "ok"},  # lom_set start_marker
            {"status": "ok"},  # load_instrument_or_effect
            {"results": []},  # set_device_parameters_batch
            {"mute": True},  # set_track_mute
        ]

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={
                "name": "onset",
                "wav_path": "/path/to/onset.wav",
                "param_name": "Onset",
                "param_index": 9,
            },
            context=MagicMock(),
        )
        parsed = json.loads(result)

        assert parsed["track_index"] == 11
        assert parsed["track_name"] == "onset_signal"
        assert parsed["param_name"] == "Onset"
        assert parsed["osc_address"] == "/Params/Onset"
        assert parsed["device_loaded"] is True

        commands = [c[0][0] for c in mock_conn.send_command.call_args_list]
        assert commands[0] == "create_audio_track"
        assert commands[1] == "set_track_name"
        assert commands[2] == "load_audio_to_arrangement"
        assert commands[3] == "lom_set"
        assert commands[6] == "load_instrument_or_effect"
        assert commands[7] == "set_device_parameters_batch"
        assert commands[8] == "set_track_mute"

    @pytest.mark.asyncio
    async def test_accepts_any_param_name(self, mcp_with_tools):
        """param_name is a free string — no validation against a fixed list."""
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.return_value = {"index": 5, "name": "Audio"}

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={
                "name": "custom",
                "wav_path": "/test.wav",
                "param_name": "MyCustomSignal",
            },
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert parsed["param_name"] == "MyCustomSignal"
        assert parsed["osc_address"] == "/Params/MyCustomSignal"

    @pytest.mark.asyncio
    async def test_custom_osc_port_and_prefix(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.return_value = {"index": 3, "name": "Audio"}

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={
                "name": "test",
                "wav_path": "/test.wav",
                "param_name": "Level",
                "osc_port": 7777,
                "osc_prefix": "/signals",
            },
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert parsed["osc_address"] == "/signals/Level"
        assert parsed["osc_port"] == 7777

    @pytest.mark.asyncio
    async def test_gate_and_invert_passed_to_device(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.side_effect = [
            {"index": 3},  # create_audio_track
            {"name": "onset_signal"},  # set_track_name
            {"created": True},  # load_audio_to_arrangement
            {"status": "ok"},  # lom_set x3
            {"status": "ok"},
            {"status": "ok"},
            {"status": "ok"},  # load_instrument_or_effect
            {"results": []},  # set_device_parameters_batch
            {"mute": True},  # set_track_mute
        ]

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={
                "name": "onset",
                "wav_path": "/test.wav",
                "param_name": "Onset",
                "gate": 0.3,
                "invert": True,
            },
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert parsed["gate"] == 0.3
        assert parsed["invert"] is True

        batch_call = mock_conn.send_command.call_args_list[7]
        params = batch_call[0][1]["parameters"]
        gate_param = next(p for p in params if p["name"] == "Gate")
        invert_param = next(p for p in params if p["name"] == "Invert")
        assert gate_param["value"] == 0.3
        assert invert_param["value"] == 1

    @pytest.mark.asyncio
    async def test_param_index_skipped_when_negative(self, mcp_with_tools):
        """When param_index is -1 (default), the device menu is not set."""
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.side_effect = [
            {"index": 3},
            {"name": "test_signal"},
            {"created": True},
            {"status": "ok"}, {"status": "ok"}, {"status": "ok"},
            {"status": "ok"},  # load device
            {"results": []},  # set_device_parameters_batch
            {"mute": True},
        ]

        tool = self._get_tool(mcp)
        await tool.run(
            arguments={
                "name": "test",
                "wav_path": "/test.wav",
                "param_name": "Anything",
            },
            context=MagicMock(),
        )

        batch_call = mock_conn.send_command.call_args_list[7]
        params = batch_call[0][1]["parameters"]
        param_names = [p["name"] for p in params]
        assert "Param Name" not in param_names

    @pytest.mark.asyncio
    async def test_device_load_failure_still_completes(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools

        def side_effect(cmd, params):
            if cmd == "load_instrument_or_effect":
                raise RuntimeError("SignalBridge not found")
            return {"index": 5, "name": "Audio", "status": "ok", "mute": True, "created": True}

        mock_conn.send_command.side_effect = side_effect

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={
                "name": "test",
                "wav_path": "/test.wav",
                "param_name": "Level",
            },
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert parsed["device_loaded"] is False
        assert parsed["track_index"] == 5

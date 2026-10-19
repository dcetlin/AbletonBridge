"""Tests for the add_signal_track workflow tool and SignalBridge maxpat."""
import json
import pathlib
import pytest
from unittest.mock import MagicMock, patch
from mcp.server.fastmcp import FastMCP

from MCP_Server.tools.workflows import register_tools, SIGNAL_BRIDGE_EXPECTED_PARAMS

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAXPAT_PATH = ROOT / "M4L_Device" / "SignalBridge.maxpat"

FULL_DEVICE_STATE = {
    "Param Name": 0, "Attack": 5.0, "Release": 50.0,
    "Gate": 0.0, "Invert": 0, "Active": 1, "Dest Port": 3333.0,
}


def _readback_from(state):
    return {"parameters": [{"name": k, "value": v} for k, v in state.items()]}


FULL_READBACK = _readback_from(FULL_DEVICE_STATE)


@pytest.fixture
def mcp_with_tools(patch_ableton):
    """Register workflow tools, resolver and time.sleep patched."""
    mcp = FastMCP("test")
    with patch("MCP_Server.tools.workflows.resolve_device_uri", return_value="query:SignalBridge"):
        with patch("MCP_Server.tools.workflows.time.sleep"):
            register_tools(mcp)
            yield mcp, patch_ableton


def _make_side_effects(track_idx=11):
    """Standard happy-path: create → name → wav → 3×lom → load → wait_readback → batch → readback → mute."""
    return [
        {"index": track_idx},       # create_audio_track
        {"name": "onset_signal"},    # set_track_name
        {"created": True},           # load_audio_to_arrangement
        {"status": "ok"},            # lom_set warping
        {"status": "ok"},            # lom_set loop_start
        {"status": "ok"},            # lom_set start_marker
        {"status": "ok"},            # load_instrument_or_effect
        FULL_READBACK,               # _wait_for_device_params (1st poll)
        {"results": []},             # set_device_parameters_batch
        FULL_READBACK,               # final readback
        {"mute": True},              # set_track_mute
    ]


class TestAddSignalTrack:
    def _get_tool(self, mcp):
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "add_signal_track":
                return tool
        raise AssertionError("add_signal_track tool not found")

    @pytest.mark.asyncio
    async def test_creates_track_and_configures(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.side_effect = _make_side_effects(11)

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "onset", "wav_path": "/path/to/onset.wav", "param_index": 3},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert parsed["track_index"] == 11
        assert parsed["track_name"] == "onset_signal"
        assert "device_state" in parsed

        commands = [c[0][0] for c in mock_conn.send_command.call_args_list]
        assert commands[0] == "create_audio_track"
        assert commands[6] == "load_instrument_or_effect"
        assert commands[7] == "get_device_parameters"  # wait poll
        assert commands[8] == "set_device_parameters_batch"
        assert commands[9] == "get_device_parameters"  # final readback
        assert commands[10] == "set_track_mute"

    @pytest.mark.asyncio
    async def test_wait_then_batch_ordering(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.side_effect = [
            *_make_side_effects()[:7],
            {"parameters": []},   # wait poll 1: empty
            FULL_READBACK,        # wait poll 2: ready
            {"results": []},      # batch
            FULL_READBACK,        # final readback
            {"mute": True},
        ]

        tool = self._get_tool(mcp)
        await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )

        commands = [c[0][0] for c in mock_conn.send_command.call_args_list]
        wait_indices = [i for i, c in enumerate(commands) if c == "get_device_parameters"]
        batch_index = commands.index("set_device_parameters_batch")
        assert all(wi < batch_index for wi in wait_indices[:2])

    @pytest.mark.asyncio
    async def test_params_never_ready_warns_and_skips_batch(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools

        def side_effect(cmd, params):
            if cmd == "create_audio_track":
                return {"index": 5}
            if cmd == "get_device_parameters":
                return {"parameters": []}
            if cmd == "set_device_parameters_batch":
                pytest.fail("batch should not be sent when params aren't ready")
            return {"status": "ok", "created": True, "mute": True}

        mock_conn.send_command.side_effect = side_effect
        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert any("not ready" in w for w in parsed.get("warnings", []))

    @pytest.mark.asyncio
    async def test_device_state_from_readback_not_inputs(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        custom_state = {**FULL_DEVICE_STATE, "Attack": 4.8, "Release": 51.2}
        effects = _make_side_effects()
        effects[9] = _readback_from(custom_state)
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
    async def test_validation_errors_raise(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        tool = self._get_tool(mcp)
        for kwargs in [
            {"param_index": 9}, {"osc_port": 0}, {"osc_port": 70000},
            {"attack_ms": 0}, {"release_ms": 5000}, {"gate": 1.5},
        ]:
            result = await tool.run(
                arguments={"name": "t", "wav_path": "/t.wav", **kwargs},
                context=MagicMock(),
            )
            parsed = json.loads(result)
            assert parsed.get("status") == "error", f"Expected error for {kwargs}"
            mock_conn.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_device_load_failure_raises(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools

        def side_effect(cmd, params):
            if cmd == "load_instrument_or_effect":
                raise RuntimeError("not found")
            return {"index": 5, "status": "ok", "created": True}

        mock_conn.send_command.side_effect = side_effect
        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert parsed.get("status") == "error"
        assert "left in place" in parsed.get("message", "")

    @pytest.mark.asyncio
    async def test_wav_load_failure_mentions_track(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools

        def side_effect(cmd, params):
            if cmd == "load_audio_to_arrangement":
                raise RuntimeError("file not found")
            return {"index": 5, "name": "t_signal"}

        mock_conn.send_command.side_effect = side_effect
        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/missing.wav", "param_index": 0},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert parsed.get("status") == "error"
        assert "left in place" in parsed.get("message", "")

    @pytest.mark.asyncio
    async def test_batch_errors_and_clamps_surfaced(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        effects = _make_side_effects()
        effects[8] = {"results": [
            {"name": "Attack", "error": "parameter not found"},
            {"name": "Dest Port", "value": 3333, "clamped": True},
        ]}
        mock_conn.send_command.side_effect = effects

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert any("Attack" in w for w in parsed.get("warnings", []))
        assert any("clamped" in w for w in parsed.get("warnings", []))

    @pytest.mark.asyncio
    async def test_dest_port_always_sent(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.side_effect = _make_side_effects()
        tool = self._get_tool(mcp)
        await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        batch_call = next(c for c in mock_conn.send_command.call_args_list
                          if c[0][0] == "set_device_parameters_batch")
        params = batch_call[0][1]["parameters"]
        assert next(p for p in params if p["name"] == "Dest Port")["value"] == 3333.0


class TestSignalBridgeMaxpat:
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
        return [line["patchline"] for line in data["patcher"]["lines"]
                if line["patchline"]["source"][0] == source_id]

    def test_valid_json(self, patch_data):
        assert len(patch_data["patcher"]["boxes"]) > 0

    def test_osc_address_uses_sprintf(self, patch_data):
        """E1: menu text → sprintf → prepend, not route → message boxes."""
        sprintf_box = self._get_box(patch_data, "obj-sprintf")
        assert sprintf_box is not None, "sprintf box must exist"
        assert "sprintf" in sprintf_box.get("text", "")
        assert "/Params/%s" in sprintf_box.get("text", "")
        lines_from_menu = self._get_lines_from(patch_data, "obj-param-name")
        sprintf_fed = any(pl["destination"][0] == "obj-sprintf" for pl in lines_from_menu)
        assert sprintf_fed, "live.menu must feed sprintf"
        lines_from_sprintf = self._get_lines_from(patch_data, "obj-sprintf")
        prepend_fed = any(pl["destination"][0] == "obj-prepend-prefix" for pl in lines_from_sprintf)
        assert prepend_fed, "sprintf must feed prepend"

    def test_no_route_message_chain(self, patch_data):
        """E1: the old route+message chain must be gone."""
        for b in patch_data["patcher"]["boxes"]:
            text = b["box"].get("text", "")
            assert "route 0 1 2" not in text, f"Old route chain found: {text}"

    def test_dest_port_range(self, patch_data):
        port_box = self._get_box(patch_data, "obj-dest-port")
        assert port_box is not None
        vr = port_box.get("saved_attribute_attributes", {}).get("valueof", {})
        assert vr.get("parameter_type") != 1
        assert vr.get("parameter_mmax", 0) >= 65535

    def test_no_loadbang_to_active_toggle(self, patch_data):
        loadbang_ids = {b["box"]["id"] for b in patch_data["patcher"]["boxes"]
                        if "loadbang" in b["box"].get("text", "")}
        for line in patch_data["patcher"]["lines"]:
            pl = line["patchline"]
            if pl["source"][0] in loadbang_ids and pl["destination"][0] == "obj-active":
                pytest.fail("loadbang → active toggle found")

    def test_envelope_uses_signal_rate(self, patch_data):
        for b in patch_data["patcher"]["boxes"]:
            assert "peakamp~" not in b["box"].get("text", "")

    def test_invert_expr_is_arithmetic(self, patch_data):
        for b in patch_data["patcher"]["boxes"]:
            text = b["box"].get("text", "")
            if "invert" in b["box"].get("id", "").lower() and "expr" in text:
                assert "if(" not in text

    def test_parameter_names_match_tool(self, patch_data):
        """C3: maxpat parameter_longname set must match the tool's expected set."""
        found = set()
        for b in patch_data["patcher"]["boxes"]:
            longname = b["box"].get("saved_attribute_attributes", {}).get(
                "valueof", {}).get("parameter_longname", "")
            if longname:
                found.add(longname)
        assert SIGNAL_BRIDGE_EXPECTED_PARAMS.issubset(found), \
            f"Missing: {SIGNAL_BRIDGE_EXPECTED_PARAMS - found}"

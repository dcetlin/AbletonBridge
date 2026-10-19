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
DISPLAY_VALUES = {"Param Name": "Param1"}


def _readback_from(state, display=None):
    params = []
    for k, v in state.items():
        entry = {"name": k, "value": v}
        if display and k in display:
            entry["display_value"] = display[k]
        params.append(entry)
    return {"parameters": params}


FULL_READBACK = _readback_from(FULL_DEVICE_STATE, DISPLAY_VALUES)


@pytest.fixture
def mcp_with_tools(patch_ableton):
    mcp = FastMCP("test")
    with patch("MCP_Server.tools.workflows.resolve_device_uri", return_value="query:SignalBridge"):
        with patch("MCP_Server.tools.workflows.time.sleep"):
            register_tools(mcp)
            yield mcp, patch_ableton


def _make_side_effects(track_idx=11):
    """create → name → wav → 3×lom → load → wait_poll → batch → readback → mute."""
    return [
        {"index": track_idx},
        {"name": "onset_signal"},
        {"created": True},
        {"status": "ok"}, {"status": "ok"}, {"status": "ok"},
        {"status": "ok"},   # load_instrument_or_effect
        FULL_READBACK,       # wait poll (ready on first try)
        {"results": []},     # set_device_parameters_batch
        FULL_READBACK,       # final readback
        {"mute": True},
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
            arguments={"name": "onset", "wav_path": "/onset.wav", "param_index": 3},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert parsed["track_index"] == 11
        assert parsed["track_name"] == "onset_signal"
        assert parsed["osc_address"] == "/Params/Param1"
        assert "device_state" in parsed

        commands = [c[0][0] for c in mock_conn.send_command.call_args_list]
        assert commands[7] == "get_device_parameters"   # wait poll
        assert commands[8] == "set_device_parameters_batch"
        assert commands[9] == "get_device_parameters"   # readback

        batch_call = mock_conn.send_command.call_args_list[8]
        batch_params = {p["name"]: p["value"] for p in batch_call[0][1]["parameters"]}
        assert batch_params["Param Name"] == 3

    @pytest.mark.asyncio
    async def test_wait_then_batch_ordering(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.side_effect = [
            *_make_side_effects()[:7],
            {"parameters": []},    # wait poll 1: empty
            FULL_READBACK,         # wait poll 2: ready
            {"results": []},       # batch
            FULL_READBACK,         # readback
            {"mute": True},
        ]
        tool = self._get_tool(mcp)
        await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        commands = [c[0][0] for c in mock_conn.send_command.call_args_list]
        batch_idx = commands.index("set_device_parameters_batch")
        wait_indices = [i for i, c in enumerate(commands) if c == "get_device_parameters" and i < batch_idx]
        assert len(wait_indices) >= 2

    @pytest.mark.asyncio
    async def test_params_never_ready_warns_and_skips_batch(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools

        def side_effect(cmd, params):
            if cmd == "create_audio_track":
                return {"index": 5}
            if cmd == "get_device_parameters":
                return {"parameters": []}
            if cmd == "set_device_parameters_batch":
                pytest.fail("batch sent when params aren't ready")
            return {"status": "ok", "created": True, "mute": True}

        mock_conn.send_command.side_effect = side_effect
        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert any("not ready" in w for w in parsed.get("warnings", []))
        assert "osc_address" not in parsed

    @pytest.mark.asyncio
    async def test_device_state_from_readback_not_inputs(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        custom = {**FULL_DEVICE_STATE, "Attack": 4.8, "Release": 51.2}
        effects = _make_side_effects()
        effects[9] = _readback_from(custom, DISPLAY_VALUES)
        mock_conn.send_command.side_effect = effects

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert parsed["device_state"]["Attack"] == 4.8

    @pytest.mark.asyncio
    async def test_missing_display_value_warns(self, mcp_with_tools):
        """G3: if readback has no display_value, warn and omit osc_address."""
        mcp, mock_conn = mcp_with_tools
        no_display = _readback_from(FULL_DEVICE_STATE)  # no display_value
        effects = _make_side_effects()
        effects[7] = no_display   # wait poll
        effects[9] = no_display   # final readback
        mock_conn.send_command.side_effect = effects

        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert "osc_address" not in parsed
        assert any("could not determine OSC address" in w for w in parsed.get("warnings", []))

    @pytest.mark.asyncio
    async def test_final_readback_failure_warns(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        call_count = [0]

        def side_effect(cmd, params):
            if cmd == "get_device_parameters":
                call_count[0] += 1
                if call_count[0] == 1:
                    return FULL_READBACK  # wait poll succeeds
                raise RuntimeError("readback failed")  # final readback fails
            if cmd == "create_audio_track":
                return {"index": 5}
            return {"status": "ok", "results": [], "created": True, "mute": True}

        mock_conn.send_command.side_effect = side_effect
        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        parsed = json.loads(result)
        assert any("readback" in w for w in parsed.get("warnings", []))

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
            assert json.loads(result).get("status") == "error"
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
                raise RuntimeError("not found")
            return {"index": 5, "name": "t_signal"}

        mock_conn.send_command.side_effect = side_effect
        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/m.wav", "param_index": 0},
            context=MagicMock(),
        )
        assert "left in place" in json.loads(result).get("message", "")

    @pytest.mark.asyncio
    async def test_batch_errors_and_clamps_surfaced(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        effects = _make_side_effects()
        effects[8] = {"results": [
            {"name": "Attack", "error": "not found"},
            {"name": "Dest Port", "value": 3333, "clamped": True},
        ]}
        mock_conn.send_command.side_effect = effects
        tool = self._get_tool(mcp)
        result = await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        ws = json.loads(result).get("warnings", [])
        assert any("Attack" in w for w in ws)
        assert any("clamped" in w for w in ws)

    @pytest.mark.asyncio
    async def test_dest_port_always_sent(self, mcp_with_tools):
        mcp, mock_conn = mcp_with_tools
        mock_conn.send_command.side_effect = _make_side_effects()
        tool = self._get_tool(mcp)
        await tool.run(
            arguments={"name": "t", "wav_path": "/t.wav", "param_index": 0},
            context=MagicMock(),
        )
        batch = next(c for c in mock_conn.send_command.call_args_list
                     if c[0][0] == "set_device_parameters_batch")
        assert next(p for p in batch[0][1]["parameters"] if p["name"] == "Dest Port")


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

    def test_osc_address_uses_sprintf_from_outlet_1(self, patch_data):
        """E1+F3: menu outlet 1 (text) → sprintf → prepend."""
        sprintf_box = self._get_box(patch_data, "obj-sprintf")
        assert sprintf_box is not None
        assert "/Params/%s" in sprintf_box.get("text", "")
        lines = self._get_lines_from(patch_data, "obj-param-name")
        sprintf_line = next((pl for pl in lines if pl["destination"][0] == "obj-sprintf"), None)
        assert sprintf_line is not None, "menu must feed sprintf"
        assert sprintf_line["source"][1] == 1, "must use outlet 1 (text), not 0 (index)"

    def test_no_route_message_chain(self, patch_data):
        for b in patch_data["patcher"]["boxes"]:
            assert "route 0 1 2" not in b["box"].get("text", "")

    def test_dest_port_range(self, patch_data):
        port = self._get_box(patch_data, "obj-dest-port")
        assert port is not None
        vr = port.get("saved_attribute_attributes", {}).get("valueof", {})
        assert vr.get("parameter_type") != 1
        assert vr.get("parameter_mmax", 0) >= 65535

    def test_no_loadbang_to_active_toggle(self, patch_data):
        lb_ids = {b["box"]["id"] for b in patch_data["patcher"]["boxes"]
                  if "loadbang" in b["box"].get("text", "")}
        for line in patch_data["patcher"]["lines"]:
            pl = line["patchline"]
            if pl["source"][0] in lb_ids and pl["destination"][0] == "obj-active":
                pytest.fail("loadbang → active")

    def test_envelope_uses_signal_rate(self, patch_data):
        for b in patch_data["patcher"]["boxes"]:
            assert "peakamp~" not in b["box"].get("text", "")

    def test_invert_expr_is_arithmetic(self, patch_data):
        for b in patch_data["patcher"]["boxes"]:
            t = b["box"].get("text", "")
            if "invert" in b["box"].get("id", "").lower() and "expr" in t:
                assert "if(" not in t

    def test_parameter_names_match_tool(self, patch_data):
        found = set()
        for b in patch_data["patcher"]["boxes"]:
            ln = b["box"].get("saved_attribute_attributes", {}).get(
                "valueof", {}).get("parameter_longname", "")
            if ln:
                found.add(ln)
        assert SIGNAL_BRIDGE_EXPECTED_PARAMS.issubset(found)

    def test_parameter_enum_is_array(self, patch_data):
        """G1: parameter_enum must be a JSON array, not a space-separated string."""
        menu = self._get_box(patch_data, "obj-param-name")
        assert menu is not None
        enum = menu.get("saved_attribute_attributes", {}).get(
            "valueof", {}).get("parameter_enum", None)
        assert isinstance(enum, list), f"parameter_enum must be a list, got {type(enum)}"
        assert len(enum) >= 1

    def test_menu_initial_fires_on_load(self, patch_data):
        """F4: menu must have parameter_initial_enable so it emits on load."""
        menu = self._get_box(patch_data, "obj-param-name")
        assert menu is not None
        vr = menu.get("saved_attribute_attributes", {}).get("valueof", {})
        assert vr.get("parameter_initial_enable") == 1

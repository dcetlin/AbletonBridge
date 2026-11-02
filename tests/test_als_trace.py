"""Tests for als-trace against small synthetic sets with OSC plugin racks."""

from __future__ import annotations

import gzip
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

import pytest

from als_tools import liveset as ls
from als_tools.trace import MacroTrace, RackTrace, juce_hash, main, trace


class _Builder:
    """Builds a set, handing out unique ids so macros in different racks don't collide."""

    def __init__(self) -> None:
        self.root = Element("Ableton")
        live = SubElement(self.root, "LiveSet")
        self.tracks = SubElement(live, "Tracks")
        self.main = self.track(live, "MainTrack", "Main")
        self.next_id = 1000

    def take(self) -> str:
        self.next_id += 1
        return str(self.next_id)

    def track(self, parent: Element, tag: str, name: str) -> Element:
        track = SubElement(parent, tag)
        _v(SubElement(track, "Name"), "EffectiveName", name)
        SubElement(SubElement(track, "AutomationEnvelopes"), "Envelopes")
        SubElement(SubElement(SubElement(track, "DeviceChain"), "DeviceChain"), "Devices")
        return track

    def audio_track(self, name: str = "SOURCE") -> Element:
        return self.track(self.tracks, "AudioTrack", name)

    def rack(self, parent: Element, names: dict[int, str] | None = None, macros: int = 16) -> Element:
        rack = SubElement(parent, "AudioEffectGroupDevice")
        for i in range(macros):
            macro = SubElement(rack, f"MacroControls.{i}")
            _v(macro, "LomId", self.take())
            SubElement(macro, "AutomationTarget", Id=self.take())
            _v(rack, f"MacroDisplayNames.{i}", (names or {}).get(i + 1, f"Macro {i + 1}"))
        return rack

    def follower(self, track: Element, rack: Element, number: int) -> None:
        device = SubElement(ls.devices(track), "MxDeviceAudioEffect")
        _v(SubElement(device, "MxDIdRef"), "LomId", ls.value(ls.macro(rack, number), "LomId"))


def _v(parent: Element, tag: str, value: str) -> Element:
    return SubElement(parent, tag, Value=value)


def _key_midi(parent: Element, number: int, channel: str = "16") -> None:
    mapping = SubElement(parent, "KeyMidi")
    _v(mapping, "IsNote", "false")
    _v(mapping, "Channel", channel)
    _v(mapping, "NoteOrController", str(number - 1))


def _plugin(
    rack: Element,
    osc: dict[str, str] | None,
    slots: dict[str, int],
    *,
    channel: str = "16",
    output: str = "1",
    global_output: str = "1",
) -> Element:
    """A plugin in a rack. osc is its saved list (None: no list); slots maps parameter to macro."""
    plugin = SubElement(rack, "PluginDevice")
    if osc is not None:
        items = "".join(
            f'<Parameter parameterName="{n}" oscAddress="{a}" oscOutputEnabled="{output}"/>' for n, a in osc.items()
        )
        xml = (
            f'<State><OSCSettings oscOutputEnabled="{global_output}"/>'
            f"<OSCParameters>{items}</OSCParameters></State>"
        ).encode()
        state = b"VC2!" + struct.pack("<I", len(xml)) + xml + b"tail"
        SubElement(plugin, "ProcessorState").text = state.hex().upper()
    for name, number in slots.items():
        param = SubElement(plugin, "PluginFloatParameter")
        _v(param, "ParameterName", f"{name} ")
        _v(param, "ParameterId", str(juce_hash(name)))
        _key_midi(SubElement(param, "ParameterValue"), number, channel)
    return plugin


def _osc_rack(b: _Builder, name: str = "Level", address: str = "/x/Level") -> Element:
    """A track with one OSC rack whose macro 1 is mapped to an address."""
    track = b.audio_track("OSC")
    rack = b.rack(ls.devices(track), {1: name})
    _plugin(rack, {"param1": address}, {"param1": 1})
    return rack


def _only(b: _Builder) -> RackTrace:
    racks = trace(b.root)
    assert len(racks) == 1
    return racks[0]


def _first(b: _Builder) -> MacroTrace:
    return _only(b).macros[0]


def _envelope(parent: Element, tag: str, target: str, values: list[str], event: str = "FloatEvent") -> None:
    envelope = SubElement(parent, tag)
    _v(SubElement(envelope, "EnvelopeTarget"), "PointeeId", target)
    events = SubElement(SubElement(envelope, "Automation"), "Events")
    for value in values:
        SubElement(events, event, Value=value)


def _write(root: Element, path: Path) -> str:
    with gzip.open(path, "wb") as f:
        f.write(ET.tostring(root))
    return str(path)


def test_juce_hash_matches_known_ids() -> None:
    assert juce_hash("param1") == 1152055620
    assert juce_hash("param72") == 1353986088
    assert juce_hash("param73") == 1353986089


def test_complete_path_is_ok() -> None:
    b = _Builder()
    b.follower(b.audio_track(), _osc_rack(b), 1)
    entry = _first(b)
    assert entry.status == "ok"
    assert entry.devices == ("SOURCE: MxDeviceAudioEffect",)
    assert [s.address for s in entry.slots] == ["/x/Level"]


def test_device_on_main_track_counts_as_feeder() -> None:
    b = _Builder()
    b.follower(b.main, _osc_rack(b), 1)
    assert _first(b).status == "ok"


def test_rack_on_main_track_is_traced() -> None:
    b = _Builder()
    rack = b.rack(ls.devices(b.main), {1: "Level"})
    _plugin(rack, {"param1": "/x/Level"}, {"param1": 1})
    b.follower(b.audio_track(), rack, 1)
    assert _only(b).track == "Main"
    assert _first(b).status == "ok"


@pytest.mark.parametrize("tag", ["AutomationEnvelope", "ClipEnvelope"])
def test_envelope_feeds_only_when_it_moves(tag: str) -> None:
    b = _Builder()
    target = ls.automation_target_id(ls.macro(_osc_rack(b), 1))
    _envelope(b.root, tag, target, ["0.5"])
    assert _first(b).status == "no feeder"
    _envelope(b.root, tag, target, ["0.5", "0.7"])
    assert _first(b).status == "ok"


def test_unmapped_macro_is_unused() -> None:
    b = _Builder()
    _osc_rack(b)
    assert _only(b).macros[1].status == "unused"


def test_fed_macro_with_no_destination_stops() -> None:
    b = _Builder()
    b.follower(b.audio_track(), _osc_rack(b), 2)
    assert _only(b).macros[1].status == "stops at macro"


def test_fed_macro_driving_something_else_is_local() -> None:
    b = _Builder()
    rack = _osc_rack(b)
    b.follower(b.audio_track(), rack, 2)
    _plugin(rack, None, {"cutoff": 2})
    assert _only(b).macros[1].status == "local only"


def test_mapped_parameter_with_no_feeder_is_reported_without_failing() -> None:
    b = _Builder()
    _osc_rack(b)
    assert _first(b).status == "no feeder"


@pytest.mark.parametrize(
    ("osc", "kwargs"),
    [
        pytest.param({}, {}, id="not-in-list"),
        pytest.param({"param1": ""}, {}, id="empty-address"),
        pytest.param({"param1": "/x/Level"}, {"output": "0"}, id="parameter-output-off"),
        pytest.param({"param1": "/x/Level"}, {"global_output": "0"}, id="global-output-off"),
    ],
)
def test_parameter_that_sends_nothing(osc: dict[str, str], kwargs: dict[str, str]) -> None:
    b = _Builder()
    track = b.audio_track("OSC")
    rack = b.rack(ls.devices(track))
    _plugin(rack, osc, {"param1": 1}, **kwargs)
    b.follower(b.audio_track(), rack, 1)
    assert _first(b).status == "not sent"


def test_hardware_midi_map_is_not_a_macro_mapping() -> None:
    b = _Builder()
    rack = _osc_rack(b)
    b.follower(b.audio_track(), rack, 1)
    _plugin(rack, {"param9": "/x/Other"}, {"param9": 1}, channel="1")
    assert [s.address for s in _first(b).slots] == ["/x/Level"]


def test_two_devices_on_a_macro_warn() -> None:
    b = _Builder()
    rack = _osc_rack(b)
    source = b.audio_track()
    b.follower(source, rack, 1)
    b.follower(source, rack, 1)
    assert _first(b).status == "multiple devices"


@pytest.mark.parametrize(
    ("name", "address", "status"),
    [
        ("Macro 1", "/x/Anything", "ok"),
        ("master_gain", "/x/master_gain", "ok"),
        ("Master Gain", "/x/master-gain", "ok"),
        ("Amp", "/x/Amp/", "ok"),
        ("kick trigger", "/x/Kick", "ok"),
        ("Brightness", "/x/Level", "name mismatch"),
    ],
)
def test_name_check(name: str, address: str, status: str) -> None:
    b = _Builder()
    b.follower(b.audio_track(), _osc_rack(b, name, address), 1)
    assert _first(b).status == status


def test_name_needs_to_match_only_one_of_two_addresses() -> None:
    b = _Builder()
    track = b.audio_track("OSC")
    rack = b.rack(ls.devices(track), {1: "Brightness"})
    _plugin(rack, {"p1": "/x/Brightness", "p2": "/y/Glow"}, {"p1": 1, "p2": 1})
    b.follower(b.audio_track(), rack, 1)
    assert _first(b).status == "ok"


def test_second_plugin_in_a_rack_uses_its_own_list() -> None:
    b = _Builder()
    rack = _osc_rack(b)
    _plugin(rack, {"param1": "/y/Level"}, {"param1": 2})
    assert [s.address for s in _only(b).macros[1].slots] == ["/y/Level"]


def test_every_osc_rack_is_traced() -> None:
    b = _Builder()
    _osc_rack(b)
    _osc_rack(b, "Other", "/y/Other")
    assert len(trace(b.root)) == 2


def test_nested_plugin_maps_to_its_own_rack_and_follows_outer_macro() -> None:
    b = _Builder()
    track = b.audio_track("OSC")
    outer = b.rack(ls.devices(track), {1: "Outer"})
    inner = b.rack(SubElement(outer, "Branches"), {3: "Cutoff"})
    _key_midi(ls.macro(inner, 3), 1)
    _plugin(inner, {"p1": "/x/Cutoff"}, {"p1": 3})
    b.follower(b.audio_track(), outer, 1)
    macros = _only(b).macros
    assert [s.address for s in macros[2].slots] == ["/x/Cutoff"]
    assert macros[2].devices == ("SOURCE: MxDeviceAudioEffect",)
    assert macros[2].status == "ok"


def test_rack_with_eight_macros() -> None:
    b = _Builder()
    track = b.audio_track("OSC")
    rack = b.rack(ls.devices(track), {1: "Level"}, macros=8)
    _plugin(rack, {"p1": "/x/Level"}, {"p1": 1})
    assert len(_only(b).macros) == 8


def test_cli_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = _Builder()
    good.follower(good.audio_track(), _osc_rack(good), 1)
    broken = _Builder()
    broken.follower(broken.audio_track(), _osc_rack(broken), 2)
    misnamed = _Builder()
    misnamed.follower(misnamed.audio_track(), _osc_rack(misnamed, "Brightness"), 1)
    plain = _Builder()
    plain.audio_track()

    assert main([_write(good.root, tmp_path / "good.als")]) == 0
    assert main([_write(broken.root, tmp_path / "broken.als")]) == 1
    assert "stops at macro" in capsys.readouterr().out
    misnamed_path = _write(misnamed.root, tmp_path / "misnamed.als")
    assert main([misnamed_path]) == 0
    assert main(["--strict", misnamed_path]) == 1
    assert main([_write(plain.root, tmp_path / "plain.als")]) == 0
    assert "nothing to trace" in capsys.readouterr().out


def test_cli_reports_bad_file_and_continues(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "bad.als"
    bad.write_bytes(b"not gzip")
    good = _Builder()
    good.follower(good.audio_track(), _osc_rack(good), 1)
    assert main([str(bad), _write(good.root, tmp_path / "good.als")]) == 1
    captured = capsys.readouterr()
    assert "als-trace:" in captured.err
    assert "good.als" in captured.out


def test_one_silent_parameter_among_several_is_not_sent() -> None:
    b = _Builder()
    track = b.audio_track("OSC")
    rack = b.rack(ls.devices(track), {1: "Level"})
    _plugin(rack, {"p1": "/x/Level", "p2": ""}, {"p1": 1, "p2": 1})
    b.follower(b.audio_track(), rack, 1)
    assert _first(b).status == "not sent"


def _switch(device: Element, value: str) -> str:
    switch = SubElement(device, "On")
    _v(switch, "Manual", value)
    target = SubElement(switch, "AutomationTarget", Id="9")
    return ls.attr(target, "Id")


def test_switched_off_device_does_not_feed_unless_automated() -> None:
    b = _Builder()
    b.follower(b.audio_track(), _osc_rack(b), 1)
    device = next(b.root.iter("MxDeviceAudioEffect"))
    target = _switch(device, "false")
    assert _first(b).status == "no feeder"
    _envelope(b.root, "AutomationEnvelope", target, ["false", "true"], "BoolEvent")
    assert _first(b).status == "ok"


def test_switched_off_plugin_sends_nothing() -> None:
    b = _Builder()
    rack = _osc_rack(b)
    b.follower(b.audio_track(), rack, 1)
    _switch(next(rack.iter("PluginDevice")), "false")
    assert _first(b).status == "not sent"


def test_automated_plugin_switch_counts_as_on() -> None:
    b = _Builder()
    rack = _osc_rack(b)
    b.follower(b.audio_track(), rack, 1)
    target = _switch(next(rack.iter("PluginDevice")), "false")
    _envelope(b.root, "AutomationEnvelope", target, ["false", "true"], "BoolEvent")
    assert _first(b).status == "ok"


def test_device_label_uses_file_stem_on_any_platform() -> None:
    for path in ("C:\\Max\\Follower.amxd", "/Users/me/Max/Follower.amxd"):
        b = _Builder()
        b.follower(b.audio_track(), _osc_rack(b), 1)
        _v(next(b.root.iter("MxDeviceAudioEffect")), "Path", path)
        assert _first(b).devices == ("SOURCE: Follower",)


def test_unknown_state_encoding_is_not_an_osc_list() -> None:
    b = _Builder()
    track = b.audio_track("OSC")
    plugin = _plugin(b.rack(ls.devices(track)), None, {})
    xml = b'<?xml version="1.0" encoding="nope"?><State><OSCParameters/></State>'
    state = b"VC2!" + struct.pack("<I", len(xml)) + xml
    SubElement(plugin, "ProcessorState").text = state.hex()
    assert trace(b.root) == []


def test_cli_reports_malformed_value(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    b = _Builder()
    _osc_rack(b)
    ls.set_value(next(b.root.iter("KeyMidi")), "NoteOrController", "x")
    assert main([_write(b.root, tmp_path / "bad.als")]) == 1
    assert "als-trace:" in capsys.readouterr().err


def test_plugin_in_a_drum_rack_is_traced_without_changing_rack_lookup() -> None:
    b = _Builder()
    track = b.audio_track("OSC")
    rack = b.rack(ls.devices(track), {1: "Level"})
    rack.tag = "DrumGroupDevice"
    _plugin(rack, {"p1": "/x/Level"}, {"p1": 1})
    assert _first(b).status == "no feeder"
    with pytest.raises(ls.AlsError, match="has no rack"):
        ls.rack(track)


def test_cli_reports_corrupt_gzip_and_continues(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = _Builder()
    good.follower(good.audio_track(), _osc_rack(good), 1)
    path = Path(_write(good.root, tmp_path / "good.als"))
    data = bytearray(path.read_bytes())
    data[20:30] = bytes(10)
    corrupt = tmp_path / "corrupt.als"
    corrupt.write_bytes(data)
    assert main([str(corrupt), str(path)]) == 1
    captured = capsys.readouterr()
    assert "als-trace:" in captured.err
    assert "good.als" in captured.out

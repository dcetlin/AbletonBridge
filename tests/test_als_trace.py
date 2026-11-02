"""Tests for als-trace against a small synthetic set with an OSC plugin rack."""

from __future__ import annotations

import gzip
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

import pytest

from als_tools import liveset as ls
from als_tools.trace import MacroTrace, Slot, juce_hash, main, trace

MACRO_LOM_BASE = 40


def _v(parent: Element, tag: str, value: str) -> Element:
    return SubElement(parent, tag, Value=value)


def _track(parent: Element, tag: str, name: str) -> Element:
    track = SubElement(parent, tag)
    _v(SubElement(track, "Name"), "EffectiveName", name)
    SubElement(SubElement(track, "AutomationEnvelopes"), "Envelopes")
    SubElement(SubElement(SubElement(track, "DeviceChain"), "DeviceChain"), "Devices")
    return track


def _state(params: dict[str, str]) -> str:
    items = "".join(f'<Parameter parameterName="{n}" oscAddress="{a}"/>' for n, a in params.items())
    xml = f"<State><OSCParameters>{items}</OSCParameters></State>".encode()
    return (b"VC2!" + struct.pack("<I", len(xml)) + xml + b"tail").hex().upper()


def _hub(tracks: Element, names: dict[int, str], osc: dict[str, str], slots: dict[str, int]) -> Element:
    """A rack with named macros and a plugin; slots maps parameter name to macro number."""
    track = _track(tracks, "AudioTrack", "HUB")
    rack = SubElement(ls.devices(track), "AudioEffectGroupDevice")
    for i in range(16):
        macro = SubElement(rack, f"MacroControls.{i}")
        _v(macro, "LomId", str(MACRO_LOM_BASE + i + 1))
        SubElement(macro, "AutomationTarget", Id=str(500 + i))
        _v(rack, f"MacroDisplayNames.{i}", names.get(i + 1, f"Macro {i + 1}"))
    plugin = SubElement(rack, "PluginDevice")
    SubElement(plugin, "ProcessorState").text = _state(osc)
    for name, number in slots.items():
        param = SubElement(plugin, "PluginFloatParameter")
        _v(param, "ParameterName", f"{name} ")
        _v(param, "ParameterId", str(juce_hash(name)))
        value = SubElement(param, "ParameterValue")
        _v(SubElement(value, "KeyMidi"), "NoteOrController", str(number - 1))
    return track


def _follower(track: Element, macro_number: int) -> None:
    device = SubElement(ls.devices(track), "MxDeviceAudioEffect")
    _v(SubElement(device, "MxDIdRef"), "LomId", str(MACRO_LOM_BASE + macro_number))


def _set() -> tuple[Element, Element]:
    root = Element("Ableton")
    live = SubElement(root, "LiveSet")
    tracks = SubElement(live, "Tracks")
    _track(live, "MainTrack", "Main")
    return root, tracks


def _entry(root: Element, number: int) -> MacroTrace:
    entries = trace(root)
    assert entries is not None
    return entries[number - 1]


def test_juce_hash_matches_saved_nativize_ids() -> None:
    assert juce_hash("param1") == 1152055620
    assert juce_hash("param72") == 1353986088
    assert juce_hash("param73") == 1353986089


def test_complete_path_is_ok() -> None:
    root, tracks = _set()
    _hub(tracks, {1: "Violin"}, {"param1": "/Params/Violin"}, {"param1": 1})
    _follower(_track(tracks, "AudioTrack", "VIOLIN"), 1)
    entry = _entry(root, 1)
    assert entry.status == "ok"
    assert entry.devices == ("VIOLIN: MxDeviceAudioEffect",)
    assert entry.slots == (Slot("param1", "/Params/Violin"),)


def test_device_on_main_track_counts_as_feeder() -> None:
    root, tracks = _set()
    _hub(tracks, {2: "Master"}, {"param2": "/Params/Master"}, {"param2": 2})
    _follower(ls.main_track(root), 2)
    assert _entry(root, 2).status == "ok"


def test_automation_counts_only_when_it_moves() -> None:
    root, tracks = _set()
    hub = _hub(tracks, {3: "Bilat Amount"}, {"param3": "/Params/Bilatamount"}, {"param3": 3})
    envelope = SubElement(ls.envelopes(hub), "AutomationEnvelope")
    _v(SubElement(envelope, "EnvelopeTarget"), "PointeeId", "502")
    events = SubElement(SubElement(envelope, "Automation"), "Events")
    SubElement(events, "FloatEvent", Value="0.5")
    assert _entry(root, 3).status == "no feeder"
    SubElement(events, "FloatEvent", Value="0.7")
    assert _entry(root, 3).status == "ok"


@pytest.mark.parametrize(
    ("names", "osc", "slots", "followers", "status"),
    [
        pytest.param({}, {}, {}, 0, "unused", id="unused"),
        pytest.param({1: "Water"}, {}, {}, 1, "stops at macro", id="fed-but-no-slot"),
        pytest.param({1: "Water"}, {}, {"param1": 1}, 1, "no OSC address", id="slot-without-address"),
        pytest.param({1: "Violin"}, {"param1": "/Params/Violin"}, {"param1": 1}, 0, "no feeder", id="slot-not-fed"),
        pytest.param({1: "Violin"}, {"param1": "/Params/Violin"}, {"param1": 1}, 2, "multiple devices", id="two-devices"),
        pytest.param({1: "water amp"}, {"param1": "/Params/Bilatlive"}, {"param1": 1}, 1, "name mismatch", id="wrong-destination"),
        pytest.param({}, {"param1": "/Params/Bilatlive"}, {"param1": 1}, 1, "ok", id="default-name-not-compared"),
        pytest.param({1: "onset signal"}, {"param1": "/Params/Onset"}, {"param1": 1}, 1, "ok", id="signal-suffix-ignored"),
    ],
)
def test_status(
    names: dict[int, str], osc: dict[str, str], slots: dict[str, int], followers: int, status: str
) -> None:
    root, tracks = _set()
    _hub(tracks, names, osc, slots)
    source = _track(tracks, "AudioTrack", "SOURCE")
    for _ in range(followers):
        _follower(source, 1)
    assert _entry(root, 1).status == status


def test_set_without_osc_plugin() -> None:
    root, tracks = _set()
    _track(tracks, "AudioTrack", "PLAIN")
    assert trace(root) is None


def _write(root: Element, path: Path) -> str:
    with gzip.open(path, "wb") as f:
        f.write(ET.tostring(root))
    return str(path)


def test_cli_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good, tracks = _set()
    _hub(tracks, {1: "Violin"}, {"param1": "/Params/Violin"}, {"param1": 1})
    _follower(_track(tracks, "AudioTrack", "VIOLIN"), 1)
    broken, tracks = _set()
    _hub(tracks, {1: "Water"}, {}, {})
    _follower(_track(tracks, "AudioTrack", "WATER"), 1)
    assert main([_write(good, tmp_path / "good.als")]) == 0
    assert main([_write(broken, tmp_path / "broken.als")]) == 1
    assert "stops at macro" in capsys.readouterr().out
    assert main([]) == 2


def test_find_track_reaches_main_track() -> None:
    root, _ = _set()
    assert ls.find_track(root, "Main") is ls.main_track(root)

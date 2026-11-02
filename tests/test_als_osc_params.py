"""Tests for adding OSC parameters and setting device parameters through als-clone."""

from __future__ import annotations

import copy
import gzip
import struct
import wave
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

import pytest

from als_tools import liveset as ls
from als_tools.clone import _wav_frames, apply, main  # pyright: ignore[reportPrivateUsage]
from als_tools.osc_plugin import EMPTY_VISUAL_INDEX, juce_hash, macro_mapping, osc_list, read_state
from als_tools.spec import parse_spec
from als_tools.trace import trace
from als_tools.validate import main as validate_main, validate

TAIL = b"tail"


def _v(parent: Element, tag: str, value: str) -> Element:
    return SubElement(parent, tag, Value=value)


def _track(tracks: Element, tag: str, tid: int, name: str) -> Element:
    track = SubElement(tracks, tag, Id=str(tid))
    _v(SubElement(track, "Name"), "EffectiveName", name)
    SubElement(SubElement(track, "AutomationEnvelopes"), "Envelopes")
    SubElement(SubElement(SubElement(track, "DeviceChain"), "DeviceChain"), "Devices")
    return track


def _set() -> Element:
    """A rack with an OSC plugin: param1 on macro 1, param2 on macro 2, three empty slots.

    SOURCE holds a follower mapped to macro 1, which specs copy to feed other macros.
    """
    existing = 2
    root = Element("Ableton")
    live = SubElement(root, "LiveSet")
    tracks = SubElement(live, "Tracks")
    osc = _track(tracks, "AudioTrack", 1, "OSC")
    source = _track(tracks, "AudioTrack", 2, "SOURCE")
    _track(tracks, "ReturnTrack", 3, "RETURN")
    _track(live, "MainTrack", 4, "Main")
    _v(live, "NextPointeeId", "5000")

    rack = SubElement(ls.devices(osc), "AudioEffectGroupDevice", Id="0")
    for i in range(16):
        macro = SubElement(rack, f"MacroControls.{i}")
        _v(macro, "LomId", str(101 + i) if i == 0 else "0")
        SubElement(macro, "AutomationTarget", Id=str(1000 + i))
        _v(rack, f"MacroDisplayNames.{i}", f"Macro {i + 1}")
    plugin = SubElement(rack, "PluginDevice", Id="0")
    items = "".join(
        f'<Parameter parameterName="param{n}" displayLabel="Param {n} " oscAddress="/x/P{n}" oscOutputEnabled="1"/>'
        for n in range(1, existing + 1)
    )
    declared = "".join(f'<PARAM id="param{n}" value="0"/>' for n in range(1, 9))
    xml = f"<State><Parameters>{declared}</Parameters><OSCParameters>{items}</OSCParameters></State>".encode()
    SubElement(plugin, "ProcessorState").text = (b"VC2!" + struct.pack("<I", len(xml)) + xml + TAIL).hex().upper()
    for slot in range(existing + 3):
        param = SubElement(plugin, "PluginFloatParameter", Id=str(slot))
        filled = slot < existing
        _v(param, "ParameterName", "" if not filled else f"P{slot + 1} ")
        _v(param, "ParameterId", str(juce_hash(f"param{slot + 1}")) if filled else "-1")
        _v(param, "VisualIndex", str(slot) if filled else EMPTY_VISUAL_INDEX)
        value = SubElement(param, "ParameterValue")
        _v(value, "LomId", "0")
        if filled:
            value.append(macro_mapping(slot + 1))
        _v(value, "Manual", "0.5")

    follower = SubElement(ls.devices(source), "MxDeviceAudioEffect", Id="0")
    _v(SubElement(follower, "MxDIdRef"), "LomId", "101")
    gain = SubElement(follower, "MxDFloatParameter")
    _v(gain, "Name", "Gain")
    _v(gain, "MinValue", "-70")
    _v(gain, "MaxValue", "30")
    _v(SubElement(gain, "Timeable"), "Manual", "1.0")
    return root


def _write(root: Element, path: Path) -> str:
    with gzip.open(path, "wb") as f:
        f.write(ET.tostring(root))
    return str(path)


def _apply(tmp_path: Path, root: Element, **sections: object) -> Element:
    source = _write(root, tmp_path / "in.als")
    out = str(tmp_path / "out.als")
    apply(parse_spec({"reference": source, "target": source, "output": out, **sections}))
    return ls.read_set(out)


def _osc_item(macro: int, address: str = "/x/New", **target: str) -> dict[str, object]:
    return {"label": "New", "address": address, "map": {"track": "OSC", "macro": macro, **target}}


def _plugin(root: Element) -> Element:
    return next(root.iter("PluginDevice"))


def _saved(root: Element) -> list[Element]:
    state = read_state(_plugin(root))
    assert state is not None
    found = osc_list(state)
    assert found is not None
    return list(found[1])


def _follower_item(macro: int, position: int = 99, gain: float = 6.5) -> dict[str, object]:
    return {
        "template_track": "SOURCE",
        "device_index": 0,
        "into": "OSC",
        "position": position,
        "map": {"track": "OSC", "macro": macro},
        "params": [{"name": "Gain", "value": gain}],
    }


def test_added_param_is_traced_end_to_end(tmp_path: Path) -> None:
    root = _apply(tmp_path, _set(), osc_params=[_osc_item(3)], devices=[_follower_item(3)])
    assert validate(root).ok
    entry = trace(root)[0].macros[2]
    assert [s.address for s in entry.slots] == ["/x/New"]
    assert entry.status == "ok"


def test_existing_params_keep_their_numbers_and_state_tail(tmp_path: Path) -> None:
    root = _apply(tmp_path, _set(), osc_params=[_osc_item(3), _osc_item(4, "/x/Newer")])
    assert [p.get("parameterName") for p in _saved(root)] == ["param1", "param2", "param3", "param4"]
    state = read_state(_plugin(root))
    assert state is not None and state.tail == TAIL
    slots = {ls.attr(p, "Id"): ls.value(p, "ParameterId") for p in root.iter("PluginFloatParameter")}
    assert slots["0"] == str(juce_hash("param1"))
    assert slots["2"] == str(juce_hash("param3"))
    assert slots["3"] == str(juce_hash("param4"))
    assert slots["4"] == "-1"


def test_filled_slot_matches_what_live_saves(tmp_path: Path) -> None:
    root = _apply(tmp_path, _set(), osc_params=[_osc_item(3)])
    slot = next(p for p in root.iter("PluginFloatParameter") if ls.attr(p, "Id") == "2")
    assert ls.value(slot, "ParameterName") == "New "
    assert ls.value(slot, "VisualIndex") == "2"
    value = ls.child(slot, "ParameterValue")
    assert [c.tag for c in value] == ["LomId", "KeyMidi", "Manual"]
    assert ls.value(value, "Manual") == "0"
    text = ls.child(_plugin(root), "ProcessorState").text
    assert text is not None and text == text.upper() and text.startswith("\n")


def test_new_param_takes_over_the_macro_and_reports_it(tmp_path: Path) -> None:
    source = _write(_set(), tmp_path / "in.als")
    out = str(tmp_path / "out.als")
    spec = {"reference": source, "target": source, "output": out, "osc_params": [_osc_item(2)]}
    result = apply(parse_spec(spec))
    assert "(unmapped: Param 2)" in result.actions[0]
    root = ls.read_set(out)
    assert [s.address for s in trace(root)[0].macros[1].slots] == ["/x/New"]
    assert sum(1 for _ in root.iter("KeyMidi")) == 2


def test_reused_slot_ends_with_one_mapping(tmp_path: Path) -> None:
    root = _set()
    slot = next(p for p in root.iter("PluginFloatParameter") if ls.attr(p, "Id") == "4")
    ls.set_value(slot, "ParameterId", str(juce_hash("param3")))
    ls.child(slot, "ParameterValue").insert(1, macro_mapping(7))
    source = _write(root, tmp_path / "in.als")
    out = str(tmp_path / "out.als")
    spec = {"reference": source, "target": source, "output": out, "osc_params": [_osc_item(3)]}
    assert "(unmapped: param3 from macro 7)" in apply(parse_spec(spec)).actions[0]
    result = ls.read_set(out)
    slot = next(p for p in result.iter("PluginFloatParameter") if ls.attr(p, "Id") == "4")
    assert len(ls.child(slot, "ParameterValue").findall("KeyMidi")) == 1
    assert [s.address for s in trace(result)[0].macros[2].slots] == ["/x/New"]


def test_reused_slot_already_on_the_macro_reports_nothing(tmp_path: Path) -> None:
    root = _set()
    slot = next(p for p in root.iter("PluginFloatParameter") if ls.attr(p, "Id") == "4")
    ls.set_value(slot, "ParameterId", str(juce_hash("param3")))
    ls.child(slot, "ParameterValue").insert(1, macro_mapping(3))
    source = _write(root, tmp_path / "in.als")
    spec = {"reference": source, "target": source, "output": str(tmp_path / "o.als"), "osc_params": [_osc_item(3)]}
    assert "unmapped" not in apply(parse_spec(spec)).actions[0]


def test_visual_index_stays_unique_after_a_reorder(tmp_path: Path) -> None:
    root = _set()
    slots = {ls.attr(p, "Id"): p for p in root.iter("PluginFloatParameter")}
    ls.set_value(slots["0"], "VisualIndex", "2")
    ls.set_value(slots["1"], "VisualIndex", "0")
    result = _apply(tmp_path, root, osc_params=[_osc_item(3)])
    indexes = [ls.value(p, "VisualIndex") for p in result.iter("PluginFloatParameter")]
    assert sorted(i for i in indexes if i != EMPTY_VISUAL_INDEX) == ["0", "2", "3"]


def test_reused_slot_keeps_its_visual_index(tmp_path: Path) -> None:
    root = _set()
    slot = next(p for p in root.iter("PluginFloatParameter") if ls.attr(p, "Id") == "4")
    ls.set_value(slot, "ParameterId", str(juce_hash("param3")))
    ls.set_value(slot, "VisualIndex", "4")
    result = _apply(tmp_path, root, osc_params=[_osc_item(3)])
    slot = next(p for p in result.iter("PluginFloatParameter") if ls.attr(p, "Id") == "4")
    assert ls.value(slot, "VisualIndex") == "4"


def test_rejects_two_osc_plugins_in_a_rack(tmp_path: Path) -> None:
    root = _set()
    rack = next(root.iter("AudioEffectGroupDevice"))
    rack.append(copy.deepcopy(_plugin(root)))
    with pytest.raises(ls.AlsError, match="2 plugins with OSC lists"):
        _apply(tmp_path, root, osc_params=[_osc_item(3)])


@pytest.mark.parametrize("text", ["x\x01", "x\ud800"])
def test_spec_rejects_text_xml_cannot_hold(text: str) -> None:
    for spec in (
        {"osc_params": [_osc_item(3, rename=text)]},
        {"tracks": [{"template": "a", "name": text, "sample": "s", "map": {"track": "t", "macro": 1}}]},
    ):
        with pytest.raises(ls.AlsError, match="XML can't hold"):
            parse_spec({"reference": "a", "target": "a", "output": "b", **spec})


def test_rejects_slot_with_hardware_map(tmp_path: Path) -> None:
    root = _set()
    slot = next(p for p in root.iter("PluginFloatParameter") if ls.attr(p, "Id") == "4")
    ls.set_value(slot, "ParameterId", str(juce_hash("param3")))
    mapping = macro_mapping(7)
    ls.set_value(mapping, "Channel", "1")
    ls.child(slot, "ParameterValue").insert(1, mapping)
    with pytest.raises(ls.AlsError, match="hardware MIDI map"):
        _apply(tmp_path, root, osc_params=[_osc_item(3)])


@pytest.mark.parametrize("macro", [0, -1, 17, 40])
def test_rejects_macro_out_of_range(tmp_path: Path, macro: int) -> None:
    with pytest.raises(ls.AlsError, match="out of range"):
        _apply(tmp_path, _set(), osc_params=[_osc_item(macro)])


@pytest.mark.parametrize(
    ("label", "address", "message"),
    [
        ("x\x01", "/x/New", "label"),
        ("New", "/x/\x01", "address"),
        ("New", "", "must start"),
        ("New", "no/slash", "must start"),
    ],
)
def test_rejects_bad_text(tmp_path: Path, label: str, address: str, message: str) -> None:
    item = {"label": label, "address": address, "map": {"track": "OSC", "macro": 3}}
    with pytest.raises(ls.AlsError, match=message):
        _apply(tmp_path, _set(), osc_params=[item])
    assert not (tmp_path / "out.als").exists()


def test_custom_range_and_default(tmp_path: Path) -> None:
    item = {**_osc_item(3), "minimum": -180, "maximum": 180}
    entry = _saved(_apply(tmp_path, _set(), osc_params=[item]))[-1]
    assert (entry.get("minValue"), entry.get("maxValue"), entry.get("defaultValue")) == ("-180.0", "180.0", "-180.0")


def test_rejects_empty_range(tmp_path: Path) -> None:
    item = {**_osc_item(3), "minimum": 1, "maximum": 1}
    with pytest.raises(ls.AlsError, match="must be below"):
        _apply(tmp_path, _set(), osc_params=[item])


def test_rejects_param_the_plugin_does_not_declare(tmp_path: Path) -> None:
    root = _set()
    plugin = _plugin(root)
    state = read_state(plugin)
    assert state is not None
    xml = state.xml.replace(b'<PARAM id="param3" value="0"/>', b"")
    blob = b"VC2!" + struct.pack("<I", len(xml)) + xml + state.tail
    ls.child(plugin, "ProcessorState").text = blob.hex()
    with pytest.raises(ls.AlsError, match="declares no parameter param3"):
        _apply(tmp_path, root, osc_params=[_osc_item(3)])


def _replace_state(root: Element, xml: bytes) -> None:
    blob = b"VC2!" + struct.pack("<I", len(xml)) + xml + TAIL
    ls.child(_plugin(root), "ProcessorState").text = blob.hex()


def test_adds_to_an_empty_list(tmp_path: Path) -> None:
    root = _set()
    _replace_state(root, b'<State><Parameters><PARAM id="param1"/></Parameters><OSCParameters/></State>')
    assert [p.get("parameterName") for p in _saved(_apply(tmp_path, root, osc_params=[_osc_item(3)]))] == ["param1"]


def test_numbering_continues_past_gaps(tmp_path: Path) -> None:
    root = _set()
    _replace_state(
        root,
        b'<State><Parameters><PARAM id="param6"/></Parameters><OSCParameters>'
        b'<Parameter index="4" parameterName="param5" oscAddress="/x/A"/></OSCParameters></State>',
    )
    entry = _saved(_apply(tmp_path, root, osc_params=[_osc_item(3)]))[-1]
    assert (entry.get("parameterName"), entry.get("index")) == ("param6", "5")


def test_rejects_non_utf8_state(tmp_path: Path) -> None:
    root = _set()
    _replace_state(root, b'<?xml version="1.0" encoding="ISO-8859-1"?><State><Parameters><PARAM id="param1"/></Parameters><OSCParameters/></State>')
    with pytest.raises(ls.AlsError, match="only UTF-8"):
        _apply(tmp_path, root, osc_params=[_osc_item(3)])


def test_utf8_declared_with_single_quotes_is_accepted(tmp_path: Path) -> None:
    root = _set()
    _replace_state(root, b"<?xml version='1.0' encoding='utf-8'?><State><Parameters><PARAM id=\"param1\"/></Parameters><OSCParameters/></State>")
    assert _saved(_apply(tmp_path, root, osc_params=[_osc_item(3)]))[-1].get("parameterName") == "param1"


def test_other_utf8_spellings_are_refused(tmp_path: Path) -> None:
    root = _set()
    _replace_state(root, b'<?xml version="1.0" encoding="UTF8"?><State><Parameters><PARAM id="param1"/></Parameters><OSCParameters/></State>')
    with pytest.raises(ls.AlsError, match="only UTF-8"):
        _apply(tmp_path, root, osc_params=[_osc_item(3)])


def test_latin1_declared_with_single_quotes_is_refused(tmp_path: Path) -> None:
    root = _set()
    _replace_state(root, b"<?xml version='1.0' encoding='ISO-8859-1'?><State><Parameters><PARAM id=\"param1\"/></Parameters><OSCParameters/></State>")
    with pytest.raises(ls.AlsError, match="only UTF-8"):
        _apply(tmp_path, root, osc_params=[_osc_item(3)])


def test_plugin_in_a_nested_rack_is_not_used(tmp_path: Path) -> None:
    root = _set()
    rack = next(root.iter("AudioEffectGroupDevice"))
    plugin = _plugin(root)
    rack.remove(plugin)
    SubElement(rack, "AudioEffectGroupDevice", Id="9").append(plugin)
    with pytest.raises(ls.AlsError, match="no plugin with an OSC list"):
        _apply(tmp_path, root, osc_params=[_osc_item(3)])


def test_uses_a_slot_that_already_exposes_the_param(tmp_path: Path) -> None:
    root = _set()
    slot = next(p for p in root.iter("PluginFloatParameter") if ls.attr(p, "Id") == "4")
    ls.set_value(slot, "ParameterId", str(juce_hash("param3")))
    result = _apply(tmp_path, root, osc_params=[_osc_item(3)])
    slots = {ls.attr(p, "Id"): ls.value(p, "ParameterId") for p in result.iter("PluginFloatParameter")}
    assert slots["4"] == str(juce_hash("param3"))
    assert slots["2"] == "-1"


def test_address_is_escaped(tmp_path: Path) -> None:
    root = _apply(tmp_path, _set(), osc_params=[_osc_item(3, '/x/"a&b"')])
    assert _saved(root)[-1].get("oscAddress") == '/x/"a&b"'


def test_macro_can_be_renamed(tmp_path: Path) -> None:
    root = _apply(tmp_path, _set(), osc_params=[_osc_item(3, rename="New")])
    assert trace(root)[0].macros[2].name == "New"


def test_rejects_duplicate_address(tmp_path: Path) -> None:
    with pytest.raises(ls.AlsError, match="already sends"):
        _apply(tmp_path, _set(), osc_params=[_osc_item(3, "/x/P1")])


def test_rejects_when_no_slot_is_free(tmp_path: Path) -> None:
    items = [_osc_item(3 + i, f"/x/New{i}") for i in range(4)]
    with pytest.raises(ls.AlsError, match="no empty parameter slot"):
        _apply(tmp_path, _set(), osc_params=items)


def test_rejects_rack_without_osc_plugin(tmp_path: Path) -> None:
    root = _set()
    rack = next(root.iter("AudioEffectGroupDevice"))
    rack.remove(_plugin(root))
    with pytest.raises(ls.AlsError, match="no plugin with an OSC list"):
        _apply(tmp_path, root, osc_params=[_osc_item(3)])


def test_device_params_and_append_position(tmp_path: Path) -> None:
    root = _apply(tmp_path, _set(), devices=[_follower_item(3)])
    chain = list(ls.devices(ls.find_track(root, "OSC")))
    assert [d.tag for d in chain] == ["AudioEffectGroupDevice", "MxDeviceAudioEffect"]
    assert ls.value(chain[1], ".//MxDFloatParameter/Timeable/Manual") == "6.5"


def test_unknown_device_param_is_rejected(tmp_path: Path) -> None:
    item = _follower_item(3)
    item["params"] = [{"name": "Nope", "value": 1}]
    with pytest.raises(ls.AlsError, match="0 parameters named 'Nope'"):
        _apply(tmp_path, _set(), devices=[item])


def test_device_param_outside_range_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ls.AlsError, match="outside the range"):
        _apply(tmp_path, _set(), devices=[_follower_item(3, gain=1000)])


def test_int_param_takes_whole_numbers_only(tmp_path: Path) -> None:
    root = _set()
    follower = next(root.iter("MxDeviceAudioEffect"))
    steps = SubElement(follower, "MxDIntParameter")
    _v(steps, "Name", "Steps")
    _v(steps, "MinValue", "0")
    _v(steps, "MaxValue", "8")
    _v(SubElement(steps, "Timeable"), "Manual", "1")
    item = _follower_item(3)
    item["params"] = [{"name": "Steps", "value": 4}]
    result = _apply(tmp_path, root, devices=[item])
    assert ls.value(ls.devices(ls.find_track(result, "OSC"))[-1], ".//MxDIntParameter/Timeable/Manual") == "4"
    item["params"] = [{"name": "Steps", "value": 2.5}]
    with pytest.raises(ls.AlsError, match="whole number"):
        _apply(tmp_path, root, devices=[item])


def test_duplicate_param_name_is_rejected(tmp_path: Path) -> None:
    root = _set()
    follower = next(root.iter("MxDeviceAudioEffect"))
    follower.append(next(follower.iter("MxDFloatParameter")))
    with pytest.raises(ls.AlsError, match="2 parameters named 'Gain'"):
        _apply(tmp_path, root, devices=[_follower_item(3)])


def test_huge_position_appends(tmp_path: Path) -> None:
    root = _apply(tmp_path, _set(), devices=[_follower_item(3, position=10**30)])
    assert ls.devices(ls.find_track(root, "OSC"))[-1].tag == "MxDeviceAudioEffect"


def test_malformed_values_are_reported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _set()
    next(t for t in ls.tracks(root)).set("Id", "x")
    source = _write(root, tmp_path / "in.als")
    spec = tmp_path / "spec.json"
    spec.write_text(f'{{"reference": "{source}", "target": "{source}", "output": "{tmp_path / "o.als"}"}}')
    assert main([str(spec)]) == 1
    assert "als-clone: track Id" in capsys.readouterr().err


def test_malformed_param_range_is_reported(tmp_path: Path) -> None:
    root = _set()
    ls.set_value(next(root.iter("MxDFloatParameter")), "MinValue", "x")
    with pytest.raises(ls.AlsError, match="Gain MinValue"):
        _apply(tmp_path, root, devices=[_follower_item(3)])


@pytest.mark.parametrize("content", [b"\xff\xfe", b"{", b'{"a": ' + b"9" * 5000 + b"}"])
def test_bad_spec_files_are_reported(tmp_path: Path, capsys: pytest.CaptureFixture[str], content: bytes) -> None:
    spec = tmp_path / "spec.json"
    spec.write_bytes(content)
    assert main([str(spec)]) == 1
    assert "can't read spec" in capsys.readouterr().err


def test_unknown_xml_encoding_is_reported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "bad.als"
    with gzip.open(path, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="nope"?><Ableton/>')
    assert validate_main([str(path)]) == 1
    assert "can't read" in capsys.readouterr().out


def test_malformed_tempo_is_reported() -> None:
    root = Element("Ableton")
    main_track = SubElement(SubElement(root, "LiveSet"), "MainTrack")
    _v(SubElement(SubElement(main_track, "DeviceChain"), "Mixer"), "Tempo", "").clear()
    tempo = ls.child(main_track, "DeviceChain/Mixer/Tempo")
    _v(tempo, "Manual", "x")
    with pytest.raises(ls.AlsError, match="Tempo"):
        ls.tempo(root)


def test_multibyte_encoding_is_reported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "bad.als"
    with gzip.open(path, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="shift_jis"?><Ableton/>')
    assert validate_main([str(path)]) == 1
    assert "can't read" in capsys.readouterr().out


def test_plugin_state_with_multibyte_encoding_has_no_osc_list() -> None:
    root = _set()
    _replace_state(root, b'<?xml version="1.0" encoding="shift_jis"?><State><OSCParameters/></State>')
    assert trace(root) == []


def test_deeply_nested_spec_is_reported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text("[" * 200000)
    assert main([str(spec)]) == 1
    assert "can't read spec" in capsys.readouterr().err


def test_wav_without_sample_rate_is_refused(tmp_path: Path) -> None:
    sample = tmp_path / "zero.wav"
    with wave.open(str(sample), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(bytes(4))
    data = bytearray(sample.read_bytes())
    data[24:28] = bytes(4)
    sample.write_bytes(data)
    with pytest.raises(ls.AlsError, match="no sample rate|can't read"):
        _wav_frames(str(sample))


def test_negative_position_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ls.AlsError, match="negative"):
        _apply(tmp_path, _set(), devices=[_follower_item(3, position=-1)])


def test_macro_past_the_visible_count_is_shown(tmp_path: Path) -> None:
    root = _set()
    _v(next(root.iter("AudioEffectGroupDevice")), "NumVisibleMacroControls", "8")
    result = _apply(tmp_path, root, osc_params=[_osc_item(9)])
    assert ls.value(next(result.iter("AudioEffectGroupDevice")), "NumVisibleMacroControls") == "10"


def test_set_without_return_track_is_accepted(tmp_path: Path) -> None:
    root = _set()
    tracks = ls.tracks(root)
    tracks.remove(next(t for t in tracks if t.tag == "ReturnTrack"))
    assert validate(_apply(tmp_path, root, osc_params=[_osc_item(3)])).ok


def test_spec_rejects_non_numeric_param_value() -> None:
    item = _follower_item(3)
    item["params"] = [{"name": "Gain", "value": "loud"}]
    with pytest.raises(ls.AlsError, match="expected a finite number"):
        parse_spec({"reference": "a", "target": "a", "output": "b", "devices": [item]})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), 10**400])
def test_spec_rejects_non_finite_param_value(value: float) -> None:
    item = _follower_item(3)
    item["params"] = [{"name": "Gain", "value": value}]
    with pytest.raises(ls.AlsError, match="expected a finite number"):
        parse_spec({"reference": "a", "target": "a", "output": "b", "devices": [item]})


def test_clone_reports_non_wav_sample(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = _write(_set(), tmp_path / "in.als")
    sample = tmp_path / "not.wav"
    sample.write_bytes(b"nope")
    spec = tmp_path / "spec.json"
    spec.write_text(
        f'{{"reference": "{source}", "target": "{source}", "output": "{tmp_path / "o.als"}", "tracks": '
        f'[{{"template": "SOURCE", "name": "N", "sample": "{sample}", "map": {{"track": "OSC", "macro": 3}}}}]}}'
    )
    assert main([str(spec)]) == 1
    assert "als-clone:" in capsys.readouterr().err


def test_validate_and_clone_report_bad_files(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "bad.als"
    bad.write_bytes(b"not gzip")
    good = _write(_set(), tmp_path / "good.als")
    assert validate_main([str(bad), good]) == 1
    out = capsys.readouterr().out
    assert "FAIL" in out and "good.als" in out

    spec = tmp_path / "spec.json"
    spec.write_text(f'{{"reference": "{bad}", "target": "{bad}", "output": "{tmp_path / "o.als"}"}}')
    assert main([str(spec)]) == 1
    assert "als-clone:" in capsys.readouterr().err


@pytest.mark.parametrize("text", ["x", "nan", "inf"])
def test_non_finite_numbers_are_reported(text: str) -> None:
    with pytest.raises(ls.AlsError, match="number"):
        ls.to_float(text, "field")


def test_oversized_param_number_is_reported(tmp_path: Path) -> None:
    root = _set()
    name = "param" + "9" * 5000
    _replace_state(
        root,
        f'<State><Parameters/><OSCParameters><Parameter parameterName="{name}" oscAddress="/x/A"/></OSCParameters></State>'.encode(),
    )
    with pytest.raises(ls.AlsError, match="not an integer"):
        _apply(tmp_path, root, osc_params=[_osc_item(3)])


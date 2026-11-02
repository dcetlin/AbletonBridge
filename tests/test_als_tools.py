"""Tests for als_tools against small synthetic Live sets built in the test.

The fixture reproduces only the structure the tools touch. That's enough to check
id renumbering, mapping retargeting, clip placement and automation edits without a
real .als.
"""

from __future__ import annotations

import gzip
import wave
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

import pytest

from als_tools import liveset as ls
from als_tools.clone import apply, main
from als_tools.spec import CloneSpec, parse_spec
from als_tools.validate import validate

RACK_LOM_BASE = 40      # macro N gets LomId RACK_LOM_BASE + N in the reference
REF_MAPPED_MACRO = 11   # the reference's signal track maps to this macro


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------

class _Ids:
    def __init__(self) -> None:
        self.n = 100

    def take(self) -> str:
        self.n += 1
        return str(self.n)


def _v(parent: Element, tag: str, value: str) -> Element:
    return SubElement(parent, tag, Value=value)


def _track(tracks: Element, tag: str, tid: int, name: str, ids: _Ids) -> Element:
    t = SubElement(tracks, tag, Id=str(tid))
    n = SubElement(t, "Name")
    _v(n, "EffectiveName", name)
    _v(n, "UserName", name)
    SubElement(SubElement(t, "AutomationEnvelopes"), "Envelopes")
    chain = SubElement(SubElement(t, "DeviceChain"), "DeviceChain")
    SubElement(chain, "Devices")
    SubElement(t, "VolumeTarget", Id=ids.take())
    return t


def _rack(track: Element, ids: _Ids, lom_ids: bool) -> Element:
    rack = SubElement(ls.devices(track), "AudioEffectGroupDevice", Id="0")
    for i in range(16):
        m = SubElement(rack, f"MacroControls.{i}")
        _v(m, "LomId", str(RACK_LOM_BASE + i + 1) if lom_ids else "0")
        SubElement(m, "AutomationTarget", Id=ids.take())
        _v(rack, f"MacroDisplayNames.{i}", f"Macro {i + 1}")
    return rack


def _envelope(track: Element, target_id: str, points: list[tuple[float, float]]) -> None:
    envs = ls.envelopes(track)
    env = SubElement(envs, "AutomationEnvelope", Id=str(len(envs)))
    _v(SubElement(env, "EnvelopeTarget"), "PointeeId", target_id)
    events = SubElement(SubElement(env, "Automation"), "Events")
    for k, (t, val) in enumerate(points):
        SubElement(events, "FloatEvent", Id=str(k), Time=str(t), Value=str(val))


def _audio_clip(track: Element, time: float, loop_start: float, sample: str) -> Element:
    events = SubElement(SubElement(SubElement(track, "MainSequencer"), "Sample"), "ArrangerAutomation")
    clip = SubElement(SubElement(events, "Events"), "AudioClip", Time=str(time))
    for tag, val in (("CurrentStart", str(time)), ("CurrentEnd", "8"), ("Name", "old"), ("IsWarped", "true")):
        _v(clip, tag, val)
    loop = SubElement(clip, "Loop")
    for tag, val in (("LoopStart", str(loop_start)), ("LoopEnd", "4"), ("StartRelative", "0"),
                     ("LoopOn", "false"), ("OutMarker", "4")):
        _v(loop, tag, val)
    sref = SubElement(clip, "SampleRef")
    fref = SubElement(sref, "FileRef")
    for tag, val in (("RelativePath", sample), ("Path", "/" + sample), ("OriginalFileSize", "1"),
                     ("OriginalCrc", "1")):
        _v(fref, tag, val)
    _v(sref, "LastModDate", "0")
    _v(sref, "DefaultDuration", "1")
    _v(sref, "DefaultSampleRate", "44100")
    return clip


def _mapped_ef(track: Element, lom: str, ids: _Ids) -> Element:
    """A Max device whose mapping points at LomId `lom`, like an Envelope Follower."""
    dev = SubElement(ls.devices(track), "MxDeviceAudioEffect", Id="0")
    _v(dev, "LomId", str(1000 + int(ids.take())))  # the device's own LomId
    SubElement(dev, "Pointee", Id=ids.take())
    SubElement(dev, "ModulationTarget", Id=ids.take())
    refs = SubElement(SubElement(dev, "IdRefList"), "IdRefList")
    for k, v in enumerate((lom, lom, "0")):
        _v(SubElement(refs, "MxDIdRef", Id=str(k)), "LomId", v)
    return dev


def _live_set(reference: bool) -> Element:
    ids = _Ids()
    root = Element("Ableton")
    liveset = SubElement(root, "LiveSet")
    tracks = SubElement(liveset, "Tracks")
    fx = _track(tracks, "AudioTrack", 1, "FX", ids)
    _rack(fx, ids, lom_ids=reference)
    synth = _track(tracks, "AudioTrack", 2, "Synth", ids)
    synth_rack = _rack(synth, ids, lom_ids=False)
    _envelope(synth, ls.automation_target_id(ls.macro(synth_rack, 5)),
              [(0, 1), (4, 2), (8, 3)] if not reference else [(0, 9)])
    lead = _track(tracks, "AudioTrack", 3, "Lead", ids)
    _audio_clip(lead, time=2.0, loop_start=1.5, sample="lead.wav")
    if reference:
        _mapped_ef(lead, str(RACK_LOM_BASE + 1), ids)
        sig = _track(tracks, "AudioTrack", 4, "onset_signal", ids)
        _mapped_ef(sig, str(RACK_LOM_BASE + REF_MAPPED_MACRO), ids)
        _audio_clip(sig, time=0.0, loop_start=0.0, sample="ref_onset.wav")
    # automation on FX macro 1 (song-specific in a real set), cleared in one test
    _envelope(fx, ls.automation_target_id(ls.macro(ls.rack(fx), 1)), [(0, 5), (1, 6)])
    _track(tracks, "ReturnTrack", 9, "A-Reverb", ids)
    main_track = SubElement(liveset, "MainTrack")
    _v(SubElement(main_track, "Name"), "EffectiveName", "Main")
    tempo = SubElement(SubElement(SubElement(main_track, "DeviceChain"), "Mixer"), "Tempo")
    _v(tempo, "Manual", "120")
    _v(liveset, "NextPointeeId", str(ids.n + 1))
    return root


def _write(root: Element, path: Path) -> str:
    with gzip.open(path, "wb") as f:
        f.write(ET.tostring(root, encoding="utf-8", xml_declaration=True))
    return str(path)


def _wav(path: Path, seconds: float, rate: int = 8000) -> str:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(seconds * rate))
    return str(path)


@pytest.fixture
def sets(tmp_path: Path) -> tuple[str, str, Path]:
    ref = _write(_live_set(reference=True), tmp_path / "ref.als")
    target = _write(_live_set(reference=False), tmp_path / "target.als")
    return ref, target, tmp_path


def _spec(ref: str, target: str, out: str, **sections: object) -> CloneSpec:
    return parse_spec({"reference": ref, "target": target, "output": out, **sections})


# ---------------------------------------------------------------------------
# Tracks
# ---------------------------------------------------------------------------

def test_cloned_track_maps_to_target_macro(sets: tuple[str, str, Path]) -> None:
    ref, target, tmp = sets
    sample = _wav(tmp / "song_onset.wav", seconds=3.0)
    out = str(tmp / "out.als")
    apply(_spec(ref, target, out, tracks=[{
        "template": "onset_signal", "name": "onset", "sample": sample, "align_to": "Lead",
        "map": {"track": "FX", "macro": 9, "rename": "water amp"}}]))

    root = ls.read_set(out)
    assert validate(root).ok
    macro = ls.macro(ls.rack(ls.find_track(root, "FX")), 9)
    macro_lom = ls.value(macro, "LomId")
    assert macro_lom != "0"
    new = ls.find_track(root, "onset")
    mapped = {ls.value(r, "LomId") for r in new.iter("MxDIdRef")} - {"0"}
    assert mapped == {macro_lom}
    assert ls.value(ls.rack(ls.find_track(root, "FX")), "MacroDisplayNames.8") == "water amp"
    names = [ls.track_name(t) for t in ls.tracks(root)]
    assert names.index("onset") == names.index("A-Reverb") - 1


def test_cloned_clip_points_at_sample_and_aligns(sets: tuple[str, str, Path]) -> None:
    ref, target, tmp = sets
    sample = _wav(tmp / "song_onset.wav", seconds=3.0)
    out = str(tmp / "out.als")
    apply(_spec(ref, target, out, tracks=[{
        "template": "onset_signal", "name": "onset", "sample": sample, "align_to": "Lead",
        "map": {"track": "FX", "macro": 11}}]))

    clip = next(ls.find_track(ls.read_set(out), "onset").iter("AudioClip"))
    assert ls.value(clip, "SampleRef/FileRef/Path") == sample
    assert ls.value(clip, "IsWarped") == "false"
    assert float(ls.attr(clip, "Time")) == 2.0                    # Lead's clip Time
    assert float(ls.value(clip, "Loop/LoopStart")) == 1.5          # Lead's LoopStart
    assert float(ls.value(clip, "Loop/LoopEnd")) == pytest.approx(3.0)
    assert float(ls.value(clip, "CurrentEnd")) == pytest.approx(2.0 + (3.0 - 1.5) * 2)  # 120 bpm


def test_pointees_renumbered_from_next_pointee_id(sets: tuple[str, str, Path]) -> None:
    ref, target, tmp = sets
    before = int(ls.value(ls.read_set(target), "LiveSet/NextPointeeId"))
    out = str(tmp / "out.als")
    item = {"template": "onset_signal", "sample": _wav(tmp / "s.wav", 1.0), "map": {"track": "FX", "macro": 11}}
    apply(_spec(ref, target, out, tracks=[{**item, "name": "a"}, {**item, "name": "b"}]))

    root = ls.read_set(out)
    report = validate(root)
    assert report.ok, report.problems
    new_ids = [int(ls.attr(e, "Id")) for name in ("a", "b") for e in ls.pointees(ls.find_track(root, name))]
    assert min(new_ids) >= before
    assert int(ls.value(root, "LiveSet/NextPointeeId")) == before + len(new_ids)


# ---------------------------------------------------------------------------
# Devices and automation
# ---------------------------------------------------------------------------

def test_cloned_device_inserted_and_mapped(sets: tuple[str, str, Path]) -> None:
    ref, target, tmp = sets
    out = str(tmp / "out.als")
    apply(_spec(ref, target, out, devices=[{
        "template_track": "Lead", "device_index": 0, "into": "Lead", "map": {"track": "FX", "macro": 1}}]))

    root = ls.read_set(out)
    assert validate(root).ok
    first = list(ls.devices(ls.find_track(root, "Lead")))[0]
    assert first.tag == "MxDeviceAudioEffect"
    macro_lom = ls.value(ls.macro(ls.rack(ls.find_track(root, "FX")), 1), "LomId")
    assert {ls.value(r, "LomId") for r in first.iter("MxDIdRef")} - {"0"} == {macro_lom}


def test_copy_and_clear_automation(sets: tuple[str, str, Path]) -> None:
    ref, target, tmp = sets
    out = str(tmp / "out.als")
    apply(_spec(ref, target, out,
                clear_automation=[{"track": "FX", "macro": 1}],
                copy_automation=[{"source": {"track": "Synth", "macro": 5}, "dest": {"track": "FX", "macro": 3}}]))

    root = ls.read_set(out)
    fx = ls.find_track(root, "FX")
    rack = ls.rack(fx)
    targets = [ls.envelope_target(e) for e in ls.envelopes(fx)]
    assert ls.automation_target_id(ls.macro(rack, 1)) not in targets
    dest_id = ls.automation_target_id(ls.macro(rack, 3))
    env = next(e for e in ls.envelopes(fx) if ls.envelope_target(e) == dest_id)
    assert [ls.attr(e, "Value") for e in ls.child(env, "Automation/Events")] == ["1", "2", "3"]  # target's own Synth curve
    assert validate(root).ok


def test_in_place_write_keeps_one_backup(sets: tuple[str, str, Path]) -> None:
    ref, target, _ = sets
    original = Path(target).read_bytes()
    spec = _spec(ref, target, target, clear_automation=[{"track": "FX", "macro": 1}])
    apply(spec)
    apply(spec)
    assert Path(target + ".bak").read_bytes() == original


# ---------------------------------------------------------------------------
# Errors and validation
# ---------------------------------------------------------------------------

def test_template_must_map_exactly_one_parameter(sets: tuple[str, str, Path]) -> None:
    ref, target, tmp = sets
    with pytest.raises(ls.AlsError, match="exactly one mapped parameter"):
        apply(_spec(ref, target, str(tmp / "o.als"), tracks=[{
            "template": "FX", "name": "x", "sample": _wav(tmp / "s.wav", 1.0), "map": {"track": "FX", "macro": 1}}]))


def test_cli_reports_missing_track(sets: tuple[str, str, Path], capsys: pytest.CaptureFixture[str]) -> None:
    ref, target, tmp = sets
    spec_path = tmp / "spec.json"
    spec_path.write_text(
        '{"reference": "%s", "target": "%s", "output": "%s", "clear_automation": [{"track": "Nope", "macro": 1}]}'
        % (ref, target, tmp / "o.als"))
    assert main([str(spec_path)]) == 1
    assert "no track named 'Nope'" in capsys.readouterr().err


@pytest.mark.parametrize("bad, message", [
    ({"reference": "a", "target": "b"}, "missing 'output'"),
    ({"reference": "a", "target": "b", "output": "c", "extra": 1}, "unknown field"),
    ({"reference": "a", "target": "b", "output": "c",
      "tracks": [{"template": "t", "name": "n", "sample": "s", "map": {"track": "R", "macro": True}}]},
     "map.macro: expected an integer"),
])
def test_parse_spec_rejects(bad: dict[str, object], message: str) -> None:
    with pytest.raises(ls.AlsError, match=message):
        parse_spec(bad)


def test_validate_flags_duplicates_and_unresolved_mappings() -> None:
    root = _live_set(reference=True)
    lead = ls.find_track(root, "Lead")
    ls.child(lead, "VolumeTarget").set("Id", ls.attr(ls.child(ls.find_track(root, "FX"), "VolumeTarget"), "Id"))
    SubElement(SubElement(lead, "IdRefList"), "MxDIdRef").append(Element("LomId", Value="999"))
    report = validate(root)
    assert report.duplicate_pointee_ids
    assert report.unresolved_mappings == ["999"]
    assert not report.ok


def test_reference_fixture_is_valid() -> None:
    assert validate(_live_set(reference=True)).ok
    assert validate(_live_set(reference=False)).ok


def test_find_track_reaches_main_track(sets: tuple[str, str, Path]) -> None:
    root = ls.read_set(sets[0])
    assert ls.find_track(root, "Main") is ls.main_track(root)
    assert ls.main_track(root) in ls.all_tracks(root)


def test_main_track_accepts_older_master_track() -> None:
    root = Element("Ableton")
    live = SubElement(root, "LiveSet")
    SubElement(live, "Tracks")
    master = SubElement(live, "MasterTrack")
    _v(SubElement(master, "Name"), "EffectiveName", "Master")
    assert ls.main_track(root) is master
    with pytest.raises(ls.AlsError, match="no track named"):
        ls.find_track(root, "Nope")

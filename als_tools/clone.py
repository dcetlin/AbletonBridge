"""Copy Max for Live-mapped tracks and devices, and rack-macro automation, from a
reference Live set into a target set.

Use this when a setup has to be replicated across sets and the LOM can't do it,
e.g. an Envelope Follower's Map. See `als_tools.liveset` for how mappings are
stored. Close the target set in Live first, or Live overwrites the edit on its next
save.

    als-clone spec.json        # spec format: als_tools.spec.CloneSpec
"""

from __future__ import annotations

import copy
import json
import os
import sys
import wave
from dataclasses import dataclass, field
from xml.etree.ElementTree import Element

from als_tools import liveset as ls
from als_tools.spec import AutomationCopy, CloneSpec, DeviceItem, MacroRef, MacroTarget, TrackItem, parse_spec


@dataclass
class _Ids:
    """Next free ids in the target set."""
    lom: int
    track: int


@dataclass
class CloneResult:
    output: str
    actions: list[str] = field(default_factory=list[str])


# ---------------------------------------------------------------------------
# Mapping
# ---------------------------------------------------------------------------

def _mapped_lom_id(el: Element, label: str) -> str:
    """The one nonzero LomId that `el`'s Max mappings point at."""
    loms = {ls.value(ref, "LomId") for ref in el.iter("MxDIdRef")} - {"0"}
    if len(loms) != 1:
        raise ls.AlsError(f"{label}: expected exactly one mapped parameter, found LomIds {sorted(loms)}")
    return loms.pop()


def _retarget(el: Element, target: MacroTarget, root: Element, ids: _Ids, label: str) -> str:
    """Renumber `el` for the target set and point its mapping at `target`.
    Returns the macro's LomId."""
    ref_lom = _mapped_lom_id(el, label)
    ls.renumber_pointees(el, root)
    rack = ls.rack(ls.find_track(root, target["track"]))
    mac = ls.macro(rack, target["macro"])
    if ls.value(mac, "LomId") == "0":
        ls.set_value(mac, "LomId", str(ids.lom))
        ids.lom += 1
    macro_lom = ls.value(mac, "LomId")
    ids.lom = ls.renumber_lom_ids(el, ids.lom, keep={ref_lom})
    for ref in el.iter("MxDIdRef"):
        if ls.value(ref, "LomId") == ref_lom:
            ls.set_value(ref, "LomId", macro_lom)
    if "rename" in target:
        ls.set_value(rack, f"MacroDisplayNames.{target['macro'] - 1}", target["rename"])
    return macro_lom


# ---------------------------------------------------------------------------
# Automation
# ---------------------------------------------------------------------------

def _macro_envelopes(root: Element, ref: MacroRef) -> tuple[Element, str, list[Element]]:
    """(the track's Envelopes element, the macro's target id, envelopes driving it)."""
    track = ls.find_track(root, ref["track"])
    target_id = ls.automation_target_id(ls.macro(ls.rack(track), ref["macro"]))
    envs = ls.envelopes(track)
    return envs, target_id, [e for e in envs if ls.envelope_target(e) == target_id]


def clear_automation(root: Element, ref: MacroRef) -> str:
    envs, _, found = _macro_envelopes(root, ref)
    for e in found:
        envs.remove(e)
    return f"cleared {ref['track']} macro {ref['macro']} ({len(found)} envelope)"


def copy_automation(root: Element, item: AutomationCopy) -> str:
    _, _, src = _macro_envelopes(root, item["source"])
    if not src:
        raise ls.AlsError(f"{item['source']['track']} macro {item['source']['macro']} has no automation")
    envs, dest_id, old = _macro_envelopes(root, item["dest"])
    for e in old:
        envs.remove(e)
    new = copy.deepcopy(src[0])
    new.set("Id", str(max((int(ls.attr(e, "Id")) for e in envs), default=-1) + 1))
    ls.set_value(new, "EnvelopeTarget/PointeeId", dest_id)
    envs.append(new)
    points = len(ls.child(new, "Automation/Events"))
    s, d = item["source"], item["dest"]
    return f"copied {s['track']} macro {s['macro']} -> {d['track']} macro {d['macro']} ({points} points)"


# ---------------------------------------------------------------------------
# Devices and tracks
# ---------------------------------------------------------------------------

def clone_device(ref_root: Element, root: Element, item: DeviceItem, ids: _Ids) -> str:
    chain = list(ls.devices(ls.find_track(ref_root, item["template_track"])))
    if not 0 <= item["device_index"] < len(chain):
        raise ls.AlsError(f"{item['template_track']!r} has no device {item['device_index']}")
    dev = copy.deepcopy(chain[item["device_index"]])
    lom = _retarget(dev, item["map"], root, ids, f"{item['template_track']} device {item['device_index']}")
    dest = ls.devices(ls.find_track(root, item["into"]))
    dev.set("Id", str(max((int(ls.attr(d, "Id")) for d in dest), default=-1) + 1))
    dest.insert(item.get("position", 0), dev)
    m = item["map"]
    return f"device {dev.tag} -> {item['into']}, mapped to {m['track']} macro {m['macro']} (LomId {lom})"


def _wav_frames(path: str) -> tuple[int, int]:
    with wave.open(path, "rb") as w:
        return w.getnframes(), w.getframerate()


def _set_sample(clip: Element, sample: str, set_dir: str) -> float:
    """Point `clip` at `sample` (unwarped). Returns the sample length in seconds."""
    frames, rate = _wav_frames(sample)
    for ref in clip.iter("FileRef"):
        ls.set_value(ref, "RelativePath", os.path.relpath(sample, set_dir))
        ls.set_value(ref, "Path", sample)
        ls.set_value(ref, "OriginalFileSize", str(os.path.getsize(sample)))
        ls.set_value(ref, "OriginalCrc", "0")
    sref = ls.child(clip, "SampleRef")
    ls.set_value(sref, "LastModDate", str(int(os.path.getmtime(sample))))
    for tag, val in (("DefaultDuration", frames), ("DefaultSampleRate", rate)):
        if sref.find(tag) is not None:
            ls.set_value(sref, tag, str(val))
    browser = clip.find(".//SourceContext/SourceContext/BrowserContentPath")
    if browser is not None:
        browser.set("Value", "")
    ls.set_value(clip, "Name", os.path.splitext(os.path.basename(sample))[0])
    ls.set_value(clip, "IsWarped", "false")
    return frames / rate


def _place_clip(clip: Element, seconds: float, bpm: float, anchor: Element | None) -> None:
    """Unwarped clip: Loop* and OutMarker are seconds into the file; Time and
    Current* are beats on the timeline. With an anchor, start where it starts."""
    t0 = float(ls.attr(anchor, "Time")) if anchor is not None else 0.0
    start = float(ls.value(anchor, "Loop/LoopStart")) if anchor is not None else 0.0
    clip.set("Time", repr(t0))
    ls.set_value(clip, "CurrentStart", repr(t0))
    ls.set_value(clip, "CurrentEnd", repr(t0 + (seconds - start) * bpm / 60.0))
    for path, val in (("Loop/LoopStart", repr(start)), ("Loop/LoopEnd", repr(seconds)),
                      ("Loop/StartRelative", "0"), ("Loop/LoopOn", "false"),
                      ("Loop/OutMarker", repr(seconds))):
        ls.set_value(clip, path, val)


def clone_track(ref_root: Element, root: Element, item: TrackItem, ids: _Ids, set_dir: str) -> Element:
    new = copy.deepcopy(ls.find_track(ref_root, item["template"]))
    new.set("Id", str(ids.track))
    ids.track += 1
    for tag in ("EffectiveName", "UserName"):
        ls.set_value(new, f"Name/{tag}", item["name"])
    _retarget(new, item["map"], root, ids, item["template"])

    clips = list(new.iter("AudioClip"))
    if len(clips) != 1:
        raise ls.AlsError(f"{item['template']!r}: expected 1 audio clip, found {len(clips)}")
    anchor = None
    if "align_to" in item:
        anchor = next(ls.find_track(root, item["align_to"]).iter("AudioClip"), None)
        if anchor is None:
            raise ls.AlsError(f"{item['align_to']!r} has no audio clip to align to")
    seconds = _set_sample(clips[0], item["sample"], set_dir)
    _place_clip(clips[0], seconds, ls.tempo(root), anchor)
    return new


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def apply(spec: CloneSpec) -> CloneResult:
    """Apply `spec` and write the result. Runs clear_automation, copy_automation,
    devices, then tracks."""
    ref_root = ls.read_set(spec["reference"])
    root = ls.read_set(spec["target"])
    track_list = ls.tracks(root)
    ids = _Ids(lom=max(ls.max_lom_id(root), ls.max_lom_id(ref_root)) + 1,
               track=max(int(ls.attr(t, "Id")) for t in track_list) + 1)
    result = CloneResult(output=spec["output"])

    for ref in spec.get("clear_automation", []):
        result.actions.append(clear_automation(root, ref))
    for auto in spec.get("copy_automation", []):
        result.actions.append(copy_automation(root, auto))
    for dev in spec.get("devices", []):
        result.actions.append(clone_device(ref_root, root, dev, ids))

    set_dir = os.path.dirname(os.path.abspath(spec["target"]))
    insert_at = next(i for i, t in enumerate(track_list) if t.tag == "ReturnTrack")
    for trk in spec.get("tracks", []):
        track_list.insert(insert_at, clone_track(ref_root, root, trk, ids, set_dir))
        insert_at += 1
        m = trk["map"]
        result.actions.append(f"track {trk['name']} ({os.path.basename(trk['sample'])}) "
                              f"-> {m['track']} macro {m['macro']}")

    ls.write_set(root, spec["output"], backup=os.path.abspath(spec["output"]) == os.path.abspath(spec["target"]))
    return result


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: als-clone spec.json", file=sys.stderr)
        return 2
    try:
        with open(args[0]) as f:
            result = apply(parse_spec(json.load(f)))
    except ls.AlsError as e:
        print(f"als-clone: {e}", file=sys.stderr)
        return 1
    for line in result.actions:
        print(line)
    print(f"wrote {result.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

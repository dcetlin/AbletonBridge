"""Copy Max for Live mappings, tracks and rack-macro automation between Live sets by
editing the .als files.

Use it when you need to replicate one set's setup across other sets. An Envelope
Follower's Map, for example, cannot be set through the Live Object Model, so a live
MCP session cannot rebuild it.

How Live stores a Max device's mapping: an MxDIdRef inside the device holds a LomId,
and the mapped parameter (e.g. a rack macro) carries the same LomId. LomIds and
pointee Ids are numbered per set, so a plain copy breaks the link. This tool
renumbers both for the target set and re-points the mapping.

Close the target set in Live before running, or Live will overwrite the edit on its
next save. When output == target, a .bak copy is written once.

Spec (JSON). Every section is optional and they run in this order:
{
  "reference": "/path/reference.als",
  "target":    "/path/target.als",
  "output":    "/path/out.als",

  "clear_automation": [ {"track": "FX Rack", "macro": 1} ],

  "copy_automation":  [ {"from": {"track": "Synth", "macro": 5},
                         "to":   {"track": "FX Rack", "macro": 3}} ],

  "devices": [ {"template_track": "Lead",  "device_index": 0,     # in the reference
                "into": "Lead", "position": 0,                    # in the target
                "map": {"track": "FX Rack", "macro": 1}} ],

  "tracks":  [ {"template": "onset_signal", "name": "onset_signal",
                "sample": "/abs/path/onset.wav",                  # unwarped
                "align_to": "Lead",           # target track whose first audio clip gives Time/LoopStart
                "map": {"track": "FX Rack", "macro": 11, "rename": "onset"}} ]
}

Macros are 1-based. A template (track or device) must map exactly one parameter.
Validate the result with scripts/als_validate.py, then open the set in Live once.
"""
import copy
import gzip
import json
import os
import shutil
import sys
import wave
import xml.etree.ElementTree as ET


def read_set(path):
    with gzip.open(path, "rb") as f:
        return ET.parse(f)


def write_set(tree, path):
    data = ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True)
    tmp = path + ".tmp"
    with gzip.open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


def track_name(t):
    return t.find("Name/EffectiveName").get("Value")


def find_track(root, name):
    for t in root.find("LiveSet/Tracks"):
        if track_name(t) == name:
            return t
    raise SystemExit(f"track not found: {name!r}")


def rack_macro(track, macro):
    """The MacroControls.N element (1-based macro) of the track's first rack."""
    for tag in ("AudioEffectGroupDevice", "InstrumentGroupDevice", "MidiEffectGroupDevice"):
        rack = track.find(f"DeviceChain/DeviceChain/Devices/{tag}")
        if rack is not None:
            return rack, rack.find(f"MacroControls.{macro - 1}")
    raise SystemExit(f"no rack on track {track_name(track)!r}")


def max_lom_id(root):
    return max(int(e.get("Value")) for e in root.iter("LomId"))


def wav_info(path):
    with wave.open(path, "rb") as w:
        return w.getnframes(), w.getframerate()


POINTEE_REF_TAGS = ("PointeeId",)  # <EnvelopeTarget><PointeeId Value=..>


def renumber_pointees(track, root):
    """Give every Id-bearing pointee element in `track` a fresh Id from NextPointeeId."""
    npid = root.find("LiveSet/NextPointeeId")
    nxt = int(npid.get("Value"))
    remap = {}
    for e in track.iter():
        if e is track:
            continue
        if (e.tag == "Pointee" or e.tag.endswith("Target")) and e.get("Id") is not None:
            remap[e.get("Id")] = str(nxt)
            e.set("Id", str(nxt))
            nxt += 1
    for e in track.iter("PointeeId"):
        if e.get("Value") in remap:
            e.set("Value", remap[e.get("Value")])
    npid.set("Value", str(nxt))


def renumber_lom_ids(track, start, keep):
    """Renumber nonzero LomIds inside `track` from `start`; values in `keep` are left
    alone (they point outside the track and are retargeted separately)."""
    remap = {}
    nxt = start
    for e in track.iter("LomId"):
        v = e.get("Value")
        if v == "0" or v in keep:
            continue
        if v not in remap:
            remap[v] = str(nxt)
            nxt += 1
        e.set("Value", remap[v])
    return nxt


def set_sample(clip, sample, set_dir, anchor):
    frames, rate = wav_info(sample)
    seconds = frames / rate
    rel = os.path.relpath(sample, set_dir)
    for fr in clip.iter("FileRef"):
        fr.find("RelativePath").set("Value", rel)
        fr.find("Path").set("Value", sample)
        fr.find("OriginalFileSize").set("Value", str(os.path.getsize(sample)))
        fr.find("OriginalCrc").set("Value", "0")
    sr = clip.find("SampleRef")
    sr.find("LastModDate").set("Value", str(int(os.path.getmtime(sample))))
    for tag, val in (("DefaultDuration", frames), ("DefaultSampleRate", rate)):
        e = sr.find(tag)
        if e is not None:
            e.set("Value", str(val))
    bcp = clip.find(".//SourceContext/SourceContext/BrowserContentPath")
    if bcp is not None:
        bcp.set("Value", "")
    clip.find("Name").set("Value", os.path.splitext(os.path.basename(sample))[0])
    clip.find("IsWarped").set("Value", "false")
    return seconds


def place_clip(clip, seconds, tempo, anchor_clip):
    """Unwarped clip: Loop* and OutMarker are seconds in the file; Time/Current* are beats."""
    t0 = float(anchor_clip.get("Time")) if anchor_clip is not None else 0.0
    start_s = float(anchor_clip.find("Loop/LoopStart").get("Value")) if anchor_clip is not None else 0.0
    beats = (seconds - start_s) * tempo / 60.0
    clip.set("Time", repr(t0))
    clip.find("CurrentStart").set("Value", repr(t0))
    clip.find("CurrentEnd").set("Value", repr(t0 + beats))
    loop = clip.find("Loop")
    loop.find("LoopStart").set("Value", repr(start_s))
    loop.find("LoopEnd").set("Value", repr(seconds))
    loop.find("StartRelative").set("Value", "0")
    loop.find("LoopOn").set("Value", "false")
    loop.find("OutMarker").set("Value", repr(seconds))


def clone(spec):
    ref = read_set(spec["reference"]).getroot()
    tree = read_set(spec["target"])
    root = tree.getroot()
    set_dir = os.path.dirname(os.path.abspath(spec["target"]))
    tempo = float(root.find(".//MainTrack/DeviceChain/Mixer/Tempo/Manual").get("Value"))
    tracks_el = root.find("LiveSet/Tracks")
    first_return = next(i for i, t in enumerate(tracks_el) if t.tag == "ReturnTrack")
    next_track_id = max(int(t.get("Id")) for t in tracks_el) + 1
    lom_next = max(max_lom_id(root), max_lom_id(ref)) + 1
    report = []

    lom = [lom_next]

    def retarget(el, m, label):
        """Renumber `el`'s pointees and LomIds for the target set, and point its one
        mapping at macro m["macro"] of the rack on track m["track"]."""
        ref_loms = {x.find("LomId").get("Value") for x in el.iter("MxDIdRef")} - {"0"}
        if len(ref_loms) != 1:
            raise SystemExit(f"{label}: expected one mapped LomId, found {sorted(ref_loms)}")
        ref_lom = ref_loms.pop()
        renumber_pointees(el, root)
        rack, macro = rack_macro(find_track(root, m["track"]), m["macro"])
        if macro.find("LomId").get("Value") == "0":
            macro.find("LomId").set("Value", str(lom[0])); lom[0] += 1
        target_lom = macro.find("LomId").get("Value")
        lom[0] = renumber_lom_ids(el, lom[0], keep={ref_lom})
        for x in el.iter("MxDIdRef"):
            if x.find("LomId").get("Value") == ref_lom:
                x.find("LomId").set("Value", target_lom)
        if m.get("rename"):
            rack.find(f"MacroDisplayNames.{m['macro'] - 1}").set("Value", m["rename"])
        return target_lom

    for item in spec.get("clear_automation", []):
        track = find_track(root, item["track"])
        _, macro = rack_macro(track, item["macro"])
        envs = track.find("AutomationEnvelopes/Envelopes")
        aid = macro.find("AutomationTarget").get("Id")
        gone = [e for e in envs if e.find("EnvelopeTarget/PointeeId").get("Value") == aid]
        for e in gone:
            envs.remove(e)
        report.append(f"cleared {item['track']} macro {item['macro']} automation ({len(gone)} envelope)")

    for item in spec.get("copy_automation", []):
        src_t = find_track(root, item["from"]["track"]); dst_t = find_track(root, item["to"]["track"])
        _, src_m = rack_macro(src_t, item["from"]["macro"]); _, dst_m = rack_macro(dst_t, item["to"]["macro"])
        sid = src_m.find("AutomationTarget").get("Id"); did = dst_m.find("AutomationTarget").get("Id")
        src_env = next(e for e in src_t.find("AutomationEnvelopes/Envelopes")
                       if e.find("EnvelopeTarget/PointeeId").get("Value") == sid)
        envs = dst_t.find("AutomationEnvelopes/Envelopes")
        for e in [e for e in envs if e.find("EnvelopeTarget/PointeeId").get("Value") == did]:
            envs.remove(e)
        new_env = copy.deepcopy(src_env)
        new_env.set("Id", str(max([int(e.get("Id")) for e in envs] + [-1]) + 1))
        new_env.find("EnvelopeTarget/PointeeId").set("Value", did)
        envs.append(new_env)
        n = len(new_env.find("Automation/Events"))
        report.append(f"copied {item['from']['track']} macro {item['from']['macro']} -> "
                      f"{item['to']['track']} macro {item['to']['macro']} ({n} points)")

    for item in spec.get("devices", []):
        src = find_track(ref, item["template_track"])
        dev = copy.deepcopy(list(src.find("DeviceChain/DeviceChain/Devices"))[item["device_index"]])
        target_lom = retarget(dev, item["map"], f"{item['template_track']} device {item['device_index']}")
        devices = find_track(root, item["into"]).find("DeviceChain/DeviceChain/Devices")
        dev.set("Id", str(max([int(d.get("Id")) for d in devices] + [-1]) + 1))
        devices.insert(item.get("position", 0), dev)
        report.append(f"device {dev.tag} from {item['template_track']} -> {item['into']}, "
                      f"mapped to {item['map']['track']} macro {item['map']['macro']} (LomId {target_lom})")

    for item in spec.get("tracks", []):
        tmpl = find_track(ref, item["template"])
        m = item["map"]
        new = copy.deepcopy(tmpl)
        new.set("Id", str(next_track_id)); next_track_id += 1
        for tag in ("EffectiveName", "UserName"):
            new.find(f"Name/{tag}").set("Value", item["name"])
        target_lom = retarget(new, m, item["template"])

        clips = list(new.iter("AudioClip"))
        if len(clips) != 1:
            raise SystemExit(f"{item['template']}: expected 1 audio clip, found {len(clips)}")
        anchor = None
        if item.get("align_to"):
            anchor = next(find_track(root, item["align_to"]).iter("AudioClip"), None)
        seconds = set_sample(clips[0], item["sample"], set_dir, anchor)
        place_clip(clips[0], seconds, tempo, anchor)

        tracks_el.insert(first_return, new); first_return += 1
        report.append(f"{item['name']}: {os.path.basename(item['sample'])} ({seconds:.1f}s) -> "
                      f"{m['track']} macro {m['macro']} (LomId {target_lom})")

    out = spec["output"]
    if os.path.abspath(out) == os.path.abspath(spec["target"]):
        bak = out + ".bak"
        if not os.path.exists(bak):
            shutil.copy2(out, bak)
    write_set(tree, out)
    return report


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        for line in clone(json.load(f)):
            print(line)

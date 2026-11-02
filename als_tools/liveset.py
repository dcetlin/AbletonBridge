"""Reading, writing and navigating a Live set (.als) as XML.

A .als file is gzip-compressed XML. Two kinds of identifier matter when moving
elements between sets:

- **Pointee Ids**: the `Id` attribute on `Pointee` and `*Target` elements (e.g.
  `AutomationTarget`). They are unique per set and allocated from
  `LiveSet/NextPointeeId`. `PointeeId Value=...` elements refer to them; an
  automation envelope uses one to name the parameter it drives.
- **LomIds**: `LomId Value=...` on objects that something in the set refers to. A
  Max device's mapping is an `MxDIdRef` whose `LomId` equals the LomId of the
  mapped parameter. `0` means "no LomId assigned".
"""

from __future__ import annotations

import gzip
import os
import shutil
import xml.etree.ElementTree as ET
import zlib
from collections.abc import Iterator
from xml.etree.ElementTree import Element

RACK_TAGS = ("AudioEffectGroupDevice", "InstrumentGroupDevice", "MidiEffectGroupDevice")
# Every device that holds chains. rack() finds only RACK_TAGS, so a track's first rack stays stable.
CONTAINER_TAGS = (*RACK_TAGS, "DrumGroupDevice")


class AlsError(Exception):
    """A Live set doesn't have the structure an operation expects."""


# ---------------------------------------------------------------------------
# Element access that fails loudly instead of returning None
# ---------------------------------------------------------------------------

def child(el: Element, path: str) -> Element:
    found = el.find(path)
    if found is None:
        raise AlsError(f"<{el.tag}> has no {path}")
    return found


def attr(el: Element, name: str) -> str:
    value = el.get(name)
    if value is None:
        raise AlsError(f"<{el.tag}> has no {name} attribute")
    return value


def value(el: Element, path: str) -> str:
    """The `Value` attribute of the element at `path`."""
    return attr(child(el, path), "Value")


def to_int(text: str, where: str) -> int:
    try:
        return int(text)
    except ValueError:
        raise AlsError(f"{where}: {text!r} is not an integer") from None


def set_value(el: Element, path: str, new: str) -> None:
    child(el, path).set("Value", new)


# ---------------------------------------------------------------------------
# File IO
# ---------------------------------------------------------------------------

def read_set(path: str) -> Element:
    """The root (<Ableton>) element of the set at `path`. A file that can't be read as
    a set raises AlsError naming it."""
    try:
        with gzip.open(path, "rb") as f:
            return ET.parse(f).getroot()
    except (OSError, EOFError, ET.ParseError, zlib.error) as e:
        raise AlsError(f"can't read {path}: {e}") from e


def write_set(root: Element, path: str, backup: bool = True) -> None:
    """Write `root` to `path` atomically. With `backup`, an existing file is copied to
    `<path>.bak` the first time it is overwritten."""
    if backup and os.path.exists(path) and not os.path.exists(path + ".bak"):
        shutil.copy2(path, path + ".bak")
    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    tmp = path + ".tmp"
    with gzip.open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def tracks(root: Element) -> Element:
    return child(root, "LiveSet/Tracks")


def main_track(root: Element) -> Element:
    """Live's main output track. It sits outside LiveSet/Tracks and can hold devices.

    Live 12 calls it MainTrack; earlier versions call it MasterTrack.
    """
    found = root.find("LiveSet/MainTrack")
    return found if found is not None else child(root, "LiveSet/MasterTrack")


def all_tracks(root: Element) -> list[Element]:
    """Every track that can hold devices. Use this for audits, not tracks()."""
    return [*tracks(root), main_track(root)]


def track_name(track: Element) -> str:
    return value(track, "Name/EffectiveName")


def find_track(root: Element, name: str) -> Element:
    for t in all_tracks(root):
        if track_name(t) == name:
            return t
    raise AlsError(f"no track named {name!r}")


def devices(track: Element) -> Element:
    return child(track, "DeviceChain/DeviceChain/Devices")


def rack(track: Element) -> Element:
    """The first rack device on the track."""
    for dev in devices(track):
        if dev.tag in RACK_TAGS:
            return dev
    raise AlsError(f"track {track_name(track)!r} has no rack")


def own_devices(rack_el: Element, tag: str) -> Iterator[Element]:
    """Devices with this tag in the rack's chains, not looking inside nested racks."""
    for sub in rack_el:
        if sub.tag == tag:
            yield sub
        if sub.tag not in CONTAINER_TAGS:
            yield from own_devices(sub, tag)


def macro(rack_el: Element, number: int) -> Element:
    """MacroControls element for a 1-based macro number."""
    if not 1 <= number <= 16:
        raise AlsError(f"macro {number} out of range 1-16")
    return child(rack_el, f"MacroControls.{number - 1}")


def envelopes(track: Element) -> Element:
    return child(track, "AutomationEnvelopes/Envelopes")


def envelope_target(env: Element) -> str:
    return value(env, "EnvelopeTarget/PointeeId")


def automation_target_id(param: Element) -> str:
    return attr(child(param, "AutomationTarget"), "Id")


def tempo(root: Element) -> float:
    return float(value(main_track(root), "DeviceChain/Mixer/Tempo/Manual"))


# ---------------------------------------------------------------------------
# Identifiers
# ---------------------------------------------------------------------------

def is_pointee(el: Element) -> bool:
    return el.get("Id") is not None and (el.tag == "Pointee" or el.tag.endswith("Target"))


def pointees(el: Element) -> Iterator[Element]:
    return (e for e in el.iter() if is_pointee(e))


def lom_definitions(root: Element) -> Iterator[Element]:
    """Nonzero LomId elements that define an id rather than refer to one."""
    for holder in root.iter():
        if holder.tag == "MxDIdRef":
            continue
        for lom in holder.findall("LomId"):
            if attr(lom, "Value") != "0":
                yield lom


def max_lom_id(root: Element) -> int:
    return max((to_int(attr(e, "Value"), "LomId") for e in root.iter("LomId")), default=0)


def renumber_pointees(el: Element, root: Element) -> None:
    """Give every pointee inside `el` a fresh Id from the set's NextPointeeId, and
    update PointeeId references inside `el` to match."""
    counter = child(root, "LiveSet/NextPointeeId")
    nxt = to_int(attr(counter, "Value"), "NextPointeeId")
    remap: dict[str, str] = {}
    for e in pointees(el):
        if e is el:
            continue
        remap[attr(e, "Id")] = str(nxt)
        e.set("Id", str(nxt))
        nxt += 1
    for ref in el.iter("PointeeId"):
        old = attr(ref, "Value")
        if old in remap:
            ref.set("Value", remap[old])
    counter.set("Value", str(nxt))


def renumber_lom_ids(el: Element, start: int, keep: set[str]) -> int:
    """Renumber nonzero LomIds inside `el` consistently, starting at `start`. Values
    in `keep` are left alone. Returns the next free LomId."""
    remap: dict[str, str] = {}
    nxt = start
    for e in el.iter("LomId"):
        old = attr(e, "Value")
        if old == "0" or old in keep:
            continue
        if old not in remap:
            remap[old] = str(nxt)
            nxt += 1
        e.set("Value", remap[old])
    return nxt

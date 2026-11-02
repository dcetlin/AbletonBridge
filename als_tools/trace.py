"""Trace each rack macro from what feeds it to the OSC address it reaches.

    als-trace set.als [more.als ...]     # exit 1 if any signal path is broken

A macro's path has three links: a Max device mapped to it (or its automation), a
plugin parameter mapped to it, and that parameter's OSC address in the plugin's
saved state. als-validate can't see a missing link, because the file is consistent
without it. This reads the file only: a clean trace still needs a playback check.
"""

from __future__ import annotations

import re
import struct
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Literal
from xml.etree.ElementTree import Element

from als_tools import liveset as ls

MACRO_COUNT = 16
MAX_DEVICE_TAGS = ("MxDeviceAudioEffect", "MxDeviceMidiEffect", "MxDeviceInstrument")
STATE_MAGIC = b"VC2!"

Status = Literal[
    "ok", "unused", "no feeder", "stops at macro", "no OSC address", "multiple devices", "name mismatch"
]
BROKEN: frozenset[Status] = frozenset(
    {"stops at macro", "no OSC address", "multiple devices", "name mismatch"}
)


@dataclass(frozen=True)
class Slot:
    label: str
    address: str | None


@dataclass(frozen=True)
class MacroTrace:
    number: int
    name: str
    devices: tuple[str, ...]
    automated: bool
    slots: tuple[Slot, ...]

    @property
    def status(self) -> Status:
        if len(self.devices) > 1:
            return "multiple devices"
        fed = bool(self.devices) or self.automated
        if not fed:
            return "no feeder" if self.slots else "unused"
        if not self.slots:
            return "stops at macro"
        if any(s.address is None for s in self.slots):
            return "no OSC address"
        if not all(_names_match(self.name, s.address) for s in self.slots):
            return "name mismatch"
        return "ok"


def _names_match(macro_name: str, address: str | None) -> bool:
    """Whether a named macro agrees with its OSC address. Default names ("Macro 9") always do."""
    if address is None or re.fullmatch(r"Macro \d+", macro_name):
        return True
    wanted = re.sub(r"[^a-z0-9]", "", re.sub(r"\bsignal\b", "", macro_name.lower()))
    return wanted == address.rsplit("/", 1)[-1].lower()


def juce_hash(text: str) -> int:
    """A plugin's ParameterId: the JUCE string hash of the parameter name."""
    h = 0
    for char in text:
        h = (31 * h + ord(char)) & 0xFFFFFFFF
    return h & 0x7FFFFFFF


def osc_addresses(plugin: Element) -> dict[int, str] | None:
    """Parameter id -> OSC address from a plugin's saved state, or None if it has no list."""
    state = plugin.find(".//ProcessorState")
    if state is None or state.text is None:
        return None
    try:
        blob = bytes.fromhex(re.sub(r"\s", "", state.text))
    except ValueError:
        return None
    if blob[:4] != STATE_MAGIC:
        return None
    size = struct.unpack("<I", blob[4:8])[0]
    try:
        params = ET.fromstring(blob[8 : 8 + size].rstrip(b"\0")).find("OSCParameters")
    except ET.ParseError:
        return None
    if params is None:
        return None
    return {juce_hash(ls.attr(p, "parameterName")): ls.attr(p, "oscAddress") for p in params}


def find_hub(root: Element) -> tuple[Element, Element, dict[int, str]] | None:
    """The first track whose rack holds a plugin with an OSC list."""
    for track in ls.tracks(root):
        for rack in ls.devices(track):
            if rack.tag not in ls.RACK_TAGS:
                continue
            for plugin in rack.iter("PluginDevice"):
                addresses = osc_addresses(plugin)
                if addresses is not None:
                    return track, rack, addresses
    return None


def _device_label(device: Element) -> str:
    path = next((p.get("Value") for p in device.iter("Path") if p.get("Value")), None)
    return PurePosixPath(path).name if path else device.tag


def _max_devices(root: Element) -> list[tuple[str, Element]]:
    return [
        (ls.track_name(track), device)
        for track in ls.all_tracks(root)
        for tag in MAX_DEVICE_TAGS
        for device in track.iter(tag)
    ]


def _is_automated(track: Element, macro: Element) -> bool:
    target = ls.automation_target_id(macro)
    for envelope in ls.envelopes(track):
        if ls.envelope_target(envelope) == target:
            return len({e.get("Value") for e in envelope.iter("FloatEvent")}) > 1
    return False


def _mapped_slots(rack: Element, addresses: dict[int, str]) -> dict[int, list[Slot]]:
    slots: dict[int, list[Slot]] = {}
    for param in rack.iter("PluginFloatParameter"):
        mapping = param.find("ParameterValue/KeyMidi")
        if mapping is None:
            continue
        number = int(ls.value(mapping, "NoteOrController")) + 1
        address = addresses.get(int(ls.value(param, "ParameterId")))
        slots.setdefault(number, []).append(Slot(ls.value(param, "ParameterName").strip(), address))
    return slots


def trace(root: Element) -> list[MacroTrace] | None:
    """One entry per macro of the OSC rack, or None if the set has no such rack."""
    hub = find_hub(root)
    if hub is None:
        return None
    track, rack, addresses = hub
    slots = _mapped_slots(rack, addresses)
    devices = _max_devices(root)
    result: list[MacroTrace] = []
    for number in range(1, MACRO_COUNT + 1):
        macro = ls.macro(rack, number)
        lom = ls.value(macro, "LomId")
        feeders = (
            tuple(
                f"{name}: {_device_label(device)}"
                for name, device in devices
                if lom in {ls.value(r, "LomId") for r in device.iter("MxDIdRef")}
            )
            if lom != "0"
            else ()
        )
        result.append(
            MacroTrace(
                number=number,
                name=ls.value(rack, f"MacroDisplayNames.{number - 1}"),
                devices=feeders,
                automated=_is_automated(track, macro),
                slots=tuple(slots.get(number, ())),
            )
        )
    return result


def _line(entry: MacroTrace) -> str:
    source = ", ".join(entry.devices) or ("automation" if entry.automated else "-")
    target = ", ".join(s.address or f"{s.label}: no address" for s in entry.slots) or "-"
    return f"  M{entry.number:<2} {entry.name:<22} {source} -> {target}  [{entry.status}]"


def main(argv: list[str] | None = None) -> int:
    paths = sys.argv[1:] if argv is None else argv
    if not paths:
        print("usage: als-trace set.als [more.als ...]", file=sys.stderr)
        return 2
    failed = False
    for path in paths:
        entries = trace(ls.read_set(path))
        print(path)
        if entries is None:
            print("  no rack with an OSC plugin")
            failed = True
            continue
        for entry in entries:
            if entry.status != "unused":
                print(_line(entry))
        failed = failed or any(e.status in BROKEN for e in entries)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

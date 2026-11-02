"""Trace each rack macro from what feeds it to the OSC address it reaches.

    als-trace [--strict] set.als [more.als ...]

Exit 1 if a signal path is broken. --strict also fails on the warnings below.

A macro's path has three links: a Max device mapped to it (or moving automation), a
plugin parameter mapped to it, and that parameter's OSC address in the plugin's saved
state. als-validate can't see a missing link, because the file is consistent without
it. This reads the file only: a clean trace still needs a playback check.

Supported plugins are Nativize, or any JUCE VST3 saving the same <OSCParameters> list
of <Parameter parameterName oscAddress oscOutputEnabled> elements. A set with no such
plugin has nothing to trace. Devices and plugins switched off don't count, but a device
inside a rack that's switched off still does.
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import PureWindowsPath
from typing import Literal
from xml.etree.ElementTree import Element

from als_tools import liveset as ls

MAX_DEVICE_TAGS = ("MxDeviceAudioEffect", "MxDeviceMidiEffect", "MxDeviceInstrument")
RACK_TAGS = (*ls.RACK_TAGS, "DrumGroupDevice")
JUCE_XML_MAGIC = b"VC2!"  # header of JUCE's copyXmlToBinary state
MACRO_MAP_CHANNEL = "16"  # Live stores macro mappings as KeyMidi on channel 16

Status = Literal[
    "ok",
    "unused",
    "no feeder",
    "local only",
    "stops at macro",
    "not sent",
    "multiple devices",
    "name mismatch",
]
BROKEN: frozenset[Status] = frozenset({"stops at macro", "not sent"})
WARNINGS: frozenset[Status] = frozenset({"multiple devices", "name mismatch"})


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
    drives_something_else: bool = False

    @property
    def status(self) -> Status:
        fed = bool(self.devices) or self.automated
        if not self.slots:
            if not fed:
                return "unused"
            return "local only" if self.drives_something_else else "stops at macro"
        if not fed:
            return "no feeder"
        addresses = [s.address for s in self.slots if s.address is not None]
        if len(addresses) < len(self.slots):
            return "not sent"
        if len(self.devices) > 1:
            return "multiple devices"
        if not any(_names_match(self.name, a) for a in addresses):
            return "name mismatch"
        return "ok"


@dataclass(frozen=True)
class RackTrace:
    track: str
    macros: tuple[MacroTrace, ...]


def _letters(text: str) -> str:
    return "".join(c for c in text.casefold() if c.isalnum())


def _names_match(macro_name: str, address: str) -> bool:
    """Whether a named macro shares a name with its address's last part. "Macro 9" always does."""
    if re.fullmatch(r"Macro \d+", macro_name):
        return True
    name, leaf = _letters(macro_name), _letters(address.rstrip("/").rsplit("/", 1)[-1])
    return bool(name and leaf) and (name in leaf or leaf in name)


def juce_hash(text: str) -> int:
    """A JUCE VST3's ParameterId: the JUCE string hash of the parameter name."""
    h = 0
    for char in text:
        h = (31 * h + ord(char)) & 0xFFFFFFFF
    return h & 0x7FFFFFFF


def osc_addresses(plugin: Element) -> dict[int, str | None] | None:
    """Parameter id -> OSC address (None if not sent) from saved state; None if there's no list."""
    state = plugin.find(".//ProcessorState")
    if state is None or state.text is None:
        return None
    try:
        blob = bytes.fromhex(re.sub(r"\s", "", state.text))
    except ValueError:
        return None
    if blob[:4] != JUCE_XML_MAGIC or len(blob) < 8:
        return None
    size = struct.unpack("<I", blob[4:8])[0]
    try:
        saved = ET.fromstring(blob[8 : 8 + size].rstrip(b"\0"))
    except (ET.ParseError, LookupError):
        return None
    params = saved.find("OSCParameters")
    if params is None:
        return None
    settings = saved.find("OSCSettings")
    sending = settings is None or settings.get("oscOutputEnabled", "1") != "0"
    return {juce_hash(p.get("parameterName", "")): _sent_address(p, sending) for p in params}


def _sent_address(param: Element, plugin_sending: bool) -> str | None:
    if not plugin_sending or param.get("oscOutputEnabled", "1") == "0":
        return None
    return param.get("oscAddress") or None


def _enclosing_rack(el: Element, parents: dict[Element, Element]) -> Element | None:
    current = parents.get(el)
    while current is not None and current.tag not in RACK_TAGS:
        current = parents.get(current)
    return current


def _macro_count(rack: Element) -> int:
    return sum(1 for c in rack if c.tag.startswith("MacroControls."))


def _macro_map(mapping: Element) -> int | None:
    """The 1-based macro a KeyMidi maps to, or None if it's a hardware MIDI map."""
    if ls.value(mapping, "Channel") != MACRO_MAP_CHANNEL or ls.value(mapping, "IsNote") != "false":
        return None
    return int(ls.value(mapping, "NoteOrController")) + 1


def _moving_targets(root: Element) -> set[str]:
    """Automation target ids whose arrangement or clip envelope changes value."""
    moving: set[str] = set()
    for tag in ("AutomationEnvelope", "ClipEnvelope"):
        for envelope in root.iter(tag):
            if len({e.get("Value") for e in envelope.iter("FloatEvent")}) > 1:
                moving.add(ls.envelope_target(envelope))
    return moving


def _is_off(device: Element, moving: set[str]) -> bool:
    """Whether a device is switched off and nothing automates its switch."""
    switch = device.find("On")
    if switch is None or ls.value(switch, "Manual") != "false":
        return False
    target = switch.find("AutomationTarget")
    return target is None or ls.attr(target, "Id") not in moving


def _device_label(device: Element) -> str:
    path = next((p.get("Value") for p in device.iter("Path") if p.get("Value")), None)
    return PureWindowsPath(path).stem if path else device.tag


class _SetIndex:
    """Everything a trace looks up, read once from the set."""

    def __init__(self, root: Element) -> None:
        self.parents = {child: parent for parent in root.iter() for child in parent}
        self.moving = _moving_targets(root)
        self.devices_by_lom: dict[str, list[str]] = {}
        self.slots: defaultdict[tuple[Element, int], list[Slot]] = defaultdict(list)
        self.other_targets: set[tuple[Element, int]] = set()
        self.osc_racks: dict[Element, str] = {}  # rack -> track name
        for track in ls.all_tracks(root):
            for tag in MAX_DEVICE_TAGS:
                for device in track.iter(tag):
                    if _is_off(device, self.moving):
                        continue
                    label = f"{ls.track_name(track)}: {_device_label(device)}"
                    for lom in {ls.value(r, "LomId") for r in device.iter("MxDIdRef")} - {"0"}:
                        self.devices_by_lom.setdefault(lom, []).append(label)
            self._read_mappings(track)

    def _read_mappings(self, track: Element) -> None:
        addresses_by_plugin = {
            plugin: addresses
            for plugin in track.iter("PluginDevice")
            if (addresses := osc_addresses(plugin)) is not None
        }
        for plugin in addresses_by_plugin:
            osc_rack = _enclosing_rack(plugin, self.parents)
            if osc_rack is not None:
                self.osc_racks[osc_rack] = ls.track_name(track)
        slot_owner = {
            param: plugin for plugin in addresses_by_plugin for param in plugin.iter("PluginFloatParameter")
        }
        for mapping in track.iter("KeyMidi"):
            number = _macro_map(mapping)
            target_rack = self._mapped_rack(mapping)
            if number is None or target_rack is None:
                continue
            key = (target_rack, number)
            holder = self.parents[mapping]
            param = self.parents[holder] if holder.tag == "ParameterValue" else None
            owner = slot_owner.get(param) if param is not None else None
            if param is None or owner is None:
                self.other_targets.add(key)
                continue
            param_id = ls.value(param, "ParameterId")
            label = f"{ls.value(param, 'ParameterName').strip()} (id {param_id})"
            address = None if _is_off(owner, self.moving) else addresses_by_plugin[owner].get(int(param_id))
            self.slots[key].append(Slot(label, address))

    def _mapped_rack(self, mapping: Element) -> Element | None:
        """The rack whose macros a KeyMidi refers to. A macro's own KeyMidi refers to the parent rack."""
        rack = _enclosing_rack(mapping, self.parents)
        if rack is not None and self.parents[mapping].tag.startswith("MacroControls."):
            return _enclosing_rack(rack, self.parents)
        return rack

    def feeders(self, rack: Element, number: int) -> tuple[list[str], bool]:
        """Devices and automation feeding a macro, following it up through parent racks."""
        macro = ls.macro(rack, number)
        lom = ls.value(macro, "LomId")
        devices = list(self.devices_by_lom.get(lom, [])) if lom != "0" else []
        automated = ls.automation_target_id(macro) in self.moving
        mapping = macro.find("KeyMidi")
        parent = _enclosing_rack(rack, self.parents)
        parent_number = _macro_map(mapping) if mapping is not None else None
        if parent is not None and parent_number is not None and parent_number <= _macro_count(parent):
            parent_devices, parent_automated = self.feeders(parent, parent_number)
            devices += parent_devices
            automated = automated or parent_automated
        return devices, automated

    def macro_trace(self, rack: Element, number: int) -> MacroTrace:
        devices, automated = self.feeders(rack, number)
        return MacroTrace(
            number=number,
            name=ls.value(rack, f"MacroDisplayNames.{number - 1}"),
            devices=tuple(devices),
            automated=automated,
            slots=tuple(self.slots.get((rack, number), ())),
            drives_something_else=(rack, number) in self.other_targets,
        )


def trace(root: Element) -> list[RackTrace]:
    """One entry per rack that directly holds a plugin with an OSC list."""
    index = _SetIndex(root)
    return [
        RackTrace(track, tuple(index.macro_trace(rack, n) for n in range(1, _macro_count(rack) + 1)))
        for rack, track in index.osc_racks.items()
    ]


def _line(entry: MacroTrace) -> str:
    source = ", ".join(entry.devices) or ("automation" if entry.automated else "-")
    target = ", ".join(s.address or f"{s.label}: not sent" for s in entry.slots) or "-"
    return f"  M{entry.number:<2} {entry.name:<22} {source} -> {target}  [{entry.status}]"


def _report(path: str, strict: bool) -> bool:
    """Print one set's trace and return whether it passed."""
    racks = trace(ls.read_set(path))
    failing = BROKEN | WARNINGS if strict else BROKEN
    passed = not any(m.status in failing for rack in racks for m in rack.macros)
    print(f"{'ok  ' if passed else 'FAIL'}  {path}")
    if not racks:
        print("      no rack holds a plugin with an OSC list; nothing to trace")
    for rack in racks:
        print(f"      rack on track {rack.track!r}")
        for entry in rack.macros:
            if entry.status != "unused":
                print(f"    {_line(entry)}")
    return passed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="als-trace", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--strict", action="store_true", help="also fail on multiple devices and name mismatches")
    parser.add_argument("paths", nargs="+", metavar="set.als")
    args = parser.parse_args(argv)
    failed = False
    for path in args.paths:
        try:
            failed = not _report(path, args.strict) or failed
        except (ls.AlsError, OSError, EOFError, ET.ParseError, ValueError, zlib.error) as e:
            print(f"als-trace: {path}: {e}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

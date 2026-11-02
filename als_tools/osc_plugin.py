"""Read and extend the OSC parameter list a plugin saves in a Live set.

Supported plugins are Nativize, or any JUCE VST3 saving the same state: a <Parameters>
list declaring paramN ids and an <OSCParameters> list. Live only exposes a plugin
parameter that has a filled <PluginFloatParameter>, so adding one takes two edits: the
plugin's saved state, and that Live slot.
"""

from __future__ import annotations

import codecs
import re
import struct
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from xml.etree.ElementTree import Element, SubElement
from xml.sax.saxutils import quoteattr

from als_tools import liveset as ls

JUCE_XML_MAGIC = b"VC2!"  # header of JUCE's copyXmlToBinary state
MACRO_MAP_CHANNEL = "16"  # Live stores macro mappings as KeyMidi on channel 16
EMPTY_SLOT_ID = "-1"
HEX_LINE = 80
DEFAULT_MINIMUM, DEFAULT_MAXIMUM = 0.0, 1.0
OSC_SOURCE = "Touch"  # what saved OSC parameters carry
EMPTY_VISUAL_INDEX = "1073741823"  # what Live saves on an empty slot


def juce_hash(text: str) -> int:
    """A JUCE VST3's ParameterId: the JUCE string hash of the parameter name."""
    h = 0
    for char in text:
        h = (31 * h + ord(char)) & 0xFFFFFFFF
    return h & 0x7FFFFFFF


@dataclass(frozen=True)
class SavedState:
    xml: bytes
    tail: bytes  # whatever the plugin stores after its XML


def read_state(plugin: Element) -> SavedState | None:
    """A plugin's saved XML state, or None if it doesn't have that format."""
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
    return SavedState(blob[8 : 8 + size], blob[8 + size :])


def osc_list(state: SavedState) -> tuple[Element, Element] | None:
    """(the parsed state, its OSCParameters), or None if the state has no such list."""
    try:
        saved = ET.fromstring(state.xml.rstrip(b"\0"))
    except (ET.ParseError, LookupError):
        return None
    params = saved.find("OSCParameters")
    return None if params is None else (saved, params)


def _write_state(plugin: Element, state: SavedState) -> None:
    blob = JUCE_XML_MAGIC + struct.pack("<I", len(state.xml)) + state.xml + state.tail
    hexed = blob.hex().upper()
    lines = (hexed[i : i + HEX_LINE] for i in range(0, len(hexed), HEX_LINE))
    ls.child(plugin, ".//ProcessorState").text = "\n" + "\n".join(lines) + "\n"


def macro_mapping(number: int) -> Element:
    """A KeyMidi mapping a parameter to a 1-based macro of its rack."""
    mapping = Element("KeyMidi")
    for tag, value in (
        ("PersistentKeyString", ""),
        ("IsNote", "false"),
        ("Channel", MACRO_MAP_CHANNEL),
        ("NoteOrController", str(number - 1)),
        ("LowerRangeNote", "-1"),
        ("UpperRangeNote", "-1"),
        ("ControllerMapMode", "0"),
    ):
        SubElement(mapping, tag, Value=value)
    return mapping


def mapped_macro(mapping: Element) -> int | None:
    """The 1-based macro a KeyMidi maps to, or None if it's a hardware MIDI map."""
    if ls.value(mapping, "Channel") != MACRO_MAP_CHANNEL or ls.value(mapping, "IsNote") != "false":
        return None
    return ls.to_int(ls.value(mapping, "NoteOrController"), "KeyMidi") + 1


@dataclass(frozen=True)
class AddedParam:
    name: str
    displaced: tuple[str, ...]  # mappings this replaced, for reporting


def _find_osc_plugin(rack: Element) -> tuple[Element, SavedState, Element, Element]:
    found: list[tuple[Element, SavedState, Element, Element]] = []
    for plugin in ls.own_devices(rack, "PluginDevice"):
        state = read_state(plugin)
        listed = osc_list(state) if state is not None else None
        if state is not None and listed is not None:
            found.append((plugin, state, listed[0], listed[1]))
    if not found:
        raise ls.AlsError("rack holds no plugin with an OSC list")
    if len(found) > 1:
        raise ls.AlsError(f"rack holds {len(found)} plugins with OSC lists; can't tell which to add to")
    return found[0]


def _next_number(params: Element) -> int:
    numbers = (re.fullmatch(r"param(\d+)", p.get("parameterName", "")) for p in params)
    return max((int(m[1]) for m in numbers if m), default=0) + 1


def _is_utf8(encoding: bytes) -> bool:
    try:
        return codecs.lookup(encoding.decode("ascii")).name == "utf-8"
    except (LookupError, UnicodeDecodeError):
        return False


def _append_entry(xml: bytes, entry: bytes) -> bytes:
    declared = re.match(rb"""<\?xml[^>]*encoding=["']([^"']+)["']""", xml)
    if declared and not _is_utf8(declared[1]):
        raise ls.AlsError(f"plugin state declares {declared[1]!r}; only UTF-8 can be edited")
    if xml.count(b"</OSCParameters>") == 1:
        return xml.replace(b"</OSCParameters>", entry + b"</OSCParameters>")
    patched, count = re.subn(rb"<OSCParameters\s*/>", b"<OSCParameters>" + entry + b"</OSCParameters>", xml)
    if count != 1:
        raise ls.AlsError("can't find the end of the OSCParameters list")
    return patched


def _slot_for(plugin: Element, param_id: int) -> Element:
    """The Live slot already exposing this parameter, or the first empty one."""
    slots = list(plugin.iter("PluginFloatParameter"))
    for slot in slots:
        if ls.value(slot, "ParameterId") == str(param_id):
            return slot
    for slot in slots:
        if ls.value(slot, "ParameterId") == EMPTY_SLOT_ID:
            return slot
    raise ls.AlsError("plugin has no empty parameter slot")


def _labels(params: Element) -> dict[str, str]:
    """Parameter id -> the label the plugin saves. Live's own slot names can be placeholders."""
    return {str(juce_hash(p.get("parameterName", ""))): p.get("displayLabel", "").strip() for p in params}


def _unmap_others(plugin: Element, filling: Element, macro: int, labels: dict[str, str]) -> list[str]:
    """Unmap this macro from the plugin's other parameters. Returns their labels."""
    displaced: list[str] = []
    for param in plugin.iter("PluginFloatParameter"):
        holder = ls.child(param, "ParameterValue")
        mapping = holder.find("KeyMidi")
        if param is not filling and mapping is not None and mapped_macro(mapping) == macro:
            holder.remove(mapping)
            param_id = ls.value(param, "ParameterId")
            displaced.append(labels.get(param_id) or ls.value(param, "ParameterName").strip())
    return displaced


def _next_visual_index(plugin: Element) -> int:
    used = (ls.value(p, "VisualIndex") for p in plugin.iter("PluginFloatParameter"))
    return max((ls.to_int(v, "VisualIndex") for v in used if v != EMPTY_VISUAL_INDEX), default=-1) + 1


def add_osc_param(
    rack: Element,
    label: str,
    address: str,
    macro: int,
    minimum: float = DEFAULT_MINIMUM,
    maximum: float = DEFAULT_MAXIMUM,
) -> AddedParam:
    """Append an OSC parameter to the plugin directly in this rack and map it to a macro.

    The rack must hold exactly one plugin with an OSC list, and that plugin must declare
    the next `paramN`, as Nativize does. Other parameters of that plugin lose their mapping
    to this macro, since it now drives the new one. Other plugins and devices on the macro
    keep theirs. Existing parameters keep their numbers.
    """
    ls.macro(rack, macro)
    if not address.startswith("/"):
        raise ls.AlsError(f'address {address!r} must start with "/"')
    if minimum >= maximum:
        raise ls.AlsError(f"minimum {minimum} must be below maximum {maximum}")
    plugin, state, saved, params = _find_osc_plugin(rack)
    if any(p.get("oscAddress") == address for p in params):
        raise ls.AlsError(f"plugin already sends {address}")
    number = _next_number(params)
    name = f"param{number}"
    if not any(p.get("id") == name for p in saved.findall("Parameters/*")):
        raise ls.AlsError(f"plugin declares no parameter {name}")
    slot = _slot_for(plugin, juce_hash(name))
    holder = ls.child(slot, "ParameterValue")
    existing = holder.find("KeyMidi")
    if existing is not None and mapped_macro(existing) is None:
        raise ls.AlsError(f"{name}'s Live slot has a hardware MIDI map; remove it first")

    index = max((ls.to_int(p.get("index", "-1"), "OSC index") for p in params), default=-1) + 1
    entry = (
        f'<Parameter index="{index}" parameterName="{name}" displayLabel={quoteattr(f"{label} ")} '
        f'oscAddress={quoteattr(address)} minValue="{float(minimum)}" maxValue="{float(maximum)}" '
        f'defaultValue="{float(minimum)}" oscInputEnabled="1" oscOutputEnabled="1" source="{OSC_SOURCE}"/>'
    ).encode()
    _write_state(plugin, SavedState(_append_entry(state.xml, entry), state.tail))

    displaced = _unmap_others(plugin, slot, macro, _labels(params))
    if existing is not None:
        previous = mapped_macro(existing)
        holder.remove(existing)
        if previous != macro:
            displaced.append(f"{name} from macro {previous}")
    ls.set_value(slot, "ParameterName", f"{label} ")
    ls.set_value(slot, "ParameterId", str(juce_hash(name)))
    if ls.value(slot, "VisualIndex") == EMPTY_VISUAL_INDEX:
        ls.set_value(slot, "VisualIndex", str(_next_visual_index(plugin)))
    ls.set_value(holder, "Manual", "0")
    holder.insert(1, macro_mapping(macro))
    return AddedParam(name, tuple(displaced))

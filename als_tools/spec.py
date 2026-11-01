"""The clone spec: the one definition of what `als-clone` accepts.

`parse_spec` checks a decoded JSON object against these types, so a malformed spec
fails with a message that names the bad field before any set is read.
"""

from __future__ import annotations

from typing import TypedDict, cast, get_args, get_origin, get_type_hints, is_typeddict

from als_tools.liveset import AlsError


class MacroRef(TypedDict):
    track: str        # name of the track whose first rack holds the macro
    macro: int        # 1-based


class MacroTarget(MacroRef, total=False):
    rename: str       # new macro display name


class AutomationCopy(TypedDict):
    source: MacroRef
    dest: MacroRef


class _DeviceItem(TypedDict):
    template_track: str   # track in the reference set
    device_index: int     # index in that track's device chain
    into: str             # track in the target set
    map: MacroTarget


class DeviceItem(_DeviceItem, total=False):
    position: int         # insert position in the target chain (default 0)


class _TrackItem(TypedDict):
    template: str         # track in the reference set
    name: str             # name of the new track
    sample: str           # absolute path of the audio file for its clip
    map: MacroTarget


class TrackItem(_TrackItem, total=False):
    align_to: str         # target track whose first audio clip gives Time/LoopStart


class _CloneSpec(TypedDict):
    reference: str
    target: str
    output: str


class CloneSpec(_CloneSpec, total=False):
    clear_automation: list[MacroRef]
    copy_automation: list[AutomationCopy]
    devices: list[DeviceItem]
    tracks: list[TrackItem]


# ---------------------------------------------------------------------------
# Validation of untyped input, driven by the TypedDicts above
# ---------------------------------------------------------------------------

def _check(obj: object, hint: object, where: str) -> None:
    origin = get_origin(hint)
    if is_typeddict(hint):
        if not isinstance(obj, dict):
            raise AlsError(f"{where}: expected an object")
        d = cast(dict[str, object], obj)
        td = cast(type, hint)
        fields = get_type_hints(td)
        required = cast(frozenset[str], getattr(td, "__required_keys__"))
        unknown = set(d) - set(fields)
        if unknown:
            raise AlsError(f"{where}: unknown field(s) {sorted(unknown)}")
        for name in sorted(required - set(d)):
            raise AlsError(f"{where}: missing {name!r}")
        for name, sub in fields.items():
            if name in d:
                _check(d[name], sub, f"{where}.{name}")
    elif origin is list:
        if not isinstance(obj, list):
            raise AlsError(f"{where}: expected a list")
        (item,) = get_args(hint)
        for i, x in enumerate(cast(list[object], obj)):
            _check(x, item, f"{where}[{i}]")
    elif hint is int:
        if not isinstance(obj, int) or isinstance(obj, bool):
            raise AlsError(f"{where}: expected an integer")
    elif hint is str:
        if not isinstance(obj, str):
            raise AlsError(f"{where}: expected a string")
    else:
        raise TypeError(f"spec type {hint!r} has no checker")


def parse_spec(obj: object) -> CloneSpec:
    """Check a decoded JSON object against CloneSpec and return it typed."""
    _check(obj, CloneSpec, "spec")
    return cast(CloneSpec, obj)

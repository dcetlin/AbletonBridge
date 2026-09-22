"""Generic LOM (Live Object Model) access handlers."""

from __future__ import absolute_import, print_function, unicode_literals
import re

from ._registry import command

_RE_INDEX = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\[(\d+)\]$')

_SET_DENYLIST = frozenset(["delete", "remove", "disconnect", "dispose"])

# Cap the total number of attributes visited by a single _describe() call so a
# deep introspection of a large object (e.g. Song at depth 3) can never fan out
# into thousands of getattr() calls on Ableton's main thread and blow the
# 10s dispatch timeout / freeze the UI.
_DESCRIBE_MAX_NODES = 1500


def _resolve_path(root, path):
    """Resolve a dot-separated LOM path with optional [index] notation."""
    obj = root
    for segment in path.split("."):
        m = _RE_INDEX.match(segment)
        if m:
            attr_name, idx = m.group(1), int(m.group(2))
            collection = getattr(obj, attr_name)
            if idx < 0 or idx >= len(collection):
                raise IndexError("{0}[{1}] out of range (length {2})".format(attr_name, idx, len(collection)))
            obj = collection[idx]
        else:
            if not hasattr(obj, segment):
                raise AttributeError("'{0}' has no attribute '{1}'".format(type(obj).__name__, segment))
            obj = getattr(obj, segment)
    return obj


def _resolve_parent(root, path):
    parts = path.rsplit(".", 1)
    if len(parts) == 1:
        return root, parts[0]
    return _resolve_path(root, parts[0]), parts[1]


def _serialize(obj):
    if obj is None:
        return None
    if isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_serialize(item) for item in obj[:100]]
    result = {"_type": type(obj).__name__}
    for attr in ("name", "value", "min", "max", "is_enabled"):
        try:
            val = getattr(obj, attr)
            if isinstance(val, (bool, int, float, str)):
                result[attr] = val
        except Exception:
            pass
    return result


def _describe(obj, depth=1, _current_depth=0, _budget=None):
    if _budget is None:
        _budget = [_DESCRIBE_MAX_NODES]
    info = {"_type": type(obj).__name__}
    properties = {}
    methods = []
    for attr in sorted(dir(obj)):
        # Skip dunders/privates first so they never trip the budget check —
        # otherwise a trailing run of "_"-prefixed attrs could set _truncated
        # even though no visible content was dropped.
        if attr.startswith("_"):
            continue
        if _budget[0] <= 0:
            info["_truncated"] = True
            break
        _budget[0] -= 1
        try:
            val = getattr(obj, attr)
        except Exception:
            continue
        if callable(val):
            methods.append(attr)
            continue
        if isinstance(val, (bool, int, float, str)):
            properties[attr] = val
        elif isinstance(val, (list, tuple)):
            entry = {"_type": "collection", "length": len(val)}
            if _current_depth < depth and len(val) > 0:
                try:
                    entry["item_type"] = type(val[0]).__name__
                except Exception:
                    pass
            properties[attr] = entry
        else:
            if _current_depth < depth:
                try:
                    properties[attr] = _describe(val, depth, _current_depth + 1, _budget)
                except Exception:
                    properties[attr] = {"_type": type(val).__name__}
            else:
                properties[attr] = {"_type": type(val).__name__}
    info["properties"] = properties
    info["methods"] = methods
    return info


@command("lom_get")
def lom_get(song, path: str, ctrl=None) -> dict:
    """Resolve a LOM path and return its value."""
    obj = _resolve_path(song, path)
    return {"path": path, "value": _serialize(obj)}


@command("lom_set", modifying=True)
def lom_set(song, path: str, value, ctrl=None) -> dict:
    """Set a LOM property by path.

    This is a generic escape hatch: unlike the named setters (e.g.
    set_device_parameter), it performs NO range clamping or type coercion —
    the raw value is handed to the LOM, which enforces its own bounds/types
    and raises on an invalid assignment. Prefer a named command when one
    exists. The denylist below is a lightweight guard, not a full safety net;
    the real hazard surface is "any writable LOM property".
    """
    final_attr = path.rsplit(".", 1)[-1]
    # An indexed final segment (e.g. "tracks[0]") targets a collection element,
    # not a settable property — setattr would create a bogus attribute named
    # "tracks[0]" or raise. Reject it with a clear message.
    if _RE_INDEX.match(final_attr):
        raise ValueError(
            "Cannot set collection element '{0}'; lom_set targets a property "
            "(e.g. 'tracks[0].name')".format(final_attr))
    if final_attr.lower() in _SET_DENYLIST:
        raise ValueError("Setting '{0}' is not allowed".format(final_attr))
    parent, attr = _resolve_parent(song, path)
    setattr(parent, attr, value)
    actual = getattr(parent, attr)
    return {"path": path, "value": _serialize(actual)}


@command("lom_describe")
def lom_describe(song, path: str = "", depth: int = 1, ctrl=None) -> dict:
    """Introspect a LOM object's properties, children, and methods."""
    obj = song if not path else _resolve_path(song, path)
    return _describe(obj, max(0, min(3, depth)))

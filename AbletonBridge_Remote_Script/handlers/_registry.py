"""Command registry for AbletonBridge Remote Script.

Handler functions decorated with @command are registered here and dispatched
by name from the TCP server. This replaces the hand-written dispatch tables
in __init__.py.
"""

from __future__ import absolute_import, print_function, unicode_literals

import inspect

_SENTINEL = object()

_REGISTRY = {}


class _CommandEntry(object):
    __slots__ = ("func", "modifying", "params")

    def __init__(self, func, modifying, params):
        self.func = func
        self.modifying = modifying
        self.params = params


def command(name, modifying=False):
    """Register a handler function in the command registry.

    Usage::

        @command("set_tempo", modifying=True)
        def set_tempo(song, tempo: float, *, ctrl=None) -> dict:
            ...

    The decorator introspects the function signature to build a param spec.
    Parameters named ``song`` and ``ctrl`` are handled specially by dispatch()
    and are excluded from the param spec.
    """
    def decorator(func):
        sig = inspect.signature(func)
        params = []
        for pname, param in sig.parameters.items():
            if pname in ("song", "ctrl"):
                continue
            default = param.default if param.default is not inspect.Parameter.empty else _SENTINEL
            params.append((pname, default))
        if name in _REGISTRY:
            raise ValueError("Duplicate command registration: {0}".format(name))
        _REGISTRY[name] = _CommandEntry(func=func, modifying=modifying, params=params)
        return func
    return decorator


def dispatch(name, song, params_dict, ctrl):
    """Dispatch a command by name, unpacking params from the protocol dict."""
    entry = _REGISTRY.get(name)
    if entry is None:
        raise ValueError("Unknown command: {0}".format(name))
    kwargs = {}
    for pname, default in entry.params:
        if default is _SENTINEL:
            kwargs[pname] = params_dict.get(pname)
        else:
            kwargs[pname] = params_dict.get(pname, default)
    return entry.func(song, ctrl=ctrl, **kwargs)


def get_modifying_commands():
    """Return the set of command names that modify the Live set."""
    return frozenset(name for name, entry in _REGISTRY.items() if entry.modifying)


def get_readonly_commands():
    """Return the set of command names that only read state."""
    return frozenset(name for name, entry in _REGISTRY.items() if not entry.modifying)


def get_registry():
    """Return the full registry dict (for testing/introspection)."""
    return _REGISTRY

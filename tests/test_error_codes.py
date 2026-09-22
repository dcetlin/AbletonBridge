"""Tests for structured error codes.

These import and call the REAL ``AbletonBridge._structured_error`` method.
The Remote Script's package ``__init__`` imports ``_Framework.ControlSurface``
(Ableton's Live API), which is unavailable off-host, so we install a minimal
stub in ``sys.modules`` before importing. ``_structured_error`` itself uses no
instance state, so it can be invoked with a dummy ``self``.
"""
import sys
import types
import queue

import pytest


def _load_structured_error():
    """Import the real method, stubbing Ableton's _Framework if needed.

    The stub is only needed at *import* time (the package resolves
    ``ControlSurface`` at its top level). Once imported, we remove any
    sys.modules entries we added so the stub cannot leak into other test
    modules and mask, e.g., a future test that verifies ``_Framework`` is
    genuinely absent off-host.
    """
    added = []
    if "_Framework" not in sys.modules:
        cs = types.ModuleType("_Framework.ControlSurface")
        cs.ControlSurface = object
        fw = types.ModuleType("_Framework")
        fw.ControlSurface = cs
        sys.modules["_Framework"] = fw
        sys.modules["_Framework.ControlSurface"] = cs
        added = ["_Framework", "_Framework.ControlSurface"]
    try:
        import AbletonBridge_Remote_Script as pkg
        return pkg.AbletonBridge._structured_error
    finally:
        for name in added:
            sys.modules.pop(name, None)


# Bound to a dummy self (the method reads no instance state).
_STRUCTURED_ERROR = _load_structured_error()


def structured_error(e, command_type=None, may_have_landed=False):
    return _STRUCTURED_ERROR(None, e, command_type=command_type,
                             may_have_landed=may_have_landed)


class TestErrorCodeClassification:
    """Exercise the real error -> code mapping in _structured_error."""

    ERROR_MAP = [
        (ValueError("bad value"), "invalid_input", "bad value"),
        (IndexError("out of range"), "index_out_of_range", "out of range"),
        (KeyError("param"), "missing_parameter", "param"),
        (TypeError("wrong type"), "type_error", "wrong type"),
        (AttributeError("no attr"), "attribute_error", "no attr"),
        (NotImplementedError("nope"), "not_implemented", "nope"),
        (RuntimeError("broke"), "runtime_error", "broke"),
        (queue.Empty(), "timeout", "Operation timed out"),
        (Exception("secret"), "internal_error", "Internal error"),
    ]

    def test_error_codes(self):
        for exc, expected_code, expected_msg_substr in self.ERROR_MAP:
            result = structured_error(exc)
            assert result["code"] == expected_code, (
                f"Expected {expected_code} for {type(exc).__name__}, "
                f"got {result['code']}"
            )
            assert expected_msg_substr in result["message"], (
                f"Expected {expected_msg_substr!r} in message, "
                f"got {result['message']!r}"
            )

    def test_internal_error_hides_details(self):
        """Unknown exceptions must not leak their message to the client."""
        result = structured_error(Exception("db password is hunter2"))
        assert result["code"] == "internal_error"
        assert "hunter2" not in result["message"]


class TestMayHaveLanded:
    """The modifying/read-only distinction on timeouts (Finding 1 regression)."""

    def test_timeout_modifying_flags_may_have_landed(self):
        result = structured_error(queue.Empty(), command_type="create_clip",
                                  may_have_landed=True)
        assert result["code"] == "timeout"
        assert result["may_have_landed"] is True

    def test_timeout_readonly_does_not_flag_may_have_landed(self):
        """A read-only timeout must NOT claim the write may have landed."""
        result = structured_error(queue.Empty(), command_type="get_session_info",
                                  may_have_landed=False)
        assert result["code"] == "timeout"
        assert "may_have_landed" not in result

    def test_non_timeout_never_flags_may_have_landed_by_default(self):
        result = structured_error(ValueError("bad"))
        assert "may_have_landed" not in result


class TestResponseShape:
    """Backward-compat and optional-key contract."""

    def test_backward_compat_keys(self):
        result = structured_error(ValueError("bad value"))
        assert result["status"] == "error"
        assert "message" in result
        assert "code" in result

    def test_command_key_present_when_known(self):
        result = structured_error(ValueError("bad"), command_type="create_clip")
        assert result["command"] == "create_clip"

    def test_command_key_absent_when_unknown(self):
        result = structured_error(ValueError("bad"))
        assert "command" not in result

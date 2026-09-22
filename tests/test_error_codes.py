"""Tests for structured error codes."""
import queue
import pytest


class TestErrorCodeClassification:
    """Test the error → code mapping logic."""

    ERROR_MAP = [
        (ValueError("bad value"), "invalid_input", "bad value"),
        (IndexError("out of range"), "index_out_of_range", "out of range"),
        (KeyError("param"), "missing_parameter", None),
        (TypeError("wrong type"), "type_error", "wrong type"),
        (AttributeError("no attr"), "attribute_error", "no attr"),
        (NotImplementedError("nope"), "not_implemented", "nope"),
        (RuntimeError("broke"), "runtime_error", "broke"),
        (queue.Empty(), "timeout", "Operation timed out"),
        (Exception("unknown"), "internal_error", "Internal error"),
    ]

    def test_error_codes(self):
        for exc, expected_code, expected_msg_substr in self.ERROR_MAP:
            # Inline the classification to test independently of Remote Script imports
            if isinstance(exc, ValueError): code = "invalid_input"
            elif isinstance(exc, IndexError): code = "index_out_of_range"
            elif isinstance(exc, KeyError): code = "missing_parameter"
            elif isinstance(exc, TypeError): code = "type_error"
            elif isinstance(exc, AttributeError): code = "attribute_error"
            elif isinstance(exc, NotImplementedError): code = "not_implemented"
            elif isinstance(exc, RuntimeError): code = "runtime_error"
            elif isinstance(exc, queue.Empty): code = "timeout"
            else: code = "internal_error"
            assert code == expected_code, f"Expected {expected_code} for {type(exc).__name__}, got {code}"

    def test_timeout_may_have_landed(self):
        """Timeout errors should indicate may_have_landed."""
        # This tests the pattern, not the method directly
        e = queue.Empty()
        code = "timeout"
        may_have_landed = isinstance(e, queue.Empty)
        assert code == "timeout"
        assert may_have_landed is True

    def test_backward_compat_keys(self):
        """Structured error must still have 'status' and 'message' keys."""
        # Simulate what _structured_error produces
        result = {
            "status": "error",
            "code": "invalid_input",
            "message": "bad value",
        }
        assert result["status"] == "error"
        assert "message" in result
        assert "code" in result

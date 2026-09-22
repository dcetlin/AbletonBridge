"""Tests for command annotation taxonomy.

Spec notes:
- delete_notes is listed in the spec but does not exist in the codebase.
- add_notes_to_clip is listed under midi.py in the spec but lives in clips.py.
  Both are annotated/tested correctly based on what actually exists.
"""
import sys
import os
import pytest

_RS_DIR = os.path.join(os.path.dirname(__file__), "..", "AbletonBridge_Remote_Script")
if _RS_DIR not in sys.path:
    sys.path.insert(0, _RS_DIR)


def _load_registry():
    """Import all handler modules to trigger @command decorators, then return the registry."""
    from handlers._registry import get_registry
    from handlers import (
        session, tracks, clips, mixer, devices,
        browser, scenes, arrangement, audio, midi, automation,
    )
    return get_registry()


def _load_annotations():
    """Import all handler modules and return annotations."""
    from handlers._registry import get_command_annotations
    from handlers import (
        session, tracks, clips, mixer, devices,
        browser, scenes, arrangement, audio, midi, automation,
    )
    return get_command_annotations()


class TestAnnotationFields:
    def test_entry_has_fields(self):
        registry = _load_registry()
        for name, entry in registry.items():
            assert hasattr(entry, "destructive"), f"{name} missing destructive"
            assert hasattr(entry, "idempotent"), f"{name} missing idempotent"

    def test_defaults(self):
        """Non-annotated commands should have destructive=False, idempotent=True."""
        registry = _load_registry()
        entry = registry.get("get_session_info")
        assert entry is not None, "get_session_info should be registered"
        assert entry.destructive is False
        assert entry.idempotent is True

    def test_destructive_implies_modifying(self):
        """Every destructive command must also be modifying."""
        registry = _load_registry()
        for name, entry in registry.items():
            if entry.destructive:
                assert entry.modifying, f"{name} is destructive but not modifying"


class TestDestructiveCommands:
    EXPECTED_DESTRUCTIVE = [
        "delete_track", "delete_return_track", "delete_clip",
        "delete_scene", "delete_device",
        "delete_time", "delete_arrangement_clip",
        "clear_clip_automation", "clear_clip_envelope",
        "clear_all_clip_envelopes", "clear_track_automation",
    ]

    # delete_notes is in the spec but does not exist in the codebase
    SPEC_ONLY = ["delete_notes"]

    def test_destructive_flagged(self):
        registry = _load_registry()
        for cmd_name in self.EXPECTED_DESTRUCTIVE:
            entry = registry.get(cmd_name)
            assert entry is not None, f"{cmd_name} should be registered"
            assert entry.destructive is True, f"{cmd_name} should be destructive"

    def test_spec_only_commands_absent(self):
        """Commands listed in the spec but absent from the codebase."""
        registry = _load_registry()
        for cmd_name in self.SPEC_ONLY:
            assert registry.get(cmd_name) is None, f"{cmd_name} unexpectedly exists"


class TestNonIdempotentCommands:
    EXPECTED_NON_IDEMPOTENT = [
        "create_midi_track", "create_audio_track", "create_return_track",
        "create_clip", "create_scene",
        "delete_track", "delete_return_track", "delete_clip",
        "delete_scene", "delete_device", "delete_time",
        "delete_arrangement_clip",
        "duplicate_track", "duplicate_clip", "duplicate_scene",
        "add_notes_to_clip", "add_notes_extended",
    ]

    def test_non_idempotent_flagged(self):
        registry = _load_registry()
        for cmd_name in self.EXPECTED_NON_IDEMPOTENT:
            entry = registry.get(cmd_name)
            assert entry is not None, f"{cmd_name} should be registered"
            assert entry.idempotent is False, f"{cmd_name} should be non-idempotent"


class TestGetCommandAnnotations:
    def test_returns_dict(self):
        annotations = _load_annotations()
        assert isinstance(annotations, dict)
        assert len(annotations) > 0

    def test_structure(self):
        annotations = _load_annotations()
        for name, ann in annotations.items():
            assert "modifying" in ann
            assert "destructive" in ann
            assert "idempotent" in ann

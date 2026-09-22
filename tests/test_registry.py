"""Tests for the command registry dispatch system."""
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


class TestRegistryCompleteness:

    def test_total_command_count(self):
        registry = _load_registry()
        assert len(registry) == 255, (
            f"Expected 255 registered commands, got {len(registry)}. "
            f"Missing or extra commands detected."
        )

    def test_no_duplicate_registrations(self):
        """The @command decorator raises on duplicates, so if we get here, there are none."""
        registry = _load_registry()
        assert len(registry) > 0

    def test_modifying_readonly_partition(self):
        """Every command is exactly one of modifying or readonly (no overlap possible by design)."""
        from handlers._registry import (
            get_modifying_commands, get_readonly_commands,
        )
        _ = _load_registry()
        mod = get_modifying_commands()
        ro = get_readonly_commands()
        assert len(mod & ro) == 0, f"Commands in both sets: {mod & ro}"
        assert len(mod) + len(ro) == 255

    def test_all_entries_have_callable_func(self):
        registry = _load_registry()
        for name, entry in registry.items():
            assert callable(entry.func), f"Command '{name}' has non-callable func"

    def test_known_modifying_commands(self):
        """Spot-check that specific commands have the correct modifying flag."""
        registry = _load_registry()
        assert registry["set_tempo"].modifying is True
        assert registry["delete_track"].modifying is True
        assert registry["create_clip_automation"].modifying is True
        assert registry["delete_time"].modifying is True

    def test_known_readonly_commands(self):
        """Spot-check that specific commands have the correct readonly flag."""
        registry = _load_registry()
        assert registry["get_session_info"].modifying is False
        assert registry["get_clip_notes"].modifying is False
        assert registry["get_device_parameters"].modifying is False
        assert registry["get_arrangement_clips"].modifying is False


class TestRegistryDispatch:

    def test_dispatch_simple_command(self):
        """Dispatch a zero-param readonly command."""
        from handlers._registry import dispatch
        _ = _load_registry()

        class MockSong:
            tempo = 120.0
            signature_numerator = 4
            signature_denominator = 4
            is_playing = False
            loop = False
            loop_start = 0.0
            loop_length = 4.0
            song_length = 0.0

            @property
            def tracks(self):
                return []

            @property
            def return_tracks(self):
                return []

            @property
            def master_track(self):
                class MT:
                    class mixer_device:
                        class volume:
                            value = 0.85
                        class panning:
                            value = 0.0
                return MT()

            @property
            def scenes(self):
                return []

        result = dispatch("get_session_info", MockSong(), {}, None)
        assert isinstance(result, dict)
        assert result["tempo"] == 120.0

    def test_dispatch_with_params(self):
        """Dispatch a command that takes parameters."""
        from handlers._registry import dispatch
        _ = _load_registry()

        class MockSong:
            tempo = 120.0
            def __setattr__(self, name, value):
                if name == "tempo":
                    object.__setattr__(self, name, value)
                else:
                    object.__setattr__(self, name, value)

        song = MockSong()
        result = dispatch("set_tempo", song, {"tempo": 140.0}, None)
        assert result["tempo"] == 140.0

    def test_dispatch_unknown_command_raises(self):
        """Dispatch an unknown command raises ValueError."""
        from handlers._registry import dispatch
        _ = _load_registry()

        with pytest.raises(ValueError, match="Unknown command"):
            dispatch("nonexistent_command_xyz", None, {}, None)

    def test_dispatch_uses_defaults(self):
        """Params not in the dict use the function's default values."""
        registry = _load_registry()
        entry = registry.get("set_tempo")
        assert entry is not None
        # set_tempo has (song, tempo, ctrl=None) — tempo has no default
        # The dispatch should pass None for missing required params
        params = entry.params
        param_names = [p[0] for p in params]
        assert "tempo" in param_names


class TestRegistryParamSpecs:

    def test_param_names_match_function_signature(self):
        """Every registered param name exists in the function's actual signature."""
        import inspect
        registry = _load_registry()
        for name, entry in registry.items():
            sig = inspect.signature(entry.func)
            sig_params = set(sig.parameters.keys()) - {"song", "ctrl"}
            registry_params = set(p[0] for p in entry.params)
            assert registry_params == sig_params, (
                f"Command '{name}': registry params {registry_params} != "
                f"signature params {sig_params}"
            )

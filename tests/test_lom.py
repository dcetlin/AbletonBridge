import os
import sys
import pytest
from unittest.mock import MagicMock

# Import handler modules directly (as top-level `handlers` package) so the
# AbletonBridge_Remote_Script package __init__ — which imports the Ableton-only
# `_Framework` module — is never triggered. Matches tests/test_registry.py.
_RS_DIR = os.path.join(os.path.dirname(__file__), "..", "AbletonBridge_Remote_Script")
if _RS_DIR not in sys.path:
    sys.path.insert(0, _RS_DIR)

from handlers.lom import (  # noqa: E402
    _resolve_path, _resolve_parent, _serialize, lom_get, lom_set, lom_describe
)


class _Obj(object):
    """Minimal stand-in for a LOM object.

    Unlike MagicMock, a missing attribute genuinely raises AttributeError —
    which is exactly what real LOM objects do and what the resolver must handle.
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _make_song():
    param = _Obj(name="Volume", value=0.8, min=0.0, max=1.0)
    device = _Obj(name="Wavetable", parameters=[param])
    volume = _Obj(value=0.85)
    mixer = _Obj(volume=volume)
    track = _Obj(name="Track 1", devices=[device], mixer_device=mixer)
    return _Obj(tempo=120.0, tracks=[track])


class TestResolvePath:
    def test_simple(self):
        assert _resolve_path(_make_song(), "tempo") == 120.0

    def test_indexed(self):
        assert _resolve_path(_make_song(), "tracks[0]").name == "Track 1"

    def test_deep(self):
        assert _resolve_path(_make_song(), "tracks[0].devices[0].name") == "Wavetable"

    def test_bad_attr(self):
        with pytest.raises(AttributeError):
            _resolve_path(_make_song(), "nonexistent")

    def test_oob(self):
        with pytest.raises(IndexError):
            _resolve_path(_make_song(), "tracks[99]")


class TestResolveParent:
    def test_top_level(self):
        song = _make_song()
        parent, attr = _resolve_parent(song, "tempo")
        assert parent is song and attr == "tempo"

    def test_nested(self):
        song = _make_song()
        parent, attr = _resolve_parent(song, "tracks[0].name")
        assert parent is song.tracks[0] and attr == "name"


class TestSerialize:
    def test_primitive(self):
        assert _serialize(120.0) == 120.0
        assert _serialize("hi") == "hi"
        assert _serialize(True) is True

    def test_none(self):
        assert _serialize(None) is None

    def test_list(self):
        assert _serialize([1, 2, 3]) == [1, 2, 3]

    def test_object(self):
        param = MagicMock(); param.name = "Volume"; param.value = 0.8
        param.min = 0.0; param.max = 1.0; param.is_enabled = True
        out = _serialize(param)
        assert out["name"] == "Volume" and out["value"] == 0.8
        assert "_type" in out


class TestSetDenylist:
    def test_delete_blocked(self):
        with pytest.raises(ValueError, match="not allowed"):
            lom_set(_make_song(), "delete", True)

    def test_disconnect_blocked(self):
        with pytest.raises(ValueError, match="not allowed"):
            lom_set(_make_song(), "tracks[0].disconnect", True)

    def test_indexed_final_segment_rejected(self):
        # Setting a collection element by index is not a settable property.
        with pytest.raises(ValueError, match="collection element"):
            lom_set(_make_song(), "tracks[0]", None)


class TestLomGet:
    def test_returns_value(self):
        r = lom_get(_make_song(), "tempo")
        assert r["path"] == "tempo" and r["value"] == 120.0


class TestLomSet:
    def test_sets_value(self):
        song = _make_song()
        r = lom_set(song, "tempo", 140.0)
        assert song.tempo == 140.0
        assert r["path"] == "tempo" and r["value"] == 140.0


class TestLomDescribe:
    def test_has_structure(self):
        r = lom_describe(_make_song(), "")
        assert "_type" in r and "properties" in r and "methods" in r

    def test_path_scoped(self):
        r = lom_describe(_make_song(), "tracks[0]")
        assert "_type" in r and "properties" in r

    def test_nested_value_via_get(self):
        # Deep read-back through the mixer sub-object.
        r = lom_get(_make_song(), "tracks[0].mixer_device.volume.value")
        assert r["value"] == 0.85

    def test_budget_truncates_wide_object(self):
        # An object wider than the node budget must terminate and flag it,
        # never fan out unbounded.
        from handlers import lom as lom_mod
        wide = _Obj(**{"attr{0}".format(i): i for i in range(lom_mod._DESCRIBE_MAX_NODES + 50)})
        r = lom_mod._describe(wide, depth=1)
        assert r.get("_truncated") is True
        assert len(r["properties"]) <= lom_mod._DESCRIBE_MAX_NODES

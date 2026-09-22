"""Static data files for AbletonBridge MCP server."""
import json
from pathlib import Path

_DATA_DIR = Path(__file__).parent


def _load(name: str):
    with open(_DATA_DIR / name) as f:
        return json.load(f)


def _int_keys(d: dict) -> dict:
    """Recursively convert string-integer keys back to int (JSON limitation)."""
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = _int_keys(v)
        try:
            k = int(k)
        except (ValueError, TypeError):
            pass
        out[k] = v
    return out


def _load_device_properties() -> dict:
    raw = _load("device_properties.json")
    result = {}
    for device_name, props in raw.items():
        result[device_name] = {}
        for prop_name, prop_info in props.items():
            converted = dict(prop_info)
            if "values" in converted:
                converted["values"] = _int_keys(converted["values"])
            result[device_name][prop_name] = converted
    return result


DEVICE_PROPERTIES: dict = _load_device_properties()
SCALES: dict[str, list[int]] = _load("scales.json")
DRUM_PATTERNS: dict = _load("drum_patterns.json")

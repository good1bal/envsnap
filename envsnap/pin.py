"""Pin specific environment variable values as expected baselines."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

PIN_FILENAME = ".envsnap_pins.json"


def _pin_path(directory: str = ".") -> Path:
    return Path(directory) / PIN_FILENAME


def load_pins(directory: str = ".") -> Dict[str, str]:
    path = _pin_path(directory)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_pins(pins: Dict[str, str], directory: str = ".") -> None:
    path = _pin_path(directory)
    path.write_text(json.dumps(pins, indent=2, sort_keys=True))


def pin_key(key: str, value: str, directory: str = ".") -> Dict[str, str]:
    pins = load_pins(directory)
    pins[key] = value
    save_pins(pins, directory)
    return pins


def unpin_key(key: str, directory: str = ".") -> Dict[str, str]:
    pins = load_pins(directory)
    pins.pop(key, None)
    save_pins(pins, directory)
    return pins


def check_pins(env: Dict[str, str], directory: str = ".") -> List[str]:
    """Return list of violation messages for pinned keys that don't match."""
    pins = load_pins(directory)
    violations: List[str] = []
    for key, expected in pins.items():
        actual = env.get(key)
        if actual is None:
            violations.append(f"{key}: pinned to {expected!r} but not present")
        elif actual != expected:
            violations.append(f"{key}: expected {expected!r}, got {actual!r}")
    return violations

"""Load preset systems from presets/data/*.json.

File format (body fields match physics.body.Body):
    {"name": ..., "mode": "planet" | "comet" | "chaos", "description": ..., "dt": ...,
     "bodies": [{"name": ..., "mass": ..., "x": ..., "y": ..., "vx": ..., "vy": ...,
                 "color": ..., "radius_px": ...}, ...]}
"""
import json
from dataclasses import dataclass
from pathlib import Path

from astroorbit.physics.body import Body
from astroorbit.physics.system import System

DATA_DIR = Path(__file__).parent / "data"


@dataclass
class Preset:
    key: str  # file name without .json
    name: str
    mode: str
    description: str
    dt: float
    bodies: list

    def to_system(self):
        return System(self.bodies)


def load_preset(key):
    raw = json.loads((DATA_DIR / f"{key}.json").read_text(encoding="utf-8"))
    return Preset(key=key, name=raw["name"], mode=raw["mode"],
                  description=raw.get("description", ""), dt=raw["dt"],
                  bodies=[Body(**b) for b in raw["bodies"]])


def list_presets(mode=None):
    presets = [load_preset(p.stem) for p in sorted(DATA_DIR.glob("*.json"))]
    return [p for p in presets if mode is None or p.mode == mode]


def save_preset(system, path, name, mode, dt, description=""):
    """Save a user-built system in the same format, so it can be reloaded."""
    # TODO: write {"name", "mode", "description", "dt", "bodies": [...]} from system.bodies()
    raise NotImplementedError("save_preset (presets/loader.py)")

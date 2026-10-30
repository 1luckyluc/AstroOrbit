"""Simulation modes.

A mode is configuration, not code: which units, which force model, sensible
defaults and which plots make sense. Presets declare the mode they belong to.
"""
from dataclasses import dataclass
import json
from pathlib import Path

from astroorbit.physics.units import ASTRO, NBODY, UnitSystem



PRESET_DIR = Path(__file__).parent / "presets"

def load_presets(mode_key):
    """All presets of one mode, as {name: JSON contents}."""
    presets = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(PRESET_DIR.glob("*.json"))]
    return {p["name"]: p for p in presets if p["mode"] == mode_key}

@dataclass(frozen=True)
class Mode:
    key: str
    label: str
    description: str
    units: UnitSystem
    force_model: str = "newtonian"  # name of a function in physics/forces.py
    default_integrator: str = "Leapfrog"
    default_dt: float = 1e-3
    plots: tuple = ()  # quantities offered in the plots panel

MODES = {
    "planet": Mode(
        key="planet",
        label="Planet mode",
        description="Planets around a star: long-lived, near-circular orbits. "
                    "Track semi-major axis, eccentricity and energy conservation.",
        units=ASTRO,
        default_dt=1e-3,
        plots=("Total System Energy", "Semi-major axis", "Eccentricity",),
    ),
    "comet": Mode(
        key="comet",
        label="Comet mode",
        description="Comets and asteroids: near-massless bodies on eccentric orbits, "
                    "perturbed by the planets. Small time steps near perihelion.",
        units=ASTRO,
        default_dt=1e-4,
        plots=("Total System Energy", "Distance to Sun",),
    ),
    "chaos": Mode(
        key="chaos",
        label="Chaos mode",
        description="Few-body systems that are extremely sensitive to initial conditions. "
                    "Compare two almost identical runs and watch them diverge.",
        units=NBODY,
        default_dt=1e-3,
        plots=("Total System Energy",),
    ),
}

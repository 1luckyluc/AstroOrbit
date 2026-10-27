"""Simulation modes.

A mode is configuration, not code: which units, which force model, sensible
defaults and which plots make sense. Presets declare the mode they belong to.
"""
from dataclasses import dataclass

from astroorbit.physics.units import ASTRO, NBODY, UnitSystem


@dataclass(frozen=True)
class Mode:
    key: str
    label: str
    description: str
    units: UnitSystem
    force_model: str = "newtonian"  # name of a function in physics/forces.py
    default_integrator: str = "Leapfrog"
    plots: tuple = ()  # quantities offered in the plots panel


MODES = {
    "planet": Mode(
        key="planet",
        label="Planet mode",
        description="Planets around a star: long-lived, near-circular orbits. "
                    "Track semi-major axis, eccentricity and energy conservation.",
        units=ASTRO,
        plots=("Semi-major axis", "Eccentricity", "Energy error"),
    ),
    "comet": Mode(
        key="comet",
        label="Comet mode",
        description="Comets and asteroids: near-massless bodies on eccentric orbits, "
                    "perturbed by the planets. Small time steps near perihelion.",
        units=ASTRO,
        plots=("Distance to Sun", "Eccentricity", "Perihelion distance"),
    ),
    "chaos": Mode(
        key="chaos",
        label="Chaos mode",
        description="Few-body systems that are extremely sensitive to initial conditions. "
                    "Compare two almost identical runs and watch them diverge.",
        units=NBODY,
        plots=("Energy error", "Twin-run separation", "Lyapunov estimate"),
    ),
}

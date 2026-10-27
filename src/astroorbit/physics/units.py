"""Unit systems. Each one fixes the value of G, so physics code never hard-codes it."""
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class UnitSystem:
    name: str
    length: str
    time: str
    mass: str
    G: float

ASTRO = UnitSystem("astro", "AU", "yr", "Msun", 4 * math.pi ** 2)
SI = UnitSystem("SI", "m", "s", "kg", 6.67430e-11)
NBODY = UnitSystem("nbody", "L", "T", "M", 1.0)  # G = 1, handy for few-body / chaos setups

UNIT_SYSTEMS = {u.name: u for u in (ASTRO, SI, NBODY)}

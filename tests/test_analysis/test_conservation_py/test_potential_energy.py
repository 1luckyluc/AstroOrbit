"""Physics checks for the integrators. Skipped until each step() is implemented."""
import math
import numpy as np
import pytest

from astroorbit.analysis.conservation import potential_energy
from astroorbit.physics.units import ASTRO


 
POS = [0.0, 0.0, 1.0, 0.0, 0.0, 2.0, 3.0, 4.0]
MASSES = [1.0, 2.0, 3.0, 4.0]
G = 1.0
 
U_REBOUND = -12.100337132350953

def test_potential_energy_4_bodies():
    assert potential_energy(POS, MASSES, G) == pytest.approx(U_REBOUND, rel=1e-12)
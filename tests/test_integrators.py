"""Physics checks for the integrators. Skipped until each step() is implemented."""
import math

import numpy as np
import pytest

from astroorbit.integrators import get_integrator
from astroorbit.physics.forces import newtonian
from astroorbit.physics.units import ASTRO

# accuracy expected after one circular orbit with dt = 1e-3 yr
TOLERANCE = {"Euler": 1.0, "RK4": 1e-3, "Leapfrog": 1e-3}


@pytest.mark.parametrize("name", list(TOLERANCE))
def test_circular_orbit_returns_to_start(name):
    integrator = get_integrator(name)
    masses = np.array([1.0, 1e-10])
    pos = np.array([0.0, 0.0, 1.0, 0.0])
    vel = np.array([0.0, 0.0, 0.0, 2 * math.pi])  # 1 AU circular orbit, period 1 yr
    dt = 1e-3

    def accel(p):
        return newtonian(p, masses, ASTRO.G)

    try:
        for _ in range(1000):
            pos, vel = integrator.step(pos, vel, accel, dt)
    except NotImplementedError:
        pytest.skip(f"{name}.step not implemented yet")

    assert np.hypot(pos[2] - 1.0, pos[3]) < TOLERANCE[name]

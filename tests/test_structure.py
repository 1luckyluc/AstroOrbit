"""The plumbing: registry, modes, presets, system editing, simulation state machine."""
import numpy as np
import pytest

from astroorbit.physics import integrators
from astroorbit.modes import MODES
from astroorbit.physics.body import Body
from astroorbit.physics.system import System
from astroorbit.presets.loader import list_presets
from astroorbit.simulation import Simulation, State


def test_integrators_registered():
    assert set(integrators.INTEGRATORS) == {"Euler", "RK4", "Leapfrog"}


@pytest.mark.parametrize("mode", list(MODES))
def test_every_mode_has_a_preset(mode):
    assert list_presets(mode)


@pytest.mark.parametrize("preset", list_presets(), ids=lambda p: p.key)
def test_presets_load(preset):
    assert preset.mode in MODES
    system = preset.to_system()
    n = len(preset.bodies)
    assert system.pos.shape == system.vel.shape == (2 * n,)
    assert system.masses.shape == (n,)


def test_system_editing():
    s = System([Body("A", 1.0, 0, 0, 0, 0), Body("B", 2.0, 1, 2, 3, 4)])
    s.add_body(Body("C", 3.0, 5, 6, 7, 8))
    s.remove_body(0)
    assert s.names == ["B", "C"]
    np.testing.assert_array_equal(s.pos, [1, 2, 5, 6])
    s.update_body(1, Body("C2", 9.0, 0, 0, 0, 0))
    assert s.body(1) == Body("C2", 9.0, 0, 0, 0, 0)


def test_simulation_state_machine():
    sim = Simulation(list_presets("planet")[0].to_system(), MODES["planet"])
    assert sim.state is State.STOPPED
    sim.start()
    assert sim.state is State.RUNNING
    sim.pause()
    assert sim.state is State.PAUSED
    sim.resume()
    assert sim.state is State.RUNNING
    sim.stop()
    assert sim.state is State.STOPPED
    sim.system.pos[0] = 99.0
    sim.reset()
    assert sim.system.pos[0] != 99.0 and sim.t == 0.0

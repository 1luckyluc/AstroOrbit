"""Simulation engine: system + force model + integrator + clock + history.

Owns the run state (stopped / running / paused). The GUI only sends commands
and calls advance() on its timer; nothing here imports the GUI.
"""
from enum import Enum

from astroorbit.physics import forces
from astroorbit.integrators import INTEGRATORS

class State(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


class Simulation:
    def __init__(self, system, mode, integrator=None, dt=None):
        self.mode = mode
        self.system = system
        self._initial = system.copy()
        self.integrator = INTEGRATORS[integrator or mode.default_integrator]
        self.dt = dt or mode.default_dt
        self.t = 0.0
        self.state = State.STOPPED
        self._force = getattr(forces, mode.force_model)
        self.history = self._empty_history()

    def accel(self, pos):
        return self._force(pos, self.system.masses, self.mode.units.G)

    # ---- controls ----
    def start(self):
        if self.state is State.STOPPED:
            self.history = self._empty_history()
        self.state = State.RUNNING

    def pause(self):
        if self.state is State.RUNNING:
            self.state = State.PAUSED

    def resume(self):
        if self.state is State.PAUSED:
            self.state = State.RUNNING

    def stop(self):
        """End the run; bodies stay where they are."""
        self.state = State.STOPPED

    def reset(self):
        """Back to the initial conditions."""
        self.system = self._initial.copy()
        self.t = 0.0
        self.state = State.STOPPED
        self.history = self._empty_history()

    def set_integrator(self, name):
        self.integrator = INTEGRATORS[name]

    # ---- time stepping ----
    def advance(self, n_steps=1):
        s = self.system
        for _ in range(n_steps):
            s.pos, s.vel = self.integrator(s.pos, s.vel, self.accel, self.dt)
            self.t += self.dt
        self._record()

    def _empty_history(self):
        return {"t": []}

    def _record(self):
        self.history["t"].append(self.t)
        self.history["pos"] = self.history.get("pos", []) + [self.system.pos.copy()]
        self.history["vel"] = self.history.get("vel", []) + [self.system.vel.copy()]
                

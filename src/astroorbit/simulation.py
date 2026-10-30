"""Simulation engine: system + force model + integrator + clock + history.

Owns the run state (stopped / running / paused). The GUI only sends commands
and calls advance() on its timer; nothing here imports the GUI.
"""
from enum import Enum

from astroorbit.physics import forces
from astroorbit.physics.integrators import INTEGRATORS
from astroorbit.analysis.conservation import total_energy
from astroorbit.analysis.elements import orbital_elements
from astroorbit.analysis.stability import ejected_bodies

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
        self.max_distance = 10 * abs(system.pos).max()
        self.ejected = []  # names of bodies that have left, each reported once

    def accel(self, pos):
        return self._force(pos, self.system.masses, self.mode.units.G)

    # ---- controls ----
    def start(self):
        if self.state is State.STOPPED:
            self.history = self._empty_history()
            self._E0 = self._energy()
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
        self.ejected = []

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
        return {"t": [], "pos": [], "vel": [], "a": {}, "e": {}, "energy_error": {}, "r": {}, "E": {}}

    def _energy(self):
        s = self.system
        return total_energy(s.pos, s.vel, s.masses, self.mode.units.G)

    def _elements(self, i):
        """Orbital elements of body i around body 0."""
        s = self.system
        rel_pos = s.pos[2 * i:2 * i + 2] - s.pos[:2]
        rel_vel = s.vel[2 * i:2 * i + 2] - s.vel[:2]
        return orbital_elements(rel_pos, rel_vel, self.mode.units.G * (s.masses[0] + s.masses[i]))

    def _record(self):
        s, h = self.system, self.history
        h["t"].append(self.t)
        h["pos"].append(s.pos.copy())
        h["vel"].append(s.vel.copy())
        h["E"]
        for i in range(1, len(s)):
            el = self._elements(i)
            h["a"].setdefault(s.names[i], []).append((self.t, el["a"]))
            h["e"].setdefault(s.names[i], []).append((self.t, el["e"]))
            dx = s.pos[2 * i] - s.pos[0]
            dy = s.pos[2 * i + 1] - s.pos[1]
            h["r"].setdefault(s.names[i], []).append((self.t, (dx * dx + dy * dy) ** 0.5))
            
        h["E"].setdefault("Total", []).append((self.t, self._energy()))
        for i in ejected_bodies(s.pos, s.vel, s.masses, self.mode.units.G, self.max_distance):
            if s.names[i] not in self.ejected:
                self.ejected.append(s.names[i])
                self.state = State.PAUSED
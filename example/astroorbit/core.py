"""AstroOrbit physics core.

Pure Python (no numpy, no GUI imports) so the exact same file runs in the
desktop app and in the browser through Pyodide.

Units for the solar-system presets: AU, years, solar masses, so G = 4 pi^2.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

G_SOLAR = 4.0 * math.pi ** 2  # AU^3 / (Msun yr^2)


@dataclass
class Body:
    name: str
    mass: float
    x: float
    y: float
    vx: float
    vy: float
    color: str = "#ffffff"
    radius_px: float = 4.0


# ---------------------------------------------------------------- forces ---

def accelerations(pos, masses, G, soft2):
    """Pairwise Newtonian gravity, O(N^2). pos is a flat list [x0, y0, x1, y1, ...]."""
    n = len(masses)
    acc = [0.0] * (2 * n)
    for i in range(n):
        xi, yi = pos[2 * i], pos[2 * i + 1]
        for j in range(i + 1, n):
            dx = pos[2 * j] - xi
            dy = pos[2 * j + 1] - yi
            r2 = dx * dx + dy * dy + soft2
            inv_r3 = 1.0 / (r2 * math.sqrt(r2))
            fi = G * masses[j] * inv_r3
            fj = G * masses[i] * inv_r3
            acc[2 * i] += fi * dx
            acc[2 * i + 1] += fi * dy
            acc[2 * j] -= fj * dx
            acc[2 * j + 1] -= fj * dy
    return acc


# ----------------------------------------------------------- integrators ---

def step_euler(pos, vel, masses, G, soft2, dt):
    a = accelerations(pos, masses, G, soft2)
    new_pos = [p + dt * v for p, v in zip(pos, vel)]
    new_vel = [v + dt * ai for v, ai in zip(vel, a)]
    return new_pos, new_vel


def step_leapfrog(pos, vel, masses, G, soft2, dt):
    """Kick-drift-kick leapfrog (symplectic, 2nd order)."""
    a = accelerations(pos, masses, G, soft2)
    v_half = [v + 0.5 * dt * ai for v, ai in zip(vel, a)]
    new_pos = [p + dt * v for p, v in zip(pos, v_half)]
    a = accelerations(new_pos, masses, G, soft2)
    new_vel = [v + 0.5 * dt * ai for v, ai in zip(v_half, a)]
    return new_pos, new_vel


def step_rk4(pos, vel, masses, G, soft2, dt):
    def deriv(p, v):
        return v, accelerations(p, masses, G, soft2)

    def add(x, k, h):
        return [xi + h * ki for xi, ki in zip(x, k)]

    k1p, k1v = deriv(pos, vel)
    k2p, k2v = deriv(add(pos, k1p, dt / 2), add(vel, k1v, dt / 2))
    k3p, k3v = deriv(add(pos, k2p, dt / 2), add(vel, k2v, dt / 2))
    k4p, k4v = deriv(add(pos, k3p, dt), add(vel, k3v, dt))
    new_pos = [p + dt / 6 * (a + 2 * b + 2 * c + d)
               for p, a, b, c, d in zip(pos, k1p, k2p, k3p, k4p)]
    new_vel = [v + dt / 6 * (a + 2 * b + 2 * c + d)
               for v, a, b, c, d in zip(vel, k1v, k2v, k3v, k4v)]
    return new_pos, new_vel


INTEGRATORS = {
    "Leapfrog": step_leapfrog,
    "RK4": step_rk4,
    "Euler": step_euler,
}


# ------------------------------------------------------------ simulation ---

@dataclass
class Simulation:
    bodies: list
    G: float = G_SOLAR
    dt: float = 0.002
    integrator: str = "Leapfrog"
    softening: float = 1e-4
    trail_length: int = 400
    t: float = 0.0
    trails: list = field(default_factory=list)
    _E0: float = 0.0

    def __post_init__(self):
        self._sync_from_bodies()
        self._E0 = self.total_energy()
        self.trails = [[] for _ in self.bodies]

    # internal flat arrays are the source of truth while running
    def _sync_from_bodies(self):
        self.masses = [b.mass for b in self.bodies]
        self.pos = [c for b in self.bodies for c in (b.x, b.y)]
        self.vel = [c for b in self.bodies for c in (b.vx, b.vy)]

    def _sync_to_bodies(self):
        for i, b in enumerate(self.bodies):
            b.x, b.y = self.pos[2 * i], self.pos[2 * i + 1]
            b.vx, b.vy = self.vel[2 * i], self.vel[2 * i + 1]

    def step(self, n=1):
        f = INTEGRATORS[self.integrator]
        soft2 = self.softening ** 2
        for _ in range(n):
            self.pos, self.vel = f(self.pos, self.vel, self.masses, self.G, soft2, self.dt)
            self.t += self.dt
        self._sync_to_bodies()
        for i, tr in enumerate(self.trails):
            tr.append((self.pos[2 * i], self.pos[2 * i + 1]))
            if len(tr) > self.trail_length:
                del tr[0]

    # ---- editing (items 3-4 of the brief) ----
    def add_body(self, body):
        self._sync_to_bodies()
        self.bodies.append(body)
        self.trails.append([])
        self._sync_from_bodies()
        self._E0 = self.total_energy()

    def update_body(self, index, **values):
        self._sync_to_bodies()
        for k, v in values.items():
            setattr(self.bodies[index], k, v)
        self.trails[index] = []
        self._sync_from_bodies()
        self._E0 = self.total_energy()

    def remove_body(self, index):
        self._sync_to_bodies()
        del self.bodies[index]
        del self.trails[index]
        self._sync_from_bodies()
        self._E0 = self.total_energy()

    # ---- diagnostics ----
    def total_energy(self):
        n = len(self.masses)
        ke = 0.5 * sum(self.masses[i] * (self.vel[2 * i] ** 2 + self.vel[2 * i + 1] ** 2)
                       for i in range(n))
        pe = 0.0
        soft2 = self.softening ** 2
        for i in range(n):
            for j in range(i + 1, n):
                dx = self.pos[2 * j] - self.pos[2 * i]
                dy = self.pos[2 * j + 1] - self.pos[2 * i + 1]
                pe -= self.G * self.masses[i] * self.masses[j] / math.sqrt(dx * dx + dy * dy + soft2)
        return ke + pe

    def energy_error(self):
        if self._E0 == 0:
            return 0.0
        return (self.total_energy() - self._E0) / abs(self._E0)

    def orbital_elements(self, index, central=0):
        """Semi-major axis and eccentricity of body `index` around body `central`."""
        if index == central or index >= len(self.bodies):
            return None
        mu = self.G * (self.masses[index] + self.masses[central])
        rx = self.pos[2 * index] - self.pos[2 * central]
        ry = self.pos[2 * index + 1] - self.pos[2 * central + 1]
        vx = self.vel[2 * index] - self.vel[2 * central]
        vy = self.vel[2 * index + 1] - self.vel[2 * central + 1]
        r = math.hypot(rx, ry)
        v2 = vx * vx + vy * vy
        eps = 0.5 * v2 - mu / r
        a = -mu / (2 * eps) if eps < 0 else float("inf")
        h = rx * vy - ry * vx  # z-component of specific angular momentum
        ex = (vy * h) / mu - rx / r
        ey = (-vx * h) / mu - ry / r
        return {"a": a, "e": math.hypot(ex, ey), "r": r}

    def snapshot(self):
        """Flat data the browser front-end reads each frame."""
        return {
            "t": self.t,
            "pos": list(self.pos),
            "trails": [[c for p in tr for c in p] for tr in self.trails],
            "energy_error": self.energy_error(),
        }


# --------------------------------------------------------------- presets ---

def _circular(name, mass, a, color, radius_px, M=1.0, G=G_SOLAR, phase=0.0):
    v = math.sqrt(G * M / a)
    return Body(name, mass, a * math.cos(phase), a * math.sin(phase),
                -v * math.sin(phase), v * math.cos(phase), color, radius_px)


def preset_two_body():
    e = 0.5
    a = 1.0
    r_peri = a * (1 - e)
    v_peri = math.sqrt(G_SOLAR * (1 + e) / r_peri)
    return Simulation([
        Body("Sun", 1.0, 0, 0, 0, 0, "#ffd34d", 8),
        Body("Planet", 3e-6, r_peri, 0, 0, v_peri, "#4da6ff", 4),
    ], dt=0.002)


def preset_inner_solar_system():
    return Simulation([
        Body("Sun", 1.0, 0, 0, 0, 0, "#ffd34d", 9),
        _circular("Mercury", 1.66e-7, 0.387, "#b0a89a", 3, phase=0.3),
        _circular("Venus", 2.45e-6, 0.723, "#e8c27a", 4, phase=2.1),
        _circular("Earth", 3.0e-6, 1.000, "#4da6ff", 4, phase=4.0),
        _circular("Mars", 3.2e-7, 1.524, "#e0603a", 3, phase=5.2),
        _circular("Jupiter", 9.55e-4, 5.203, "#d9a066", 6, phase=1.0),
    ], dt=0.001, trail_length=600)


def preset_binary_star():
    m = 0.5
    d = 1.0
    v = math.sqrt(G_SOLAR * m / (2 * d)) * 0.9
    return Simulation([
        Body("Star A", m, -d / 2, 0, 0, -v, "#ffb84d", 7),
        Body("Star B", m, d / 2, 0, 0, v, "#9fc5ff", 7),
        _circular("Circumbinary", 1e-6, 3.0, "#7dd87d", 3, M=2 * m),
    ], dt=0.002)

def preset_figure_eight():
    """Chenciner & Montgomery (2000) choreography, G = m = 1."""
    x1, y1 = 0.97000436, -0.24308753
    vx3, vy3 = -0.93240737, -0.86473146
    return Simulation([
        Body("A", 1.0, x1, y1, -vx3 / 2, -vy3 / 2, "#ff7b7b", 5),
        Body("B", 1.0, -x1, -y1, -vx3 / 2, -vy3 / 2, "#7bb8ff", 5),
        Body("C", 1.0, 0, 0, vx3, vy3, "#9bff7b", 5),
    ], G=1.0, dt=0.002, softening=0.0, trail_length=800)

PRESETS = {
    "Inner Solar System": preset_inner_solar_system,
    "Two-body (e = 0.5)": preset_two_body,
    "Binary star": preset_binary_star,
    "Figure-eight 3-body": preset_figure_eight,
}

"""System: the state of all bodies, stored as flat numpy arrays.

Layout matches forces.newtonian:
    pos    = [x0, y0, x1, y1, ...]   shape (2n,)
    vel    = [vx0, vy0, vx1, vy1, ...]
    masses = [m0, m1, ...]           shape (n,)
Names, colours and display radii live in parallel lists for the GUI.
"""
import copy

import numpy as np

from astroorbit.physics.body import Body

class System:
    def __init__(self, bodies=()):
        self.names = []
        self.colors = []
        self.radii = []
        self.masses = np.zeros(0)
        self.pos = np.zeros(0)
        self.pos_past = np.array([tuple()])
        self.vel = np.zeros(0)
        for b in bodies:
            self.add_body(b)

    def __len__(self):
        return len(self.masses)

    def copy(self):
        return copy.deepcopy(self)

    # ---- editing ----
    def add_body(self, body):
        self.names.append(body.name)
        self.colors.append(body.color)
        self.radii.append(body.radius_px)
        self.masses = np.append(self.masses, body.mass)
        self.pos = np.append(self.pos, [body.x, body.y])
        self.pos_past = np.append(self.pos_past, list([tuple([body.x, body.y])]))
        self.vel = np.append(self.vel, [body.vx, body.vy])

    def remove_body(self, i):
        for lst in (self.names, self.colors, self.radii):
            del lst[i]
        self.masses = np.delete(self.masses, i)
        self.pos = np.delete(self.pos, [2 * i, 2 * i + 1])
        self.pos_past = np.delete(self.pos_past, [i])
        self.vel = np.delete(self.vel, [2 * i, 2 * i + 1])

    def update_body(self, i, body):
        self.names[i], self.colors[i], self.radii[i] = body.name, body.color, body.radius_px
        self.masses[i] = body.mass
        self.pos[2 * i:2 * i + 2] = body.x, body.y
        self.pos_past = np.append(self.pos_past, list([tuple([body.x, body.y])]))
        self.vel[2 * i:2 * i + 2] = body.vx, body.vy

    # ---- views for the GUI ----
    def body(self, i):
        return Body(self.names[i], float(self.masses[i]),
                    float(self.pos[2 * i]), float(self.pos[2 * i + 1]),
                    float(self.vel[2 * i]), float(self.vel[2 * i + 1]),
                    self.colors[i], self.radii[i])

    def bodies(self):
        return [self.body(i) for i in range(len(self))]

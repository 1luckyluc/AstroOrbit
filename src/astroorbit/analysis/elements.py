"""Orbital elements from state vectors."""

import numpy as np

def orbital_elements(rel_pos, rel_vel, mu):
    """Elements of an orbit relative to a central body.

    rel_pos, rel_vel: (x, y) and (vx, vy) of the body minus the central body.
    mu: G * (M_central + m_body).
    Returns a dict, e.g. {"a": ..., "e": ..., "period": ...}.
    """

    a = 1 / (2 / (rel_pos[0] ** 2 + rel_pos[1] ** 2) ** 0.5 - (rel_vel[0] ** 2 + rel_vel[1] ** 2) / mu)
    h = rel_pos[0] * rel_vel[1] - rel_pos[1] * rel_vel[0]
    e = (1 - h ** 2 / (a * mu)) ** 0.5
    period = 2 * np.pi * (a ** 3 / mu) ** 0.5
    return {"a": a, "e": e, "period": period}

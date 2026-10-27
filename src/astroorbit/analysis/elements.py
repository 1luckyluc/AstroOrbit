"""Orbital elements from state vectors."""


def orbital_elements(rel_pos, rel_vel, mu):
    """Elements of an orbit relative to a central body.

    rel_pos, rel_vel: (x, y) and (vx, vy) of the body minus the central body.
    mu: G * (M_central + m_body).
    Returns a dict, e.g. {"a": ..., "e": ..., "period": ...}.
    """
    # TODO: specific energy -> a; eccentricity vector -> e; Kepler's third law -> period
    raise NotImplementedError("orbital_elements (analysis/elements.py)")

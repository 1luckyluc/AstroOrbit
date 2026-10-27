"""Conserved quantities, used to check the integrators."""


def kinetic_energy(vel, masses):
    ke = 0.0
    for i in range(len(masses)):
        ke += 0.5 * masses[i] * (vel[2 * i] ** 2 + vel[2 * i + 1] ** 2)
    return ke

def potential_energy(pos, masses, G):
    n = len(masses)
    U = 0.0
    for i in range(n):
        for j in range(i + 1, n):      # j > i: each pair once, never i == j
            dx = pos[2 * j] - pos[2 * i]
            dy = pos[2 * j + 1] - pos[2 * i + 1]
            r = (dx * dx + dy * dy) ** 0.5
            U -= G * masses[i] * masses[j] / r
    return U

def total_energy(pos, vel, masses, G):
    return kinetic_energy(vel, masses) + potential_energy(pos, masses, G)

def angular_momentum(pos, vel, masses):
    """z-component of the total angular momentum (2D)."""
    Lz = 0.0
    for i in range(len(masses)):
        Lz += masses[i] * (pos[2 * i] * vel[2 * i + 1] - pos[2 * i + 1] * vel[2 * i])
    return Lz

def relative_drift(value, initial):
    """(value - initial) / |initial|, the quantity to plot over time."""
    if np.any(initial == 0):
        raise ValueError("Initial value cannot be zero")
    return (value - initial) / np.abs(initial)

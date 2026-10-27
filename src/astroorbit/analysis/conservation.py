"""Conserved quantities, used to check the integrators."""


def kinetic_energy(vel, masses):
    raise NotImplementedError("kinetic_energy (analysis/conservation.py)")


def potential_energy(pos, masses, G):
    raise NotImplementedError("potential_energy (analysis/conservation.py)")


def total_energy(pos, vel, masses, G):
    return kinetic_energy(vel, masses) + potential_energy(pos, masses, G)


def angular_momentum(pos, vel, masses):
    """z-component of the total angular momentum (2D)."""
    raise NotImplementedError("angular_momentum (analysis/conservation.py)")


def relative_drift(value, initial):
    """(value - initial) / |initial|, the quantity to plot over time."""
    raise NotImplementedError("relative_drift (analysis/conservation.py)")

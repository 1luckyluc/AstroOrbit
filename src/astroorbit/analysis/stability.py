"""Stability indicators: close encounters, chaos, resonances."""


def close_encounters(pos, threshold):
    """Pairs (i, j) closer than `threshold`."""
    raise NotImplementedError("close_encounters (analysis/stability.py)")


def lyapunov_estimate(separations, times):
    """Growth rate of the separation between two nearby trajectories (chaos mode)."""
    raise NotImplementedError("lyapunov_estimate (analysis/stability.py)")


def period_ratios(periods):
    """Ratios of neighbouring orbital periods, to spot resonances (e.g. 2:1, 3:2)."""
    raise NotImplementedError("period_ratios (analysis/stability.py)")

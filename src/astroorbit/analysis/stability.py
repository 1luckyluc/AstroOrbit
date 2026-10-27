"""Stability indicators: close encounters, chaos, resonances."""


def close_encounters(pos, threshold):
    """Pairs (i, j) closer than `threshold`."""
    distances = []
    n = len(pos) // 2
    for i in range(n):
        for j in range(i + 1, n):
            dx = pos[2 * j] - pos[2 * i]
            dy = pos[2 * j + 1] - pos[2 * i + 1]
            r = (dx * dx + dy * dy) ** 0.5
            if r < threshold:
                distances.append((i, j))
    return distances

def period_ratios(periods):
    """Ratios of neighbouring orbital periods, to spot resonances (e.g. 2:1, 3:2)."""
    raise NotImplementedError("period_ratios (analysis/stability.py)")

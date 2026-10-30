import numpy as np

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
    return [periods[i + 1] / periods[i] for i in range(len(periods) - 1)]

from astroorbit.analysis.conservation import total_energy

def ejected_bodies(pos, vel, masses, G, max_distance):
    """Indices of bodies that are far away with enough energy to escape."""
    ejected = []
    energy = total_energy(pos, vel, masses, G)
    for i in range(len(masses)):
        slots = [2 * i, 2 * i + 1]
        energy_without = total_energy(np.delete(pos, slots), np.delete(vel, slots), np.delete(masses, i), G)
        far = np.hypot(pos[2 * i], pos[2 * i + 1]) > max_distance
        if far and energy - energy_without > 0:
            ejected.append(i)
    return ejected


import numpy as np

def newtonian(pos, masses, G):
    """pos is a numpy array of shape (2*n,) in the form of (x0, y0, x1, y1, ...)
    returns accelerations as a flat numpy array (2*n,) in the form of (ax0, ay0, ax1, ay1, ...)"""
    n = len(masses)
    acc = np.zeros(2 * n, dtype=np.float64)

    #loop through each pair of bodies to calculate the gravitational force
    for i in range(n):
        xi, yi = pos[2 * i], pos[2 * i + 1]
        for j in range(i + 1, n):
            dx = pos[2 * j] - xi
            dy = pos[2 * j + 1] - yi
            r = np.sqrt(dx * dx + dy * dy)
            fi = G * masses[j] / r**3
            fj = G * masses[i] / r ** 3
            acc[2 * i] += fi * dx
            acc[2 * i + 1] += fi * dy
            acc[2 * j] -= fj * dx
            acc[2 * j + 1] -= fj * dy
    return acc

def euler(pos, vel, accel_fn, dt):
    a = accel_fn(pos)
    new_pos = pos + dt * vel
    new_vel = vel + dt * a
    return new_pos, new_vel

def leapfrog(pos, vel, accel_fn, dt):
    a = accel_fn(pos)
    new_vel = vel + dt * a / 2
    new_pos = pos + dt * new_vel
    new_vel = new_vel + dt * accel_fn(new_pos) / 2
    return new_pos, new_vel

def rk4(pos, vel, accel_fn, dt):
    # you might want to have a look in the Newman on 8.1.3 for RK4, 8.2 for "DIFFERENTIAL EQUATIONS WITH MORE THAN ONE VARIABLE" and 8.3 for "SECOND-ORDER DIFFERENTIAL EQUATIONS". All together this gives:
    k1_pos = vel
    k1_vel = accel_fn(pos)

    k2_pos = vel + dt * k1_vel / 2
    k2_vel = accel_fn(pos + dt * k1_pos / 2)

    k3_pos = vel + dt * k2_vel / 2
    k3_vel = accel_fn(pos + dt * k2_pos / 2)

    k4_pos = vel + dt * k3_vel
    k4_vel = accel_fn(pos + dt * k3_pos)

    new_pos = pos + dt / 6 * (k1_pos + 2*k2_pos + 2*k3_pos + k4_pos)
    new_vel = vel + dt / 6 * (k1_vel + 2*k2_vel + 2*k3_vel + k4_vel)

    return new_pos, new_vel

INTEGRATORS = {
    "Euler": euler,
    "Leapfrog": leapfrog,
    "RK4": rk4,
}

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
    # TODO: four stages k1..k4 on the state (pos, vel) with derivative (vel, accel_fn(pos))
    raise NotImplementedError("RK4")

INTEGRATORS = {
    "Euler": euler,
    "Leapfrog": leapfrog,
    "RK4": rk4,
}
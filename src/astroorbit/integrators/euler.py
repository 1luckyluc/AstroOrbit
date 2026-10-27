from astroorbit.integrators.base import Integrator, register


@register
class Euler(Integrator):
    name = "Euler"
    order = 1

    def step(self, pos, vel, accel_fn, dt):
        a = accel_fn(pos)
        new_pos = pos + dt * vel
        new_vel = vel + dt * a
        return new_pos, new_vel

from astroorbit.integrators.base import Integrator, register


@register
class Euler(Integrator):
    name = "Euler"
    order = 1

    def step(self, pos, vel, accel_fn, dt):
        a = accel_fn(pos)
        new_pos = [p + dt * v for p, v in zip(pos, vel)]
        new_vel = [v + dt * ai for v, ai in zip(vel, a)]
        return new_pos, new_vel

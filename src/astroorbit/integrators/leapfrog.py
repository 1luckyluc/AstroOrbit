from astroorbit.integrators.base import Integrator, register


@register
class Leapfrog(Integrator):
    name = "Leapfrog"
    order = 2

    def step(self, pos, vel, accel_fn, dt):
        a = accel_fn(pos)
        new_vel = [v + dt * ai / 2 for v, ai in zip(vel, a)]
        new_pos = [p + dt * v for p, v in zip(pos, new_vel)]
        a = accel_fn(new_pos)
        new_vel = [v + dt * ai / 2 for v, ai in zip(new_vel, a)]
        return new_pos, new_vel

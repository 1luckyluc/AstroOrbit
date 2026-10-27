from astroorbit.integrators.base import Integrator, register


@register
class Euler(Integrator):
    name = "Euler"
    order = 1
    description = "Explicit first-order method. Simple, but energy drifts quickly."

    def step(self, pos, vel, accel_fn, dt):
        # TODO: x_{n+1} = x_n + dt * v_n,   v_{n+1} = v_n + dt * a(x_n)
        raise NotImplementedError("Euler.step (integrators/euler.py)")

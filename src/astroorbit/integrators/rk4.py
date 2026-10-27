from astroorbit.integrators.base import Integrator, register


@register
class RK4(Integrator):
    name = "RK4"
    order = 4
    description = "Classic 4th-order Runge-Kutta. Very accurate per step, but not symplectic."

    def step(self, pos, vel, accel_fn, dt):
        # TODO: four stages k1..k4 on the state (pos, vel) with derivative (vel, accel_fn(pos))
        raise NotImplementedError("RK4.step (integrators/rk4.py)")

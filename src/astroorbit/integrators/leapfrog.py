from astroorbit.integrators.base import Integrator, register


@register
class Leapfrog(Integrator):
    name = "Leapfrog"
    order = 2
    description = "Kick-drift-kick, 2nd order and symplectic: energy error stays bounded."

    def step(self, pos, vel, accel_fn, dt):
        # TODO: half kick (v += a dt/2), drift (x += v dt), half kick with the new a
        raise NotImplementedError("Leapfrog.step (integrators/leapfrog.py)")

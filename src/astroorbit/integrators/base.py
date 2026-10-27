"""Integrator interface and registry.

Every integrator works on flat arrays and an acceleration function, so it knows
nothing about gravity: a mode can swap the force model without touching this code.

    new_pos, new_vel = integrator.step(pos, vel, accel_fn, dt)
    accel_fn(pos) -> acc   (same flat layout as pos)

To add a method: subclass Integrator, decorate it with @register, and import the
module in integrators/__init__.py. The GUI dropdown picks it up automatically.
"""
from abc import ABC, abstractmethod


class Integrator(ABC):
    name = "base"
    order = 0
    description = ""

    @abstractmethod
    def step(self, pos, vel, accel_fn, dt):
        """Advance one time step. Return (new_pos, new_vel)."""


_REGISTRY = {}


def register(cls):
    _REGISTRY[cls.name] = cls
    return cls


def get_integrator(name):
    return _REGISTRY[name]()


def available_integrators():
    return list(_REGISTRY)

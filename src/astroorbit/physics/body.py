from dataclasses import dataclass


@dataclass
class Body:
    name: str
    mass: float
    x: float
    y: float
    vx: float
    vy: float
    color: str = "#ffffff"
    radius_px: float = 4.0
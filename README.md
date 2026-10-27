# AstroOrbit
orbital simulator application

AstroOrbit/
├── README.md
├── src/astroorbit/
│   ├── physics/              # pure physics
│   │   ├── body.py           # Body dataclass (name, mass, pos, vel)
│   │   ├── system.py         # System: numpy arrays + add/edit/remove bodies
│   │   ├── forces.py         # Newtonian / other??
│   │   └── units.py          # AU/yr/Msun, SI, G=1 unit systems
│   ├── integrators/
│   │   ├── base.py           # Integrator interface + registry
│   │   ├── euler.py
│   │   ├── rk4.py
│   │   └── leapfrog.py
│   ├── analysis/
│   │   ├── elements.py       # a, e, i, ω… from state vectors
│   │   ├── conservation.py   # energy, angular momentum drift
│   │   └── stability.py      # close encounters, Lyapunov estimate, period ratios
│   ├── simulation.py         # engine: system + force + integrator + clock + history
│   ├── modes.py              # planetary / black hole / comet
│   ├── presets/
│   │   ├── loader.py
│   │   └── data/             # solar_system, two-body
│   ├── gui/                  # desktop front-end
│   │   ├── main_window.py
│   │   ├── canvas.py         
│   │   ├── panels/           
│   │   ├── plots.py          
│   │   └── help.py           
│   └── web/                  
└── tests/                    

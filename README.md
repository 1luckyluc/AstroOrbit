# AstroOrbit
orbital simulator application

## Running

```
python -m pip install -e ".[dev]"   # once, inside your environment
astroorbit                          # or: python -m astroorbit
pytest                              # run the tests
```

Without installing: `cd src && python -m astroorbit`. Needs a Python with Tk
(e.g. Anaconda's; Homebrew Python needs `brew install python-tk`).

## Structure

```
AstroOrbit/
├── README.md
├── pyproject.toml            # dependencies, `astroorbit` command, pytest config
├── src/astroorbit/
│   ├── __main__.py           # `python -m astroorbit`
│   ├── physics/              # pure physics, never imports the GUI
│   │   ├── body.py           # Body dataclass (name, mass, x, y, vx, vy)
│   │   ├── system.py         # System: flat numpy arrays + add/edit/remove bodies
│   │   ├── forces.py         # Newtonian / other??
│   │   └── units.py          # AU/yr/Msun, SI, G=1 unit systems
│   ├── integrators/
│   │   ├── base.py           # Integrator interface + registry
│   │   ├── euler.py
│   │   ├── rk4.py
│   │   └── leapfrog.py
│   ├── analysis/
│   │   ├── elements.py       # a, e, ... from state vectors
│   │   ├── conservation.py   # energy, angular momentum drift
│   │   └── stability.py      # close encounters, Lyapunov estimate, period ratios
│   ├── simulation.py         # engine: system + force + integrator + clock + history
│   ├── modes.py              # planet / comet / chaos
│   ├── presets/
│   │   ├── loader.py
│   │   └── data/             # one JSON file per preset, tagged with its mode
│   ├── gui/                  # desktop front-end (tkinter)
│   │   ├── main_window.py    # wires everything together
│   │   ├── canvas.py         # drawing, zoom, pan
│   │   ├── panels/           # controls.py, bodies.py
│   │   ├── plots.py
│   │   └── help.py           # tooltip texts
│   └── web/                  # browser version (later)
└── tests/
```

## Status

Plumbing works (modes, presets, body editing, start/pause/resume/stop/reset).
Still to implement, each raising `NotImplementedError`:

- `integrators/euler.py`, `rk4.py`, `leapfrog.py` → `step()`
- `analysis/elements.py`, `conservation.py`, `stability.py`
- `presets/loader.py` → `save_preset()`
- GUI: trails (`canvas.py`), plots (`plots.py`), browser version (`web/`)

`tests/test_integrators.py` skips each integrator until its `step()` exists.

## Adding things

- **Preset:** drop a JSON file in `presets/data/` with `"mode": "planet" | "comet" | "chaos"`.
- **Integrator:** subclass `Integrator`, decorate with `@register`, import it in `integrators/__init__.py`.
- **Mode:** add an entry to `MODES` in `modes.py`; the GUI picks it up.

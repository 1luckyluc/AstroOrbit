"""Main window: wires the mode bar, canvas, plots and side panels to a Simulation."""
import tkinter as tk
from dataclasses import replace
from tkinter import ttk

from astroorbit.gui.canvas import OrbitCanvas
from astroorbit.gui.help import Tooltip
from astroorbit.gui.panels.bodies import BodyPanel
from astroorbit.gui.panels.controls import ControlPanel
from astroorbit.gui.plots import PlotsPanel
from astroorbit.modes import MODES
from astroorbit.physics.body import Body
from astroorbit.presets.loader import list_presets
from astroorbit.simulation import Simulation, State
from astroorbit.integrators import INTEGRATORS

FRAME_MS = 16


class MainWindow:
    def __init__(self, root):
        self.root = root
        root.title("AstroOrbit")
        root.geometry("1200x780")
        self.mode = None
        self.sim = None
        self.presets = {}
        self.message = ""  # shown in the status bar until replaced
        self.mode_var = tk.StringVar(value="planet")

        self._build()
        self.load_mode("planet")
        self._tick()

    # ------------------------------------------------------------ layout ---
    def _build(self):
        top = ttk.Frame(self.root, padding=(10, 6))
        top.pack(fill="x")
        ttk.Label(top, text="AstroOrbit", font=("Helvetica", 16, "bold")).pack(side="left")
        for key, mode in MODES.items():
            rb = ttk.Radiobutton(top, text=mode.label, value=key, variable=self.mode_var,
                                 command=lambda: self.load_mode(self.mode_var.get()))
            rb.pack(side="left", padx=(16, 0))
            Tooltip(rb, mode.description)

        self.status = ttk.Label(self.root, anchor="w", padding=(10, 4))
        self.status.pack(side="bottom", fill="x")

        main = ttk.PanedWindow(self.root, orient="horizontal")
        main.pack(fill="both", expand=True)

        left = ttk.PanedWindow(main, orient="vertical")
        self.canvas = OrbitCanvas(left)
        self.canvas.on_view_change = self.redraw
        self.plots = PlotsPanel(left)
        left.add(self.canvas, weight=4)
        left.add(self.plots, weight=1)

        right = ttk.Frame(main, padding=10)
        self.controls = ControlPanel(right, on_preset=self.load_preset,
                                     on_integrator=self.set_integrator,
                                     on_command=self.command, on_view=self.redraw)
        self.controls.pack(fill="x")
        self.body_panel = BodyPanel(right, on_select=lambda i: self.redraw(),
                                    on_add=self.add_body, on_apply=self.apply_body,
                                    on_delete=self.delete_body)
        self.body_panel.pack(fill="both", expand=True, pady=(10, 0))

        main.add(left, weight=1)
        main.add(right, weight=0)

    # ------------------------------------------------------- modes/presets ---
    def load_mode(self, key):
        self.mode = MODES[key]
        self.presets = {p.name: p for p in list_presets(key)}
        self.controls.set_presets(list(self.presets))
        self.controls.set_integrators(list(INTEGRATORS.keys()), self.mode.default_integrator)
        self.plots.set_mode(self.mode)
        if self.presets:
            self.load_preset(self.controls.preset.get())

    def load_preset(self, name):
        preset = self.presets[name]
        self.sim = Simulation(preset.to_system(), self.mode,
                              integrator=self.controls.integrator.get(), dt=preset.dt)
        self.controls.dt.set(f"{self.sim.dt:g}")
        self.message = preset.description
        self.root.update_idletasks()
        self.canvas.fit(self.sim.system)
        self.refresh_bodies()

    def set_integrator(self, name):
        self.sim.set_integrator(name)
        self.redraw()

    # ------------------------------------------------------------ controls ---
    def command(self, cmd):
        self.message = ""
        try:
            self.sim.dt = float(self.controls.dt.get())
        except ValueError:
            self.message = "dt must be a number"
            self.redraw()
            return
        else:
            getattr(self.sim, cmd)()  # start / pause / resume / stop / reset
        if cmd == "reset":
            self.refresh_bodies()
        self.redraw()

    def _advance(self):
        try:
            self.sim.advance(self.controls.speed.get())
        except NotImplementedError as exc:
            self.sim.pause()
            self.message = f"Not implemented yet: {exc}"

    # -------------------------------------------------------------- bodies ---
    def refresh_bodies(self, keep=None):
        self.body_panel.set_bodies(self.sim.system.bodies(), keep)
        self.redraw()

    def add_body(self):
        n = len(self.sim.system)
        self.sim.system.add_body(Body(f"Body {n}", 1e-6, 2.0, 0.0, 0.0, 4.4, "#ff66cc", 4))
        self.refresh_bodies(keep=n)

    def apply_body(self, i, values):
        self.sim.system.update_body(i, replace(self.sim.system.body(i), **values))
        self.refresh_bodies(keep=i)

    def delete_body(self, i):
        if len(self.sim.system) > 1:
            self.sim.system.remove_body(i)
            self.refresh_bodies()

    # ---------------------------------------------------------------- loop ---
    def _tick(self):
        if self.sim and self.sim.state is State.RUNNING:
            self._advance()
            self.plots.refresh(self.sim.history)
            self.redraw()
        self.root.after(FRAME_MS, self._tick)

    def redraw(self):
        if not self.sim:
            return
        self.canvas.draw(self.sim.system,
                         show_labels=self.controls.show_labels.get(),
                         show_trails=self.controls.show_trails.get(),
                         selected=self.body_panel.selected())
        self.controls.update_buttons(self.sim.state)
        self.update_status()

    def update_status(self):
        s, u = self.sim, self.mode.units
        text = (f"{self.mode.label}  ·  {s.state.value}  ·  t = {s.t:.3f} {u.time}  ·  "
                f"{s.integrator.__name__}  ·  {len(s.system)} bodies")
        self.status.config(text=f"{text}   |   {self.message}" if self.message else text)


def main():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()

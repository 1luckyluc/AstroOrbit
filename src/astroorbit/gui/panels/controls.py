"""Simulation controls: preset, integrator, time step, speed, start/pause/resume/stop/reset."""
import tkinter as tk
from tkinter import ttk

from astroorbit.gui.help import HELP, Tooltip
from astroorbit.simulation import State

class ControlPanel(ttk.LabelFrame):
    """Calls on_preset(name), on_integrator(name), on_command(cmd), on_view()."""

    def __init__(self, master, on_preset, on_integrator, on_command, on_view):
        super().__init__(master, text="Simulation", padding=8)
        self.preset = tk.StringVar()
        self.integrator = tk.StringVar()
        self.dt = tk.StringVar()
        self.speed = tk.IntVar(value=5)
        self.show_trails = tk.BooleanVar(value=True)
        self.show_labels = tk.BooleanVar(value=True)

        ttk.Label(self, text="Preset").pack(anchor="w")
        self.preset_box = ttk.Combobox(self, textvariable=self.preset, state="readonly")
        self.preset_box.pack(fill="x")
        self.preset_box.bind("<<ComboboxSelected>>", lambda e: on_preset(self.preset.get()))

        ttk.Label(self, text="Integrator").pack(anchor="w", pady=(6, 0))
        self.integrator_box = ttk.Combobox(self, textvariable=self.integrator, state="readonly")
        self.integrator_box.pack(fill="x")
        self.integrator_box.bind("<<ComboboxSelected>>",
                                 lambda e: on_integrator(self.integrator.get()))
        Tooltip(self.integrator_box, HELP["integrator"])

        row = ttk.Frame(self)
        row.pack(fill="x", pady=(6, 0))
        ttk.Label(row, text="dt").pack(side="left")
        dt_entry = ttk.Entry(row, textvariable=self.dt, width=10)
        dt_entry.pack(side="left", padx=(4, 12))
        Tooltip(dt_entry, HELP["dt"])
        ttk.Label(row, text="speed").pack(side="left")
        speed = ttk.Scale(row, from_=1, to=50, variable=self.speed, orient="horizontal")
        speed.pack(side="left", fill="x", expand=True, padx=(4, 0))
        Tooltip(speed, HELP["speed"])

        self.buttons = {}
        row = ttk.Frame(self)
        row.pack(fill="x", pady=(6, 0))
        for label in ("Start", "Pause", "Resume", "Stop", "Reset"):
            b = ttk.Button(row, text=label, command=lambda c=label.lower(): on_command(c))
            b.pack(side="left", expand=True, fill="x")
            self.buttons[label.lower()] = b

        row = ttk.Frame(self)
        row.pack(fill="x", pady=(6, 0))
        for text, var in (("Trails", self.show_trails), ("Labels", self.show_labels)):
            cb = ttk.Checkbutton(row, text=text, variable=var, command=on_view)
            cb.pack(side="left", padx=(0, 10))
            Tooltip(cb, HELP[text.lower()])

    def set_presets(self, names):
        self.preset_box["values"] = names
        self.preset.set(names[0] if names else "")

    def set_integrators(self, names, default):
        self.integrator_box["values"] = names
        self.integrator.set(default)

    def update_buttons(self, state):
        enabled = {
            State.STOPPED: {"start", "step", "reset"},
            State.RUNNING: {"pause", "stop", "reset"},
            State.PAUSED: {"resume", "step", "stop", "reset"},
        }[state]
        for name, b in self.buttons.items():
            b.state(["!disabled"] if name in enabled else ["disabled"])

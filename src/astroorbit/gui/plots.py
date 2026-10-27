"""Plots of quantities over time (orbital elements, energy error, ...). Placeholder for now."""
from tkinter import ttk


class PlotsPanel(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="Plots", padding=8)
        self._inner = ttk.Frame(self)
        self._inner.pack(fill="both", expand=True)

    def set_mode(self, mode):
        """Show the plots this mode offers."""
        for w in self._inner.winfo_children():
            w.destroy()
        ttk.Label(self._inner, text="  ·  ".join(f"{q} vs time" for q in mode.plots)).pack(anchor="w")
        ttk.Label(self._inner, foreground="#888888",
                  text="TODO: embed matplotlib (FigureCanvasTkAgg) and draw from Simulation.history"
                  ).pack(anchor="w", pady=(6, 0))

    def refresh(self, history):
        # TODO: update the plot lines from history
        pass

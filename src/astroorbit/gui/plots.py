"""Plots of quantities over time (orbital elements, energy error, ...)."""
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

BG = "#0b0e17"
TEXT = "#c8cbe0"
REFRESH_EVERY = 10  # redraw once every this many frames: matplotlib is slow

MIN_SPAN = {"a": 0.1, "e": 0.1, "r": 0.1, "E": 0.1}  # smallest y-range per plot: stops noise being magnified

HISTORY_KEYS = {
    "Semi-major axis": "a",
    "Eccentricity": "e",
    "Energy error": "energy_error",
    "Distance to Sun": "r",
    "Total System Energy": "E",
}

class PlotsPanel(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="Plots", padding=4)
        self.fig = Figure(figsize=(8, 2), facecolor=BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.axes = {}   # history key -> matplotlib axes
        self.lines = {}  # (history key, line name) -> matplotlib line
        self.frame = 0

    def set_mode(self, mode):
        """Make one small plot for each entry in mode.plots."""
        self.fig.clear()
        self.axes, self.lines = {}, {}
        for n, title in enumerate(mode.plots):
            ax = self.fig.add_subplot(1, len(mode.plots), n + 1, facecolor=BG)
            ax.set_title(title, color=TEXT, fontsize=9)
            ax.tick_params(colors=TEXT, labelsize=7)
            ax.yaxis.get_offset_text().set_fontsize(7)
            for spine in ax.spines.values():
                spine.set_color("#444a60")
            if title in HISTORY_KEYS:
                self.axes[HISTORY_KEYS[title]] = ax
        self.fig.subplots_adjust(left=0.06, right=0.98, bottom=0.14, top=0.86, wspace=0.28)
        self.canvas.draw_idle()

    def clear(self):
        """Remove all lines, e.g. after Reset or a new preset."""
        for line in self.lines.values():
            line.remove()
        self.lines = {}
        self.canvas.draw_idle()

    def refresh(self, history, colors):
        """Update the lines from history. colors = {body name: colour}."""
        self.frame += 1
        if self.frame % REFRESH_EVERY:
            return
        for key, ax in self.axes.items():
            for name, points in history[key].items():
                if (key, name) not in self.lines:
                    self.lines[key, name] = ax.plot([], [], lw=1, color=colors.get(name, TEXT))[0]
                t, values = zip(*points)
                self.lines[key, name].set_data(t, values)
            ax.relim()
            ax.autoscale_view()
            low, high = ax.get_ylim()
            span = MIN_SPAN.get(key, 0)
            if high - low < span:
                middle = (low + high) / 2
                ax.set_ylim(middle - span / 2, middle + span / 2, auto=True)

        self.canvas.draw_idle()
"""The 2D view of the system: bodies, labels, zoom (scroll) and pan (drag)."""
import tkinter as tk

BG = "#0b0e17"


class OrbitCanvas(tk.Canvas):
    def __init__(self, master):
        super().__init__(master, bg=BG, highlightthickness=0)
        self.scale = 100.0  # pixels per length unit
        self.cx, self.cy = 0.0, 0.0  # world coordinates at the centre of the view
        self._drag = None
        self.on_view_change = lambda: None

        self.bind("<MouseWheel>", lambda e: self.zoom(1.1 if e.delta > 0 else 1 / 1.1))
        self.bind("<Button-4>", lambda e: self.zoom(1.1))  # Linux scroll
        self.bind("<Button-5>", lambda e: self.zoom(1 / 1.1))
        self.bind("<ButtonPress-1>", self._pan_start)
        self.bind("<B1-Motion>", self._pan_move)
        self.bind("<Configure>", lambda e: self.on_view_change())

    # ---- view ----
    def fit(self, system):
        """Zoom so every body is visible."""
        w, h = max(self.winfo_width(), 400), max(self.winfo_height(), 400)
        extent = max(abs(system.pos).max(initial=0) * 1.2, 1e-3)
        self.scale = min(w, h) / (2 * extent)
        self.cx, self.cy = 0.0, 0.0

    def zoom(self, factor):
        self.scale *= factor
        self.on_view_change()

    def to_screen(self, x, y):
        w, h = self.winfo_width(), self.winfo_height()
        return w / 2 + (x - self.cx) * self.scale, h / 2 - (y - self.cy) * self.scale

    def _pan_start(self, e):
        self._drag = (e.x, e.y)

    def _pan_move(self, e):
        self.cx -= (e.x - self._drag[0]) / self.scale
        self.cy += (e.y - self._drag[1]) / self.scale
        self._drag = (e.x, e.y)
        self.on_view_change()

    # ---- drawing ----
    def draw(self, system, show_labels=True, show_trails=True, selected=None):
        self.delete("all")
        # TODO: trails (needs position history from Simulation.history)
        for i in range(len(system)):
            sx, sy = self.to_screen(system.pos[2 * i], system.pos[2 * i + 1])
            r = system.radii[i]
            self.create_oval(sx - r, sy - r, sx + r, sy + r, fill=system.colors[i], outline="")
            if i == selected:
                self.create_oval(sx - r - 4, sy - r - 4, sx + r + 4, sy + r + 4, outline="#ffffff")
            if show_labels:
                self.create_text(sx + r + 4, sy - r - 2, text=system.names[i], anchor="sw",
                                 fill="#c8cbe0", font=("Helvetica", 10))

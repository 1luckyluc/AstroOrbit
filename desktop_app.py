"""AstroOrbit desktop front-end (tkinter, stdlib only).

Run:  python desktop_app.py
All physics lives in astroorbit/core.py, shared with the browser version.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from astroorbit.core import INTEGRATORS, PRESETS, Body

BG = "#0b0e17"
FRAME_MS = 16


class Tooltip:
    """Minimal hover tooltip (item 14: contextual help)."""

    def __init__(self, widget, text):
        self.widget, self.text, self.tip = widget, text, None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _):
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, justify="left", wraplength=260,
                 background="#ffffe0", relief="solid", borderwidth=1,
                 padx=6, pady=4).pack()

    def hide(self, _):
        if self.tip:
            self.tip.destroy()
            self.tip = None


class AstroOrbitApp:
    def __init__(self, root):
        self.root = root
        root.title("AstroOrbit — proof of concept")
        root.geometry("1100x720")

        self.running = False
        self.preset_name = tk.StringVar(value=next(iter(PRESETS)))
        self.integrator = tk.StringVar(value="Leapfrog")
        self.steps_per_frame = tk.IntVar(value=5)
        self.show_trails = tk.BooleanVar(value=True)
        self.show_labels = tk.BooleanVar(value=True)

        self._build_layout()
        self.load_preset()
        self._tick()

    # ------------------------------------------------------------ layout ---
    def _build_layout(self):
        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw())
        self.canvas.bind("<MouseWheel>", self._on_wheel)          # macOS / Windows
        self.canvas.bind("<Button-4>", lambda e: self._zoom(1.1, e))  # Linux
        self.canvas.bind("<Button-5>", lambda e: self._zoom(1 / 1.1, e))
        self.canvas.bind("<ButtonPress-1>", self._pan_start)
        self.canvas.bind("<B1-Motion>", self._pan_move)

        panel = ttk.Frame(self.root, padding=10, width=300)
        panel.pack(side="right", fill="y")

        ttk.Label(panel, text="Preset").pack(anchor="w")
        cb = ttk.Combobox(panel, textvariable=self.preset_name, values=list(PRESETS),
                          state="readonly")
        cb.pack(fill="x")
        cb.bind("<<ComboboxSelected>>", lambda e: self.load_preset())

        ttk.Label(panel, text="Integrator").pack(anchor="w", pady=(8, 0))
        ic = ttk.Combobox(panel, textvariable=self.integrator, values=list(INTEGRATORS),
                          state="readonly")
        ic.pack(fill="x")
        ic.bind("<<ComboboxSelected>>", lambda e: setattr(self.sim, "integrator", self.integrator.get()))
        Tooltip(ic, "Euler: 1st order, energy drifts.\nRK4: 4th order, accurate short-term, "
                    "slow drift.\nLeapfrog: 2nd order symplectic, energy error stays bounded.")

        ttk.Label(panel, text="Steps per frame (speed)").pack(anchor="w", pady=(8, 0))
        ttk.Scale(panel, from_=1, to=50, variable=self.steps_per_frame,
                  orient="horizontal").pack(fill="x")

        btns = ttk.Frame(panel)
        btns.pack(fill="x", pady=8)
        self.run_btn = ttk.Button(btns, text="Start", command=self.toggle_run)
        self.run_btn.pack(side="left", expand=True, fill="x")
        ttk.Button(btns, text="Step", command=self.single_step).pack(side="left", expand=True, fill="x")
        ttk.Button(btns, text="Reset", command=self.load_preset).pack(side="left", expand=True, fill="x")

        ttk.Checkbutton(panel, text="Trails", variable=self.show_trails,
                        command=self.draw).pack(anchor="w")
        ttk.Checkbutton(panel, text="Labels", variable=self.show_labels,
                        command=self.draw).pack(anchor="w")

        ttk.Separator(panel).pack(fill="x", pady=8)
        ttk.Label(panel, text="Bodies").pack(anchor="w")
        self.body_list = tk.Listbox(panel, height=7, exportselection=False)
        self.body_list.pack(fill="x")
        self.body_list.bind("<<ListboxSelect>>", lambda e: self._fill_editor())

        self.fields = {}
        grid = ttk.Frame(panel)
        grid.pack(fill="x", pady=4)
        for row, key in enumerate(["mass", "x", "y", "vx", "vy"]):
            ttk.Label(grid, text=key, width=6).grid(row=row, column=0, sticky="w")
            var = tk.StringVar()
            ttk.Entry(grid, textvariable=var, width=14).grid(row=row, column=1, sticky="ew")
            self.fields[key] = var
        ebtns = ttk.Frame(panel)
        ebtns.pack(fill="x")
        ttk.Button(ebtns, text="Apply", command=self.apply_edit).pack(side="left", expand=True, fill="x")
        ttk.Button(ebtns, text="Add", command=self.add_body).pack(side="left", expand=True, fill="x")
        ttk.Button(ebtns, text="Delete", command=self.delete_body).pack(side="left", expand=True, fill="x")

        ttk.Separator(panel).pack(fill="x", pady=8)
        self.readout = ttk.Label(panel, text="", justify="left", font=("Menlo", 11))
        self.readout.pack(anchor="w")
        Tooltip(self.readout, "ΔE/E: relative drift of total energy, a check on the integrator.\n"
                              "a: semi-major axis, e: eccentricity of the selected body "
                              "relative to body 0.")

    # ------------------------------------------------------------- state ---
    def load_preset(self):
        self.sim = PRESETS[self.preset_name.get()]()
        self.sim.integrator = self.integrator.get()
        self._fit_view()
        self._refresh_list()
        self.draw()

    def toggle_run(self):
        self.running = not self.running
        self.run_btn.config(text="Pause" if self.running else "Resume")

    def single_step(self):
        self.sim.step(self.steps_per_frame.get())
        self.draw()

    def _selected(self):
        sel = self.body_list.curselection()
        return sel[0] if sel else None

    def _refresh_list(self, keep=None):
        self.body_list.delete(0, "end")
        for b in self.sim.bodies:
            self.body_list.insert("end", b.name)
        if keep is not None and keep < len(self.sim.bodies):
            self.body_list.selection_set(keep)
        self._fill_editor()

    def _fill_editor(self):
        i = self._selected()
        for key, var in self.fields.items():
            var.set("" if i is None else f"{getattr(self.sim.bodies[i], key):.6g}")

    def apply_edit(self):
        i = self._selected()
        if i is None:
            return
        try:
            vals = {k: float(v.get()) for k, v in self.fields.items()}
        except ValueError:
            return
        self.sim.update_body(i, **vals)
        self._refresh_list(keep=i)
        self.draw()

    def add_body(self):
        n = len(self.sim.bodies)
        self.sim.add_body(Body(f"Body {n}", 1e-6, 2.0, 0.0, 0.0, 4.4, "#ff66cc", 4))
        self._refresh_list(keep=n)

    def delete_body(self):
        i = self._selected()
        if i is not None and len(self.sim.bodies) > 1:
            self.sim.remove_body(i)
            self._refresh_list()

    # -------------------------------------------------------------- view ---
    def _fit_view(self):
        w = max(self.canvas.winfo_width(), 600)
        h = max(self.canvas.winfo_height(), 600)
        extent = max(max(abs(c) for c in self.sim.pos), 1e-3) * 1.2
        self.scale = min(w, h) / (2 * extent)
        self.cx, self.cy = 0.0, 0.0

    def _to_screen(self, x, y):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        return w / 2 + (x - self.cx) * self.scale, h / 2 - (y - self.cy) * self.scale

    def _on_wheel(self, e):
        self._zoom(1.1 if e.delta > 0 else 1 / 1.1, e)

    def _zoom(self, factor, _e):
        self.scale *= factor
        self.draw()

    def _pan_start(self, e):
        self._drag = (e.x, e.y)

    def _pan_move(self, e):
        dx, dy = e.x - self._drag[0], e.y - self._drag[1]
        self.cx -= dx / self.scale
        self.cy += dy / self.scale
        self._drag = (e.x, e.y)
        self.draw()

    # -------------------------------------------------------------- loop ---
    def _tick(self):
        if self.running:
            self.sim.step(self.steps_per_frame.get())
            self.draw()
        self.root.after(FRAME_MS, self._tick)

    def draw(self):
        c = self.canvas
        c.delete("all")
        sim = self.sim
        if self.show_trails.get():
            for b, tr in zip(sim.bodies, sim.trails):
                if len(tr) > 1:
                    pts = [v for p in tr for v in self._to_screen(*p)]
                    c.create_line(*pts, fill=b.color, width=1)
        for b in sim.bodies:
            sx, sy = self._to_screen(b.x, b.y)
            r = b.radius_px
            c.create_oval(sx - r, sy - r, sx + r, sy + r, fill=b.color, outline="")
            if self.show_labels.get():
                c.create_text(sx + r + 4, sy - r - 4, text=b.name, fill="#c8cbe0",
                              anchor="sw", font=("Helvetica", 10))

        lines = [f"t     = {sim.t:9.3f}", f"ΔE/E  = {sim.energy_error():+.2e}"]
        i = self._selected()
        el = sim.orbital_elements(i) if i is not None else None
        if el:
            lines += [f"a     = {el['a']:9.4f}", f"e     = {el['e']:9.4f}"]
        self.readout.config(text="\n".join(lines))


if __name__ == "__main__":
    root = tk.Tk()
    AstroOrbitApp(root)
    root.mainloop()

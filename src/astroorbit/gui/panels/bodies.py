"""Body list and editor: select, add, edit and delete bodies."""
import tkinter as tk
from tkinter import ttk
import math
from astroorbit.gui.help import HELP, Tooltip

FIELDS = ("name", "mass", "x", "y", "vx", "vy")
FIELDS_DISPLAY = ("Name", "Mass (solar mass)", "x (AU)", "y (AU)", "vx (AU/year)", "vy (AU/year)")


class BodyPanel(ttk.LabelFrame):
    """Calls on_select(i), on_add(), on_apply(i, values), on_delete(i)."""

    def __init__(self, master, on_select, on_add, on_apply, on_delete):
        super().__init__(master, text="Bodies", padding=8)
        self.listbox = tk.Listbox(self, height=8, exportselection=False)
        self.listbox.pack(fill="x")
        self.listbox.bind("<<ListboxSelect>>", lambda e: self._selected_changed(on_select))

        self.vars = {}
        self.errors = {}
        grid = ttk.Frame(self)
        grid.pack(fill="x", pady=6)
        grid.columnconfigure(1, weight=1)
        for row, key in enumerate(FIELDS):
            ttk.Label(grid, text=FIELDS_DISPLAY[row], width=15).grid(row=row, column=0, sticky="w")
            var = tk.StringVar()
            entry = ttk.Entry(grid, textvariable=var)
            entry.grid(row=row, column=1, sticky="ew", pady=1)
            if key in HELP:
                Tooltip(entry, HELP[key])
            self.vars[key] = var
            error = ttk.Label(grid, foreground="#e0483e")
            error.grid(row=row, column=2, sticky="w", padx=(4, 0))
            self.errors[key] = error

        row = ttk.Frame(self)
        row.pack(fill="x")
        ttk.Button(row, text="Add", command=lambda: self._add(on_add)).pack(side="left", expand=True, fill="x")
        ttk.Button(row, text="Apply", command=lambda: self._apply(on_apply)).pack(
            side="left", expand=True, fill="x")
        ttk.Button(row, text="Delete", command=lambda: self._delete(on_delete)).pack(
            side="left", expand=True, fill="x")
        self._bodies = []

    def set_bodies(self, bodies, keep=None):
        self._bodies = bodies
        self.listbox.delete(0, "end")
        for b in bodies:
            self.listbox.insert("end", b.name)
        if keep is not None and keep < len(bodies):
            self.listbox.selection_set(keep)
        self._fill()

    def selected(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def values(self):
        """Editor contents as a dict. Bad numbers get a red message and the result is None."""
        result = {"name": self.vars["name"].get()}
        valid = True
        for key in FIELDS[1:]:
            try:
                result[key] = float(self.vars[key].get())
                ok = math.isfinite(result[key])
            except ValueError:
                ok = False
            self.errors[key].config(text="" if ok else "must be number")
            valid = valid and ok
        return result if valid else None

    def _fill(self):
        i = self.selected()
        for error in self.errors.values():
            error.config(text="")
        for key, var in self.vars.items():
            value = "" if i is None else getattr(self._bodies[i], key)
            var.set(value if isinstance(value, str) else f"{value:.6g}")

    def _selected_changed(self, on_select):
        self._fill()
        on_select(self.selected())

    def _add(self, on_add):
        values = self.values()
        if values is not None:
            on_add(values)

    def _apply(self, on_apply):
        i, values = self.selected(), self.values()
        if i is not None and values is not None:
            on_apply(i, values)

    def _delete(self, on_delete):
        i = self.selected()
        if i is not None:
            on_delete(i)

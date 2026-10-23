"""
Inspector Panel providing precision numerical inputs for selected slots,
as well as full ship and weapon CSV specification controls.
"""

import tkinter as tk
from tkinter import ttk
from .constants import MOUNT_SIZES, MOUNT_TYPES, WEAPON_TYPES, ENGINE_STYLES, SHIELD_TYPES

class InspectorPanel(tk.Frame):
    def __init__(self, parent, on_change_callback=None):
        super().__init__(parent, bg="#161b22", width=340)
        self.pack_propagate(False)

        self.on_change_callback = on_change_callback
        self.current_selection = None
        self.ship_project = None
        self.weapon_project = None

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style(self)
        style.configure("Inspect.TNotebook", background="#161b22", borderwidth=0)
        style.configure("Inspect.TNotebook.Tab", background="#21262d", foreground="#e2e8f0", padding=[8, 4])
        style.map("Inspect.TNotebook.Tab", background=[("selected", "#2563eb")], foreground=[("selected", "#ffffff")])

        self.notebook = ttk.Notebook(self, style="Inspect.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=4, pady=4)

        # Tab 1: Selection Inspector
        self.tab_selection = tk.Frame(self.notebook, bg="#161b22")
        self.notebook.add(self.tab_selection, text="Selected Item")
        self.build_selection_tab()

        # Tab 2: Ship Stats
        self.tab_ship_stats = tk.Frame(self.notebook, bg="#161b22")
        self.notebook.add(self.tab_ship_stats, text="Ship Specs")
        self.build_ship_stats_tab()

        # Tab 3: Weapon Stats
        self.tab_weapon_stats = tk.Frame(self.notebook, bg="#161b22")
        self.notebook.add(self.tab_weapon_stats, text="Weapon Specs")
        self.build_weapon_stats_tab()

    def build_selection_tab(self):
        self.sel_container = tk.Frame(self.tab_selection, bg="#161b22", padx=8, pady=8)
        self.sel_container.pack(fill="both", expand=True)
        self.show_no_selection()

    def show_no_selection(self):
        for widget in self.sel_container.winfo_children():
            widget.destroy()
        lbl = tk.Label(self.sel_container, text="No Item Selected\n\nClick a Weapon Mount, Engine Nozzle,\nor Bound vertex on the canvas to inspect.",
                       fg="#8b949e", bg="#161b22", font=("Segoe UI", 9), justify="center")
        lbl.pack(expand=True)

    def set_selection(self, item):
        self.current_selection = item
        for widget in self.sel_container.winfo_children():
            widget.destroy()

        if not item:
            self.show_no_selection()
            return

        item_type, item_obj = item
        if item_type == "WEAPON":
            self.render_weapon_slot_inspector(item_obj)
        elif item_type == "ENGINE":
            self.render_engine_slot_inspector(item_obj)
        elif item_type == "BOUND":
            self.render_bound_inspector(item_obj)
        elif item_type == "OFFSET":
            self.render_offset_inspector(item_obj)
        elif item_type == "SHIELD":
            self.render_shield_inspector()

    def create_row(self, parent, label_text):
        row = tk.Frame(parent, bg="#161b22")
        row.pack(fill="x", pady=2)
        lbl = tk.Label(row, text=label_text, width=14, anchor="w", fg="#c9d1d9", bg="#161b22", font=("Segoe UI", 9))
        lbl.pack(side="left")
        return row

    def render_weapon_slot_inspector(self, slot):
        tk.Label(self.sel_container, text=f"Weapon Slot: {slot.id}",
                 font=("Segoe UI", 11, "bold"), fg="#38bdf8", bg="#161b22").pack(anchor="w", pady=(0, 8))

        # ID
        r = self.create_row(self.sel_container, "Slot ID:")
        id_var = tk.StringVar(value=slot.id)
        e_id = tk.Entry(r, textvariable=id_var, bg="#0d1117", fg="#ffffff", insertbackground="#fff", relief="flat")
        e_id.pack(side="left", fill="x", expand=True)
        def on_id_change(*args):
            slot.id = id_var.get()
            if self.on_change_callback: self.on_change_callback()
        id_var.trace_add("write", on_id_change)

        # Mount Type
        r = self.create_row(self.sel_container, "Mount Style:")
        mount_var = tk.StringVar(value=slot.mount)
        cb_mount = ttk.Combobox(r, values=MOUNT_TYPES, textvariable=mount_var, state="readonly", width=12)
        cb_mount.pack(side="left")
        def on_mount_change(e):
            slot.mount = mount_var.get()
            if self.on_change_callback: self.on_change_callback()
        cb_mount.bind("<<ComboboxSelected>>", on_mount_change)

        # Size
        r = self.create_row(self.sel_container, "Size:")
        size_var = tk.StringVar(value=slot.size)
        cb_size = ttk.Combobox(r, values=MOUNT_SIZES, textvariable=size_var, state="readonly", width=12)
        cb_size.pack(side="left")
        def on_size_change(e):
            slot.size = size_var.get()
            if self.on_change_callback: self.on_change_callback()
        cb_size.bind("<<ComboboxSelected>>", on_size_change)

        # Weapon Type
        r = self.create_row(self.sel_container, "Type / Affinity:")
        type_var = tk.StringVar(value=slot.type)
        cb_type = ttk.Combobox(r, values=WEAPON_TYPES, textvariable=type_var, state="readonly", width=12)
        cb_type.pack(side="left")
        def on_type_change(e):
            slot.type = type_var.get()
            if self.on_change_callback: self.on_change_callback()
        cb_type.bind("<<ComboboxSelected>>", on_type_change)

        # Position X
        r = self.create_row(self.sel_container, "Forward X (px):")
        x_var = tk.DoubleVar(value=slot.x)
        sb_x = tk.Spinbox(r, from_=-500, to=500, increment=1, textvariable=x_var,
                          bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat")
        sb_x.pack(side="left")
        def on_x_change(*args):
            try: slot.x = x_var.get()
            except: pass
            if self.on_change_callback: self.on_change_callback()
        x_var.trace_add("write", on_x_change)

        # Position Y
        r = self.create_row(self.sel_container, "Lateral Y (px):")
        y_var = tk.DoubleVar(value=slot.y)
        sb_y = tk.Spinbox(r, from_=-500, to=500, increment=1, textvariable=y_var,
                          bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat")
        sb_y.pack(side="left")
        def on_y_change(*args):
            try: slot.y = y_var.get()
            except: pass
            if self.on_change_callback: self.on_change_callback()
        y_var.trace_add("write", on_y_change)

        # Facing Angle
        r = self.create_row(self.sel_container, "Angle (deg):")
        ang_var = tk.DoubleVar(value=slot.angle)
        sb_ang = tk.Spinbox(r, from_=-360, to=360, increment=5, textvariable=ang_var,
                            bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat")
        sb_ang.pack(side="left")
        def on_ang_change(*args):
            try: slot.angle = ang_var.get()
            except: pass
            if self.on_change_callback: self.on_change_callback()
        ang_var.trace_add("write", on_ang_change)

        # Quick angle snaps
        snap_f = tk.Frame(self.sel_container, bg="#161b22")
        snap_f.pack(fill="x", pady=4)
        for label, val in [("0° (Fwd)", 0), ("90° (Port)", 90), ("180° (Aft)", 180), ("-90° (Stbd)", -90)]:
            tk.Button(snap_f, text=label, command=lambda v=val: ang_var.set(v),
                      bg="#21262d", fg="#c9d1d9", font=("Segoe UI", 8), padx=4, pady=1, relief="flat").pack(side="left", padx=2)

        # Arc
        r = self.create_row(self.sel_container, "Arc (deg):")
        arc_var = tk.DoubleVar(value=slot.arc)
        sb_arc = tk.Spinbox(r, from_=5, to=360, increment=10, textvariable=arc_var,
                            bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat")
        sb_arc.pack(side="left")
        def on_arc_change(*args):
            try: slot.arc = arc_var.get()
            except: pass
            if self.on_change_callback: self.on_change_callback()
        arc_var.trace_add("write", on_arc_change)

        # Quick Arc snaps
        snap_arc = tk.Frame(self.sel_container, bg="#161b22")
        snap_arc.pack(fill="x", pady=4)
        for label, val in [("5° (Fixed)", 5), ("120°", 120), ("180°", 180), ("360° (Omni)", 360)]:
            tk.Button(snap_arc, text=label, command=lambda v=val: arc_var.set(v),
                      bg="#21262d", fg="#c9d1d9", font=("Segoe UI", 8), padx=4, pady=1, relief="flat").pack(side="left", padx=2)

    def render_engine_slot_inspector(self, eng):
        tk.Label(self.sel_container, text="Engine Nozzle Slot",
                 font=("Segoe UI", 11, "bold"), fg="#f97316", bg="#161b22").pack(anchor="w", pady=(0, 8))

        # Position X
        r = self.create_row(self.sel_container, "Forward X (px):")
        x_var = tk.DoubleVar(value=eng.x)
        tk.Spinbox(r, from_=-500, to=500, increment=1, textvariable=x_var,
                   bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat").pack(side="left")
        x_var.trace_add("write", lambda *a: setattr(eng, "x", x_var.get()) or self.on_change_callback())

        # Position Y
        r = self.create_row(self.sel_container, "Lateral Y (px):")
        y_var = tk.DoubleVar(value=eng.y)
        tk.Spinbox(r, from_=-500, to=500, increment=1, textvariable=y_var,
                   bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat").pack(side="left")
        y_var.trace_add("write", lambda *a: setattr(eng, "y", y_var.get()) or self.on_change_callback())

        # Angle
        r = self.create_row(self.sel_container, "Angle (deg):")
        ang_var = tk.DoubleVar(value=eng.angle)
        tk.Spinbox(r, from_=-360, to=360, increment=5, textvariable=ang_var,
                   bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat").pack(side="left")
        ang_var.trace_add("write", lambda *a: setattr(eng, "angle", ang_var.get()) or self.on_change_callback())

        # Quick angle snaps for engines
        snap_f = tk.Frame(self.sel_container, bg="#161b22")
        snap_f.pack(fill="x", pady=4)
        for label, val in [("180° (Main)", 180), ("0° (Retro)", 0), ("90° (Strafe L)", 90), ("-90° (Strafe R)", -90)]:
            tk.Button(snap_f, text=label, command=lambda v=val: ang_var.set(v),
                      bg="#21262d", fg="#c9d1d9", font=("Segoe UI", 8), padx=3, pady=1, relief="flat").pack(side="left", padx=2)

        # Length
        r = self.create_row(self.sel_container, "Length (px):")
        len_var = tk.DoubleVar(value=eng.length)
        tk.Spinbox(r, from_=1, to=200, increment=2, textvariable=len_var,
                   bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat").pack(side="left")
        len_var.trace_add("write", lambda *a: setattr(eng, "length", len_var.get()) or self.on_change_callback())

        # Width
        r = self.create_row(self.sel_container, "Width (px):")
        w_var = tk.DoubleVar(value=eng.width)
        tk.Spinbox(r, from_=1, to=100, increment=1, textvariable=w_var,
                   bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat").pack(side="left")
        w_var.trace_add("write", lambda *a: setattr(eng, "width", w_var.get()) or self.on_change_callback())

        # Contrail
        r = self.create_row(self.sel_container, "Contrail Size:")
        c_var = tk.DoubleVar(value=eng.contrail_size)
        tk.Spinbox(r, from_=1, to=200, increment=4, textvariable=c_var,
                   bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat").pack(side="left")
        c_var.trace_add("write", lambda *a: setattr(eng, "contrail_size", c_var.get()) or self.on_change_callback())

        # Style
        r = self.create_row(self.sel_container, "Visual Style:")
        style_var = tk.StringVar(value=eng.style)
        cb_s = ttk.Combobox(r, values=ENGINE_STYLES, textvariable=style_var, state="readonly", width=12)
        cb_s.pack(side="left")
        cb_s.bind("<<ComboboxSelected>>", lambda e: setattr(eng, "style", style_var.get()) or self.on_change_callback())

    def render_bound_inspector(self, idx):
        tk.Label(self.sel_container, text=f"Collision Bound Vertex #{idx+1}",
                 font=("Segoe UI", 11, "bold"), fg="#10b981", bg="#161b22").pack(anchor="w", pady=(0, 8))
        pt = self.ship_project.bounds[idx]

        r = self.create_row(self.sel_container, "Forward X (px):")
        x_var = tk.DoubleVar(value=pt[0])
        tk.Spinbox(r, from_=-500, to=500, increment=1, textvariable=x_var,
                   bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat").pack(side="left")
        def on_x(*a):
            self.ship_project.bounds[idx] = (x_var.get(), self.ship_project.bounds[idx][1])
            if self.on_change_callback: self.on_change_callback()
        x_var.trace_add("write", on_x)

        r = self.create_row(self.sel_container, "Lateral Y (px):")
        y_var = tk.DoubleVar(value=pt[1])
        tk.Spinbox(r, from_=-500, to=500, increment=1, textvariable=y_var,
                   bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat").pack(side="left")
        def on_y(*a):
            self.ship_project.bounds[idx] = (self.ship_project.bounds[idx][0], y_var.get())
            if self.on_change_callback: self.on_change_callback()
        y_var.trace_add("write", on_y)

    def render_offset_inspector(self, idx):
        tk.Label(self.sel_container, text=f"Weapon Barrel Offset #{idx+1}",
                 font=("Segoe UI", 11, "bold"), fg="#ef4444", bg="#161b22").pack(anchor="w", pady=(0, 8))
        offsets = self.weapon_project.turret_offsets
        pt = offsets[idx]

        r = self.create_row(self.sel_container, "Forward X (px):")
        x_var = tk.DoubleVar(value=pt[0])
        tk.Spinbox(r, from_=-200, to=200, increment=1, textvariable=x_var,
                   bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat").pack(side="left")
        x_var.trace_add("write", lambda *a: offsets.__setitem__(idx, [x_var.get(), offsets[idx][1]]) or self.on_change_callback())

        r = self.create_row(self.sel_container, "Lateral Y (px):")
        y_var = tk.DoubleVar(value=pt[1])
        tk.Spinbox(r, from_=-200, to=200, increment=1, textvariable=y_var,
                   bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat").pack(side="left")
        y_var.trace_add("write", lambda *a: offsets.__setitem__(idx, [offsets[idx][0], y_var.get()]) or self.on_change_callback())

    def render_shield_inspector(self):
        tk.Label(self.sel_container, text="Shield Bubble Parameters",
                 font=("Segoe UI", 11, "bold"), fg="#06b6d4", bg="#161b22").pack(anchor="w", pady=(0, 8))
        sp = self.ship_project

        r = self.create_row(self.sel_container, "Shield Radius (px):")
        r_var = tk.DoubleVar(value=sp.shield_radius)
        tk.Spinbox(r, from_=10, to=600, increment=5, textvariable=r_var,
                   bg="#0d1117", fg="#ffffff", insertbackground="#fff", width=8, relief="flat").pack(side="left")
        r_var.trace_add("write", lambda *a: setattr(sp, "shield_radius", r_var.get()) or self.on_change_callback())

    def build_ship_stats_tab(self):
        # Scrollable container for ship specs
        canvas = tk.Canvas(self.tab_ship_stats, bg="#161b22", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_ship_stats, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#161b22", padx=6, pady=6)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yview_command=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.ship_entries = {}

        def add_section(title, fields):
            tk.Label(scrollable_frame, text=title, font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#161b22").pack(anchor="w", pady=(8, 2))
            for f_key, label in fields:
                r = tk.Frame(scrollable_frame, bg="#161b22")
                r.pack(fill="x", pady=1)
                tk.Label(r, text=label, width=13, anchor="w", fg="#c9d1d9", bg="#161b22", font=("Segoe UI", 8)).pack(side="left")
                var = tk.StringVar()
                e = tk.Entry(r, textvariable=var, bg="#0d1117", fg="#ffffff", insertbackground="#fff", relief="flat", font=("Segoe UI", 8))
                e.pack(side="left", fill="x", expand=True)
                self.ship_entries[f_key] = var
                var.trace_add("write", lambda *a, k=f_key, v=var: self.on_ship_stat_change(k, v))

        add_section("Combat Stats", [
            ("hitpoints", "Hull HP:"),
            ("armor rating", "Armor Rating:"),
            ("max flux", "Max Flux:"),
            ("flux dissipation", "Flux Diss.:"),
            ("ordnance points", "Ordnance Pts:"),
            ("supplies/rec", "Deploy Cost (DP):")
        ])

        add_section("Mobility", [
            ("max speed", "Max Speed:"),
            ("acceleration", "Acceleration:"),
            ("deceleration", "Deceleration:"),
            ("max turn rate", "Max Turn Rate:"),
            ("turn acceleration", "Turn Accel:"),
            ("mass", "Mass:")
        ])

        add_section("Shields & System", [
            ("system id", "System ID:"),
            ("shield type", "Shield Type:"),
            ("shield arc", "Shield Arc:"),
            ("shield upkeep", "Shield Upkeep:"),
            ("shield efficiency", "Shield Eff.:")
        ])

        add_section("Logistics", [
            ("min crew", "Min Crew:"),
            ("max crew", "Max Crew:"),
            ("cargo", "Cargo Space:"),
            ("fuel", "Fuel Capacity:"),
            ("max burn", "Max Burn:"),
            ("base value", "Base Value (¢):")
        ])

    def on_ship_stat_change(self, key, var):
        if self.ship_project:
            self.ship_project.stats[key] = var.get()
            if self.on_change_callback:
                self.on_change_callback()

    def update_ship_stats_display(self, project):
        self.ship_project = project
        if not project:
            return
        for k, var in self.ship_entries.items():
            val = project.stats.get(k, "")
            var.set(str(val))

    def build_weapon_stats_tab(self):
        canvas = tk.Canvas(self.tab_weapon_stats, bg="#161b22", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_weapon_stats, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#161b22", padx=6, pady=6)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yview_command=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.weapon_entries = {}

        def add_wpn_section(title, fields):
            tk.Label(scrollable_frame, text=title, font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#161b22").pack(anchor="w", pady=(8, 2))
            for f_key, label in fields:
                r = tk.Frame(scrollable_frame, bg="#161b22")
                r.pack(fill="x", pady=1)
                tk.Label(r, text=label, width=13, anchor="w", fg="#c9d1d9", bg="#161b22", font=("Segoe UI", 8)).pack(side="left")
                var = tk.StringVar()
                e = tk.Entry(r, textvariable=var, bg="#0d1117", fg="#ffffff", insertbackground="#fff", relief="flat", font=("Segoe UI", 8))
                e.pack(side="left", fill="x", expand=True)
                self.weapon_entries[f_key] = var
                var.trace_add("write", lambda *a, k=f_key, v=var: self.on_weapon_stat_change(k, v))

        add_wpn_section("Combat Output", [
            ("damage/shot", "Dmg / Shot:"),
            ("damage/second", "DPS:"),
            ("emp", "EMP Damage:"),
            ("range", "Range (px):"),
            ("proj speed", "Proj Speed:"),
            ("OPs", "Ordnance Cost:")
        ])

        add_wpn_section("Cycle & Flux", [
            ("energy/shot", "Flux / Shot:"),
            ("chargeup", "Chargeup Sec:"),
            ("chargedown", "Chargedown Sec:"),
            ("burst size", "Burst Size:"),
            ("burst delay", "Burst Delay:")
        ])

    def on_weapon_stat_change(self, key, var):
        if self.weapon_project:
            self.weapon_project.stats[key] = var.get()
            if self.on_change_callback:
                self.on_change_callback()

    def update_weapon_stats_display(self, project):
        self.weapon_project = project
        if not project:
            return
        for k, var in self.weapon_entries.items():
            val = project.stats.get(k, "")
            var.set(str(val))

"""
Inspector Panel providing precision numerical inputs for selected slots,
as well as full ship and weapon CSV specification controls.
Designed with high-contrast readable typography and distinct control frames.
"""

import tkinter as tk
from tkinter import ttk
from .constants import MOUNT_SIZES, MOUNT_TYPES, WEAPON_TYPES, ENGINE_STYLES, SHIELD_TYPES

class InspectorPanel(tk.Frame):
    def __init__(self, parent, on_change_callback=None):
        super().__init__(parent, bg="#1a2028", width=360, highlightbackground="#374151", highlightthickness=1)
        self.pack_propagate(False)

        self.on_change_callback = on_change_callback
        self.current_selection = None
        self.ship_project = None
        self.weapon_project = None
        self.active_vars = {}
        self._is_syncing_to_ui = False
        self._is_updating_model = False

        self.setup_ui()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self, style="Inspect.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=4, pady=4)

        # Tab 1: Selection Inspector
        self.tab_selection = tk.Frame(self.notebook, bg="#1a2028")
        self.notebook.add(self.tab_selection, text="Selected Item")
        self.build_selection_tab()

        # Tab 2: Ship Stats
        self.tab_ship_stats = tk.Frame(self.notebook, bg="#1a2028")
        self.notebook.add(self.tab_ship_stats, text="Ship Specs")
        self.build_ship_stats_tab()

        # Tab 3: Weapon Stats
        self.tab_weapon_stats = tk.Frame(self.notebook, bg="#1a2028")
        self.notebook.add(self.tab_weapon_stats, text="Weapon Specs")
        self.build_weapon_stats_tab()

    def build_selection_tab(self):
        self.sel_container = tk.Frame(self.tab_selection, bg="#1a2028", padx=10, pady=10)
        self.sel_container.pack(fill="both", expand=True)
        self.show_no_selection()

    def show_no_selection(self):
        for widget in self.sel_container.winfo_children():
            widget.destroy()

        card = tk.Frame(self.sel_container, bg="#242c37", padx=14, pady=16,
                        highlightbackground="#374151", highlightthickness=1)
        card.pack(fill="x", pady=15)

        tk.Label(card, text="SELECTION INSPECTOR",
                 fg="#38bdf8", bg="#242c37", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(card, text="No Mount or Slot Selected",
                 fg="#ffffff", bg="#242c37", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(2, 10))

        info_text = (
            "Click any interactive element on the canvas to inspect and edit its coordinates and properties:\n\n"
            "✦ Weapon Mounts: Arc, Angle, Type, Size\n"
            "✦ Engine Slots: Nozzle Width, Length, Angle\n"
            "✦ Collision Bounds: Drag or add vertices\n"
            "✦ Shield Bubble: Radius and Center\n\n"
            "Use '+ Add Mount' or '+ Add Engine' in the top toolbar to place new slots."
        )
        tk.Label(card, text=info_text, fg="#f0f6fc", bg="#242c37",
                 font=("Segoe UI", 9), justify="left", wraplength=280).pack(anchor="w")

    def set_selection(self, item):
        # If selecting the exact same model item, just live-sync values without UI rebuild
        if item and self.current_selection and item[0] == self.current_selection[0] and item[1] is self.current_selection[1]:
            self.sync_selection_values()
            return

        self.current_selection = item
        self.active_vars = {}
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

    def sync_selection_values(self):
        """Updates the inspector input variables from the currently selected model item without recreating widgets."""
        if not self.current_selection or getattr(self, "_is_updating_model", False):
            return

        self._is_syncing_to_ui = True
        try:
            itype, iobj = self.current_selection
            if itype == "WEAPON":
                if "x" in self.active_vars: self.active_vars["x"].set(round(iobj.x, 1))
                if "y" in self.active_vars: self.active_vars["y"].set(round(iobj.y, 1))
                if "angle" in self.active_vars: self.active_vars["angle"].set(round(iobj.angle, 1))
                if "arc" in self.active_vars: self.active_vars["arc"].set(round(iobj.arc, 1))
                if "id" in self.active_vars: self.active_vars["id"].set(iobj.id)
            elif itype == "ENGINE":
                if "x" in self.active_vars: self.active_vars["x"].set(round(iobj.x, 1))
                if "y" in self.active_vars: self.active_vars["y"].set(round(iobj.y, 1))
                if "angle" in self.active_vars: self.active_vars["angle"].set(round(iobj.angle, 1))
                if "length" in self.active_vars: self.active_vars["length"].set(round(iobj.length, 1))
                if "width" in self.active_vars: self.active_vars["width"].set(round(iobj.width, 1))
                if "contrail" in self.active_vars: self.active_vars["contrail"].set(round(iobj.contrail_size, 1))
            elif itype == "BOUND":
                idx = iobj
                if self.ship_project and idx < len(self.ship_project.bounds):
                    pt = self.ship_project.bounds[idx]
                    if "x" in self.active_vars: self.active_vars["x"].set(round(pt[0], 1))
                    if "y" in self.active_vars: self.active_vars["y"].set(round(pt[1], 1))
            elif itype == "OFFSET":
                idx = iobj
                if self.weapon_project:
                    offsets = self.weapon_project.turret_offsets
                    if idx < len(offsets):
                        pt = offsets[idx]
                        if "x" in self.active_vars: self.active_vars["x"].set(round(pt[0], 1))
                        if "y" in self.active_vars: self.active_vars["y"].set(round(pt[1], 1))
            elif itype == "SHIELD":
                if self.ship_project:
                    if "radius" in self.active_vars: self.active_vars["radius"].set(round(self.ship_project.shield_radius, 1))
        finally:
            self._is_syncing_to_ui = False

    def create_row(self, parent, label_text):
        row = tk.Frame(parent, bg="#1a2028")
        row.pack(fill="x", pady=3)
        lbl = tk.Label(row, text=label_text, width=14, anchor="w", fg="#f8fafc", bg="#1a2028", font=("Segoe UI", 9, "bold"))
        lbl.pack(side="left")
        return row

    def create_numeric_spinbox(self, parent, label_text, var_key, initial_val, from_val, to_val, step_val, on_val_change):
        r = self.create_row(parent, label_text)
        var = tk.DoubleVar(value=float(initial_val))
        self.active_vars[var_key] = var

        def commit_change(*args):
            if getattr(self, "_is_syncing_to_ui", False):
                return
            try:
                val = var.get()
            except (ValueError, tk.TclError):
                return
            self._is_updating_model = True
            try:
                on_val_change(val)
                if self.on_change_callback:
                    self.on_change_callback()
            finally:
                self._is_updating_model = False

        sb = tk.Spinbox(r, from_=from_val, to=to_val, increment=step_val, textvariable=var,
                        command=commit_change,
                        bg="#11161d", fg="#ffffff", insertbackground="#38bdf8", width=10, relief="flat",
                        highlightbackground="#475569", highlightcolor="#38bdf8", highlightthickness=1,
                        font=("Segoe UI", 9, "bold"))
        sb.pack(side="left")

        sb.bind("<KeyRelease>", lambda e: commit_change())
        sb.bind("<FocusOut>", lambda e: commit_change())
        var.trace_add("write", commit_change)

        return var, sb

    def render_weapon_slot_inspector(self, slot):
        # Header Badge
        header_f = tk.Frame(self.sel_container, bg="#0284c7", padx=8, pady=4)
        header_f.pack(fill="x", pady=(0, 10))
        tk.Label(header_f, text=f"Weapon Slot: {slot.id}",
                 font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#0284c7").pack(side="left")

        # ID
        r = self.create_row(self.sel_container, "Slot ID:")
        id_var = tk.StringVar(value=slot.id)
        e_id = tk.Entry(r, textvariable=id_var, bg="#11161d", fg="#ffffff", insertbackground="#38bdf8",
                        relief="flat", highlightbackground="#475569", highlightcolor="#38bdf8", highlightthickness=1,
                        font=("Segoe UI", 9, "bold"))
        e_id.pack(side="left", fill="x", expand=True)
        def on_id_change(*args):
            slot.id = id_var.get()
            if self.on_change_callback: self.on_change_callback()
        id_var.trace_add("write", on_id_change)

        # Mount Style (Segmented toggle buttons)
        r = self.create_row(self.sel_container, "Mount Style:")
        seg_mount = tk.Frame(r, bg="#1a2028")
        seg_mount.pack(side="left")

        def set_mount_style(new_style):
            slot.mount = new_style
            update_mount_btns()
            if self.on_change_callback: self.on_change_callback()

        btn_turret = tk.Button(seg_mount, text="Turret", font=("Segoe UI", 8, "bold"),
                               padx=6, pady=2, relief="flat", cursor="hand2",
                               command=lambda: set_mount_style("TURRET"))
        btn_turret.pack(side="left", padx=1)

        btn_hardpoint = tk.Button(seg_mount, text="Hardpoint", font=("Segoe UI", 8, "bold"),
                                  padx=6, pady=2, relief="flat", cursor="hand2",
                                  command=lambda: set_mount_style("HARDPOINT"))
        btn_hardpoint.pack(side="left", padx=1)

        btn_hidden = tk.Button(seg_mount, text="Hidden", font=("Segoe UI", 8, "bold"),
                               padx=6, pady=2, relief="flat", cursor="hand2",
                               command=lambda: set_mount_style("HIDDEN"))
        btn_hidden.pack(side="left", padx=1)

        def update_mount_btns():
            st = slot.mount
            btn_turret.configure(
                bg="#0284c7" if st == "TURRET" else "#242c37",
                fg="#ffffff" if st == "TURRET" else "#94a3b8",
                highlightbackground="#38bdf8" if st == "TURRET" else "#374151",
                highlightthickness=1
            )
            btn_hardpoint.configure(
                bg="#d97706" if st == "HARDPOINT" else "#242c37",
                fg="#ffffff" if st == "HARDPOINT" else "#94a3b8",
                highlightbackground="#f59e0b" if st == "HARDPOINT" else "#374151",
                highlightthickness=1
            )
            btn_hidden.configure(
                bg="#475569" if st == "HIDDEN" else "#242c37",
                fg="#ffffff" if st == "HIDDEN" else "#94a3b8",
                highlightbackground="#64748b" if st == "HIDDEN" else "#374151",
                highlightthickness=1
            )
        update_mount_btns()

        # Size (Segmented buttons)
        r = self.create_row(self.sel_container, "Size:")
        seg_size = tk.Frame(r, bg="#1a2028")
        seg_size.pack(side="left")

        def set_size(s):
            slot.size = s
            update_size_btns()
            if self.on_change_callback: self.on_change_callback()

        size_btns = {}
        for s_val in MOUNT_SIZES:
            s_btn = tk.Button(seg_size, text=s_val.capitalize(), font=("Segoe UI", 8, "bold"),
                              padx=6, pady=2, relief="flat", cursor="hand2",
                              command=lambda v=s_val: set_size(v))
            s_btn.pack(side="left", padx=1)
            size_btns[s_val] = s_btn

        def update_size_btns():
            for s_val, btn in size_btns.items():
                if slot.size == s_val:
                    btn.configure(bg="#2563eb", fg="#ffffff", highlightbackground="#38bdf8", highlightthickness=1)
                else:
                    btn.configure(bg="#242c37", fg="#94a3b8", highlightbackground="#374151", highlightthickness=1)
        update_size_btns()

        # Weapon Type / Affinity
        r = self.create_row(self.sel_container, "Affinity / Type:")
        type_var = tk.StringVar(value=slot.type)
        cb_type = ttk.Combobox(r, values=WEAPON_TYPES, textvariable=type_var, state="readonly", width=14)
        cb_type.pack(side="left")
        def on_type_change(e):
            slot.type = type_var.get()
            update_type_pills()
            if self.on_change_callback: self.on_change_callback()
        cb_type.bind("<<ComboboxSelected>>", on_type_change)

        # Quick Affinity Pills (including Synergy in purple)
        pills_row = tk.Frame(self.sel_container, bg="#1a2028")
        pills_row.pack(fill="x", pady=(2, 6))
        type_pills = [
            ("Ballistic", "BALLISTIC", "#f59e0b"),
            ("Energy", "ENERGY", "#06b6d4"),
            ("Missile", "MISSILE", "#10b981"),
            ("Synergy", "SYNERGY", "#8b5cf6"),
            ("Composite", "COMPOSITE", "#84cc16"),
            ("Universal", "UNIVERSAL", "#f8fafc"),
        ]
        pill_btns = {}
        def set_pill_type(t):
            slot.type = t
            type_var.set(t)
            update_type_pills()
            if self.on_change_callback: self.on_change_callback()

        for label, t_val, col in type_pills:
            fg_col = "#0f172a" if t_val == "UNIVERSAL" else "#ffffff"
            btn = tk.Button(pills_row, text=label, font=("Segoe UI", 7, "bold"),
                            padx=4, pady=1, relief="flat", cursor="hand2",
                            command=lambda v=t_val: set_pill_type(v))
            btn.pack(side="left", padx=1)
            pill_btns[t_val] = (btn, col, fg_col)

        def update_type_pills():
            for t_val, (btn, col, fg_col) in pill_btns.items():
                if slot.type == t_val:
                    btn.configure(bg=col, fg=fg_col, highlightbackground="#ffffff", highlightthickness=1)
                else:
                    btn.configure(bg="#242c37", fg="#94a3b8", highlightbackground="#374151", highlightthickness=1)
        update_type_pills()

        # Position X
        x_var, sb_x = self.create_numeric_spinbox(
            self.sel_container, "Forward X (px):", "x", slot.x, -500, 500, 1,
            lambda v: setattr(slot, "x", v)
        )

        # Position Y
        y_var, sb_y = self.create_numeric_spinbox(
            self.sel_container, "Lateral Y (px):", "y", slot.y, -500, 500, 1,
            lambda v: setattr(slot, "y", v)
        )

        # Facing Angle
        ang_var, sb_ang = self.create_numeric_spinbox(
            self.sel_container, "Angle (deg):", "angle", slot.angle, -360, 360, 5,
            lambda v: setattr(slot, "angle", v)
        )

        # Quick angle snaps
        snap_f = tk.Frame(self.sel_container, bg="#1a2028")
        snap_f.pack(fill="x", pady=4)
        for label, val in [("0° Fwd", 0), ("90° Port", 90), ("180° Aft", 180), ("-90° Stbd", -90)]:
            tk.Button(snap_f, text=label, command=lambda v=val: ang_var.set(v),
                      bg="#334155", fg="#f8fafc", activebackground="#475569", font=("Segoe UI", 8, "bold"),
                      padx=5, pady=2, relief="flat", highlightbackground="#4b5563", highlightthickness=1).pack(side="left", padx=2)

        # Arc
        arc_var, sb_arc = self.create_numeric_spinbox(
            self.sel_container, "Arc (deg):", "arc", slot.arc, 5, 360, 10,
            lambda v: setattr(slot, "arc", v)
        )

        # Quick Arc snaps
        snap_arc = tk.Frame(self.sel_container, bg="#1a2028")
        snap_arc.pack(fill="x", pady=4)
        for label, val in [("10° (Hardpoint)", 10), ("60°", 60), ("120° (Turret)", 120), ("180°", 180), ("360° (Omni)", 360)]:
            tk.Button(snap_arc, text=label, command=lambda v=val: arc_var.set(v),
                      bg="#334155", fg="#f8fafc", activebackground="#475569", font=("Segoe UI", 8, "bold"),
                      padx=4, pady=2, relief="flat", highlightbackground="#4b5563", highlightthickness=1).pack(side="left", padx=1)

    def render_engine_slot_inspector(self, eng):
        header_f = tk.Frame(self.sel_container, bg="#d97706", padx=8, pady=4)
        header_f.pack(fill="x", pady=(0, 10))
        tk.Label(header_f, text="Engine Nozzle Slot",
                 font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#d97706").pack(side="left")

        x_var, sb_x = self.create_numeric_spinbox(
            self.sel_container, "Forward X (px):", "x", eng.x, -500, 500, 1,
            lambda v: setattr(eng, "x", v)
        )
        y_var, sb_y = self.create_numeric_spinbox(
            self.sel_container, "Lateral Y (px):", "y", eng.y, -500, 500, 1,
            lambda v: setattr(eng, "y", v)
        )
        ang_var, sb_ang = self.create_numeric_spinbox(
            self.sel_container, "Angle (deg):", "angle", eng.angle, -360, 360, 5,
            lambda v: setattr(eng, "angle", v)
        )

        snap_f = tk.Frame(self.sel_container, bg="#1a2028")
        snap_f.pack(fill="x", pady=4)
        for label, val in [("180° Main", 180), ("0° Retro", 0), ("90° Strafe L", 90), ("-90° Strafe R", -90)]:
            tk.Button(snap_f, text=label, command=lambda v=val: ang_var.set(v),
                      bg="#334155", fg="#f8fafc", activebackground="#475569", font=("Segoe UI", 8, "bold"),
                      padx=4, pady=2, relief="flat", highlightbackground="#4b5563", highlightthickness=1).pack(side="left", padx=2)

        len_var, sb_len = self.create_numeric_spinbox(
            self.sel_container, "Flame Length (px):", "length", eng.length, 1, 200, 2,
            lambda v: setattr(eng, "length", v)
        )
        w_var, sb_w = self.create_numeric_spinbox(
            self.sel_container, "Nozzle Width (px):", "width", eng.width, 1, 100, 1,
            lambda v: setattr(eng, "width", v)
        )
        c_var, sb_c = self.create_numeric_spinbox(
            self.sel_container, "Contrail Size:", "contrail", eng.contrail_size, 1, 200, 4,
            lambda v: setattr(eng, "contrail_size", v)
        )

        r = self.create_row(self.sel_container, "Visual Style:")
        style_var = tk.StringVar(value=eng.style)
        cb_s = ttk.Combobox(r, values=ENGINE_STYLES, textvariable=style_var, state="readonly", width=14)
        cb_s.pack(side="left")
        def on_style_change(e):
            eng.style = style_var.get()
            if self.on_change_callback: self.on_change_callback()
        cb_s.bind("<<ComboboxSelected>>", on_style_change)

    def render_bound_inspector(self, idx):
        header_f = tk.Frame(self.sel_container, bg="#16a34a", padx=8, pady=4)
        header_f.pack(fill="x", pady=(0, 10))
        tk.Label(header_f, text=f"Collision Bound Vertex #{idx+1}",
                 font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#16a34a").pack(side="left")

        pt = self.ship_project.bounds[idx]

        self.create_numeric_spinbox(
            self.sel_container, "Forward X (px):", "x", pt[0], -500, 500, 1,
            lambda v: self.ship_project.bounds.__setitem__(idx, (v, self.ship_project.bounds[idx][1]))
        )
        self.create_numeric_spinbox(
            self.sel_container, "Lateral Y (px):", "y", pt[1], -500, 500, 1,
            lambda v: self.ship_project.bounds.__setitem__(idx, (self.ship_project.bounds[idx][0], v))
        )

    def render_offset_inspector(self, idx):
        header_f = tk.Frame(self.sel_container, bg="#dc2626", padx=8, pady=4)
        header_f.pack(fill="x", pady=(0, 10))
        tk.Label(header_f, text=f"Weapon Barrel Offset #{idx+1}",
                 font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#dc2626").pack(side="left")

        offsets = self.weapon_project.turret_offsets
        pt = offsets[idx]

        self.create_numeric_spinbox(
            self.sel_container, "Forward X (px):", "x", pt[0], -200, 200, 1,
            lambda v: offsets[idx].__setitem__(0, v)
        )
        self.create_numeric_spinbox(
            self.sel_container, "Lateral Y (px):", "y", pt[1], -200, 200, 1,
            lambda v: offsets[idx].__setitem__(1, v)
        )

    def render_shield_inspector(self):
        header_f = tk.Frame(self.sel_container, bg="#0891b2", padx=8, pady=4)
        header_f.pack(fill="x", pady=(0, 10))
        tk.Label(header_f, text="Shield Bubble Parameters",
                 font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#0891b2").pack(side="left")

        sp = self.ship_project
        self.create_numeric_spinbox(
            self.sel_container, "Shield Radius (px):", "radius", sp.shield_radius, 10, 600, 5,
            lambda v: setattr(sp, "shield_radius", v)
        )

    def build_ship_stats_tab(self):
        canvas = tk.Canvas(self.tab_ship_stats, bg="#1a2028", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_ship_stats, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a2028", padx=8, pady=8)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.ship_entries = {}

        def add_section(title, fields):
            sec_card = tk.Frame(scrollable_frame, bg="#242c37", padx=8, pady=4,
                                highlightbackground="#374151", highlightthickness=1)
            sec_card.pack(fill="x", pady=(10, 4))
            tk.Label(sec_card, text=title, font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#242c37").pack(anchor="w")

            for f_key, label in fields:
                r = tk.Frame(scrollable_frame, bg="#1a2028")
                r.pack(fill="x", pady=2)
                tk.Label(r, text=label, width=15, anchor="w", fg="#f8fafc", bg="#1a2028", font=("Segoe UI", 8, "bold")).pack(side="left")
                var = tk.StringVar()
                e = tk.Entry(r, textvariable=var, bg="#11161d", fg="#ffffff", insertbackground="#38bdf8",
                             relief="flat", highlightbackground="#374151", highlightcolor="#38bdf8", highlightthickness=1,
                             font=("Segoe UI", 8, "bold"))
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
        canvas = tk.Canvas(self.tab_weapon_stats, bg="#1a2028", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_weapon_stats, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a2028", padx=8, pady=8)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.weapon_entries = {}

        def add_wpn_section(title, fields):
            sec_card = tk.Frame(scrollable_frame, bg="#242c37", padx=8, pady=4,
                                highlightbackground="#374151", highlightthickness=1)
            sec_card.pack(fill="x", pady=(10, 4))
            tk.Label(sec_card, text=title, font=("Segoe UI", 9, "bold"), fg="#f59e0b", bg="#242c37").pack(anchor="w")

            for f_key, label in fields:
                r = tk.Frame(scrollable_frame, bg="#1a2028")
                r.pack(fill="x", pady=2)
                tk.Label(r, text=label, width=15, anchor="w", fg="#f8fafc", bg="#1a2028", font=("Segoe UI", 8, "bold")).pack(side="left")
                var = tk.StringVar()
                e = tk.Entry(r, textvariable=var, bg="#11161d", fg="#ffffff", insertbackground="#f59e0b",
                             relief="flat", highlightbackground="#374151", highlightcolor="#f59e0b", highlightthickness=1,
                             font=("Segoe UI", 8, "bold"))
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

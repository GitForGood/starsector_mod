"""
Starsector Ship & Weapon Forge - Main Application Entrypoint
A standalone graphical tool for designing ships and weapons,
placing mounts/engines, configuring specs, and exporting to Starsector mods.
"""

import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from .constants import MOUNT_SIZES, MOUNT_TYPES, WEAPON_TYPES
from .models import ShipProject, WeaponProject
from .canvas_editor import CanvasEditor
from .inspector import InspectorPanel
from .reference_guide import ReferenceGuideDialog
from .preset_dialogs import PresetManagerDialog
from .export_dialogs import ExportDialog

class ShipForgeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Starsector Ship & Weapon Forge")
        self.geometry("1260x840")
        self.minsize(980, 680)
        self.configure(bg="#11161d")

        # Current active project
        self.current_project_path = None
        self.ship_project = ShipProject("new_ship", "New Ship", "CRUISER")
        self.weapon_project = WeaponProject("new_weapon", "New Weapon", "MEDIUM", "BALLISTIC")
        self.current_mode = "SHIP"  # "SHIP" or "WEAPON"

        # Apply comprehensive high-contrast theme
        self.apply_global_theme()

        self.setup_ui()
        self.bind_shortcuts()

        # Load initial ship project onto canvas
        self.canvas_editor.set_ship_project(self.ship_project)
        self.inspector.update_ship_stats_display(self.ship_project)
        self.update_status()

    def apply_global_theme(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Global Notebook
        self.style.configure("Inspect.TNotebook", background="#1a2028", borderwidth=0)
        self.style.configure("Inspect.TNotebook.Tab",
                             background="#242c37",
                             foreground="#cbd5e1",
                             padding=[14, 7],
                             borderwidth=1,
                             bordercolor="#374151",
                             font=("Segoe UI", 9, "bold"))
        self.style.map("Inspect.TNotebook.Tab",
                       background=[("selected", "#2d3748")],
                       foreground=[("selected", "#38bdf8")],
                       bordercolor=[("selected", "#38bdf8")])

        # Global Combobox
        self.style.configure("TCombobox",
                             fieldbackground="#11161d",
                             background="#2d3748",
                             foreground="#ffffff",
                             arrowcolor="#38bdf8",
                             bordercolor="#475569",
                             padding=3,
                             font=("Segoe UI", 9, "bold"))
        self.style.map("TCombobox",
                       fieldbackground=[("readonly", "#11161d")],
                       foreground=[("readonly", "#ffffff")],
                       selectbackground=[("readonly", "#2563eb")])

        # Global Scrollbar
        self.style.configure("TScrollbar",
                             background="#2d3748",
                             troughcolor="#161b22",
                             bordercolor="#374151",
                             arrowcolor="#cbd5e1",
                             relief="flat")
        self.style.map("TScrollbar",
                       background=[("active", "#4b5563")])

        # Global Separator
        self.style.configure("TSeparator", background="#374151")

    def setup_ui(self):
        # Top Toolbar
        toolbar = tk.Frame(self, bg="#1e242c", padx=10, pady=6,
                           highlightbackground="#374151", highlightthickness=1)
        toolbar.pack(side="top", fill="x")

        # Mode Selector
        tk.Label(toolbar, text="Mode:", fg="#f8fafc", bg="#1e242c", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 4))
        self.mode_var = tk.StringVar(value="SHIP")
        rb_ship = tk.Radiobutton(toolbar, text="Ship Hull", variable=self.mode_var, value="SHIP",
                                 command=self.on_mode_change, bg="#1e242c", fg="#38bdf8", selectcolor="#0f172a",
                                 activebackground="#1e242c", activeforeground="#38bdf8", font=("Segoe UI", 9, "bold"))
        rb_ship.pack(side="left", padx=4)

        rb_wpn = tk.Radiobutton(toolbar, text="Weapon", variable=self.mode_var, value="WEAPON",
                                command=self.on_mode_change, bg="#1e242c", fg="#f59e0b", selectcolor="#0f172a",
                                activebackground="#1e242c", activeforeground="#f59e0b", font=("Segoe UI", 9, "bold"))
        rb_wpn.pack(side="left", padx=4)

        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8, pady=2)

        # Load Sprite Button
        btn_sprite = tk.Button(toolbar, text="Load Sprite...", command=self.load_sprite_dialog,
                               bg="#334155", fg="#f8fafc", activebackground="#475569", activeforeground="#ffffff",
                               relief="flat", highlightbackground="#475569", highlightthickness=1,
                               font=("Segoe UI", 9, "bold"), padx=10, pady=2, cursor="hand2")
        btn_sprite.pack(side="left", padx=4)

        # Add Mount Tools (for Ship Mode)
        self.ship_tools_frame = tk.Frame(toolbar, bg="#1e242c")
        self.ship_tools_frame.pack(side="left")

        # Separator before mount tools
        ttk.Separator(self.ship_tools_frame, orient="vertical").pack(side="left", fill="y", padx=6, pady=2)

        # Bordered Weapon Mounts Group
        self.mount_group = tk.Frame(self.ship_tools_frame, bg="#18202c",
                                    highlightbackground="#0284c7", highlightcolor="#38bdf8",
                                    highlightthickness=1, padx=6, pady=2)
        self.mount_group.pack(side="left", padx=4)

        tk.Label(self.mount_group, text="Weapon Mounts:", fg="#38bdf8", bg="#18202c",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(2, 6))

        btn_add_mount = tk.Button(self.mount_group, text="+ Add Mount", command=self.activate_add_mount,
                                  bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
                                  relief="flat", font=("Segoe UI", 9, "bold"), padx=8, pady=2, cursor="hand2")
        btn_add_mount.pack(side="left", padx=3)

        self.cb_size = ttk.Combobox(self.mount_group, values=MOUNT_SIZES, width=8, state="readonly")
        self.cb_size.set("SMALL")
        self.cb_size.pack(side="left", padx=2)

        self.cb_type = ttk.Combobox(self.mount_group, values=WEAPON_TYPES, width=10, state="readonly")
        self.cb_type.set("BALLISTIC")
        self.cb_type.pack(side="left", padx=2)

        # Toggleable Hardpoint Checkbox
        self.hardpoint_var = tk.BooleanVar(value=False)
        self.chk_hardpoint = tk.Checkbutton(self.mount_group, text="Hardpoint", variable=self.hardpoint_var,
                                            command=self.on_toolbar_hardpoint_toggle,
                                            bg="#18202c", fg="#f8fafc", selectcolor="#0f172a",
                                            activebackground="#18202c", activeforeground="#ffffff",
                                            font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.chk_hardpoint.pack(side="left", padx=(4, 2))

        # Separator between Mounts and Engine/Bounds
        ttk.Separator(self.ship_tools_frame, orient="vertical").pack(side="left", fill="y", padx=6, pady=2)

        # Engine & Hull Tools Frame
        eng_bounds_frame = tk.Frame(self.ship_tools_frame, bg="#1e242c")
        eng_bounds_frame.pack(side="left", padx=2)

        btn_add_eng = tk.Button(eng_bounds_frame, text="+ Add Engine", command=self.activate_add_engine,
                                bg="#d97706", fg="#ffffff", activebackground="#b45309", activeforeground="#ffffff",
                                relief="flat", font=("Segoe UI", 9, "bold"), padx=8, pady=2, cursor="hand2")
        btn_add_eng.pack(side="left", padx=3)

        btn_auto_bounds = tk.Button(eng_bounds_frame, text="Auto Bounds", command=self.do_auto_bounds,
                                    bg="#16a34a", fg="#ffffff", activebackground="#15803d", activeforeground="#ffffff",
                                    relief="flat", font=("Segoe UI", 9, "bold"), padx=8, pady=2, cursor="hand2")
        btn_auto_bounds.pack(side="left", padx=3)

        # Separator before Symmetry
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8, pady=2)

        # Symmetry Checkbox
        self.sym_var = tk.BooleanVar(value=True)
        cb_sym = tk.Checkbutton(toolbar, text="Symmetry (Mirror Y)", variable=self.sym_var,
                                command=self.on_symmetry_toggle, bg="#1e242c", fg="#f8fafc", selectcolor="#0f172a",
                                activebackground="#1e242c", activeforeground="#ffffff", font=("Segoe UI", 9, "bold"))
        cb_sym.pack(side="left", padx=10)

        # Right side actions: Dimensions Guide & Export
        btn_export = tk.Button(toolbar, text="Export to Mod...", command=self.open_export_dialog,
                               bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8", activeforeground="#ffffff",
                               font=("Segoe UI", 9, "bold"), padx=14, pady=3, relief="flat", cursor="hand2")
        btn_export.pack(side="right", padx=4)

        btn_guide = tk.Button(toolbar, text="Dimensions Guide (F1)", command=self.open_reference_guide,
                              bg="#334155", fg="#38bdf8", activebackground="#475569", activeforeground="#38bdf8",
                              font=("Segoe UI", 9, "bold"), padx=10, pady=2, relief="flat",
                              highlightbackground="#475569", highlightthickness=1, cursor="hand2")
        btn_guide.pack(side="right", padx=6)

        btn_presets = tk.Button(toolbar, text="Presets...", command=self.open_preset_manager,
                                bg="#2d3748", fg="#f8fafc", activebackground="#374151", activeforeground="#ffffff",
                                font=("Segoe UI", 9, "bold"), padx=10, pady=2, relief="flat",
                                highlightbackground="#4b5563", highlightthickness=1, cursor="hand2")
        btn_presets.pack(side="right", padx=4)

        # Main Workspace Container
        main_container = tk.Frame(self, bg="#11161d")
        main_container.pack(fill="both", expand=True)

        # Right Panel: Inspector
        self.inspector = InspectorPanel(main_container, on_change_callback=self.on_inspector_change)
        self.inspector.pack(side="right", fill="y")

        # Center Panel: Canvas Editor
        self.canvas_editor = CanvasEditor(main_container,
                                          on_select_callback=self.on_canvas_select,
                                          on_change_callback=self.on_canvas_change)
        self.canvas_editor.pack(side="left", fill="both", expand=True)

        # Bottom Status Bar
        self.status_bar = tk.Label(self, text="Ready", bg="#1e242c", fg="#f8fafc",
                                   anchor="w", padx=12, font=("Segoe UI", 9), height=1,
                                   highlightbackground="#374151", highlightthickness=1)
        self.status_bar.pack(side="bottom", fill="x")

        # Setup Menus after all UI elements are created
        self.setup_menus()

    def setup_menus(self):
        menubar = tk.Menu(self, bg="#1e242c", fg="#ffffff", activebackground="#2563eb", relief="flat")

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#1e242c", fg="#ffffff", activebackground="#2563eb")
        file_menu.add_command(label="New Ship Project", accelerator="Ctrl+N", command=self.new_ship_project)
        file_menu.add_command(label="New Weapon Project", accelerator="Ctrl+Shift+N", command=self.new_weapon_project)
        file_menu.add_separator()
        file_menu.add_command(label="Open Project...", accelerator="Ctrl+O", command=self.open_project)
        file_menu.add_command(label="Save Project", accelerator="Ctrl+S", command=self.save_project)
        file_menu.add_command(label="Save Project As...", accelerator="Ctrl+Shift+S", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Load Sprite Image...", accelerator="Ctrl+L", command=self.load_sprite_dialog)
        file_menu.add_command(label="Export to Mod...", accelerator="Ctrl+E", command=self.open_export_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg="#1e242c", fg="#ffffff", activebackground="#2563eb")
        edit_menu.add_command(label="Delete Selected", accelerator="Del", command=lambda: self.canvas_editor.delete_selected())
        edit_menu.add_command(label="Toggle Symmetry", accelerator="S", command=self.toggle_symmetry)
        edit_menu.add_command(label="Auto-generate Collision Bounds", command=self.do_auto_bounds)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0, bg="#1e242c", fg="#ffffff", activebackground="#2563eb")
        view_menu.add_command(label="Reset View", accelerator="R", command=lambda: self.canvas_editor.reset_view())
        menubar.add_cascade(label="View", menu=view_menu)

        # Presets Menu
        presets_menu = tk.Menu(menubar, tearoff=0, bg="#1e242c", fg="#ffffff", activebackground="#2563eb")
        presets_menu.add_command(label="Manage & Apply Presets...", command=self.open_preset_manager)
        menubar.add_cascade(label="Presets", menu=presets_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg="#1e242c", fg="#ffffff", activebackground="#2563eb")
        help_menu.add_command(label="Dimensions & Mount Reference Guide", accelerator="F1", command=self.open_reference_guide)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self.new_ship_project())
        self.bind("<Control-N>", lambda e: self.new_weapon_project())
        self.bind("<Control-o>", lambda e: self.open_project())
        self.bind("<Control-s>", lambda e: self.save_project())
        self.bind("<Control-S>", lambda e: self.save_project_as())
        self.bind("<Control-l>", lambda e: self.load_sprite_dialog())
        self.bind("<Control-e>", lambda e: self.open_export_dialog())
        self.bind("<Delete>", lambda e: self.canvas_editor.delete_selected())
        self.bind("<F1>", lambda e: self.open_reference_guide())
        self.bind("<r>", lambda e: self.canvas_editor.reset_view())
        self.bind("<s>", lambda e: self.toggle_symmetry())

        # Arrow keys to nudge selected items
        self.bind("<Left>", lambda e: self.nudge_selected(0, 1))
        self.bind("<Right>", lambda e: self.nudge_selected(0, -1))
        self.bind("<Up>", lambda e: self.nudge_selected(1, 0))
        self.bind("<Down>", lambda e: self.nudge_selected(-1, 0))

    def nudge_selected(self, dx, dy):
        item = self.canvas_editor.selected_item
        if not item:
            return
        t, obj = item
        if t in ("WEAPON", "ENGINE"):
            obj.x += dx
            obj.y += dy
        elif t == "BOUND":
            if self.ship_project and obj < len(self.ship_project.bounds):
                pt = self.ship_project.bounds[obj]
                self.ship_project.bounds[obj] = (pt[0] + dx, pt[1] + dy)
        elif t == "OFFSET":
            offsets = self.weapon_project.turret_offsets if self.canvas_editor.active_weapon_sprite == "TURRET" else self.weapon_project.hardpoint_offsets
            if obj < len(offsets):
                offsets[obj] = [offsets[obj][0] + dx, offsets[obj][1] + dy]

        self.canvas_editor.redraw()
        self.inspector.sync_selection_values()
        self.update_status()

    def on_mode_change(self):
        self.current_mode = self.mode_var.get()
        if self.current_mode == "SHIP":
            self.canvas_editor.set_ship_project(self.ship_project)
            self.inspector.update_ship_stats_display(self.ship_project)
            self.ship_tools_frame.pack(side="left")
        else:
            self.canvas_editor.set_weapon_project(self.weapon_project)
            self.inspector.update_weapon_stats_display(self.weapon_project)
            self.ship_tools_frame.pack_forget()
        self.update_status()

    def load_sprite_dialog(self):
        path = filedialog.askopenfilename(
            title="Load Sprite Image",
            filetypes=[("PNG Images", "*.png"), ("All Files", "*.*")]
        )
        if not path:
            return

        if self.current_mode == "SHIP":
            self.ship_project.sprite_path = path
            self.canvas_editor.load_image(path)
            # Auto center if not yet set
            if self.canvas_editor.raw_image:
                w, h = self.canvas_editor.raw_image.size
                self.ship_project.sprite_w = w
                self.ship_project.sprite_h = h
                self.ship_project.center = [h // 2, w // 2]
                if not self.ship_project.bounds:
                    self.ship_project.auto_generate_bounds()
        else:
            self.weapon_project.turret_sprite_path = path
            self.canvas_editor.load_image(path)

        self.canvas_editor.reset_view()
        self.update_status()

    def activate_add_mount(self):
        self.canvas_editor.tool_mode = "ADD_WEAPON"
        self.canvas_editor.new_slot_size = self.cb_size.get()
        self.canvas_editor.new_slot_type = self.cb_type.get()
        self.canvas_editor.new_slot_mount = "HARDPOINT" if self.hardpoint_var.get() else "TURRET"
        mount_str = self.canvas_editor.new_slot_mount
        size_str = self.canvas_editor.new_slot_size
        type_str = self.canvas_editor.new_slot_type
        self.status_bar.config(text=f"Mode: ADD MOUNT [{size_str} {type_str} {mount_str}]  •  Click on the canvas to place...")

    def on_toolbar_hardpoint_toggle(self):
        self.canvas_editor.new_slot_mount = "HARDPOINT" if self.hardpoint_var.get() else "TURRET"
        if self.canvas_editor.tool_mode == "ADD_WEAPON":
            mount_str = self.canvas_editor.new_slot_mount
            size_str = self.cb_size.get()
            type_str = self.cb_type.get()
            self.status_bar.config(text=f"Mode: ADD MOUNT [{size_str} {type_str} {mount_str}]  •  Click on the canvas to place...")

    def activate_add_engine(self):
        self.canvas_editor.tool_mode = "ADD_ENGINE"
        self.status_bar.config(text="Mode: ADD ENGINE  •  Click on the canvas to place a new engine nozzle...")

    def do_auto_bounds(self):
        if self.ship_project and self.canvas_editor.raw_image:
            self.ship_project.auto_generate_bounds()
            self.canvas_editor.redraw()
            self.update_status()

    def toggle_symmetry(self):
        self.sym_var.set(not self.sym_var.get())
        self.on_symmetry_toggle()

    def on_symmetry_toggle(self):
        self.canvas_editor.symmetry_enabled = self.sym_var.get()
        self.update_status()

    def on_canvas_select(self, item):
        self.inspector.set_selection(item)
        self.update_status()

    def on_canvas_change(self):
        self.inspector.sync_selection_values()
        self.update_status()

    def on_inspector_change(self):
        self.canvas_editor.redraw()
        self.update_status()

    def open_reference_guide(self):
        ReferenceGuideDialog(self)

    def open_preset_manager(self):
        def on_applied():
            self.inspector.update_ship_stats_display(self.ship_project)
            self.canvas_editor.redraw()
            self.update_status()
        PresetManagerDialog(self, self.ship_project, on_applied)

    def open_export_dialog(self):
        proj = self.ship_project if self.current_mode == "SHIP" else self.weapon_project
        ExportDialog(self, proj, self.current_mode)

    def new_ship_project(self):
        self.ship_project = ShipProject("new_ship", "New Ship", "CRUISER")
        self.current_project_path = None
        self.mode_var.set("SHIP")
        self.on_mode_change()

    def new_weapon_project(self):
        self.weapon_project = WeaponProject("new_weapon", "New Weapon", "MEDIUM", "BALLISTIC")
        self.current_project_path = None
        self.mode_var.set("WEAPON")
        self.on_mode_change()

    def open_project(self):
        path = filedialog.askopenfilename(
            title="Open Starsector Forge Project",
            filetypes=[("Forge Projects", "*.ssproj;*.json"), ("All Files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            proj_type = data.get("type", "SHIP")
            if proj_type == "SHIP":
                self.ship_project = ShipProject.from_project_dict(data)
                self.mode_var.set("SHIP")
                self.on_mode_change()
                if self.ship_project.sprite_path and os.path.isfile(self.ship_project.sprite_path):
                    self.canvas_editor.load_image(self.ship_project.sprite_path)
            else:
                self.weapon_project = WeaponProject.from_project_dict(data)
                self.mode_var.set("WEAPON")
                self.on_mode_change()
                if self.weapon_project.turret_sprite_path and os.path.isfile(self.weapon_project.turret_sprite_path):
                    self.canvas_editor.load_image(self.weapon_project.turret_sprite_path)

            self.current_project_path = path
            self.title(f"Starsector Ship & Weapon Forge - [{os.path.basename(path)}]")
            messagebox.showinfo("Loaded", f"Loaded project: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project:\n{e}")

    def save_project(self):
        if self.current_project_path:
            self.write_project(self.current_project_path)
        else:
            self.save_project_as()

    def save_project_as(self):
        default_name = f"{self.ship_project.hull_id}.ssproj" if self.current_mode == "SHIP" else f"{self.weapon_project.weapon_id}.ssproj"
        path = filedialog.asksaveasfilename(
            title="Save Project As",
            defaultextension=".ssproj",
            filetypes=[("Forge Project", "*.ssproj"), ("JSON File", "*.json")],
            initialfile=default_name
        )
        if not path:
            return
        self.current_project_path = path
        self.write_project(path)
        self.title(f"Starsector Ship & Weapon Forge - [{os.path.basename(path)}]")

    def write_project(self, path):
        proj = self.ship_project if self.current_mode == "SHIP" else self.weapon_project
        try:
            with open(path, "w", encoding="utf-8") as fp:
                json.dump(proj.to_project_dict(), fp, indent=2)
            messagebox.showinfo("Saved", f"Project saved successfully:\n{path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save project:\n{e}")

    def update_status(self):
        if self.current_mode == "SHIP":
            sp = self.ship_project
            info = f"  Ship: {sp.hull_name} ({sp.hull_id})   •   Class: {sp.hull_size}   •   "
            info += f"Weapons: {len(sp.weapon_slots)}   •   Engines: {len(sp.engine_slots)}   •   Bounds: {len(sp.bounds)} pts   •   "
            info += f"Zoom: {self.canvas_editor.zoom:.1f}x   •   Symmetry: {'ON' if self.canvas_editor.symmetry_enabled else 'OFF'}"
        else:
            wp = self.weapon_project
            info = f"  Weapon: {wp.weapon_name} ({wp.weapon_id})   •   Size: {wp.size}   •   Type: {wp.type}   •   "
            info += f"Barrels: {len(wp.turret_offsets)}   •   Zoom: {self.canvas_editor.zoom:.1f}x"
        self.status_bar.config(text=info)

    def show_about(self):
        messagebox.showinfo(
            "About Starsector Ship & Weapon Forge",
            "Starsector Ship & Weapon Forge v1.0\n\n"
            "An open graphical toolkit for modders to design, edit, and export Starsector ships and weapons.\n\n"
            "Features:\n"
            "• Drag-and-drop weapon and engine slot editor with arc handles\n"
            "• Precise numeric inspect window\n"
            "• Built-in sprite dimensions & weapon mount reference guide\n"
            "• Automated blank sprite generator with guidelines\n"
            "• Flexible CSV row and complete table exporter\n"
            "• Project save/load support (.ssproj)"
        )

def main():
    app = ShipForgeApp()
    app.mainloop()

if __name__ == "__main__":
    main()

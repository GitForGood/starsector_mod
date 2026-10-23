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
        self.geometry("1240x820")
        self.minsize(950, 650)
        self.configure(bg="#0d1117")

        # Current active project
        self.current_project_path = None
        self.ship_project = ShipProject("new_ship", "New Ship", "CRUISER")
        self.weapon_project = WeaponProject("new_weapon", "New Weapon", "MEDIUM", "BALLISTIC")
        self.current_mode = "SHIP"  # "SHIP" or "WEAPON"

        self.setup_ui()
        self.bind_shortcuts()

        # Load initial ship project onto canvas
        self.canvas_editor.set_ship_project(self.ship_project)
        self.inspector.update_ship_stats_display(self.ship_project)
        self.update_status()

    def setup_ui(self):
        self.setup_menus()

        # Top Toolbar
        toolbar = tk.Frame(self, bg="#161b22", height=42, padx=10, pady=4)
        toolbar.pack(side="top", fill="x")

        # Mode Selector
        tk.Label(toolbar, text="Mode:", fg="#8b949e", bg="#161b22", font=("Segoe UI", 9)).pack(side="left", padx=(0, 4))
        self.mode_var = tk.StringVar(value="SHIP")
        rb_ship = tk.Radiobutton(toolbar, text="Ship Hull", variable=self.mode_var, value="SHIP",
                                 command=self.on_mode_change, bg="#161b22", fg="#38bdf8", selectcolor="#0d1117",
                                 activebackground="#161b22", activeforeground="#38bdf8", font=("Segoe UI", 9, "bold"))
        rb_ship.pack(side="left", padx=4)

        rb_wpn = tk.Radiobutton(toolbar, text="Weapon", variable=self.mode_var, value="WEAPON",
                                command=self.on_mode_change, bg="#161b22", fg="#f59e0b", selectcolor="#0d1117",
                                activebackground="#161b22", activeforeground="#f59e0b", font=("Segoe UI", 9, "bold"))
        rb_wpn.pack(side="left", padx=4)

        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8, pady=2)

        # Load Sprite Button
        btn_sprite = tk.Button(toolbar, text="Load Sprite...", command=self.load_sprite_dialog,
                               bg="#21262d", fg="#c9d1d9", relief="flat", font=("Segoe UI", 9))
        btn_sprite.pack(side="left", padx=4)

        # Add Mount Tools (for Ship Mode)
        self.ship_tools_frame = tk.Frame(toolbar, bg="#161b22")
        self.ship_tools_frame.pack(side="left")

        btn_add_mount = tk.Button(self.ship_tools_frame, text="+ Add Mount", command=self.activate_add_mount,
                                  bg="#21262d", fg="#38bdf8", relief="flat", font=("Segoe UI", 9, "bold"))
        btn_add_mount.pack(side="left", padx=4)

        self.cb_size = ttk.Combobox(self.ship_tools_frame, values=MOUNT_SIZES, width=7, state="readonly")
        self.cb_size.set("SMALL")
        self.cb_size.pack(side="left", padx=2)

        self.cb_type = ttk.Combobox(self.ship_tools_frame, values=WEAPON_TYPES[:4], width=8, state="readonly")
        self.cb_type.set("BALLISTIC")
        self.cb_type.pack(side="left", padx=2)

        btn_add_eng = tk.Button(self.ship_tools_frame, text="+ Add Engine", command=self.activate_add_engine,
                                bg="#21262d", fg="#f97316", relief="flat", font=("Segoe UI", 9, "bold"))
        btn_add_eng.pack(side="left", padx=4)

        btn_auto_bounds = tk.Button(self.ship_tools_frame, text="Auto Bounds", command=self.do_auto_bounds,
                                    bg="#21262d", fg="#10b981", relief="flat", font=("Segoe UI", 9))
        btn_auto_bounds.pack(side="left", padx=4)

        # Symmetry Checkbox
        self.sym_var = tk.BooleanVar(value=True)
        cb_sym = tk.Checkbutton(toolbar, text="Symmetry (Mirror Y)", variable=self.sym_var,
                                command=self.on_symmetry_toggle, bg="#161b22", fg="#e2e8f0", selectcolor="#0d1117",
                                activebackground="#161b22", activeforeground="#ffffff", font=("Segoe UI", 9))
        cb_sym.pack(side="left", padx=10)

        # Right side actions: Dimensions Guide & Export
        btn_export = tk.Button(toolbar, text="Export to Mod...", command=self.open_export_dialog,
                               bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8", font=("Segoe UI", 9, "bold"),
                               padx=12, relief="flat", cursor="hand2")
        btn_export.pack(side="right", padx=4)

        btn_guide = tk.Button(toolbar, text="Dimensions Guide", command=self.open_reference_guide,
                              bg="#374151", fg="#38bdf8", font=("Segoe UI", 9), relief="flat")
        btn_guide.pack(side="right", padx=6)

        btn_presets = tk.Button(toolbar, text="Presets...", command=self.open_preset_manager,
                                bg="#21262d", fg="#c9d1d9", font=("Segoe UI", 9), relief="flat")
        btn_presets.pack(side="right", padx=4)

        # Main Workspace Container
        main_container = tk.Frame(self, bg="#0d1117")
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
        self.status_bar = tk.Label(self, text="Ready", bg="#0f141c", fg="#8b949e",
                                   anchor="w", padx=10, font=("Segoe UI", 8), height=1)
        self.status_bar.pack(side="bottom", fill="x")

    def setup_menus(self):
        menubar = tk.Menu(self, bg="#161b22", fg="#ffffff", activebackground="#2563eb", relief="flat")

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#161b22", fg="#ffffff", activebackground="#2563eb")
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
        edit_menu = tk.Menu(menubar, tearoff=0, bg="#161b22", fg="#ffffff", activebackground="#2563eb")
        edit_menu.add_command(label="Delete Selected", accelerator="Del", command=self.canvas_editor.delete_selected)
        edit_menu.add_command(label="Toggle Symmetry", accelerator="S", command=self.toggle_symmetry)
        edit_menu.add_command(label="Auto-generate Collision Bounds", command=self.do_auto_bounds)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0, bg="#161b22", fg="#ffffff", activebackground="#2563eb")
        view_menu.add_command(label="Reset View", accelerator="R", command=self.canvas_editor.reset_view)
        menubar.add_cascade(label="View", menu=view_menu)

        # Presets Menu
        presets_menu = tk.Menu(menubar, tearoff=0, bg="#161b22", fg="#ffffff", activebackground="#2563eb")
        presets_menu.add_command(label="Manage & Apply Presets...", command=self.open_preset_manager)
        menubar.add_cascade(label="Presets", menu=presets_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg="#161b22", fg="#ffffff", activebackground="#2563eb")
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
            self.canvas_editor.redraw()
            self.inspector.set_selection(item)

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
        self.status_bar.config(text="Click on the canvas to place a new weapon mount...")

    def activate_add_engine(self):
        self.canvas_editor.tool_mode = "ADD_ENGINE"
        self.status_bar.config(text="Click on the canvas to place a new engine nozzle...")

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
                if self.ship_project.sprite_path:
                    self.canvas_editor.load_image(self.ship_project.sprite_path)
            else:
                self.weapon_project = WeaponProject.from_project_dict(data)
                self.mode_var.set("WEAPON")
                self.on_mode_change()
                if self.weapon_project.turret_sprite_path:
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
            info = f"Ship: {sp.hull_name} ({sp.hull_id}) | Size: {sp.hull_size} | "
            info += f"Weapons: {len(sp.weapon_slots)} | Engines: {len(sp.engine_slots)} | Bounds: {len(sp.bounds)} pts | "
            info += f"Zoom: {self.canvas_editor.zoom:.1f}x | Symmetry: {'ON' if self.canvas_editor.symmetry_enabled else 'OFF'}"
        else:
            wp = self.weapon_project
            info = f"Weapon: {wp.weapon_name} ({wp.weapon_id}) | Size: {wp.size} | Type: {wp.type} | "
            info += f"Barrels: {len(wp.turret_offsets)} | Zoom: {self.canvas_editor.zoom:.1f}x"
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

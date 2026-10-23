"""
Reference Guide Dialog & Template Generator for Sprite Designers.
Displays visual size metrics, mount dimensions, and generates starter PNG templates.
"""

import math
import os
import struct
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import zlib
from .constants import GUIDELINES_SHIPS, GUIDELINES_MOUNTS, GUIDELINES_ENGINES

class ReferenceGuideDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Starsector Sprite Dimensions & Mount Reference Guide")
        self.geometry("860x650")
        self.minsize(700, 500)
        self.configure(bg="#181e24")

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Guide.TNotebook", background="#181e24", borderwidth=0)
        style.configure("Guide.TNotebook.Tab", background="#242d38", foreground="#e2e8f0", padding=[12, 6])
        style.map("Guide.TNotebook.Tab", background=[("selected", "#3b82f6")], foreground=[("selected", "#ffffff")])

        notebook = ttk.Notebook(self, style="Guide.TNotebook")
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Weapon Mounts Visual Guide
        tab_mounts = tk.Frame(notebook, bg="#1e252e")
        notebook.add(tab_mounts, text="Weapon Mount Dimensions")
        self.build_mounts_tab(tab_mounts)

        # Tab 2: Ship Size Table
        tab_ships = tk.Frame(notebook, bg="#1e252e")
        notebook.add(tab_ships, text="Ship Hull Classes")
        self.build_ships_tab(tab_ships)

        # Tab 3: Engines & Thrusters
        tab_engines = tk.Frame(notebook, bg="#1e252e")
        notebook.add(tab_engines, text="Engine & Thruster Nozzles")
        self.build_engines_tab(tab_engines)

        # Tab 4: Template Generator
        tab_template = tk.Frame(notebook, bg="#1e252e")
        notebook.add(tab_template, text="Generate Blank Sprite Template")
        self.build_template_tab(tab_template)

    def build_mounts_tab(self, parent):
        top_frame = tk.Frame(parent, bg="#1e252e")
        top_frame.pack(fill="x", padx=15, pady=10)

        title = tk.Label(top_frame, text="Weapon Mount Recess & Well Specifications",
                         font=("Segoe UI", 12, "bold"), fg="#38bdf8", bg="#1e252e")
        title.pack(anchor="w")

        desc = tk.Label(top_frame, text="Draw these dark circular wells or rectangular notches on your hull so weapons look physically embedded.",
                        font=("Segoe UI", 9), fg="#94a3b8", bg="#1e252e")
        desc.pack(anchor="w", pady=(2, 10))

        # Visual Canvas showing relative sizes
        canvas_frame = tk.Frame(parent, bg="#12161c", relief="sunken", bd=1)
        canvas_frame.pack(fill="x", padx=15, pady=5)

        cv = tk.Canvas(canvas_frame, height=130, bg="#12161c", highlightthickness=0)
        cv.pack(fill="x", padx=10, pady=10)

        # Draw Small (12px well, 26px clearance)
        cv.create_oval(70 - 13, 60 - 13, 70 + 13, 60 + 13, outline="#475569", dash=(2, 2))
        cv.create_oval(70 - 6, 60 - 6, 70 + 6, 60 + 6, fill="#1e293b", outline="#94a3b8")
        cv.create_text(70, 95, text="SMALL TURRET\nWell: 12px | Clear: 26px", fill="#e2e8f0", font=("Segoe UI", 8), justify="center")

        # Draw Medium (22px well, 44px clearance)
        cv.create_oval(240 - 22, 60 - 22, 240 + 22, 60 + 22, outline="#475569", dash=(2, 2))
        cv.create_oval(240 - 11, 60 - 11, 240 + 11, 60 + 11, fill="#1e293b", outline="#94a3b8")
        cv.create_text(240, 95, text="MEDIUM TURRET\nWell: 22px | Clear: 44px", fill="#e2e8f0", font=("Segoe UI", 8), justify="center")

        # Draw Large (34px well, 68px clearance)
        cv.create_oval(450 - 34, 60 - 34, 450 + 34, 60 + 34, outline="#475569", dash=(2, 2))
        cv.create_oval(450 - 17, 60 - 17, 450 + 17, 60 + 17, fill="#1e293b", outline="#94a3b8")
        cv.create_text(450, 105, text="LARGE TURRET\nWell: 34px | Clear: 68px", fill="#e2e8f0", font=("Segoe UI", 8), justify="center")

        # Draw Hardpoint Notch example
        cv.create_rectangle(650 - 10, 30, 650 + 10, 70, fill="#1e293b", outline="#94a3b8")
        cv.create_line(650 - 14, 25, 650 - 10, 75, fill="#64748b", width=2)
        cv.create_line(650 + 14, 25, 650 + 10, 75, fill="#64748b", width=2)
        cv.create_text(650, 95, text="HARDPOINT NOTCH\nWidth: 12-28px | Depth: 16-36px", fill="#e2e8f0", font=("Segoe UI", 8), justify="center")

        # Table
        tree_frame = tk.Frame(parent, bg="#1e252e")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=10)

        cols = ("size", "well", "base", "clearance", "hardpoint", "examples")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=4)
        tree.heading("size", text="Mount Size")
        tree.heading("well", text="Turret Well Dia")
        tree.heading("base", text="Gun Base Dia")
        tree.heading("clearance", text="Rotation Clearance")
        tree.heading("hardpoint", text="Hardpoint Cutout (WxD)")
        tree.heading("examples", text="Common Weapons")

        tree.column("size", width=80, anchor="center")
        tree.column("well", width=100, anchor="center")
        tree.column("base", width=90, anchor="center")
        tree.column("clearance", width=110, anchor="center")
        tree.column("hardpoint", width=140, anchor="center")
        tree.column("examples", width=260, anchor="w")

        for k, v in GUIDELINES_MOUNTS.items():
            tree.insert("", "end", values=(k, v["turret_well_dia"], v["weapon_base_dia"],
                                           v["clearance_dia"], v["hardpoint_cutout"], v["typical_weapons"]))

        tree.pack(fill="both", expand=True)

    def build_ships_tab(self, parent):
        top_frame = tk.Frame(parent, bg="#1e252e")
        top_frame.pack(fill="x", padx=15, pady=10)

        title = tk.Label(top_frame, text="Ship Hull Scale & Dimension Metrics",
                         font=("Segoe UI", 12, "bold"), fg="#38bdf8", bg="#1e252e")
        title.pack(anchor="w")

        desc = tk.Label(top_frame, text="Standard Starsector dimensions (bow faces UP). Width is port-to-starboard; Height is stern-to-bow.",
                        font=("Segoe UI", 9), fg="#94a3b8", bg="#1e252e")
        desc.pack(anchor="w", pady=(2, 5))

        tree_frame = tk.Frame(parent, bg="#1e252e")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=10)

        cols = ("class", "width", "height", "examples", "notes")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=6)
        tree.heading("class", text="Hull Class")
        tree.heading("width", text="Typical Width (px)")
        tree.heading("height", text="Typical Length (px)")
        tree.heading("examples", text="Vanilla Benchmarks")
        tree.heading("notes", text="Design Notes")

        tree.column("class", width=90, anchor="center")
        tree.column("width", width=110, anchor="center")
        tree.column("height", width=110, anchor="center")
        tree.column("examples", width=260, anchor="w")
        tree.column("notes", width=220, anchor="w")

        for k, v in GUIDELINES_SHIPS.items():
            w_str = f"{v['width_range'][0]} - {v['width_range'][1]} px"
            h_str = f"{v['height_range'][0]} - {v['height_range'][1]} px"
            tree.insert("", "end", values=(k, w_str, h_str, v["examples"], v["notes"]))

        tree.pack(fill="both", expand=True)

    def build_engines_tab(self, parent):
        top_frame = tk.Frame(parent, bg="#1e252e")
        top_frame.pack(fill="x", padx=15, pady=10)

        title = tk.Label(top_frame, text="Engine Nozzle Proportions & Placement",
                         font=("Segoe UI", 12, "bold"), fg="#38bdf8", bg="#1e252e")
        title.pack(anchor="w")

        desc = tk.Label(top_frame, text="Engine bells should be drawn recessed with dark mechanical rims and subtle glow gradients.",
                        font=("Segoe UI", 9), fg="#94a3b8", bg="#1e252e")
        desc.pack(anchor="w", pady=(2, 5))

        tree_frame = tk.Frame(parent, bg="#1e252e")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=10)

        cols = ("type", "width", "depth", "contrail", "notes")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=5)
        tree.heading("type", text="Thruster Category")
        tree.heading("width", text="Nozzle Width")
        tree.heading("depth", text="Nozzle Depth")
        tree.heading("contrail", text="Contrail Size")
        tree.heading("notes", text="Angles & Usage")

        tree.column("type", width=140, anchor="center")
        tree.column("width", width=100, anchor="center")
        tree.column("depth", width=100, anchor="center")
        tree.column("contrail", width=90, anchor="center")
        tree.column("notes", width=340, anchor="w")

        for k, v in GUIDELINES_ENGINES.items():
            tree.insert("", "end", values=(k, v["nozzle_width"], v["nozzle_depth"], v["contrail"], v["notes"]))

        tree.pack(fill="both", expand=True)

    def build_template_tab(self, parent):
        frame = tk.Frame(parent, bg="#1e252e", padx=25, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Create Blank Canvas Template with Guides",
                 font=("Segoe UI", 13, "bold"), fg="#38bdf8", bg="#1e252e").pack(anchor="w")
        tk.Label(frame, text="Exports a transparent PNG pre-sized to standard dimensions with a center vertical axis guide and 1px border guide.",
                 font=("Segoe UI", 9), fg="#94a3b8", bg="#1e252e").pack(anchor="w", pady=(2, 20))

        # Size selector
        opt_frame = tk.Frame(frame, bg="#1e252e")
        opt_frame.pack(anchor="w", pady=5)

        tk.Label(opt_frame, text="Select Class Preset:", font=("Segoe UI", 10), fg="#e2e8f0", bg="#1e252e").grid(row=0, column=0, sticky="w", pady=5)
        self.preset_var = tk.StringVar(value="CRUISER (Wide / Brawler) - 200 x 170")
        
        presets = [
            "FIGHTER - 28 x 30",
            "FRIGATE (Standard) - 68 x 96",
            "FRIGATE (Wide / Brawler) - 100 x 60",
            "DESTROYER (Standard) - 120 x 160",
            "CRUISER (Standard) - 170 x 220",
            "CRUISER (Wide / Brawler) - 200 x 170",
            "CAPITAL (Standard) - 290 x 370",
            "CAPITAL (Broadside / Massive) - 340 x 400"
        ]
        preset_cb = ttk.Combobox(opt_frame, values=presets, textvariable=self.preset_var, width=40, state="readonly")
        preset_cb.grid(row=0, column=1, padx=10, pady=5)

        # Include guide marks
        self.include_guides_var = tk.BooleanVar(value=True)
        cb_guides = tk.Checkbutton(frame, text="Include subtle centerline & boundary guide markings",
                                   variable=self.include_guides_var, bg="#1e252e", fg="#e2e8f0",
                                   selectcolor="#0f172a", activebackground="#1e252e", activeforeground="#ffffff")
        cb_guides.pack(anchor="w", pady=10)

        btn_gen = tk.Button(frame, text="Generate Template PNG...", command=self.generate_template_png,
                            bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8", font=("Segoe UI", 10, "bold"),
                            padx=15, pady=6, relief="flat", cursor="hand2")
        btn_gen.pack(anchor="w", pady=15)

    def generate_template_png(self):
        txt = self.preset_var.get()
        # Parse width and height from "NAME - W x H"
        try:
            dims = txt.split("-")[-1].strip().split("x")
            w = int(dims[0].strip())
            h = int(dims[1].strip())
        except Exception:
            w, h = 200, 170

        save_path = filedialog.asksaveasfilename(
            title="Save Blank Template Sprite",
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialfile=f"template_{w}x{h}.png"
        )
        if not save_path:
            return

        cx = w // 2
        cy = h // 2
        include_guides = self.include_guides_var.get()

        raw = bytearray()
        for y in range(h):
            raw.append(0)
            for x in range(w):
                # Check for guide markings
                if include_guides:
                    # Vertical centerline (cyan 40% alpha)
                    if x == cx:
                        col = (40, 200, 240, 110)
                    # Horizontal centerline (cyan 25% alpha)
                    elif y == cy:
                        col = (40, 200, 240, 65)
                    # 1px border margin (white 15% alpha)
                    elif x in (2, w - 3) or y in (2, h - 3):
                        col = (255, 255, 255, 45)
                    else:
                        col = (0, 0, 0, 0)
                else:
                    col = (0, 0, 0, 0)
                raw.extend(col)

        compressed = zlib.compress(bytes(raw), 9)
        def chunk(tag, data):
            return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        png = b'\x89PNG\r\n\x1a\n'
        png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
        png += chunk(b'IDAT', compressed)
        png += chunk(b'IEND', b'')

        with open(save_path, "wb") as f:
            f.write(png)

        messagebox.showinfo("Template Created", f"Successfully saved blank template sprite:\n{save_path}\n({w} x {h} px)")

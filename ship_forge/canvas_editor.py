"""
Interactive, zoomable, pannable Canvas Editor for Starsector Ship & Weapon Forge.
Supports drag-and-drop slots, handles, polygons, and symmetry mirroring.
"""

import math
import os
import tkinter as tk
from PIL import Image, ImageTk
from .constants import WEAPON_COLORS
from .models import canvas_to_starsector, starsector_to_canvas, WeaponSlot, EngineSlot

class CanvasEditor(tk.Frame):
    def __init__(self, parent, on_select_callback=None, on_change_callback=None):
        super().__init__(parent, bg="#11161d")

        self.on_select_callback = on_select_callback
        self.on_change_callback = on_change_callback

        self.canvas = tk.Canvas(self, bg="#11161d", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)

        # Viewport transform
        self.zoom = 2.5
        self.pan_x = 400.0
        self.pan_y = 350.0
        self.has_initial_centered = False

        # Project reference
        self.mode = "SHIP"  # "SHIP" or "WEAPON"
        self.ship_project = None
        self.weapon_project = None
        self.active_weapon_sprite = "TURRET"  # "TURRET" or "HARDPOINT"

        # Cached PIL Images
        self.raw_image = None
        self.tk_image = None

        # Interactive selection state
        self.selected_item = None
        self.drag_data = {"x": 0, "y": 0, "orig_x": 0, "orig_y": 0}
        self.is_panning = False
        self.symmetry_enabled = True

        # Tool mode: "SELECT", "ADD_WEAPON", "ADD_ENGINE"
        self.tool_mode = "SELECT"
        self.new_slot_type = "BALLISTIC"
        self.new_slot_size = "SMALL"
        self.new_slot_mount = "TURRET"

        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_left_down)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_up)

        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.do_pan)
        self.canvas.bind("<ButtonRelease-2>", self.end_pan)

        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.do_pan)
        self.canvas.bind("<ButtonRelease-3>", self.end_pan)

        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.item_hitboxes = {}

    def on_canvas_configure(self, event):
        if not self.has_initial_centered and event.width > 100:
            self.pan_x = event.width / 2.0
            self.pan_y = event.height / 2.0
            self.has_initial_centered = True
        self.redraw()

    def set_ship_project(self, project):
        self.mode = "SHIP"
        self.ship_project = project
        self.selected_item = None
        self.load_image(project.sprite_path)
        self.reset_view()

    def set_weapon_project(self, project, view_mode="TURRET"):
        self.mode = "WEAPON"
        self.weapon_project = project
        self.active_weapon_sprite = view_mode
        self.selected_item = None
        path = project.turret_sprite_path if view_mode == "TURRET" else project.hardpoint_sprite_path
        self.load_image(path)
        self.reset_view()

    def load_image(self, path):
        if path and os.path.isfile(path):
            try:
                self.raw_image = Image.open(path).convert("RGBA")
                if self.mode == "SHIP" and self.ship_project:
                    self.ship_project.sprite_w = self.raw_image.width
                    self.ship_project.sprite_h = self.raw_image.height
                elif self.mode == "WEAPON" and self.weapon_project:
                    if self.active_weapon_sprite == "TURRET":
                        self.weapon_project.turret_w = self.raw_image.width
                        self.weapon_project.turret_h = self.raw_image.height
                    else:
                        self.weapon_project.hardpoint_w = self.raw_image.width
                        self.weapon_project.hardpoint_h = self.raw_image.height
            except Exception as e:
                print(f"Error loading image: {e}")
                self.raw_image = None
        else:
            self.raw_image = None
        self.redraw()

    def reset_view(self):
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 600
        self.pan_x = w / 2.0
        self.pan_y = h / 2.0
        self.zoom = 2.5
        self.redraw()

    def on_mouse_wheel(self, event):
        factor = 1.15 if event.delta > 0 else 0.85
        new_zoom = max(0.4, min(16.0, self.zoom * factor))
        mx = event.x
        my = event.y
        self.pan_x = mx - (mx - self.pan_x) * (new_zoom / self.zoom)
        self.pan_y = my - (my - self.pan_y) * (new_zoom / self.zoom)
        self.zoom = new_zoom
        self.redraw()

    def start_pan(self, event):
        self.is_panning = True
        self.drag_data["pan_start_x"] = event.x
        self.drag_data["pan_start_y"] = event.y
        self.drag_data["orig_pan_x"] = self.pan_x
        self.drag_data["orig_pan_y"] = self.pan_y
        self.canvas.config(cursor="fleur")

    def do_pan(self, event):
        if self.is_panning:
            dx = event.x - self.drag_data["pan_start_x"]
            dy = event.y - self.drag_data["pan_start_y"]
            self.pan_x = self.drag_data["orig_pan_x"] + dx
            self.pan_y = self.drag_data["orig_pan_y"] + dy
            self.redraw()

    def end_pan(self, event):
        self.is_panning = False
        self.canvas.config(cursor="crosshair")

    # Coordinate mapping: Image coords (px, py) <-> Canvas Screen coords (sx, sy)
    def img_to_screen(self, ix, iy):
        if not self.raw_image:
            return self.pan_x, self.pan_y
        cx = self.raw_image.width / 2.0
        cy = self.raw_image.height / 2.0
        sx = self.pan_x + (ix - cx) * self.zoom
        sy = self.pan_y + (iy - cy) * self.zoom
        return sx, sy

    def screen_to_img(self, sx, sy):
        if not self.raw_image:
            return 0, 0
        cx = self.raw_image.width / 2.0
        cy = self.raw_image.height / 2.0
        ix = (sx - self.pan_x) / self.zoom + cx
        iy = (sy - self.pan_y) / self.zoom + cy
        return ix, iy

    # Starsector coords (ss_x, ss_y) <-> Screen coords (sx, sy)
    def ss_to_screen(self, ss_x, ss_y):
        if self.mode == "SHIP" and self.ship_project and self.raw_image:
            ix, iy = starsector_to_canvas(ss_x, ss_y, self.raw_image.height,
                                          self.ship_project.center[0], self.ship_project.center[1])
            return self.img_to_screen(ix, iy)
        elif self.mode == "WEAPON" and self.raw_image:
            cx = self.raw_image.width / 2.0
            cy = self.raw_image.height / 2.0
            ix = cx + ss_y
            iy = cy - ss_x
            return self.img_to_screen(ix, iy)
        return self.pan_x, self.pan_y

    def screen_to_ss(self, sx, sy):
        ix, iy = self.screen_to_img(sx, sy)
        if self.mode == "SHIP" and self.ship_project and self.raw_image:
            return canvas_to_starsector(ix, iy, self.raw_image.height,
                                        self.ship_project.center[0], self.ship_project.center[1])
        elif self.mode == "WEAPON" and self.raw_image:
            cx = self.raw_image.width / 2.0
            cy = self.raw_image.height / 2.0
            ss_y = round(ix - cx)
            ss_x = round(cy - iy)
            return ss_x, ss_y
        return 0, 0

    def draw_background_grid(self):
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 600

        # Subtle CAD grid lines every 40px
        step = 40.0
        start_x = self.pan_x % step
        start_y = self.pan_y % step

        x = start_x
        while x < w:
            self.canvas.create_line(x, 0, x, h, fill="#18202a", width=1)
            x += step

        y = start_y
        while y < h:
            self.canvas.create_line(0, y, w, y, fill="#18202a", width=1)
            y += step

        # Origin reference axes (Subtle cross)
        self.canvas.create_line(self.pan_x, 0, self.pan_x, h, fill="#283547", width=1, dash=(4, 4))
        self.canvas.create_line(0, self.pan_y, w, self.pan_y, fill="#283547", width=1, dash=(4, 4))

    def redraw(self):
        self.canvas.delete("all")
        self.item_hitboxes.clear()

        # 1. Background Blueprint Grid
        self.draw_background_grid()

        # 2. Draw Checkered Background & Sprite Image
        if self.raw_image:
            iw = int(self.raw_image.width * self.zoom)
            ih = int(self.raw_image.height * self.zoom)
            if iw > 0 and ih > 0:
                top_left_x = self.pan_x - iw / 2.0
                top_left_y = self.pan_y - ih / 2.0

                # Checkered transparency grid
                tile_size = 16
                rows = int(ih // tile_size) + 1
                cols = int(iw // tile_size) + 1
                for r in range(rows):
                    for c in range(cols):
                        bx1 = top_left_x + c * tile_size
                        by1 = top_left_y + r * tile_size
                        bx2 = min(bx1 + tile_size, top_left_x + iw)
                        by2 = min(by1 + tile_size, top_left_y + ih)
                        tile_color = "#1e2530" if (r + c) % 2 == 0 else "#27303d"
                        self.canvas.create_rectangle(bx1, by1, bx2, by2, fill=tile_color, outline="")

                # Crisp frame around sprite
                self.canvas.create_rectangle(top_left_x, top_left_y, top_left_x + iw, top_left_y + ih,
                                             outline="#38bdf8", width=1)

                resized = self.raw_image.resize((iw, ih), Image.Resampling.NEAREST)
                self.tk_image = ImageTk.PhotoImage(resized)
                self.canvas.create_image(self.pan_x, self.pan_y, image=self.tk_image)
        else:
            # High-Contrast Welcome / Instructions Card in Canvas Center
            cw = max(self.canvas.winfo_width(), 700)
            ch = max(self.canvas.winfo_height(), 500)
            cx = cw / 2.0
            cy = ch / 2.0

            card_w, card_h = 520, 220
            x1, y1 = cx - card_w / 2, cy - card_h / 2
            x2, y2 = cx + card_w / 2, cy + card_h / 2

            # Card drop shadow & background
            self.canvas.create_rectangle(x1 + 4, y1 + 4, x2 + 4, y2 + 4, fill="#0a0e14", outline="")
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#1e242c", outline="#38bdf8", width=2)

            self.canvas.create_text(cx, y1 + 26, text="✦ STARSECTOR SHIP & WEAPON FORGE ✦",
                                    fill="#38bdf8", font=("Segoe UI", 12, "bold"))
            self.canvas.create_text(cx, y1 + 48, text="No Sprite Image Currently Loaded",
                                    fill="#ffffff", font=("Segoe UI", 11, "bold"))
            self.canvas.create_line(x1 + 20, y1 + 64, x2 - 20, y1 + 64, fill="#374151", width=1)

            self.canvas.create_text(cx - 220, y1 + 88, text="1. Click 'Load Sprite...' in the toolbar (or Ctrl+L) to load a ship PNG.",
                                    fill="#f8fafc", font=("Segoe UI", 9, "bold"), anchor="w")
            self.canvas.create_text(cx - 220, y1 + 112, text="2. Press F1 (Dimensions Guide) to view pixel guidelines or create a template.",
                                    fill="#f8fafc", font=("Segoe UI", 9, "bold"), anchor="w")
            self.canvas.create_text(cx - 220, y1 + 136, text="3. Open 'File -> Open Project...' (Ctrl+O) to load an existing project.",
                                    fill="#f8fafc", font=("Segoe UI", 9, "bold"), anchor="w")

            # Sample callout box
            self.canvas.create_rectangle(x1 + 20, y1 + 160, x2 - 20, y2 - 14, fill="#252e3b", outline="#475569")
            self.canvas.create_text(cx, y1 + 178, text="★ Quick Test: Open 'File -> Open Project' and select 'samples/carcinus.ssproj'!",
                                    fill="#facc15", font=("Segoe UI", 9, "bold"))
            return

        # 3. Ship Mode Overlays
        if self.mode == "SHIP" and self.ship_project:
            self.draw_ship_elements()
        # 4. Weapon Mode Overlays
        elif self.mode == "WEAPON" and self.weapon_project:
            self.draw_weapon_elements()

    def draw_ship_elements(self):
        sp = self.ship_project

        # Center point (0, 0)
        cx, cy = self.ss_to_screen(0, 0)
        self.canvas.create_line(cx - 20, cy, cx + 20, cy, fill="#38bdf8", width=2)
        self.canvas.create_line(cx, cy - 20, cx, cy + 20, fill="#38bdf8", width=2)
        self.canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="#38bdf8", outline="#ffffff", width=1)
        self.canvas.create_text(cx + 8, cy - 8, text="(0, 0)", fill="#38bdf8", font=("Segoe UI", 8, "bold"))

        # Shield Bubble
        scx, scy = self.ss_to_screen(sp.shield_center[0], sp.shield_center[1])
        s_rad = sp.shield_radius * self.zoom
        self.canvas.create_oval(scx - s_rad, scy - s_rad, scx + s_rad, scy + s_rad,
                                outline="#06b6d4", width=2, dash=(6, 4))
        # Shield drag handle at right edge
        self.canvas.create_oval(scx + s_rad - 6, scy - 6, scx + s_rad + 6, scy + 6,
                                fill="#06b6d4", outline="#ffffff", width=2, tags="shield_handle")
        self.item_hitboxes["shield_handle"] = ("SHIELD", None)

        # Bounds Polygon
        if len(sp.bounds) >= 3:
            pts = []
            for idx, pt in enumerate(sp.bounds):
                bx, by = self.ss_to_screen(pt[0], pt[1])
                pts.extend([bx, by])
            # Draw connecting perimeter line
            pts.extend([pts[0], pts[1]])
            self.canvas.create_line(pts, fill="#22c55e", width=2)

            # Draw clickable vertex dots
            for idx, pt in enumerate(sp.bounds):
                bx, by = self.ss_to_screen(pt[0], pt[1])
                is_sel = (self.selected_item == ("BOUND", idx))
                fill_c = "#facc15" if is_sel else "#ffffff"
                outline_c = "#ffffff" if is_sel else "#15803d"
                tag = f"bound_{idx}"
                self.canvas.create_oval(bx - 5, by - 5, bx + 5, by + 5, fill=fill_c, outline=outline_c, width=2, tags=tag)
                self.item_hitboxes[tag] = ("BOUND", idx)

        # Engine Slots
        for idx, eng in enumerate(sp.engine_slots):
            self.draw_engine_slot(eng, idx)

        # Weapon Slots
        for idx, slot in enumerate(sp.weapon_slots):
            self.draw_weapon_slot(slot, idx)

    def draw_engine_slot(self, eng, idx):
        sx, sy = self.ss_to_screen(eng.x, eng.y)
        is_sel = (self.selected_item == ("ENGINE", eng))

        screen_deg = 270.0 - eng.angle
        rad = math.radians(screen_deg)

        flame_len = eng.length * self.zoom * 0.75
        flame_w = eng.width * self.zoom * 0.55

        fx = sx + math.cos(rad) * flame_len
        fy = sy + math.sin(rad) * flame_len
        perp = rad + math.pi / 2.0
        p1x = sx + math.cos(perp) * flame_w
        p1y = sy + math.sin(perp) * flame_w
        p2x = sx - math.cos(perp) * flame_w
        p2y = sy - math.sin(perp) * flame_w

        # Vibrant exhaust plume
        flame_fill = "#38bdf8" if eng.style == "HIGH_TECH" else "#f97316"
        self.canvas.create_polygon([p1x, p1y, fx, fy, p2x, p2y],
                                   fill=flame_fill, stipple="gray50", outline="")

        tag = f"engine_{idx}"
        bar_col = "#facc15" if is_sel else "#ef4444"
        self.canvas.create_line(p1x, p1y, p2x, p2y, fill=bar_col, width=4, tags=tag)
        self.canvas.create_oval(sx - 5, sy - 5, sx + 5, sy + 5, fill=bar_col, outline="#ffffff", width=2, tags=tag)
        self.item_hitboxes[tag] = ("ENGINE", eng)

    def draw_weapon_slot(self, slot, idx):
        sx, sy = self.ss_to_screen(slot.x, slot.y)
        is_sel = (self.selected_item == ("WEAPON", slot))

        rad_map = {"SMALL": 8, "MEDIUM": 14, "LARGE": 22}
        base_r = rad_map.get(slot.size, 11) * max(0.8, min(2.5, self.zoom * 0.4))

        color = WEAPON_COLORS.get(slot.type, "#ffffff")
        outline_col = "#ffffff" if is_sel else "#0f172a"
        tag = f"weapon_{idx}"

        # Firing Arc Cone
        if slot.arc < 360:
            cone_len = base_r + 28 * max(0.6, min(1.5, self.zoom * 0.4))
            center_deg = 270.0 - slot.angle
            half_arc = slot.arc / 2.0
            tk_start = - (center_deg + half_arc)
            self.canvas.create_arc(sx - cone_len, sy - cone_len, sx + cone_len, sy + cone_len,
                                   start=tk_start, extent=slot.arc,
                                   fill=color, stipple="gray25", outline=color, width=1)

        # Mount Base Shape
        if slot.mount == "HARDPOINT":
            self.canvas.create_rectangle(sx - base_r, sy - base_r * 1.3, sx + base_r, sy + base_r * 1.3,
                                         fill=color, outline=outline_col, width=3 if is_sel else 2, tags=tag)
        elif slot.mount == "HIDDEN":
            self.canvas.create_oval(sx - base_r, sy - base_r, sx + base_r, sy + base_r,
                                    outline=color, width=2, dash=(3, 3), tags=tag)
        else:  # TURRET
            self.canvas.create_oval(sx - base_r, sy - base_r, sx + base_r, sy + base_r,
                                    fill=color, outline=outline_col, width=3 if is_sel else 2, tags=tag)

        # Facing Arrow
        screen_deg = 270.0 - slot.angle
        rad = math.radians(screen_deg)
        arrow_len = base_r + 12
        ax = sx + math.cos(rad) * arrow_len
        ay = sy + math.sin(rad) * arrow_len
        self.canvas.create_line(sx, sy, ax, ay, fill="#ffffff", width=2, arrow="last", tags=tag)

        # High-Contrast Label Pill
        bbox_w = len(slot.id) * 3.8 + 6
        self.canvas.create_rectangle(sx - bbox_w, sy + base_r + 4, sx + bbox_w, sy + base_r + 18,
                                     fill="#11161d", outline="#475569", width=1)
        self.canvas.create_text(sx, sy + base_r + 11, text=slot.id, fill="#ffffff", font=("Segoe UI", 7, "bold"))
        self.item_hitboxes[tag] = ("WEAPON", slot)

    def draw_weapon_elements(self):
        wp = self.weapon_project
        offsets = wp.turret_offsets if self.active_weapon_sprite == "TURRET" else wp.hardpoint_offsets

        cx, cy = self.ss_to_screen(0, 0)
        self.canvas.create_line(cx - 15, cy, cx + 15, cy, fill="#38bdf8", width=2)
        self.canvas.create_line(cx, cy - 15, cx, cy + 15, fill="#38bdf8", width=2)

        for idx, pt in enumerate(offsets):
            sx, sy = self.ss_to_screen(pt[0], pt[1])
            is_sel = (self.selected_item == ("OFFSET", idx))
            col = "#facc15" if is_sel else "#ef4444"
            tag = f"offset_{idx}"

            self.canvas.create_line(sx - 10, sy, sx + 10, sy, fill=col, width=2, tags=tag)
            self.canvas.create_line(sx, sy - 10, sx, sy + 10, fill=col, width=2, tags=tag)
            self.canvas.create_oval(sx - 5, sy - 5, sx + 5, sy + 5, outline=col, width=2, tags=tag)

            bbox_w = 34
            self.canvas.create_rectangle(sx + 10, sy - 18, sx + 10 + bbox_w, sy - 4, fill="#11161d", outline="#475569")
            self.canvas.create_text(sx + 27, sy - 11, text=f"B-{idx+1}", fill="#ffffff", font=("Segoe UI", 7, "bold"))
            self.item_hitboxes[tag] = ("OFFSET", idx)

    # Mouse Handlers
    def on_left_down(self, event):
        hit = self.find_hit(event.x, event.y)
        if hit:
            self.selected_item = hit
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

            if hit[0] == "WEAPON":
                self.drag_data["orig_ss_x"] = hit[1].x
                self.drag_data["orig_ss_y"] = hit[1].y
            elif hit[0] == "ENGINE":
                self.drag_data["orig_ss_x"] = hit[1].x
                self.drag_data["orig_ss_y"] = hit[1].y
            elif hit[0] == "BOUND":
                pt = self.ship_project.bounds[hit[1]]
                self.drag_data["orig_ss_x"] = pt[0]
                self.drag_data["orig_ss_y"] = pt[1]
            elif hit[0] == "OFFSET":
                offsets = self.weapon_project.turret_offsets if self.active_weapon_sprite == "TURRET" else self.weapon_project.hardpoint_offsets
                pt = offsets[hit[1]]
                self.drag_data["orig_ss_x"] = pt[0]
                self.drag_data["orig_ss_y"] = pt[1]
            elif hit[0] == "SHIELD":
                self.drag_data["orig_rad"] = self.ship_project.shield_radius

            if self.on_select_callback:
                self.on_select_callback(self.selected_item)
            self.redraw()
            return

        # Empty click in Add tool mode
        if self.tool_mode == "ADD_WEAPON" and self.ship_project:
            ss_x, ss_y = self.screen_to_ss(event.x, event.y)
            num = len(self.ship_project.weapon_slots) + 1
            default_arc = 10.0 if self.new_slot_mount == "HARDPOINT" else 120.0
            new_slot = WeaponSlot(
                slot_id=f"WS {num:03d}",
                x=ss_x, y=ss_y, angle=0.0, arc=default_arc,
                size=self.new_slot_size, mount=self.new_slot_mount, wpn_type=self.new_slot_type
            )
            self.ship_project.weapon_slots.append(new_slot)
            self.selected_item = ("WEAPON", new_slot)

            if self.symmetry_enabled and abs(ss_y) > 4:
                m_slot = WeaponSlot(
                    slot_id=f"WS {num+1:03d}",
                    x=ss_x, y=-ss_y, angle=-new_slot.angle, arc=new_slot.arc,
                    size=new_slot.size, mount=new_slot.mount, wpn_type=new_slot.type
                )
                self.ship_project.weapon_slots.append(m_slot)

            self.tool_mode = "SELECT"
            if self.on_change_callback: self.on_change_callback()
            if self.on_select_callback: self.on_select_callback(self.selected_item)
            self.redraw()

        elif self.tool_mode == "ADD_ENGINE" and self.ship_project:
            ss_x, ss_y = self.screen_to_ss(event.x, event.y)
            new_eng = EngineSlot(x=ss_x, y=ss_y, angle=180.0, length=40.0, width=12.0)
            self.ship_project.engine_slots.append(new_eng)
            self.selected_item = ("ENGINE", new_eng)

            if self.symmetry_enabled and abs(ss_y) > 4:
                m_eng = EngineSlot(x=ss_x, y=-ss_y, angle=360.0 - new_eng.angle, length=40.0, width=12.0)
                self.ship_project.engine_slots.append(m_eng)

            self.tool_mode = "SELECT"
            if self.on_change_callback: self.on_change_callback()
            if self.on_select_callback: self.on_select_callback(self.selected_item)
            self.redraw()

        else:
            self.selected_item = None
            if self.on_select_callback:
                self.on_select_callback(None)
            self.redraw()

    def on_left_drag(self, event):
        if not self.selected_item:
            return

        cur_ss_x, cur_ss_y = self.screen_to_ss(event.x, event.y)
        init_ss_x, init_ss_y = self.screen_to_ss(self.drag_data["x"], self.drag_data["y"])
        d_ss_x = cur_ss_x - init_ss_x
        d_ss_y = cur_ss_y - init_ss_y

        item_type = self.selected_item[0]
        item_obj = self.selected_item[1]

        if item_type == "WEAPON":
            item_obj.x = self.drag_data["orig_ss_x"] + d_ss_x
            item_obj.y = self.drag_data["orig_ss_y"] + d_ss_y
        elif item_type == "ENGINE":
            item_obj.x = self.drag_data["orig_ss_x"] + d_ss_x
            item_obj.y = self.drag_data["orig_ss_y"] + d_ss_y
        elif item_type == "BOUND":
            idx = item_obj
            self.ship_project.bounds[idx] = (self.drag_data["orig_ss_x"] + d_ss_x,
                                             self.drag_data["orig_ss_y"] + d_ss_y)
        elif item_type == "OFFSET":
            idx = item_obj
            offsets = self.weapon_project.turret_offsets if self.active_weapon_sprite == "TURRET" else self.weapon_project.hardpoint_offsets
            offsets[idx] = [self.drag_data["orig_ss_x"] + d_ss_x,
                            self.drag_data["orig_ss_y"] + d_ss_y]
        elif item_type == "SHIELD":
            scx, scy = self.ss_to_screen(self.ship_project.shield_center[0], self.ship_project.shield_center[1])
            dist = math.sqrt((event.x - scx)**2 + (event.y - scy)**2)
            self.ship_project.shield_radius = max(10.0, round(dist / self.zoom))

        if self.on_change_callback:
            self.on_change_callback()
        self.redraw()

    def on_left_up(self, event):
        if self.selected_item:
            item_type, item_obj = self.selected_item
            if item_type in ("WEAPON", "ENGINE"):
                self.drag_data["orig_ss_x"] = item_obj.x
                self.drag_data["orig_ss_y"] = item_obj.y
            elif item_type == "BOUND":
                if self.ship_project and item_obj < len(self.ship_project.bounds):
                    pt = self.ship_project.bounds[item_obj]
                    self.drag_data["orig_ss_x"] = pt[0]
                    self.drag_data["orig_ss_y"] = pt[1]
            elif item_type == "OFFSET":
                offsets = self.weapon_project.turret_offsets if self.active_weapon_sprite == "TURRET" else self.weapon_project.hardpoint_offsets
                if item_obj < len(offsets):
                    pt = offsets[item_obj]
                    self.drag_data["orig_ss_x"] = pt[0]
                    self.drag_data["orig_ss_y"] = pt[1]
            elif item_type == "SHIELD":
                self.drag_data["orig_rad"] = self.ship_project.shield_radius

            if self.on_change_callback:
                self.on_change_callback()
            self.redraw()

    def find_hit(self, sx, sy):
        for tag, item in self.item_hitboxes.items():
            bbox = self.canvas.bbox(tag)
            if bbox:
                x1, y1, x2, y2 = bbox
                if (x1 - 8 <= sx <= x2 + 8) and (y1 - 8 <= sy <= y2 + 8):
                    return item
        return None

    def delete_selected(self):
        if not self.selected_item:
            return
        item_type, item_obj = self.selected_item
        if item_type == "WEAPON" and self.ship_project:
            if item_obj in self.ship_project.weapon_slots:
                self.ship_project.weapon_slots.remove(item_obj)
        elif item_type == "ENGINE" and self.ship_project:
            if item_obj in self.ship_project.engine_slots:
                self.ship_project.engine_slots.remove(item_obj)
        elif item_type == "BOUND" and self.ship_project:
            idx = item_obj
            if 0 <= idx < len(self.ship_project.bounds):
                self.ship_project.bounds.pop(idx)
        elif item_type == "OFFSET" and self.weapon_project:
            offsets = self.weapon_project.turret_offsets if self.active_weapon_sprite == "TURRET" else self.weapon_project.hardpoint_offsets
            idx = item_obj
            if len(offsets) > 1 and 0 <= idx < len(offsets):
                offsets.pop(idx)

        self.selected_item = None
        if self.on_change_callback: self.on_change_callback()
        if self.on_select_callback: self.on_select_callback(None)
        self.redraw()

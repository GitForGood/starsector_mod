"""
Data models and coordinate transformations for ships, weapons, and project files.
"""

import copy
import csv
import json
import os
from .constants import (
    SHIP_DATA_HEADERS, WEAPON_DATA_HEADERS,
    DEFAULT_PRESETS
)

def canvas_to_starsector(cx, cy, img_h, center_x, center_y):
    """Converts image pixel coords (0,0 at top-left) to Starsector ship coordinates."""
    ss_x = round((img_h - cy) - center_x)
    ss_y = round(center_y - cx)
    return ss_x, ss_y

def starsector_to_canvas(ss_x, ss_y, img_h, center_x, center_y):
    """Converts Starsector ship coordinates to image pixel coords (0,0 at top-left)."""
    cx = center_y - ss_y
    cy = img_h - (center_x + ss_x)
    return cx, cy

class WeaponSlot:
    def __init__(self, slot_id="WS 001", x=0, y=0, angle=0.0, arc=120.0,
                 size="SMALL", mount="TURRET", wpn_type="BALLISTIC"):
        self.id = slot_id
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)
        self.arc = float(arc)
        self.size = size.upper()
        self.mount = mount.upper()
        self.type = wpn_type.upper()

    def to_dict(self):
        return {
            "angle": self.angle,
            "arc": self.arc,
            "id": self.id,
            "locations": [self.x, self.y],
            "mount": self.mount,
            "size": self.size,
            "type": self.type
        }

    @classmethod
    def from_dict(cls, data):
        loc = data.get("locations", [0, 0])
        return cls(
            slot_id=data.get("id", "WS 001"),
            x=loc[0],
            y=loc[1],
            angle=data.get("angle", 0.0),
            arc=data.get("arc", 120.0),
            size=data.get("size", "SMALL"),
            mount=data.get("mount", "TURRET"),
            wpn_type=data.get("type", "BALLISTIC")
        )

class EngineSlot:
    def __init__(self, x=-40, y=0, angle=180.0, length=40.0, width=12.0,
                 contrail_size=32.0, style="MIDLINE"):
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)
        self.length = float(length)
        self.width = float(width)
        self.contrail_size = float(contrail_size)
        self.style = style.upper()

    def to_dict(self):
        return {
            "angle": self.angle,
            "contrailSize": self.contrail_size,
            "length": self.length,
            "location": [self.x, self.y],
            "style": self.style,
            "width": self.width
        }

    @classmethod
    def from_dict(cls, data):
        loc = data.get("location", [0, 0])
        return cls(
            x=loc[0],
            y=loc[1],
            angle=data.get("angle", 180.0),
            length=data.get("length", 40.0),
            width=data.get("width", 12.0),
            contrail_size=data.get("contrailSize", 32.0),
            style=data.get("style", "MIDLINE")
        )

class ShipProject:
    def __init__(self, hull_id="my_ship", hull_name="My Ship", hull_size="CRUISER"):
        self.hull_id = hull_id
        self.hull_name = hull_name
        self.hull_size = hull_size.upper()
        self.designation = "Cruiser"
        self.tech = "Midline"
        
        # Sprite
        self.sprite_path = ""
        self.sprite_w = 200
        self.sprite_h = 200
        self.center = [100, 100]  # [center_x (from bottom), center_y (from left)]
        
        # Geometry
        self.collision_radius = 120.0
        self.shield_center = [0.0, 0.0]
        self.shield_radius = 130.0
        self.bounds = []  # list of (x, y)
        
        # Slots
        self.weapon_slots = []
        self.engine_slots = []
        
        # CSV Stats (56 columns)
        self.stats = {h: "" for h in SHIP_DATA_HEADERS}
        self.apply_preset("CRUISER_MIDLINE")
        
        # Lore
        self.description = "A newly constructed vessel ready for sector deployment."

    def apply_preset(self, preset_key):
        p = DEFAULT_PRESETS.get(preset_key)
        if not p:
            return
        self.hull_size = p.get("size", self.hull_size)
        self.tech = p.get("tech", self.tech)
        
        s = self.stats
        s["name"] = self.hull_name
        s["id"] = self.hull_id
        s["designation"] = self.designation
        s["tech/manufacturer"] = self.tech
        s["system id"] = "maneuveringjets"
        s["fleet pts"] = str(p.get("fp", 15))
        s["hitpoints"] = str(p.get("hp", 8000))
        s["armor rating"] = str(p.get("armor", 1000))
        s["max flux"] = str(p.get("flux", 10000))
        s["flux dissipation"] = str(p.get("dissipation", 600))
        s["ordnance points"] = str(p.get("op", 150))
        s["max speed"] = str(p.get("speed", 55))
        s["acceleration"] = str(p.get("accel", 45))
        s["deceleration"] = str(p.get("decel", 35))
        s["max turn rate"] = str(p.get("turn", 25))
        s["turn acceleration"] = str(p.get("turn_accel", 35))
        s["mass"] = str(p.get("mass", 1200))
        s["shield type"] = p.get("shield_type", "FRONT")
        s["shield arc"] = str(p.get("shield_arc", 180))
        s["shield upkeep"] = str(p.get("shield_upkeep", 0.4))
        s["shield efficiency"] = str(p.get("shield_eff", 0.8))
        s["min crew"] = str(p.get("min_crew", 100))
        s["max crew"] = str(p.get("max_crew", 200))
        s["cargo"] = str(p.get("cargo", 120))
        s["fuel"] = str(p.get("fuel", 100))
        s["fuel/ly"] = str(p.get("fuel_ly", 3))
        s["range"] = "35"
        s["max burn"] = str(p.get("burn", 8))
        s["base value"] = str(p.get("value", 100000))
        s["cr %/day"] = "3"
        s["CR to deploy"] = "12"
        s["peak CR sec"] = "480"
        s["CR loss/sec"] = "0.25"
        s["supplies/rec"] = str(p.get("dp", 18))
        s["supplies/mo"] = str(p.get("dp", 18))
        s["tags"] = '"rare_bp, merc, ind"'
        s["codex variant id"] = f"{self.hull_id}_Assault"
        s["breakProb"] = "0.5"
        s["minPieces"] = "2"
        s["maxPieces"] = "3"

    def auto_generate_bounds(self):
        """Generates a starter symmetrical bounds polygon around the sprite dimensions."""
        h = self.sprite_h
        w = self.sprite_w
        cx = self.center[0]
        cy = self.center[1]
        
        # Use sprite box with 10% inset
        front_x = (h - int(h * 0.1)) - cx
        rear_x = -int(cx * 0.85)
        half_w = int(w * 0.42)
        
        self.bounds = [
            (front_x, 0),
            (int(front_x * 0.7), half_w),
            (0, half_w),
            (rear_x, int(half_w * 0.75)),
            (rear_x, int(half_w * 0.2)),
            (rear_x, -int(half_w * 0.2)),
            (rear_x, -int(half_w * 0.75)),
            (0, -half_w),
            (int(front_x * 0.7), -half_w)
        ]

    def to_ship_dict(self, sprite_rel_path=None):
        # Flatten bounds to [x1, y1, x2, y2, ...]
        flat_bounds = []
        for pt in self.bounds:
            flat_bounds.extend([pt[0], pt[1]])

        rel_spr = sprite_rel_path or f"graphics/ships/{self.hull_id}/{self.hull_id}.png"

        return {
            "bounds": flat_bounds,
            "builtInMods": [],
            "center": [self.center[0], self.center[1]],
            "collisionRadius": self.collision_radius,
            "engineSlots": [e.to_dict() for e in self.engine_slots],
            "height": self.sprite_h,
            "hullId": self.hull_id,
            "hullName": self.hull_name,
            "hullSize": self.hull_size,
            "shieldCenter": [self.shield_center[0], self.shield_center[1]],
            "shieldRadius": self.shield_radius,
            "spriteName": rel_spr,
            "style": self.tech.upper(),
            "viewOffset": 0,
            "weaponSlots": [w.to_dict() for w in self.weapon_slots],
            "width": self.sprite_w
        }

    def to_project_dict(self):
        return {
            "version": "1.0",
            "type": "SHIP",
            "hull_id": self.hull_id,
            "hull_name": self.hull_name,
            "hull_size": self.hull_size,
            "designation": self.designation,
            "tech": self.tech,
            "sprite_path": self.sprite_path,
            "sprite_w": self.sprite_w,
            "sprite_h": self.sprite_h,
            "center": self.center,
            "collision_radius": self.collision_radius,
            "shield_center": self.shield_center,
            "shield_radius": self.shield_radius,
            "bounds": self.bounds,
            "weapon_slots": [w.to_dict() for w in self.weapon_slots],
            "engine_slots": [e.to_dict() for e in self.engine_slots],
            "stats": self.stats,
            "description": self.description
        }

    @classmethod
    def from_project_dict(cls, d):
        proj = cls(d.get("hull_id", "my_ship"), d.get("hull_name", "My Ship"), d.get("hull_size", "CRUISER"))
        proj.designation = d.get("designation", "Cruiser")
        proj.tech = d.get("tech", "Midline")
        proj.sprite_path = d.get("sprite_path", "")
        proj.sprite_w = d.get("sprite_w", 200)
        proj.sprite_h = d.get("sprite_h", 200)
        proj.center = d.get("center", [proj.sprite_h // 2, proj.sprite_w // 2])
        proj.collision_radius = d.get("collision_radius", 120.0)
        proj.shield_center = d.get("shield_center", [0, 0])
        proj.shield_radius = d.get("shield_radius", 130.0)
        proj.bounds = [tuple(p) for p in d.get("bounds", [])]
        proj.weapon_slots = [WeaponSlot.from_dict(w) for w in d.get("weapon_slots", [])]
        proj.engine_slots = [EngineSlot.from_dict(e) for e in d.get("engine_slots", [])]
        proj.stats = d.get("stats", {h: "" for h in SHIP_DATA_HEADERS})
        proj.description = d.get("description", "")
        return proj

    def get_csv_row_values(self):
        self.stats["id"] = self.hull_id
        self.stats["name"] = self.hull_name
        self.stats["designation"] = self.designation
        self.stats["tech/manufacturer"] = self.tech
        self.stats["codex variant id"] = f"{self.hull_id}_Assault"
        return [self.stats.get(h, "") for h in SHIP_DATA_HEADERS]


class WeaponProject:
    def __init__(self, weapon_id="my_weapon", weapon_name="My Weapon", size="MEDIUM", wpn_type="BALLISTIC"):
        self.weapon_id = weapon_id
        self.weapon_name = weapon_name
        self.size = size.upper()
        self.type = wpn_type.upper()
        self.tech = "Midline"
        
        # Sprites
        self.turret_sprite_path = ""
        self.hardpoint_sprite_path = ""
        self.turret_w = 40
        self.turret_h = 40
        self.hardpoint_w = 26
        self.hardpoint_h = 44
        
        # Offsets where shots emerge [ [x1, y1], [x2, y2] ]
        self.turret_offsets = [[15, 0]]
        self.hardpoint_offsets = [[20, 0]]
        
        # CSV Stats (49 columns)
        self.stats = {h: "" for h in WEAPON_DATA_HEADERS}
        self.init_default_stats()
        
        self.description = "A newly manufactured tactical weapon platform."

    def init_default_stats(self):
        s = self.stats
        s["id"] = self.weapon_id
        s["name"] = self.weapon_name
        s["tier"] = "2"
        s["rarity"] = "0.5"
        s["base value"] = "1500"
        s["range"] = "700"
        s["damage/second"] = "200"
        s["damage/shot"] = "100"
        s["emp"] = "0"
        s["impact"] = "50"
        s["turn rate"] = "25"
        s["OPs"] = "8"
        s["type"] = "BALLISTIC"
        s["energy/shot"] = "50"
        s["chargeup"] = "0"
        s["chargedown"] = "0.5"
        s["burst size"] = "1"
        s["burst delay"] = "0"
        s["proj speed"] = "800"
        s["tags"] = '"rare_bp, merc, ind"'
        s["tech/manufacturer"] = self.tech

    def to_wpn_dict(self, turret_rel="", hardpoint_rel=""):
        # Flatten offsets: [x1, y1, x2, y2]
        t_off = []
        for pt in self.turret_offsets:
            t_off.extend([pt[0], pt[1]])
        h_off = []
        for pt in self.hardpoint_offsets:
            h_off.extend([pt[0], pt[1]])

        return {
            "id": self.weapon_id,
            "specClass": "projectile" if self.type != "BEAM" else "beam",
            "type": self.type,
            "size": self.size,
            "turretSprite": turret_rel or f"graphics/weapons/{self.weapon_id}_turret.png",
            "hardpointSprite": hardpoint_rel or f"graphics/weapons/{self.weapon_id}_hardpoint.png",
            "turretOffsets": t_off,
            "turretAngleOffsets": [0] * len(self.turret_offsets),
            "hardpointOffsets": h_off,
            "hardpointAngleOffsets": [0] * len(self.hardpoint_offsets),
            "barrelMode": "LINKED",
            "animationType": "MUZZLE_FLASH" if self.type != "BEAM" else "NONE",
            "projectileSpecId": f"{self.weapon_id}_shot"
        }

    def to_project_dict(self):
        return {
            "version": "1.0",
            "type": "WEAPON",
            "weapon_id": self.weapon_id,
            "weapon_name": self.weapon_name,
            "size": self.size,
            "wpn_type": self.type,
            "tech": self.tech,
            "turret_sprite_path": self.turret_sprite_path,
            "hardpoint_sprite_path": self.hardpoint_sprite_path,
            "turret_w": self.turret_w,
            "turret_h": self.turret_h,
            "hardpoint_w": self.hardpoint_w,
            "hardpoint_h": self.hardpoint_h,
            "turret_offsets": self.turret_offsets,
            "hardpoint_offsets": self.hardpoint_offsets,
            "stats": self.stats,
            "description": self.description
        }

    @classmethod
    def from_project_dict(cls, d):
        wpn = cls(d.get("weapon_id", "my_weapon"), d.get("weapon_name", "My Weapon"),
                  d.get("size", "MEDIUM"), d.get("wpn_type", "BALLISTIC"))
        wpn.tech = d.get("tech", "Midline")
        wpn.turret_sprite_path = d.get("turret_sprite_path", "")
        wpn.hardpoint_sprite_path = d.get("hardpoint_sprite_path", "")
        wpn.turret_w = d.get("turret_w", 40)
        wpn.turret_h = d.get("turret_h", 40)
        wpn.hardpoint_w = d.get("hardpoint_w", 26)
        wpn.hardpoint_h = d.get("hardpoint_h", 44)
        wpn.turret_offsets = d.get("turret_offsets", [[15, 0]])
        wpn.hardpoint_offsets = d.get("hardpoint_offsets", [[20, 0]])
        wpn.stats = d.get("stats", {h: "" for h in WEAPON_DATA_HEADERS})
        wpn.description = d.get("description", "")
        return wpn

    def get_csv_row_values(self):
        self.stats["id"] = self.weapon_id
        self.stats["name"] = self.weapon_name
        self.stats["tech/manufacturer"] = self.tech
        self.stats["type"] = self.type
        return [self.stats.get(h, "") for h in WEAPON_DATA_HEADERS]

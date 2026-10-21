#!/usr/bin/env python3
"""
Ship Scaffolding Tool for Starsector Mods
-----------------------------------------
Automates the creation of a new ship:
- Generates a templated PNG sprite
- Generates data/hulls/<id>.ship with bounds, engine slots, and weapon mounts
- Appends a balanced entry to data/hulls/ship_data.csv
- Generates data/variants/<id>/<id>_Assault.variant
- Appends lore to data/strings/descriptions.csv

Usage:
  Interactive:
    python tools/create_ship.py

  CLI:
    python tools/create_ship.py --id lobster --name "Lobster" --size CRUISER --tech Midline
"""

import argparse
import csv
import json
import math
import os
import struct
import sys
import zlib

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SHIP_DATA_CSV = os.path.join(BASE_DIR, "data", "hulls", "ship_data.csv")
DESCRIPTIONS_CSV = os.path.join(BASE_DIR, "data", "strings", "descriptions.csv")

# Baseline stats presets for quick balance
SIZE_PRESETS = {
    "FRIGATE": {
        "width": 80,
        "height": 90,
        "collisionRadius": 55,
        "fleet_pts": 5,
        "supplies_rec": 5,
        "hitpoints": 2400,
        "armor": 350,
        "flux": 3500,
        "dissipation": 220,
        "op": 55,
        "speed": 110,
        "accel": 150,
        "decel": 120,
        "turn": 75,
        "turn_accel": 120,
        "mass": 150,
        "min_crew": 15,
        "max_crew": 35,
        "cargo": 40,
        "fuel": 40,
        "base_value": 18000,
        "peak_cr": 240,
    },
    "DESTROYER": {
        "width": 120,
        "height": 130,
        "collisionRadius": 85,
        "fleet_pts": 9,
        "supplies_rec": 10,
        "hitpoints": 5000,
        "armor": 650,
        "flux": 6500,
        "dissipation": 400,
        "op": 100,
        "speed": 80,
        "accel": 80,
        "decel": 60,
        "turn": 40,
        "turn_accel": 60,
        "mass": 500,
        "min_crew": 50,
        "max_crew": 100,
        "cargo": 80,
        "fuel": 70,
        "base_value": 45000,
        "peak_cr": 360,
    },
    "CRUISER": {
        "width": 180,
        "height": 190,
        "collisionRadius": 130,
        "fleet_pts": 15,
        "supplies_rec": 18,
        "hitpoints": 9500,
        "armor": 1000,
        "flux": 11000,
        "dissipation": 650,
        "op": 160,
        "speed": 55,
        "accel": 45,
        "decel": 35,
        "turn": 22,
        "turn_accel": 30,
        "mass": 1400,
        "min_crew": 140,
        "max_crew": 250,
        "cargo": 150,
        "fuel": 120,
        "base_value": 110000,
        "peak_cr": 480,
    },
    "CAPITAL_SHIP": {
        "width": 260,
        "height": 300,
        "collisionRadius": 210,
        "fleet_pts": 30,
        "supplies_rec": 40,
        "hitpoints": 22000,
        "armor": 1700,
        "flux": 20000,
        "dissipation": 1100,
        "op": 300,
        "speed": 30,
        "accel": 20,
        "decel": 15,
        "turn": 10,
        "turn_accel": 12,
        "mass": 3200,
        "min_crew": 450,
        "max_crew": 800,
        "cargo": 350,
        "fuel": 300,
        "base_value": 350000,
        "peak_cr": 600,
    },
}

def generate_placeholder_sprite(filepath, width, height, tech):
    """Draws a clean pixel-art hull sprite template with centerline and mount markings."""
    grid = bytearray()
    
    # Color scheme based on tech
    if tech.upper() == "HIGH_TECH":
        hull_col = (30, 45, 65, 255)
        edge_col = (60, 110, 160, 255)
        core_col = (40, 190, 230, 255)
    elif tech.upper() == "LOW_TECH":
        hull_col = (55, 48, 42, 255)
        edge_col = (110, 85, 60, 255)
        core_col = (210, 110, 40, 255)
    else:  # MIDLINE / default
        hull_col = (45, 52, 60, 255)
        edge_col = (90, 105, 120, 255)
        core_col = (200, 140, 50, 255)

    cx = width / 2.0
    cy = height / 2.0
    
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0
        ny = (y - cy) / cy  # -1 at front (top), +1 at rear (bottom)
        for x in range(width):
            nx = (x - cx) / cx  # -1 to +1
            
            # Tapered teardrop / wedge hull formula
            max_r = 0.85 - 0.45 * (ny + 1) * 0.5  # wider at front/mid, tapering rear
            r = math.sqrt(nx * nx + ny * ny * 0.8)
            
            if r <= max_r:
                # Hull interior
                if r > max_r - 0.08:
                    col = edge_col
                elif abs(nx) < 0.03:
                    col = core_col  # Centerline marking
                elif (x + y) % 18 == 0:
                    col = edge_col  # Panel lines
                else:
                    col = hull_col
            else:
                col = (0, 0, 0, 0)
                
            raw.extend(col)

    compressed = zlib.compress(bytes(raw), 9)
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(png)

def create_ship(hull_id, hull_name, hull_size, tech="Midline", designation=None):
    hull_size = hull_size.upper()
    if hull_size not in SIZE_PRESETS:
        hull_size = "CRUISER"
        
    preset = SIZE_PRESETS[hull_size]
    w = preset["width"]
    h = preset["height"]
    radius = preset["collisionRadius"]
    
    if designation is None:
        designation = hull_size.capitalize().replace("_", " ")

    # 1. Generate Sprite
    sprite_rel = f"graphics/ships/{hull_id}/{hull_id}.png"
    sprite_path = os.path.join(BASE_DIR, *sprite_rel.split("/"))
    generate_placeholder_sprite(sprite_path, w, h, tech)
    print(f" [+] Generated sprite: {sprite_rel} ({w}x{h})")

    # 2. Build .ship JSON
    center_x = h // 2
    center_y = w // 2
    
    # Symmetrical placeholder bounds
    half_w = int(w * 0.42)
    half_h = int(h * 0.45)
    bounds = [
        half_h, 0,
        int(half_h * 0.6), half_w,
        -int(half_h * 0.7), int(half_w * 0.8),
        -half_h, int(half_w * 0.3),
        -half_h, -int(half_w * 0.3),
        -int(half_h * 0.7), -int(half_w * 0.8),
        int(half_h * 0.6), -half_w
    ]
    
    rear_x = -int(half_h * 0.85)
    eng_y = int(half_w * 0.35)
    engine_slots = [
        {
            "angle": 180,
            "contrailSize": 30,
            "length": 40,
            "location": [rear_x, eng_y],
            "style": tech.upper(),
            "width": 12
        },
        {
            "angle": 180,
            "contrailSize": 30,
            "length": 40,
            "location": [rear_x, -eng_y],
            "style": tech.upper(),
            "width": 12
        },
        # Lateral maneuver thrusters
        {
            "angle": 90,
            "contrailSize": 18,
            "length": 20,
            "location": [0, half_w - 4],
            "style": tech.upper(),
            "width": 8
        },
        {
            "angle": -90,
            "contrailSize": 18,
            "length": 20,
            "location": [0, -(half_w - 4)],
            "style": tech.upper(),
            "width": 8
        }
    ]
    
    # Starter weapon mounts
    weapon_slots = [
        {
            "angle": 0,
            "arc": 140,
            "id": "WS 001",
            "locations": [int(half_h * 0.4), 0],
            "mount": "TURRET",
            "size": "MEDIUM" if hull_size in ("CRUISER", "CAPITAL_SHIP") else "SMALL",
            "type": "BALLISTIC"
        },
        {
            "angle": 45,
            "arc": 120,
            "id": "WS 002",
            "locations": [0, int(half_w * 0.5)],
            "mount": "TURRET",
            "size": "SMALL",
            "type": "ENERGY"
        },
        {
            "angle": -45,
            "arc": 120,
            "id": "WS 003",
            "locations": [0, -int(half_w * 0.5)],
            "mount": "TURRET",
            "size": "SMALL",
            "type": "ENERGY"
        }
    ]

    ship_json = {
        "bounds": bounds,
        "builtInMods": [],
        "center": [center_x, center_y],
        "collisionRadius": radius,
        "engineSlots": engine_slots,
        "height": h,
        "hullId": hull_id,
        "hullName": hull_name,
        "hullSize": hull_size,
        "shieldCenter": [0, 0],
        "shieldRadius": radius + 4,
        "spriteName": sprite_rel,
        "style": tech.upper(),
        "viewOffset": 0,
        "weaponSlots": weapon_slots,
        "width": w
    }

    ship_file = os.path.join(BASE_DIR, "data", "hulls", f"{hull_id}.ship")
    with open(ship_file, "w") as f:
        json.dump(ship_json, f, indent=2)
    print(f" [+] Generated hull file: data/hulls/{hull_id}.ship")

    # 3. Add to ship_data.csv
    # Read existing headers
    with open(SHIP_DATA_CSV, "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
    
    row_dict = {col: "" for col in header}
    row_dict["name"] = hull_name
    row_dict["id"] = hull_id
    row_dict["designation"] = designation
    row_dict["tech/manufacturer"] = tech
    row_dict["system id"] = "maneuveringjets"
    row_dict["fleet pts"] = str(preset["fleet_pts"])
    row_dict["hitpoints"] = str(preset["hitpoints"])
    row_dict["armor rating"] = str(preset["armor"])
    row_dict["max flux"] = str(preset["flux"])
    row_dict["flux dissipation"] = str(preset["dissipation"])
    row_dict["ordnance points"] = str(preset["op"])
    row_dict["max speed"] = str(preset["speed"])
    row_dict["acceleration"] = str(preset["accel"])
    row_dict["deceleration"] = str(preset["decel"])
    row_dict["max turn rate"] = str(preset["turn"])
    row_dict["turn acceleration"] = str(preset["turn_accel"])
    row_dict["mass"] = str(preset["mass"])
    row_dict["shield type"] = "FRONT"
    row_dict["shield arc"] = "180"
    row_dict["shield upkeep"] = "0.4"
    row_dict["shield efficiency"] = "0.8"
    row_dict["min crew"] = str(preset["min_crew"])
    row_dict["max crew"] = str(preset["max_crew"])
    row_dict["cargo"] = str(preset["cargo"])
    row_dict["fuel"] = str(preset["fuel"])
    row_dict["fuel/ly"] = "2"
    row_dict["range"] = "30"
    row_dict["max burn"] = "8"
    row_dict["base value"] = str(preset["base_value"])
    row_dict["cr %/day"] = "3"
    row_dict["CR to deploy"] = "12"
    row_dict["peak CR sec"] = str(preset["peak_cr"])
    row_dict["CR loss/sec"] = "0.25"
    row_dict["supplies/rec"] = str(preset["supplies_rec"])
    row_dict["supplies/mo"] = str(preset["supplies_rec"])
    row_dict["tags"] = '"rare_bp, merc, ind"'
    row_dict["codex variant id"] = f"{hull_id}_Assault"
    row_dict["breakProb"] = "0.5"
    row_dict["minPieces"] = "2"
    row_dict["maxPieces"] = "3"

    # Append row
    row_values = [row_dict.get(c, "") for c in header]
    with open(SHIP_DATA_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row_values)
    print(f" [+] Appended entry to data/hulls/ship_data.csv")

    # 4. Generate Default Variant
    var_id = f"{hull_id}_Assault"
    variant_json = {
        "displayName": "Assault",
        "fluxCapacitors": 10,
        "fluxVents": 15,
        "goalVariant": True,
        "hullId": hull_id,
        "hullMods": ["targetingunit"],
        "permaMods": [],
        "sMods": [],
        "variantId": var_id,
        "weaponGroups": [
            {
                "autofire": False,
                "mode": "LINKED",
                "weapons": {
                    "WS 001": "heavymortar" if hull_size in ("CRUISER", "CAPITAL_SHIP") else "lightdualac"
                }
            },
            {
                "autofire": True,
                "mode": "LINKED",
                "weapons": {
                    "WS 002": "pdlaser",
                    "WS 003": "pdlaser"
                }
            }
        ],
        "wings": []
    }
    
    var_dir = os.path.join(BASE_DIR, "data", "variants", hull_id)
    os.makedirs(var_dir, exist_ok=True)
    var_file = os.path.join(var_dir, f"{var_id}.variant")
    with open(var_file, "w") as f:
        json.dump(variant_json, f, indent=2)
    print(f" [+] Generated variant: data/variants/{hull_id}/{var_id}.variant")

    # 5. Append to descriptions.csv
    desc_entry = [
        hull_id,
        "SHIP",
        f"A newly commissioned {designation.lower()} developed for frontline combat operations.",
        "", "", "", "", ""
    ]
    with open(DESCRIPTIONS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(desc_entry)
    print(f" [+] Appended lore to data/strings/descriptions.csv")

    print("\n=======================================================")
    print(f" Ship '{hull_name}' ({hull_id}) created successfully!")
    print(" Next steps:")
    print(f"  1. Edit sprite at: {sprite_rel}")
    print(f"  2. Open with Trylobot Ship Editor to place weapon mounts visually.")
    print(f"  3. Spawn in simulator or campaign with: addship {var_id}")
    print("=======================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Create a new Starsector ship.")
    parser.add_argument("--id", help="Hull ID (e.g., mantis)")
    parser.add_argument("--name", help="Display Name (e.g., Mantis)")
    parser.add_argument("--size", choices=["FRIGATE", "DESTROYER", "CRUISER", "CAPITAL_SHIP"], help="Hull size")
    parser.add_argument("--tech", default="Midline", help="Tech / Manufacturer (Midline, Low Tech, High Tech)")
    parser.add_argument("--designation", help="Designation (e.g., Heavy Cruiser, Fast Skiff)")

    args = parser.parse_args()

    if not args.id:
        print("=== Starsector Ship Creation Wizard ===")
        hull_id = input("Hull ID (e.g. karkinos): ").strip().lower().replace(" ", "_")
        if not hull_id:
            print("Error: Hull ID cannot be empty.")
            sys.exit(1)
        hull_name = input(f"Hull Name [{hull_id.capitalize()}]: ").strip() or hull_id.capitalize()
        print("\nShip Sizes: 1) FRIGATE  2) DESTROYER  3) CRUISER  4) CAPITAL_SHIP")
        size_choice = input("Select size [3]: ").strip()
        size_map = {"1": "FRIGATE", "2": "DESTROYER", "3": "CRUISER", "4": "CAPITAL_SHIP"}
        hull_size = size_map.get(size_choice, "CRUISER")
        tech = input("Tech style [Midline]: ").strip() or "Midline"
        designation = input(f"Designation [{hull_size.capitalize()}]: ").strip() or None
        create_ship(hull_id, hull_name, hull_size, tech, designation)
    else:
        name = args.name or args.id.capitalize()
        size = args.size or "CRUISER"
        create_ship(args.id, name, size, args.tech, args.designation)

if __name__ == "__main__":
    main()

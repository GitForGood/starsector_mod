"""
Constants, reference dimensions, CSV headers, and baseline presets
for the Starsector Ship & Weapon Forge.
"""

# CSV Headers
SHIP_DATA_HEADERS = [
    "name", "id", "designation", "tech/manufacturer", "system id", "fleet pts",
    "hitpoints", "armor rating", "max flux", "8/6/5/4%", "flux dissipation",
    "ordnance points", "fighter bays", "max speed", "acceleration", "deceleration",
    "max turn rate", "turn acceleration", "mass", "shield type", "defense id",
    "shield arc", "shield upkeep", "shield efficiency", "phase cost", "phase upkeep",
    "min crew", "max crew", "cargo", "fuel", "fuel/ly", "range", "max burn",
    "base value", "cr %/day", "CR to deploy", "peak CR sec", "CR loss/sec",
    "supplies/rec", "supplies/mo", "c/s", "c/f", "f/s", "f/f", "crew/s", "crew/f",
    "hints", "tags", "logistics n/a reason", "codex variant id", "rarity",
    "breakProb", "minPieces", "maxPieces", "travel drive", "number"
]

WEAPON_DATA_HEADERS = [
    "name", "id", "tier", "rarity", "base value", "range", "damage/second",
    "damage/shot", "emp", "impact", "turn rate", "OPs", "ammo", "ammo/sec",
    "reload size", "type", "energy/shot", "energy/second", "chargeup", "chargedown",
    "burst size", "burst delay", "min spread", "max spread", "spread/shot",
    "spread decay/sec", "beam speed", "proj speed", "launch speed", "flight time",
    "proj hitpoints", "autofireAccBonus", "extraArcForAI", "hints", "tags",
    "groupTag", "tech/manufacturer", "for weapon tooltip>>", "primaryRoleStr",
    "speedStr", "trackingStr", "turnRateStr", "accuracyStr", "customPrimary",
    "customPrimaryHL", "customAncillary", "customAncillaryHL", "noDPSInTooltip", "number"
]

# Color Coding for Weapon Mount Types on Canvas
WEAPON_COLORS = {
    "BALLISTIC": "#f59e0b",   # Amber / Orange
    "ENERGY": "#06b6d4",      # Cyan
    "MISSILE": "#10b981",     # Green
    "COMPOSITE": "#84cc16",   # Lime
    "SYNERGY": "#8b5cf6",     # Purple
    "HYBRID": "#ec4899",      # Pink
    "UNIVERSAL": "#f8fafc",   # White
    "DECORATIVE": "#64748b",  # Slate
    "SYSTEM": "#38bdf8",      # Sky blue
}

MOUNT_SIZES = ["SMALL", "MEDIUM", "LARGE"]
MOUNT_TYPES = ["TURRET", "HARDPOINT", "HIDDEN"]
WEAPON_TYPES = ["BALLISTIC", "ENERGY", "MISSILE", "COMPOSITE", "SYNERGY", "HYBRID", "UNIVERSAL", "DECORATIVE", "SYSTEM"]
ENGINE_STYLES = ["MIDLINE", "LOW_TECH", "HIGH_TECH"]
SHIELD_TYPES = ["FRONT", "OMNI", "NONE", "PHASE"]

# Dimensional Guidelines
GUIDELINES_SHIPS = {
    "FIGHTER": {
        "width_range": (20, 35),
        "height_range": (20, 40),
        "examples": "Talon (24x24), Broadsword (30x33), Warthog (30x28)",
        "notes": "Minimal hull greebles, 1-3 small mounts or built-in weapons."
    },
    "FRIGATE": {
        "width_range": (50, 85),
        "height_range": (70, 115),
        "examples": "Wolf (52x96), Lasher (68x96), Tempest (64x92), Brawler (110x54)",
        "notes": "Typically 3-6 small mounts, occasionally 1 medium mount."
    },
    "DESTROYER": {
        "width_range": (100, 145),
        "height_range": (130, 185),
        "examples": "Hammerhead (108x164), Enforcer (136x136), Sunder (112x192), Medusa (134x138)",
        "notes": "Workhorse ships with 1-3 medium mounts and multiple smalls."
    },
    "CRUISER": {
        "width_range": (140, 200),
        "height_range": (200, 270),
        "examples": "Eagle (168x218), Falcon (162x222), Dominator (220x180), Champion (180x240)",
        "notes": "Wide silhouettes up to 220px. 1-2 large mounts or heavy medium batteries."
    },
    "CAPITAL": {
        "width_range": (180, 340),
        "height_range": (300, 420),
        "examples": "Onslaught (288x384), Paragon (330x364), Odyssey (168x400), Invictus (364x420)",
        "notes": "Dominant presence, multi-layered plating, 2-5 large weapon mounts."
    }
}

GUIDELINES_MOUNTS = {
    "SMALL": {
        "turret_well_dia": "10 - 14 px",
        "weapon_base_dia": "14 - 16 px",
        "clearance_dia": "24 - 30 px",
        "hardpoint_cutout": "10 - 14 px wide x 12 - 18 px deep",
        "typical_weapons": "PD Laser, Vulcan, Light Dual AC, Railgun, Harpoon Rack"
    },
    "MEDIUM": {
        "turret_well_dia": "18 - 24 px",
        "weapon_base_dia": "22 - 28 px",
        "clearance_dia": "40 - 48 px",
        "hardpoint_cutout": "18 - 22 px wide x 20 - 28 px deep",
        "typical_weapons": "Heavy Mauler, Heavy Needler, Pulse Laser, Heavy Blaster, Flak"
    },
    "LARGE": {
        "turret_well_dia": "30 - 38 px",
        "weapon_base_dia": "36 - 46 px",
        "clearance_dia": "64 - 72 px",
        "hardpoint_cutout": "28 - 36 px wide x 32 - 45 px deep",
        "typical_weapons": "Mark IX, Hellbore, Plasma Cannon, Autopulse, Gauss Cannon, Cyclone"
    }
}

GUIDELINES_ENGINES = {
    "Maneuvering / Retro": {
        "nozzle_width": "4 - 8 px",
        "nozzle_depth": "3 - 6 px",
        "contrail": "16 - 28",
        "notes": "Use 90°/-90° for strafe thrusters, 0° for braking thrusters."
    },
    "Frigate / Secondary": {
        "nozzle_width": "8 - 14 px",
        "nozzle_depth": "6 - 10 px",
        "contrail": "24 - 40",
        "notes": "Standard thrusters for frigates or wing thrusters on larger hulls."
    },
    "Cruiser Main": {
        "nozzle_width": "14 - 20 px",
        "nozzle_depth": "8 - 14 px",
        "contrail": "40 - 64",
        "notes": "Main engine bells positioned at aft hull recesses."
    },
    "Capital Main": {
        "nozzle_width": "22 - 36 px",
        "nozzle_depth": "12 - 20 px",
        "contrail": "64 - 128",
        "notes": "Massive fusion drives with prominent flame plumes."
    }
}

# Standard Baseline Presets
DEFAULT_PRESETS = {
    "FRIGATE_MIDLINE": {
        "size": "FRIGATE",
        "tech": "Midline",
        "hp": 2400, "armor": 350, "flux": 3500, "dissipation": 220, "op": 55,
        "speed": 110, "accel": 150, "decel": 120, "turn": 75, "turn_accel": 120,
        "mass": 150, "dp": 5, "fp": 5, "min_crew": 15, "max_crew": 35,
        "cargo": 40, "fuel": 40, "fuel_ly": 1, "burn": 10, "value": 18000,
        "shield_type": "FRONT", "shield_arc": 180, "shield_eff": 0.8, "shield_upkeep": 0.4
    },
    "DESTROYER_MIDLINE": {
        "size": "DESTROYER",
        "tech": "Midline",
        "hp": 5000, "armor": 650, "flux": 6500, "dissipation": 400, "op": 100,
        "speed": 80, "accel": 80, "decel": 60, "turn": 40, "turn_accel": 60,
        "mass": 500, "dp": 10, "fp": 9, "min_crew": 50, "max_crew": 100,
        "cargo": 80, "fuel": 70, "fuel_ly": 2, "burn": 9, "value": 45000,
        "shield_type": "FRONT", "shield_arc": 210, "shield_eff": 0.8, "shield_upkeep": 0.4
    },
    "CRUISER_MIDLINE": {
        "size": "CRUISER",
        "tech": "Midline",
        "hp": 9500, "armor": 1000, "flux": 11000, "dissipation": 650, "op": 160,
        "speed": 55, "accel": 45, "decel": 35, "turn": 22, "turn_accel": 30,
        "mass": 1400, "dp": 18, "fp": 15, "min_crew": 140, "max_crew": 250,
        "cargo": 150, "fuel": 120, "fuel_ly": 3, "burn": 8, "value": 110000,
        "shield_type": "FRONT", "shield_arc": 240, "shield_eff": 0.8, "shield_upkeep": 0.4
    },
    "CAPITAL_MIDLINE": {
        "size": "CAPITAL_SHIP",
        "tech": "Midline",
        "hp": 22000, "armor": 1600, "flux": 20000, "dissipation": 1100, "op": 300,
        "speed": 30, "accel": 20, "decel": 15, "turn": 10, "turn_accel": 12,
        "mass": 3200, "dp": 40, "fp": 30, "min_crew": 450, "max_crew": 800,
        "cargo": 350, "fuel": 300, "fuel_ly": 5, "burn": 7, "value": 350000,
        "shield_type": "FRONT", "shield_arc": 270, "shield_eff": 0.8, "shield_upkeep": 0.4
    }
}

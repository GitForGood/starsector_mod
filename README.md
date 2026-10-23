# Starsector Ship & Weapon Forge

A standalone desktop graphical interface tool for designing ships and weapons, configuring stats, placing mounts, and exporting directly into Starsector mods.

---

## Quick Start

### Option 1: Run Executable (No Python Required)
Double-click:
```text
StarsectorShipForge.exe
```

### Option 2: Run via Python
If you prefer running from source or want to modify the tool:
```bash
pip install -r requirements.txt
python run_ship_forge.py
```

---

## Key Features

### 1. Interactive Visual Canvas Editor
- **Pan & Zoom**: Scroll wheel to zoom (0.5x to 16x) centered on your cursor; right-click or middle-click drag to pan.
- **Weapon Mounts**: Drag-and-drop placement with mount style indicators (Turret circle vs Hardpoint notch), live firing arc cones (5° to 360°), and type color-coding (Ballistic = Amber, Energy = Cyan, Missile = Green, Synergy = Purple, etc.).
- **Engine Thrusters**: Live contrail flame triangles and nozzle bars oriented at exact exhaust angles (0° retro, 90°/-90° strafe, 180° main).
- **Collision Bounds**: Visual polygon boundary vertex editor with click-to-drag, auto-generation, and vertex management.
- **Symmetry (Mirror Y)**: Automatically creates and mirrors opposing flank mounts and engines with inverted angles.
- **Keyboard Nudge**: Arrow keys nudge selected mounts by 1 pixel for micro-adjustments.

### 2. Built-in Dimensions & Guidance (`F1`)
Open the **Dimensions Guide** anytime:
- **Mount Recess Specifications**: Exact pixel sizes for Small (`12px` well), Medium (`22px` well), and Large (`34px` well) turret wells, plus hardpoint notch cutouts and clearance buffers.
- **Ship Hull Class Scale**: Benchmark width and length ranges for Fighters, Frigates, Destroyers, Cruisers, and Capitals.
- **Engine Nozzle Proportions**: Nozzle width, depth, and contrail guidelines.
- **Blank Template Generator**: Choose a hull size class to generate a transparent PNG pre-marked with a vertical centerline and margin boundaries.

### 3. Precision Inspector Window
- **Selected Item Tab**: Exact numerical spinboxes for `Forward X`, `Lateral Y`, `Facing Angle` (with quick snap buttons for 0°, 90°, 180°, -90°), `Arc`, mount type, and size.
- **Ship Specs Tab**: Full control over all 56 `ship_data.csv` columns (Combat, Mobility, Shields, Logistics, System, and Codex lore).
- **Weapon Specs Tab**: Full control over all 49 `weapon_data.csv` columns (Damage, DPS, EMP, Range, Proj Speed, Refire cycles, and Flux costs).

### 4. Weapon Creation Mode
Switch toolbar to **Weapon Mode**:
- Load turret and hardpoint sprites.
- Place and drag **barrel offset points** where muzzle flashes and projectile origins are positioned.
- Export `.wpn` and `weapon_data.csv`.

### 5. Presets & Project Files
- **Project Files (`.ssproj`)**: Save and load complete project states, including paths to assets, placed mounts, polygon vertices, and custom stats. A complete sample is included at `samples/carcinus.ssproj`.
- **Preset Manager**: Apply baseline stats across hull sizes (Frigate, Destroyer, Cruiser, Capital; Midline, Low Tech, High Tech) or save your current tuning as a reusable custom preset.

### 6. Flexible Export to Mods (`Ctrl+E`)
- Pick any Starsector mod directory.
- **Ship Export**: Generates `.ship`, starter `.variant`, appends/updates codex lore in `descriptions.csv`, and copies the sprite to `graphics/ships/<id>/`.
- **Weapon Export**: Generates `.wpn`, `descriptions.csv`, and copies sprites to `graphics/weapons/`.
- **CSV Data Options**:
  - *Append / Update*: Inserts or updates the row directly in the mod's `ship_data.csv` or `weapon_data.csv`.
  - *Full Standalone Table*: Exports a complete standalone CSV table.
  - *Copy to Clipboard*: Copies the comma-separated data row to the Windows clipboard for pasting into spreadsheets.

---

## Repository Structure

```
├── StarsectorShipForge.exe     # Standalone Windows executable
├── run_ship_forge.py           # Python entrypoint
├── requirements.txt            # Python dependencies (pillow)
├── ship_forge/                 # Application source package
│   ├── app.py                  # Main application window & menus
│   ├── canvas_editor.py        # Interactive pan/zoom canvas & slot editor
│   ├── inspector.py            # Precision numeric inspector & specs tabs
│   ├── reference_guide.py      # Sprite dimensions guide & template generator
│   ├── export_dialogs.py       # CSV and mod exporter
│   ├── preset_dialogs.py       # Preset manager
│   ├── models.py               # Ship & weapon data structures & math
│   ├── constants.py            # CSV headers, guidelines, color tables
│   └── presets/                # Reusable JSON presets
└── samples/                    # Example projects
    ├── carcinus.ssproj
    └── carcinus/
        └── carcinus.png
```

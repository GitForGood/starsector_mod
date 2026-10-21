# Starsector Ship Modding Guide & Workflow

This guide explains how to add new ships to your Starsector mod easily and reliably, with clear workflows, balance guidelines, coordinate math, and debugging tips.

---

## 1. Mod Architecture Overview

In Starsector, adding a ship involves these linked files:

```
├── mod_info.json                             # Mod metadata (ID, version, dependencies)
├── data/
│   ├── hulls/
│   │   ├── ship_data.csv                     # Core stats (HP, armor, flux, speed, OP, DP)
│   │   └── <ship_id>.ship                   # Hull geometry (bounds, mounts, engines, sprite link)
│   ├── variants/
│   │   └── <ship_id>/
│   │       └── <ship_id>_<Variant>.variant   # Loadout (weapons, hullmods, vents, capacitors)
│   ├── hullmods/
│   │   └── hull_mods.csv                     # Custom hullmods (e.g. Decapod Propulsion)
│   ├── shipsystems/
│   │   ├── ship_systems.csv                  # Custom active systems (e.g. Skitter Drive)
│   │   └── <system_id>.system               # System visual/audio properties
│   ├── scripts/
│   │   ├── hullmods/*.java                   # Janino-compiled hullmod logic
│   │   └── shipsystems/*.java                # Janino-compiled system behavior
│   └── strings/
│       └── descriptions.csv                  # In-game lore and descriptions
└── graphics/
    └── ships/
        └── <ship_id>/<ship_id>.png          # Ship sprite (PNG format)
```

> [!NOTE]
> **No JDK or compilation required!** Starsector includes an internal Janino compiler. Any `.java` file in `data/scripts/` compiles automatically when the game launches.

---

## 2. Fast 1-Command Ship Scaffolding

To eliminate repetitive manual file creation and formatting errors, use `tools/create_ship.py`:

### Interactive Mode:
```bash
python tools/create_ship.py
```
Follow the interactive prompts to choose ship ID, display name, size class, and tech style.

### CLI Mode:
```bash
python tools/create_ship.py --id birgus --name "Birgus" --size DESTROYER --tech Midline
```

### What this tool automatically does:
1. Generates a pixel-art placeholder sprite in `graphics/ships/<id>/<id>.png`.
2. Generates `data/hulls/<id>.ship` with balanced collision bounds, engine slots, and starter weapon mounts.
3. Appends a balanced 56-column row to `data/hulls/ship_data.csv`.
4. Creates a combat-ready variant at `data/variants/<id>/<id>_Assault.variant`.
5. Adds codex lore to `data/strings/descriptions.csv`.

---

## 3. Visual Editing with the Starsector Ship Editor

While you can edit `.ship` files by hand, the official community **Trylobot Ship Editor** allows visual point-and-click placement of weapons, engines, and collision bounds.

1. Download the tool from the Fractal Softworks forums:
   - Search: *"Starsector Ship and Weapon Pack Ship Editor Trylobot"*
2. Run `ShipEditor.jar`.
3. In File -> Set Starsector Core Directory, select `C:\Program Files (x86)\Fractal Softworks\Starsector\starsector-core`.
4. Open any `.ship` file in `data/hulls/`.
5. Visually drag and drop weapon mounts, set firing arcs, and tweak engine nozzle positions.

---

## 4. Starsector Coordinate & Orientation Conventions

Understanding Starsector's coordinate space prevents misplaced weapon mounts and inverted engines:

### Sprite Orientation:
- Sprites in `graphics/ships/` are saved with the **bow (front) facing UP**.
- Image width is the lateral axis (port to starboard).
- Image height is the longitudinal axis (stern to bow).

### In-Game Coordinate Space (`.ship` file):
- `(0, 0)` is at the specified `"center": [centerX, centerY]`.
- **+X** is **Forward** (towards bow / top of sprite).
- **-X** is **Aft / Rear** (towards stern / bottom of sprite).
- **+Y** is **Port / Left** (towards left side of sprite).
- **-Y** is **Starboard / Right** (towards right side of sprite).

### Facing Angles:
- `0°`: Facing Forward (+X)
- `90°`: Facing Port / Left (+Y)
- `180°`: Facing Aft / Rear (-X)
- `270°` (or `-90°`): Facing Starboard / Right (-Y)

### Engine Angles & Plumes:
Engine nozzles point in the direction the exhaust **flame shoots out**:
- **Main forward thrust**: `angle: 180` (shoots flame rearward, pushing ship forward).
- **Retro / braking thrust**: `angle: 0` (shoots flame forward, stopping forward movement).
- **Port strafe thruster**: `angle: -90` (shoots flame right to push ship left).
- **Starboard strafe thruster**: `angle: 90` (shoots flame left to push ship right).

---

## 5. Quick Balance Reference Table

Use these baseline stats to keep your custom ships feeling balanced alongside vanilla ships:

| Size Class | Deployment (DP) | Hull HP | Armor | Max Speed | Max Flux | Flux Diss. | Ordnance Pts (OP) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Frigate** | 4 – 8 | 1,800 – 3,500 | 250 – 500 | 90 – 140 | 2,500 – 4,500 | 150 – 300 | 45 – 70 |
| **Destroyer** | 8 – 14 | 4,000 – 6,500 | 500 – 800 | 70 – 100 | 5,000 – 8,000 | 300 – 500 | 85 – 125 |
| **Cruiser** | 15 – 25 | 8,000 – 13,000 | 900 – 1,400 | 45 – 70 | 9,000 – 14,000 | 550 – 850 | 140 – 190 |
| **Capital** | 30 – 50 | 18,000 – 30,000 | 1,400 – 2,200 | 25 – 45 | 18,000 – 28,000 | 900 – 1,500 | 270 – 370 |

---

## 6. Case Study: The "Crab" Locomotion Model

The **Carcinus-class Skitter Cruiser** demonstrates how to create unique movement archetypes:

1. **Base Hull (`ship_data.csv`)**:
   - `max speed`: **45** (intentionally low forward advance).
   - `max turn rate`: **30** & `turn acceleration`: **55** (exceptionally high turn agility).
2. **Built-in Hullmod (`Decapod Propulsion Grid`)**:
   - Monitored every combat tick via `advanceInCombat()`.
   - When strafing (`isStrafingLeft()` or `isStrafingRight()`):
     - Adds **+35 flat speed** (raising strafe speed to **80**).
     - Boosts acceleration by **+120%**.
   - Result: The ship moves sideways faster than it can move forward or reverse!
3. **Lateral Thruster Array**:
   - 6 engine slots configured with `90°` and `-90°` angles along the flanks fire active plumes during lateral movement.
4. **Ship System (`Lateral Skitter Drive`)**:
   - Provides an instant burst of +75 speed and +300% acceleration for evasive repositioning.

---

## 7. Pre-Flight Verification & Testing

Before launching Starsector, run the validator to prevent launch-time crashes:

```bash
python tools/validate_mod.py
```

This verifies:
- All CSV column counts match vanilla requirements (preventing comma offset crashes).
- All `.ship` files have valid corresponding sprites.
- All `.variant` files link to existing hulls.
- Java packages match directory paths.

### In-Game Playtesting:
1. Ensure your repo is linked via `scripts/link_mod.ps1`.
2. Enable **Carcinus Shipyards** in the Starsector launcher.
3. In combat simulator or campaign with Console Commands enabled, press `Ctrl + Backspace`:
   ```text
   addship carcinus_Assault
   addship carcinus_Strike
   ```
